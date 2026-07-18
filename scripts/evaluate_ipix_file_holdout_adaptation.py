from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evaluate_aistap_target_preservation_ablation import load_trainable_model
from evaluate_aistap_full_asset_candidate import conservative_cfar_threshold
from evaluate_ipix_external_detector_transfer import (
    low_rank_residual,
    read_ipix_windows,
    score_map,
    summarize_finished_detector,
    summarize_score,
)


IPIX_TARGET_BINS = {
    "19931107_135603_starea.cdf": (9, [8, 9, 10, 11]),
    "19931107_141630_starea.cdf": (9, [8, 9, 10, 11]),
    "19931107_145028_starea.cdf": (8, [7, 8, 9]),
    "19931108_213827_starea.cdf": (7, [6, 7, 8]),
    "19931108_220902_starea.cdf": (7, [6, 7, 8]),
    "19931109_191449_starea.cdf": (7, [6, 7, 8]),
    "19931109_202217_starea.cdf": (7, [6, 7, 8, 9]),
    "19931110_001635_starea.cdf": (7, [5, 6, 7, 8]),
    "19931111_163625_starea.cdf": (8, [7, 8, 9, 10]),
    "19931118_023604_stareC0000.cdf": (8, [7, 8, 9, 10]),
    "19931118_035737_stareC0000.cdf": (10, [8, 9, 10, 11, 12]),
    "19931118_162155_stareC0000.cdf": (7, [6, 7, 8, 9]),
    "19931118_162658_stareC0000.cdf": (7, [6, 7, 8, 9]),
    "19931118_174259_stareC0000.cdf": (7, [6, 7, 8, 9]),
}


def robust_z(score: np.ndarray, background_mask: np.ndarray) -> np.ndarray:
    logged = np.log1p(np.maximum(score, 0.0))
    bg = logged[background_mask]
    med = float(np.median(bg))
    mad = float(np.median(np.abs(bg - med)))
    scale = max(1.4826 * mad, 1e-6)
    return (logged - med) / scale


def feature_stack(
    raw_score: np.ndarray,
    low_score: np.ndarray,
    model_residual_score: np.ndarray,
    gate_score: np.ndarray,
    background_mask: np.ndarray,
) -> np.ndarray:
    raw_z = robust_z(raw_score, background_mask)
    low_z = robust_z(low_score, background_mask)
    residual_z = robust_z(model_residual_score, background_mask)
    gate_z = robust_z(gate_score, background_mask)
    raw_log = np.log1p(np.maximum(raw_score, 0.0))
    range_contrast = raw_log - np.median(raw_log, axis=0, keepdims=True)
    return np.stack(
        [
            raw_z,
            low_z,
            residual_z,
            gate_z,
            raw_z - low_z,
            gate_z - raw_z,
            residual_z - raw_z,
            range_contrast,
        ],
        axis=-1,
    )


def masks_for_file(filename: str, shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray, int, list[int]]:
    primary_bin, guard_bins = IPIX_TARGET_BINS[filename]
    primary_idx = primary_bin - 1
    guard_idx = {b - 1 for b in guard_bins}
    target_mask = np.zeros(shape, dtype=bool)
    target_mask[primary_idx, :] = True
    background_mask = np.ones(shape, dtype=bool)
    for idx in guard_idx:
        if 0 <= idx < background_mask.shape[0]:
            background_mask[idx, :] = False
    return target_mask, background_mask, primary_bin, guard_bins


