from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Dataset


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"C:\sevir1")


def load_year_rows(year: int, per_year: int) -> pd.DataFrame:
    catalog = pd.read_csv(DATA_ROOT / "data" / "sevir" / "CATALOG.csv", low_memory=False)
    # Restrict to storm-event labels that are stable in the local full-sample files.
    sub = catalog[
        (catalog["img_type"] == "vil")
        & (catalog["event_type"].isin(["Thunderstorm Wind", "Hail"]))
        & (catalog["file_name"].str.contains(f"/{year}/"))
    ].copy()
    available_parts = []
    for file_name, grp in sub.groupby("file_name", sort=False):
        h5_ids = _load_h5_ids(file_name)
        available_parts.append(grp[grp["id"].astype(str).isin(h5_ids)])
    sub = pd.concat(available_parts, ignore_index=True) if available_parts else sub.iloc[0:0].copy()
    sub["label"] = (sub["event_type"] == "Thunderstorm Wind").astype(int)
    if len(sub) > per_year:
        pos = sub[sub["label"] == 1]
        neg = sub[sub["label"] == 0]
        pos_n = min(len(pos), int(round(per_year * len(pos) / len(sub))))
        neg_n = per_year - pos_n
        if pos_n == 0:
            pos_n = min(len(pos), per_year // 2)
            neg_n = per_year - pos_n
        if neg_n > len(neg):
            neg_n = len(neg)
            pos_n = min(len(pos), per_year - neg_n)
        sampled = pd.concat(
            [
                pos.sample(n=pos_n, random_state=year),
                neg.sample(n=neg_n, random_state=year + 1),
            ],
            ignore_index=True,
        ).sample(frac=1.0, random_state=year + 2).reset_index(drop=True)
        return sampled
    return sub.sample(frac=1.0, random_state=year).reset_index(drop=True)


def _file_to_h5(rel_path: str) -> Path:
    return DATA_ROOT / "data" / "sevir" / rel_path


@lru_cache(maxsize=64)
def _load_id_index(rel_path: str) -> dict[str, int]:
    with h5py.File(_file_to_h5(rel_path), "r") as f:
        return {sid.decode("utf-8"): i for i, sid in enumerate(f["id"][()])}


@lru_cache(maxsize=64)
def _load_h5_ids(rel_path: str) -> set[str]:
    with h5py.File(_file_to_h5(rel_path), "r") as f:
        return {sid.decode("utf-8") for sid in f["id"][()]}


class SevirYearDataset(Dataset):
    def __init__(self, frame: pd.DataFrame):
        self.rows = frame.reset_index(drop=True)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        row = self.rows.iloc[idx]
        rel_path = row["file_name"]
        sample_id = str(row["id"])
        with h5py.File(_file_to_h5(rel_path), "r") as f:
            id_to_idx = _load_id_index(rel_path)
            if sample_id not in id_to_idx:
                raise IndexError(f"Sample id {sample_id} not found in {rel_path}")
            vil = f["vil"][id_to_idx[sample_id]].astype(np.float32)
        max_img = vil.max(axis=-1)
        mean_img = vil.mean(axis=-1)
        last_img = vil[..., -1]
        stack = np.stack([max_img, mean_img, last_img], axis=0) / 255.0
        x = torch.tensor(stack, dtype=torch.float32)
        x = F.interpolate(x.unsqueeze(0), size=(64, 64), mode="bilinear", align_corners=False).squeeze(0)
        y = torch.tensor(float(row["label"]), dtype=torch.float32)
        return x, y


class SmallCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.features(x)).squeeze(-1)


def threshold_metrics(y_true: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    thresholds = np.unique(np.quantile(scores, np.linspace(0.05, 0.95, 19)))
    best = {"bal_acc": -1.0, "thr": float(thresholds[0])}
    for thr in thresholds:
        pred = (scores >= thr).astype(np.int32)
        bal = balanced_accuracy_score(y_true, pred)
        if bal > best["bal_acc"]:
            best = {"bal_acc": float(bal), "thr": float(thr)}
    return best


def train_model(train_ds: Dataset, val_ds: Dataset) -> tuple[SmallCNN, dict[str, float]]:
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False, num_workers=0)
    model = SmallCNN()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    all_y = torch.cat([y for _, y in train_loader], dim=0)
    pos = float(all_y.sum())
    neg = float(len(all_y) - all_y.sum())
    pos_weight = torch.tensor(max(1.0, neg / max(pos, 1.0)), dtype=torch.float32)

    best_state = None
    best_val_auc = -1.0
    best_val_bal = -1.0
    for epoch in range(15):
        model.train()
        for xb, yb in train_loader:
            opt.zero_grad()
            logits = model(xb)
            loss = F.binary_cross_entropy_with_logits(logits, yb, pos_weight=pos_weight)
            loss.backward()
            opt.step()

        model.eval()
        val_scores = []
        val_targets = []
        with torch.no_grad():
            for xb, yb in val_loader:
                val_scores.append(torch.sigmoid(model(xb)).cpu().numpy())
                val_targets.append(yb.cpu().numpy())
        val_scores = np.concatenate(val_scores)
        val_targets = np.concatenate(val_targets)
        val_auc = float(roc_auc_score(val_targets, val_scores))
        val_thr = threshold_metrics(val_targets, val_scores)
        if (val_thr["bal_acc"] > best_val_bal) or (np.isclose(val_thr["bal_acc"], best_val_bal) and val_auc > best_val_auc):
            best_val_auc = val_auc
            best_val_bal = float(val_thr["bal_acc"])
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    assert best_state is not None
    model.load_state_dict(best_state)
    return model, {"val_auc": best_val_auc, "val_bal_acc": best_val_bal}


