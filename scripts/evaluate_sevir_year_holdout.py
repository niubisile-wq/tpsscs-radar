from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import roc_auc_score as sk_roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
import torch
from torch import nn


def split_year_from_path(path: str) -> int:
    m = re.search(r"/(\d{4})/SEVIR_", path.replace("\\", "/"))
    if not m:
        raise ValueError(f"Cannot infer year from {path!r}")
    return int(m.group(1))


def file_label(path: str) -> int:
    return 1 if "STORMEVENTS" in Path(path).name else 0


def episode_features(vil: np.ndarray) -> np.ndarray:
    # vil: [H, W, T] uint8
    # Use a deterministic spatial/temporal subsample to keep the feature
    # extractor cheap enough for the embedded runtime.
    x = vil[::4, ::4, ::2].astype(np.float32)
    frame_max = x.max(axis=(0, 1))
    frame_mean = x.mean(axis=(0, 1))
    frame_std = x.std(axis=(0, 1))
    quantiles = np.quantile(x.reshape(-1), [0.1, 0.25, 0.5, 0.75, 0.9]).astype(np.float32)
    diffs = np.diff(frame_mean, prepend=frame_mean[:1])
    trend = np.polyfit(np.arange(frame_mean.size, dtype=np.float32), frame_mean, deg=1)
    features = np.concatenate(
        [
            np.array(
                [
                    float(x.max()),
                    float(x.mean()),
                    float(x.std()),
                    float((x >= 20).mean()),
                    float((x >= 40).mean()),
                    float((x >= 60).mean()),
                    float(frame_max.mean()),
                    float(frame_max.std()),
                    float(frame_mean.mean()),
                    float(frame_mean.std()),
                    float(frame_std.mean()),
                    float(frame_std.std()),
                    float(diffs.mean()),
                    float(diffs.std()),
                    float(trend[0]),
                    float(trend[1]),
                ],
                dtype=np.float32,
            ),
            frame_max.astype(np.float32),
            frame_mean.astype(np.float32),
            frame_std.astype(np.float32),
            quantiles,
        ]
    )
    return features.astype(np.float32)


def roc_auc_score(y_true: np.ndarray, y_score: np.ndarray) -> float:
    try:
        return float(sk_roc_auc_score(np.asarray(y_true, dtype=np.int32), np.asarray(y_score, dtype=np.float64)))
    except Exception:
        return float("nan")


def best_threshold_metric(y_true: np.ndarray, y_score: np.ndarray) -> dict[str, float]:
    thresholds = np.unique(np.quantile(y_score, np.linspace(0.05, 0.95, 19)))
    best = {"bal_acc": -1.0, "threshold": float(thresholds[0])}
    for thr in thresholds:
        pred = (y_score >= thr).astype(np.int32)
        tp = int(((pred == 1) & (y_true == 1)).sum())
        tn = int(((pred == 0) & (y_true == 0)).sum())
        fp = int(((pred == 1) & (y_true == 0)).sum())
        fn = int(((pred == 0) & (y_true == 1)).sum())
        tpr = tp / max(tp + fn, 1)
        tnr = tn / max(tn + fp, 1)
        bal_acc = 0.5 * (tpr + tnr)
        if bal_acc > best["bal_acc"]:
            best = {
                "bal_acc": float(bal_acc),
                "threshold": float(thr),
                "tpr": float(tpr),
                "tnr": float(tnr),
                "tp": tp,
                "tn": tn,
                "fp": fp,
                "fn": fn,
            }
    return best


class TinyLogReg(nn.Module):
    def __init__(self, d: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d, 64),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)


def load_split_features(root: Path, year: int, max_per_file: int | None = None) -> pd.DataFrame:
    manifest = pd.read_csv(root / "data" / "manifests" / "sevir_evaluation_grid.csv")
    file_rows = manifest[manifest["file_name"].str.contains(f"/{year}/")].copy()
    file_rows["label"] = file_rows["file_name"].apply(file_label)

    rows: list[dict[str, Any]] = []
    for sample_file, grp in file_rows.groupby("file_name"):
        h5_path = root / "data" / "sevir" / sample_file
        indices = grp["h5_index"].tolist()
        with h5py.File(h5_path, "r") as f:
            chosen = indices[:max_per_file] if max_per_file is not None else indices
            for i in chosen:
                i = int(i)
                vil = f["vil"][i]
                feats = episode_features(vil)
                rows.append(
                    {
                        "sample_id": str(f["id"][i].decode("utf-8")),
                        "sample_file": sample_file,
                        "year": year,
                        "label": int(grp.loc[grp["h5_index"] == i, "label"].iloc[0]),
                        **{f"f{j}": float(v) for j, v in enumerate(feats)},
                    }
                )
    return pd.DataFrame(rows)


def standardize(train_x: np.ndarray, *xs: np.ndarray) -> tuple[np.ndarray, ...]:
    mean = train_x.mean(axis=0, keepdims=True)
    std = train_x.std(axis=0, keepdims=True) + 1e-6
    out = [(train_x - mean) / std]
    for x in xs:
        out.append((x - mean) / std)
    return tuple(out)