def compute_item(
    x_np: np.ndarray,
    model: torch.nn.Module,
    filename: str,
) -> dict[str, Any]:
    target_mask, background_mask, primary_bin, guard_bins = masks_for_file(filename, x_np.shape[1:])
    x = torch.from_numpy(x_np).to(torch.complex128)
    with torch.no_grad():
        out = model(x)
    raw_score = score_map(x_np)
    low_score = score_map(low_rank_residual(x_np, model.rank))
    model_residual_score = score_map(out["residual"].detach().cpu().numpy())
    gate_score = out["score"].detach().cpu().numpy()
    features = feature_stack(raw_score, low_score, model_residual_score, gate_score, background_mask)
    return {
        "raw_score": raw_score,
        "low_score": low_score,
        "model_residual_score": model_residual_score,
        "gate_score": gate_score,
        "features": features,
        "target_mask": target_mask,
        "background_mask": background_mask,
        "primary_bin": primary_bin,
        "guard_bins": guard_bins,
    }


def sample_training_rows(
    item: dict[str, Any],
    rng: np.random.Generator,
    positives_per_window: int,
    negatives_per_window: int,
) -> tuple[np.ndarray, np.ndarray]:
    features = item["features"].reshape(-1, item["features"].shape[-1])
    target_flat = item["target_mask"].reshape(-1)
    background_flat = item["background_mask"].reshape(-1)
    pos_idx = np.flatnonzero(target_flat)
    neg_idx = np.flatnonzero(background_flat)
    if positives_per_window > 0 and pos_idx.size > positives_per_window:
        pos_idx = rng.choice(pos_idx, size=positives_per_window, replace=False)
    if negatives_per_window > 0 and neg_idx.size > negatives_per_window:
        neg_idx = rng.choice(neg_idx, size=negatives_per_window, replace=False)
    idx = np.concatenate([pos_idx, neg_idx])
    y = np.concatenate([np.ones(pos_idx.size, dtype=int), np.zeros(neg_idx.size, dtype=int)])
    return features[idx], y


def load_items(
    root: Path,
    files: list[str],
    model: torch.nn.Module,
    window: int,
    stride: int,
    max_windows_per_file: int | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    items: list[dict[str, Any]] = []
    info: dict[str, Any] = {"files": [], "window": window, "stride": stride}
    for filename in files:
        path = root / "data" / "downloads" / "ipix" / filename
        windows, file_info = read_ipix_windows(path, window=window, stride=stride, max_windows=max_windows_per_file)
        info["files"].append(file_info)
        for window_index, x_np in enumerate(windows):
            item = compute_item(x_np, model=model, filename=filename)
            item.update({"file": filename, "window_index": window_index, "item_id": f"{filename}#{window_index}"})
            items.append(item)
    return items, info


def train_calibrator(
    train_items: list[dict[str, Any]],
    seed: int,
    positives_per_window: int,
    negatives_per_window: int,
) -> tuple[Any, dict[str, Any]]:
    rng = np.random.default_rng(seed)
    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    for item in train_items:
        x, y = sample_training_rows(item, rng, positives_per_window, negatives_per_window)
        xs.append(x)
        ys.append(y)
    x_train = np.concatenate(xs, axis=0)
    y_train = np.concatenate(ys, axis=0)
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=500, class_weight="balanced", solver="lbfgs", random_state=seed),
    )
    model.fit(x_train, y_train)
    info = {
        "train_rows": int(x_train.shape[0]),
        "train_positive_rows": int(y_train.sum()),
        "train_negative_rows": int((1 - y_train).sum()),
        "feature_count": int(x_train.shape[1]),
    }
    return model, info