def eval_model(model: SmallCNN, ds: Dataset) -> tuple[np.ndarray, np.ndarray]:
    loader = DataLoader(ds, batch_size=64, shuffle=False, num_workers=0)
    scores = []
    targets = []
    model.eval()
    with torch.no_grad():
        for xb, yb in loader:
            scores.append(torch.sigmoid(model(xb)).cpu().numpy())
            targets.append(yb.cpu().numpy())
    return np.concatenate(targets), np.concatenate(scores)


def build_fallback_split(frames: list[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pooled = pd.concat([df for df in frames if len(df)], ignore_index=True)
    if pooled.empty:
        raise RuntimeError("No accessible SEVIR rows found in local mirror.")
    if len(pooled) < 20:
        raise RuntimeError(f"Accessible SEVIR subset too small for fallback split: n={len(pooled)}")
    train_df, temp_df = train_test_split(
        pooled,
        test_size=0.3,
        random_state=20260713,
        stratify=pooled["label"],
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        random_state=20260714,
        stratify=temp_df["label"],
    )
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


def main() -> int:
    per_year = 3000
    train_df = load_year_rows(2017, per_year)
    val_df = load_year_rows(2018, per_year)
    test_df = load_year_rows(2019, per_year)

    used_fallback = False
    if len(val_df) == 0 or len(test_df) == 0:
        train_df, val_df, test_df = build_fallback_split([train_df, val_df, test_df])
        used_fallback = True

    train_ds = SevirYearDataset(train_df)
    val_ds = SevirYearDataset(val_df)
    test_ds = SevirYearDataset(test_df)

    model, sel = train_model(train_ds, val_ds)
    y_train, train_scores = eval_model(model, train_ds)
    y_val, val_scores = eval_model(model, val_ds)
    y_test, test_scores = eval_model(model, test_ds)

    val_thr = threshold_metrics(y_val, val_scores)
    test_pred = (test_scores >= val_thr["thr"]).astype(np.int32)

    rows = [
        {"split": "train_2017", "n": len(y_train), "pos": int(y_train.sum()), "neg": int((1 - y_train).sum()), "auc": float(roc_auc_score(y_train, train_scores)), "best_bal_acc": threshold_metrics(y_train, train_scores)["bal_acc"]},
        {"split": "val_2018", "n": len(y_val), "pos": int(y_val.sum()), "neg": int((1 - y_val).sum()), "auc": float(roc_auc_score(y_val, val_scores)), "best_bal_acc": threshold_metrics(y_val, val_scores)["bal_acc"]},
        {"split": "test_2019", "n": len(y_test), "pos": int(y_test.sum()), "neg": int((1 - y_test).sum()), "auc": float(roc_auc_score(y_test, test_scores)), "best_bal_acc": threshold_metrics(y_test, test_scores)["bal_acc"], "acc@val_thr": float((test_pred == y_test).mean())},
    ]

    out_dir = ROOT / "results" / "sevir_external"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = ROOT / "figures" / "main"
    fig_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(rows).to_csv(out_dir / "sevir_year_holdout_cnn_fullsample_summary.csv", index=False, encoding="utf-8-sig")
    (out_dir / "sevir_year_holdout_cnn_fullsample_summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8-sig")

    summary = [
        "SEVIR year-holdout CNN full-sample validation",
        f"Per-year sample cap: {per_year}",
        f"Fallback split used: {used_fallback}",
        f"Train 2017 AUC={rows[0]['auc']:.4f} best_bal_acc={rows[0]['best_bal_acc']:.4f}",
        f"Val 2018 AUC={rows[1]['auc']:.4f} best_bal_acc={rows[1]['best_bal_acc']:.4f}",
        f"Test 2019 AUC={rows[2]['auc']:.4f} best_bal_acc={rows[2]['best_bal_acc']:.4f} acc@val_thr={rows[2]['acc@val_thr']:.4f}",
        f"Selected val metric: AUC={sel['val_auc']:.4f}, best_bal_acc={sel['val_bal_acc']:.4f}",
        f"Validation threshold={val_thr['thr']:.4f}",
    ]
    (log_dir / "sevir_year_holdout_cnn_fullsample_external_radar_validation_20260713.md").write_text("\n".join(summary), encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(6, 4))
    bins = np.linspace(0, 1, 21)
    ax.hist(test_scores[y_test == 0], bins=bins, alpha=0.7, label="neg")
    ax.hist(test_scores[y_test == 1], bins=bins, alpha=0.7, label="pos")
    ax.set_xlabel("Predicted probability")
    ax.set_ylabel("Count")
    ax.set_title("SEVIR full-sample year-holdout scores")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "figure7_sevir_year_holdout_cnn_fullsample.svg", dpi=160)
    plt.close(fig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