def train_logreg(x_train: np.ndarray, y_train: np.ndarray, steps: int = 600, lr: float = 0.05) -> TinyLogReg:
    x = torch.tensor(x_train, dtype=torch.float32)
    y = torch.tensor(y_train, dtype=torch.float32)
    model = TinyLogReg(x.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    pos = float(y.sum().item())
    neg = float((1.0 - y).sum().item())
    pos_weight = torch.tensor(max(1.0, neg / max(pos, 1.0)), dtype=torch.float32)
    for _ in range(steps):
        opt.zero_grad()
        logits = model(x)
        loss = nn.functional.binary_cross_entropy_with_logits(logits, y, pos_weight=pos_weight)
        loss.backward()
        opt.step()
    return model


def eval_probs(model: TinyLogReg, x: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        logits = model(torch.tensor(x, dtype=torch.float32))
        return torch.sigmoid(logits).cpu().numpy()


def summarize_split(name: str, y_true: np.ndarray, probs: np.ndarray, raw_score: np.ndarray) -> dict[str, Any]:
    auc = roc_auc_score(y_true, probs)
    raw_auc = roc_auc_score(y_true, raw_score)
    pred = (probs >= 0.5).astype(np.int32)
    acc = float((pred == y_true).mean())
    raw_best = best_threshold_metric(y_true, raw_score)
    prob_best = best_threshold_metric(y_true, probs)
    return {
        "split": name,
        "n": int(len(y_true)),
        "pos": int(y_true.sum()),
        "neg": int((1 - y_true).sum()),
        "auc": auc,
        "raw_auc": raw_auc,
        "acc@0.5": acc,
        "best_prob_bal_acc": prob_best["bal_acc"],
        "best_prob_thr": prob_best["threshold"],
        "best_raw_bal_acc": raw_best["bal_acc"],
        "best_raw_thr": raw_best["threshold"],
        "best_raw_tpr": raw_best["tpr"],
        "best_raw_tnr": raw_best["tnr"],
        "best_prob_tpr": prob_best["tpr"],
        "best_prob_tnr": prob_best["tnr"],
    }


def fit_candidate_models(x_train: np.ndarray, y_train: np.ndarray) -> dict[str, Any]:
    candidates = {
        "logreg": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=5000, class_weight="balanced", C=2.0, solver="lbfgs"),
        ),
        "gbdt": GradientBoostingClassifier(random_state=0, n_estimators=200, learning_rate=0.05, max_depth=2),
        "rf": RandomForestClassifier(
            random_state=0,
            n_estimators=400,
            max_depth=4,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
        ),
        "extra_trees": ExtraTreesClassifier(
            random_state=0,
            n_estimators=500,
            max_depth=5,
            min_samples_leaf=2,
            class_weight="balanced",
        ),
        "mlp": make_pipeline(
            StandardScaler(),
            MLPClassifier(
                random_state=0,
                hidden_layer_sizes=(64, 32),
                activation="relu",
                alpha=1e-3,
                learning_rate_init=0.01,
                max_iter=5000,
                early_stopping=True,
                n_iter_no_change=50,
            ),
        ),
    }
    fitted = {}
    for name, model in candidates.items():
        model.fit(x_train, y_train)
        fitted[name] = model
    return fitted


