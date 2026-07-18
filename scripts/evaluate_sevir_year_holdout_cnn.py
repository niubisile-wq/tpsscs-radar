from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"C:\sevir1")


def load_manifest(year: int) -> list[dict[str, Any]]:
    manifest = pd.read_csv(DATA_ROOT / "data" / "manifests" / "sevir_evaluation_grid.csv")
    subset = manifest[manifest["file_name"].str.contains(f"/{year}/")].copy()
    subset["label"] = subset["file_name"].str.contains("STORMEVENTS").astype(int)
    return subset.to_dict(orient="records")


def load_image(h5_path: Path, idx: int) -> np.ndarray:
    with h5py.File(h5_path, "r") as f:
        vil = f["vil"][idx].astype(np.float32)  # [H, W, T]
    # Build a compact 3-channel representation: max, mean, last frame.
    max_img = vil.max(axis=-1)
    mean_img = vil.mean(axis=-1)
    last_img = vil[..., -1]
    stack = np.stack([max_img, mean_img, last_img], axis=0) / 255.0
    # Downsample to a fixed size so the CNN stays light.
    t = torch.tensor(stack, dtype=torch.float32).unsqueeze(0)
    t = F.interpolate(t, size=(96, 96), mode="bilinear", align_corners=False)
    return t.squeeze(0).numpy().astype(np.float32)


def build_split(year: int) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    rows = load_manifest(year)
    xs = []
    ys = []
    metas = []
    for row in rows:
        h5_path = DATA_ROOT / "data" / "sevir" / row["file_name"]
        x = load_image(h5_path, int(row["h5_index"]))
        xs.append(x)
        ys.append(int(row["label"]))
        metas.append(row)
    return np.stack(xs), np.asarray(ys, dtype=np.int64), metas


class SmallCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
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
        return self.head(self.net(x)).squeeze(-1)


def threshold_metrics(y_true: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    thresholds = np.unique(np.quantile(scores, np.linspace(0.05, 0.95, 19)))
    best = {"bal_acc": -1.0, "thr": float(thresholds[0])}
    for thr in thresholds:
        pred = (scores >= thr).astype(np.int32)
        bal = balanced_accuracy_score(y_true, pred)
        if bal > best["bal_acc"]:
            best = {"bal_acc": float(bal), "thr": float(thr)}
    return best


def train_model(x_train: np.ndarray, y_train: np.ndarray, x_val: np.ndarray, y_val: np.ndarray) -> tuple[SmallCNN, dict[str, float]]:
    train_ds = TensorDataset(torch.tensor(x_train), torch.tensor(y_train, dtype=torch.float32))
    train_loader = DataLoader(train_ds, batch_size=min(16, len(train_ds)), shuffle=True)

    model = SmallCNN()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    pos = float(y_train.sum())
    neg = float(len(y_train) - y_train.sum())
    pos_weight = torch.tensor(max(1.0, neg / max(pos, 1.0)), dtype=torch.float32)

    best_state = None
    best_val_auc = -1.0
    best_val_bal = -1.0
    for epoch in range(60):
        model.train()
        for xb, yb in train_loader:
            opt.zero_grad()
            logits = model(xb)
            loss = F.binary_cross_entropy_with_logits(logits, yb, pos_weight=pos_weight)
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            val_scores = torch.sigmoid(model(torch.tensor(x_val))).cpu().numpy()
        val_auc = float(roc_auc_score(y_val, val_scores))
        val_thr = threshold_metrics(y_val, val_scores)
        if (val_thr["bal_acc"] > best_val_bal) or (np.isclose(val_thr["bal_acc"], best_val_bal) and val_auc > best_val_auc):
            best_val_auc = val_auc
            best_val_bal = float(val_thr["bal_acc"])
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    assert best_state is not None
    model.load_state_dict(best_state)
    return model, {"val_auc": best_val_auc, "val_bal_acc": best_val_bal}


def main() -> int:
    train_x, train_y, train_meta = build_split(2017)
    val_x, val_y, val_meta = build_split(2018)
    test_x, test_y, test_meta = build_split(2019)

    model, sel = train_model(train_x, train_y, val_x, val_y)
    with torch.no_grad():
        train_scores = torch.sigmoid(model(torch.tensor(train_x))).cpu().numpy()
        val_scores = torch.sigmoid(model(torch.tensor(val_x))).cpu().numpy()
        test_scores = torch.sigmoid(model(torch.tensor(test_x))).cpu().numpy()

    val_thr = threshold_metrics(val_y, val_scores)
    test_pred = (test_scores >= val_thr["thr"]).astype(np.int32)

    rows = [
        {"split": "train_2017", "auc": float(roc_auc_score(train_y, train_scores)), "best_bal_acc": threshold_metrics(train_y, train_scores)["bal_acc"], "n": len(train_y), "pos": int(train_y.sum()), "neg": int((1 - train_y).sum())},
        {"split": "val_2018", "auc": float(roc_auc_score(val_y, val_scores)), "best_bal_acc": threshold_metrics(val_y, val_scores)["bal_acc"], "n": len(val_y), "pos": int(val_y.sum()), "neg": int((1 - val_y).sum())},
        {"split": "test_2019", "auc": float(roc_auc_score(test_y, test_scores)), "best_bal_acc": threshold_metrics(test_y, test_scores)["bal_acc"], "acc@val_thr": float((test_pred == test_y).mean()), "n": len(test_y), "pos": int(test_y.sum()), "neg": int((1 - test_y).sum())},
    ]

    out_dir = ROOT / "results" / "sevir_external"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = ROOT / "figures" / "main"
    fig_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(rows).to_csv(out_dir / "sevir_year_holdout_cnn_summary.csv", index=False, encoding="utf-8-sig")
    (out_dir / "sevir_year_holdout_cnn_summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8-sig")

    summary = [
        "SEVIR year-holdout CNN external radar validation",
        f"Train 2017 AUC={rows[0]['auc']:.4f} best_bal_acc={rows[0]['best_bal_acc']:.4f}",
        f"Val 2018 AUC={rows[1]['auc']:.4f} best_bal_acc={rows[1]['best_bal_acc']:.4f}",
        f"Test 2019 AUC={rows[2]['auc']:.4f} best_bal_acc={rows[2]['best_bal_acc']:.4f} acc@val_thr={rows[2]['acc@val_thr']:.4f}",
        f"Selected val threshold={val_thr['thr']:.4f}",
        f"Selection metric on val: AUC={sel['val_auc']:.4f}, best_bal_acc={sel['val_bal_acc']:.4f}",
    ]
    (log_dir / "sevir_year_holdout_cnn_external_radar_validation_20260713.md").write_text("\n".join(summary), encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(6, 4))
    bins = np.linspace(0, 1, 21)
    ax.hist(test_scores[test_y == 0], bins=bins, alpha=0.7, label="neg")
    ax.hist(test_scores[test_y == 1], bins=bins, alpha=0.7, label="pos")
    ax.set_xlabel("Predicted probability")
    ax.set_ylabel("Count")
    ax.set_title("SEVIR year-holdout CNN scores")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "figure6_sevir_year_holdout_cnn.svg", dpi=160)
    plt.close(fig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