def evaluate_items(
    items: list[dict[str, Any]],
    calibrator: Any,
    pfas: list[float],
    rank: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for item in items:
        adapted_score = calibrator.decision_function(item["features"].reshape(-1, item["features"].shape[-1])).reshape(
            item["target_mask"].shape
        )
        method_rows: list[tuple[str, list[dict[str, Any]]]] = [
            (
                "raw",
                summarize_score(
                    item["raw_score"],
                    item["target_mask"],
                    item["background_mask"],
                    pfas,
                    "conservative_topk_strict_gt",
                ),
            ),
            (
                f"low_rank_residual_k{rank}",
                summarize_score(
                    item["low_score"],
                    item["target_mask"],
                    item["background_mask"],
                    pfas,
                    "conservative_topk_strict_gt",
                ),
            ),
            (
                "tpsscs_trainable_gate",
                summarize_score(
                    item["gate_score"],
                    item["target_mask"],
                    item["background_mask"],
                    pfas,
                    "conservative_topk_strict_gt",
                ),
            ),
            (
                "tpsscs_finished_detector",
                summarize_finished_detector(
                    item["model_residual_score"],
                    item["gate_score"],
                    item["target_mask"],
                    item["background_mask"],
                    pfas,
                ),
            ),
            (
                "ipix_adapted_tpsscs_calibrator",
                summarize_score(
                    adapted_score,
                    item["target_mask"],
                    item["background_mask"],
                    pfas,
                    "conservative_topk_strict_gt",
                ),
            ),
        ]
        for method, summaries in method_rows:
            for row in summaries:
                row.update(
                    {
                        "dataset": "IPIX_Dartmouth",
                        "file": item["file"],
                        "window_index": item["window_index"],
                        "item_id": item["item_id"],
                        "method": method,
                        "primary_target_bin_1indexed": item["primary_bin"],
                        "guard_bins_1indexed": ",".join(str(b) for b in item["guard_bins"]),
                    }
                )
                rows.append(row)
    return pd.DataFrame(rows)


def summarize_protocol(df: pd.DataFrame, lowrank_method: str, pfa_tolerance: float) -> dict[str, Any]:
    summary = (
        df.groupby(["method", "pfa_target"])
        .agg(
            pd_mean=("pd", "mean"),
            pd_std=("pd", "std"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_windows=("item_id", "nunique"),
        )
        .reset_index()
        if not df.empty
        else pd.DataFrame()
    )
    result: dict[str, Any] = {"passed": False, "failures": [], "comparisons": [], "summary": summary.to_dict("records")}
    methods = set(summary["method"].astype(str)) if not summary.empty else set()
    required = {"raw", lowrank_method, "ipix_adapted_tpsscs_calibrator"}
    missing = sorted(required - methods)
    if missing:
        result["failures"].append("missing methods: " + ", ".join(missing))
        return result
    pfas = sorted(summary["pfa_target"].unique())
    for pfa in pfas:
        adapted = summary[
            (summary["method"] == "ipix_adapted_tpsscs_calibrator") & (summary["pfa_target"] == pfa)
        ].iloc[0]
        raw = summary[(summary["method"] == "raw") & (summary["pfa_target"] == pfa)].iloc[0]
        low = summary[(summary["method"] == lowrank_method) & (summary["pfa_target"] == pfa)].iloc[0]
        observed = float(adapted["empirical_pfa_mean"])
        ceiling = float(pfa) * pfa_tolerance + 1e-7
        row = {
            "pfa": float(pfa),
            "adapted_pd": float(adapted["pd_mean"]),
            "raw_pd": float(raw["pd_mean"]),
            "lowrank_pd": float(low["pd_mean"]),
            "adapted_empirical_pfa": observed,
            "beats_raw": float(adapted["pd_mean"]) >= float(raw["pd_mean"]),
            "beats_lowrank": float(adapted["pd_mean"]) >= float(low["pd_mean"]),
            "pfa_calibrated": observed <= ceiling,
        }
        result["comparisons"].append(row)
        if not row["beats_raw"]:
            result["failures"].append(f"adapted TP-SSCS does not beat raw at Pfa {pfa:g}")
        if not row["beats_lowrank"]:
            result["failures"].append(f"adapted TP-SSCS does not beat {lowrank_method} at Pfa {pfa:g}")
        if not row["pfa_calibrated"]:
            result["failures"].append(f"adapted empirical Pfa {observed:.6g} exceeds ceiling {ceiling:.6g}")
    result["passed"] = not result["failures"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "第三批3"))
    parser.add_argument("--state", default="results/aistap_sample/tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt")
    parser.add_argument("--train-files", default="19931107_135603_starea.cdf,19931107_141630_starea.cdf")
    parser.add_argument("--test-files", default="19931107_145028_starea.cdf")
    parser.add_argument("--window", type=int, default=1024)
    parser.add_argument("--stride", type=int, default=1024)
    parser.add_argument("--max-windows-per-file", type=int, default=128)
    parser.add_argument("--positive-samples-per-window", type=int, default=256)
    parser.add_argument("--negative-samples-per-window", type=int, default=512)
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    root = Path(args.root)
    state_path = Path(args.state)
    if not state_path.is_absolute():
        state_path = root / state_path
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]
    train_files = [x.strip() for x in args.train_files.split(",") if x.strip()]
    test_files = [x.strip() for x in args.test_files.split(",") if x.strip()]
    max_windows = None if args.max_windows_per_file <= 0 else args.max_windows_per_file
    model = load_trainable_model(state_path)
    model.eval()

    train_items, train_load_info = load_items(root, train_files, model, args.window, args.stride, max_windows)
    test_items, test_load_info = load_items(root, test_files, model, args.window, args.stride, max_windows)
    calibrator, train_info = train_calibrator(
        train_items,
        seed=args.seed,
        positives_per_window=args.positive_samples_per_window,
        negatives_per_window=args.negative_samples_per_window,
    )
    df = evaluate_items(test_items, calibrator=calibrator, pfas=pfas, rank=int(model.rank))
    lowrank_method = f"low_rank_residual_k{int(model.rank)}"
    protocol = summarize_protocol(df, lowrank_method=lowrank_method, pfa_tolerance=args.pfa_tolerance)

    result_dir = root / "results" / "ipix_external"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    tag = args.date
    csv_path = result_dir / f"ipix_file_holdout_adaptation_{tag}.csv"
    json_path = result_dir / f"ipix_file_holdout_adaptation_{tag}.json"
    md_path = log_dir / f"ipix_file_holdout_adaptation_{tag}.md"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    payload = {
        "date": args.date,
        "state": str(state_path),
        "train_files": train_files,
        "test_files": test_files,
        "train_load_info": train_load_info,
        "test_load_info": test_load_info,
        "train_info": train_info,
        "protocol": protocol,
        "boundary": "Independent IPIX file-level holdout adaptation; train files and test files are disjoint.",
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# IPIX File-Holdout Adaptation",
        "",
        f"Date: {args.date}",
        "",
        "## Setup",
        "",
        f"- Train files: `{', '.join(train_files)}`",
        f"- Test files: `{', '.join(test_files)}`",
        f"- State: `{state_path}`",
        f"- Train rows: `{train_info['train_rows']}` (`{train_info['train_positive_rows']}` positive, `{train_info['train_negative_rows']}` negative)",
        "- Features: robust per-window score features from raw, low-rank residual, saved TP-SSCS residual/gate, and range-contrast; no range-bin index feature is used.",
        "",
        "## Verdict",
        "",
        f"- Passed: `{str(protocol['passed']).lower()}`",
        "",
        "## Test Comparisons",
        "",
        "| Pfa | Adapted Pd | Raw Pd | Low-rank Pd | Adapted empirical Pfa | Beats raw | Beats low-rank |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in protocol["comparisons"]:
        lines.append(
            f"| {row['pfa']:.0e} | {row['adapted_pd']:.4f} | {row['raw_pd']:.4f} | {row['lowrank_pd']:.4f} | {row['adapted_empirical_pfa']:.6g} | `{str(row['beats_raw']).lower()}` | `{str(row['beats_lowrank']).lower()}` |"
        )
    lines.extend(["", "## Failures", ""])
    if protocol["failures"]:
        for failure in protocol["failures"]:
            lines.append(f"- {failure}")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is an independent non-AISTAP IPIX file-level holdout test.",
            "- It uses target-bin annotations from the public IPIX page for training and evaluation.",
            "- It is stronger than zero-shot smoke testing only if the adapted detector beats raw and low-rank baselines on the held-out file.",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(csv_path)
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