def predict_scores(model: Any, x: np.ndarray) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(x)
        return probs[:, 1]
    if hasattr(model, "decision_function"):
        scores = model.decision_function(x)
        scores = np.asarray(scores, dtype=np.float64)
        return 1.0 / (1.0 + np.exp(-scores))
    raise TypeError(f"Model {type(model)} does not expose scores")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"C:\sevir1")
    parser.add_argument("--max_per_file", type=int, default=96)
    args = parser.parse_args()

    root = Path(args.root)
    years = [2017, 2018, 2019]
    year_frames = {year: load_split_features(root, year, max_per_file=args.max_per_file) for year in years}

    train_df = year_frames[2017]
    val_df = year_frames[2018]
    test_df = year_frames[2019]

    feat_cols = [c for c in train_df.columns if c.startswith("f")]
    x_train_raw = train_df[feat_cols].to_numpy(dtype=np.float32)
    x_val_raw = val_df[feat_cols].to_numpy(dtype=np.float32)
    x_test_raw = test_df[feat_cols].to_numpy(dtype=np.float32)
    x_train, x_val, x_test = standardize(x_train_raw, x_val_raw, x_test_raw)
    y_train = train_df["label"].to_numpy(dtype=np.int32)
    y_val = val_df["label"].to_numpy(dtype=np.int32)
    y_test = test_df["label"].to_numpy(dtype=np.int32)

    fitted_models = fit_candidate_models(x_train, y_train)
    candidate_rows: list[dict[str, Any]] = []
    selected_name = None
    selected_val_bal_acc = -1.0
    selected_val_auc = -1.0
    selected_val_thr = None
    selected_val_probs = None
    selected_test_probs = None

    for name, model in fitted_models.items():
        val_probs = predict_scores(model, x_val)
        test_probs = predict_scores(model, x_test)
        val_auc = roc_auc_score(y_val, val_probs)
        test_auc = roc_auc_score(y_test, test_probs)
        val_thr = best_threshold_metric(y_val, val_probs)
        test_thr = best_threshold_metric(y_test, test_probs)
        candidate_rows.append(
            {
                "model": name,
                "val_auc": val_auc,
                "test_auc": test_auc,
                "val_best_bal_acc": val_thr["bal_acc"],
                "test_best_bal_acc": test_thr["bal_acc"],
                "val_best_thr": val_thr["threshold"],
                "test_best_thr": test_thr["threshold"],
                "test_best_tpr": test_thr["tpr"],
                "test_best_tnr": test_thr["tnr"],
            }
        )
        if (val_thr["bal_acc"] > selected_val_bal_acc) or (
            math.isclose(val_thr["bal_acc"], selected_val_bal_acc) and val_auc > selected_val_auc
        ):
            selected_name = name
            selected_val_bal_acc = float(val_thr["bal_acc"])
            selected_val_auc = float(val_auc)
            selected_val_thr = val_thr
            selected_val_probs = val_probs
            selected_test_probs = test_probs

    assert selected_name is not None and selected_val_thr is not None and selected_test_probs is not None and selected_val_probs is not None
    test_pred = (selected_test_probs >= selected_val_thr["threshold"]).astype(np.int32)

    test_auc = roc_auc_score(y_test, selected_test_probs)
    raw_test_auc = roc_auc_score(y_test, x_test_raw[:, 0])
    raw_mean_auc = roc_auc_score(y_test, x_test_raw[:, 1])
    test_bal_acc = balanced_accuracy_score(y_test, test_pred)
    raw_test_thr = best_threshold_metric(y_test, x_test_raw[:, 0])

    repo_root = Path(__file__).resolve().parents[1]
    result_dir = repo_root / "results" / "sevir_external"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir = repo_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = repo_root / "figures" / "main"
    fig_dir.mkdir(parents=True, exist_ok=True)

    rows = [
        summarize_split("train_2017", y_train, predict_scores(fitted_models[selected_name], x_train), x_train_raw[:, 0]),
        summarize_split("val_2018", y_val, selected_val_probs, x_val_raw[:, 0]),
        summarize_split("test_2019", y_test, selected_test_probs, x_test_raw[:, 0]),
    ]
    pd.DataFrame(rows).to_csv(result_dir / "sevir_year_holdout_summary.csv", index=False, encoding="utf-8-sig")
    (result_dir / "sevir_year_holdout_summary.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )

    report_lines = [
        "SEVIR year-holdout external radar validation",
        f"Root: {root}",
        f"Max per file: {args.max_per_file}",
        "",
        "Feature set:",
        " - episode max/mean/std",
        " - fraction above 20/40/60",
        " - per-frame max mean/std",
        " - per-frame mean mean/std",
        "",
        f"Selected model: {selected_name}",
        f"Validation threshold from 2018: {selected_val_thr['threshold']:.4f}",
        "",
        f"Test 2019 AUC={test_auc:.4f}",
        f"Test 2019 raw-AUC(on f0)={raw_test_auc:.4f}",
        f"Test 2019 raw-AUC(on f1)={raw_mean_auc:.4f}",
        f"Test 2019 balanced-acc@val-threshold={test_bal_acc:.4f}",
        f"Test 2019 raw-best-bal-acc={raw_test_thr['bal_acc']:.4f}",
        f"Test 2019 prob-best-bal-acc={best_threshold_metric(y_test, selected_test_probs)['bal_acc']:.4f}",
    ]
    report_lines.append("")
    report_lines.append("Candidate model sweep:")
    for row in sorted(candidate_rows, key=lambda r: (-r["val_best_bal_acc"], -r["val_auc"])):
        report_lines.append(
            f"- {row['model']}: val_auc={row['val_auc']:.4f} val_bal_acc={row['val_best_bal_acc']:.4f} "
            f"test_auc={row['test_auc']:.4f} test_bal_acc(best={row['test_best_bal_acc']:.4f})"
        )
    (log_dir / "sevir_year_holdout_external_radar_validation_20260713.md").write_text(
        "\n".join(report_lines),
        encoding="utf-8-sig",
    )

    # A compact score plot for the test split.
    fig, ax = plt.subplots(figsize=(6, 4))
    bins = np.linspace(0, 1, 21)
    ax.hist(selected_test_probs[y_test == 0], bins=bins, alpha=0.7, label="test negatives")
    ax.hist(selected_test_probs[y_test == 1], bins=bins, alpha=0.7, label="test positives")
    ax.set_xlabel("Predicted storm probability")
    ax.set_ylabel("Count")
    ax.set_title("SEVIR 2019 holdout score distribution")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "figure5_sevir_year_holdout.svg", dpi=160)
    plt.close(fig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
