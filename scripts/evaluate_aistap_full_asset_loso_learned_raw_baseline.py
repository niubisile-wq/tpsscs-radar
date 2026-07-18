from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
from scipy import ndimage
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import evaluate_aistap_full_asset_classical_cfar_baselines as base


FEATURE_NAMES = [
    "log_raw_frame_z",
    "local_z_5",
    "local_z_17",
    "contrast_5",
    "contrast_17",
    "gradient_mag",
]


@dataclass
class TrainInfo:
    train_asset: str
    test_asset: str
    frames_seen: int
    positive_frames_seen: int
    positive_pixels: int
    background_pixels: int


def parse_floats(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def robust_scale(x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    median = float(np.median(x))
    mad = float(np.median(np.abs(x - median)))
    return (x - median) / (1.4826 * mad + eps)


def feature_cube(raw_score: np.ndarray) -> np.ndarray:
    score = np.asarray(raw_score, dtype=np.float64)
    log_raw = np.log1p(np.maximum(score, 0.0))
    frame_z = robust_scale(log_raw)

    feats = [frame_z]
    for size in (5, 17):
        local_mean = ndimage.uniform_filter(log_raw, size=size, mode="reflect")
        local_sq = ndimage.uniform_filter(log_raw * log_raw, size=size, mode="reflect")
        local_std = np.sqrt(np.maximum(local_sq - local_mean * local_mean, 1e-8))
        feats.append((log_raw - local_mean) / local_std)
    for size in (5, 17):
        local_mean = ndimage.uniform_filter(log_raw, size=size, mode="reflect")
        feats.append(log_raw - local_mean)

    gy, gx = np.gradient(log_raw)
    feats.append(np.sqrt(gx * gx + gy * gy))

    return np.stack(feats, axis=-1).astype(np.float32)


def frame_iter(asset_path: Path):
    with h5py.File(asset_path, "r") as f:
        refs = f["meta_per_image"][()].reshape(-1)
        for idx, ref in enumerate(refs):
            meta = base.read_meta(f, ref)
            x_np = base.to_complex(f["rd_img"][idx])
            raw_score = base.score_map(x_np)
            mask = base.target_mask(meta, raw_score.shape)
            yield idx, raw_score, mask


def collect_training_samples(
    asset_path: Path,
    rng: np.random.Generator,
    background_per_frame: int,
    max_frames: int | None,
) -> tuple[np.ndarray, np.ndarray, TrainInfo]:
    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    frames_seen = 0
    positive_frames_seen = 0
    positive_pixels = 0
    background_pixels = 0

    for idx, raw_score, mask in frame_iter(asset_path):
        if max_frames is not None and frames_seen >= max_frames:
            break
        frames_seen += 1
        feats = feature_cube(raw_score).reshape(-1, len(FEATURE_NAMES))
        flat_mask = mask.reshape(-1)
        pos_idx = np.flatnonzero(flat_mask)
        bg_idx = np.flatnonzero(~flat_mask)
        if pos_idx.size:
            positive_frames_seen += 1
            x_parts.append(feats[pos_idx])
            y_parts.append(np.ones(pos_idx.size, dtype=np.int8))
            positive_pixels += int(pos_idx.size)
        n_bg = min(background_per_frame, bg_idx.size)
        if n_bg:
            sample_bg = rng.choice(bg_idx, size=n_bg, replace=False)
            x_parts.append(feats[sample_bg])
            y_parts.append(np.zeros(n_bg, dtype=np.int8))
            background_pixels += int(n_bg)

    if not x_parts or positive_pixels == 0:
        raise ValueError(f"No positive training samples collected from {asset_path}")
    x = np.vstack(x_parts)
    y = np.concatenate(y_parts)
    info = TrainInfo(
        train_asset=asset_path.name,
        test_asset="",
        frames_seen=frames_seen,
        positive_frames_seen=positive_frames_seen,
        positive_pixels=positive_pixels,
        background_pixels=background_pixels,
    )
    return x, y, info


def train_logreg(x: np.ndarray, y: np.ndarray, max_iter: int, c_value: float) -> Pipeline:
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "logreg",
                LogisticRegression(
                    C=c_value,
                    class_weight="balanced",
                    max_iter=max_iter,
                    solver="lbfgs",
                    random_state=0,
                ),
            ),
        ]
    )
    model.fit(x, y)
    return model


def evaluate_model(
    model: Pipeline,
    train_asset_name: str,
    asset_path: Path,
    pfas: list[float],
    max_positive: int | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    positive_frames = 0
    evaluated_positive = 0

    for idx, raw_score, mask in frame_iter(asset_path):
        if not mask.any():
            continue
        positive_frames += 1
        if max_positive is not None and evaluated_positive >= max_positive:
            break
        feats = feature_cube(raw_score).reshape(-1, len(FEATURE_NAMES))
        score = model.predict_proba(feats)[:, 1].reshape(raw_score.shape)
        item_id = f"{asset_path.name}#{idx}"
        for row in base.summarize(score, mask, pfas, "loso_supervised_raw_feature_logreg_conservative_topk_strict_gt"):
            row.update(
                {
                    "asset": asset_path.name,
                    "image_index": idx,
                    "item_id": item_id,
                    "method": "loso_supervised_raw_feature_logreg",
                    "method_family": "learned_raw_feature_baseline",
                    "train_asset": train_asset_name,
                    "test_asset": asset_path.name,
                }
            )
            rows.append(row)
        evaluated_positive += 1

    info = {
        "test_asset": asset_path.name,
        "positive_frames": positive_frames,
        "evaluated_positive_frames": evaluated_positive,
    }
    return pd.DataFrame(rows), info


def load_existing_candidate_rows(root: Path, date_tag: str) -> pd.DataFrame:
    paths = sorted((root / "results" / "aistap_full_asset").glob(f"aistap_full_asset_detector_candidate_*_{date_tag}.csv"))
    if not paths:
        raise FileNotFoundError(f"No detector-candidate rows found for date {date_tag}")
    return pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)


def find_lowrank_method(methods: set[str]) -> str | None:
    candidates = sorted(m for m in methods if m.startswith("low_rank_residual_k"))
    rank30 = [m for m in candidates if m.endswith("30")]
    if rank30:
        return rank30[0]
    return candidates[-1] if candidates else None


def summarize_methods(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["asset", "pfa_target", "method"], dropna=False)
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined = (
        df.groupby(["pfa_target", "method"], dropna=False)
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined["asset"] = "combined"
    return pd.concat([summary, combined[summary.columns]], ignore_index=True)


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"mean": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}
    if values.size == 1:
        value = float(values[0])
        return {"mean": value, "ci_low": value, "ci_high": value}
    idx = rng.integers(0, values.size, size=(n_boot, values.size))
    boot = values[idx].mean(axis=1)
    return {
        "mean": float(values.mean()),
        "ci_low": float(np.quantile(boot, 0.025)),
        "ci_high": float(np.quantile(boot, 0.975)),
    }


def compare_to_existing(
    learned: pd.DataFrame,
    existing: pd.DataFrame,
    pfa_tolerance: float,
    n_boot: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    methods = set(existing["method"].astype(str))
    lowrank_method = find_lowrank_method(methods)
    keep = ["tpsscs_finished_detector", "raw"]
    if lowrank_method:
        keep.append(lowrank_method)
    existing_keep = existing[existing["method"].isin(keep)].copy()
    learned_keep = learned.copy()
    common_ids = set(learned_keep["item_id"].astype(str))
    existing_keep = existing_keep[existing_keep["item_id"].astype(str).isin(common_ids)]
    combined_df = pd.concat([existing_keep, learned_keep], ignore_index=True)
    summary = summarize_methods(combined_df)

    comparison_rows: list[dict[str, Any]] = []
    for asset in sorted(summary["asset"].unique()):
        asset_summary = summary[summary["asset"] == asset]
        for pfa in sorted(asset_summary["pfa_target"].unique()):
            sub = asset_summary[np.isclose(asset_summary["pfa_target"], pfa)]
            proposed = sub[sub["method"] == "tpsscs_finished_detector"]
            learned_row = sub[sub["method"] == "loso_supervised_raw_feature_logreg"]
            raw = sub[sub["method"] == "raw"]
            lowrank = sub[sub["method"] == lowrank_method] if lowrank_method else pd.DataFrame()
            if proposed.empty or learned_row.empty:
                continue
            proposed_pd = float(proposed["pd_mean"].iloc[0])
            learned_pd = float(learned_row["pd_mean"].iloc[0])
            comparison_rows.append(
                {
                    "asset": asset,
                    "pfa": float(pfa),
                    "n_items": int(learned_row["n_items"].iloc[0]),
                    "proposed_pd": proposed_pd,
                    "learned_logreg_pd": learned_pd,
                    "raw_pd": float(raw["pd_mean"].iloc[0]) if not raw.empty else float("nan"),
                    "lowrank_pd": float(lowrank["pd_mean"].iloc[0]) if not lowrank.empty else float("nan"),
                    "delta_vs_learned_logreg": proposed_pd - learned_pd,
                    "proposed_empirical_pfa": float(proposed["empirical_pfa_mean"].iloc[0]),
                    "learned_empirical_pfa": float(learned_row["empirical_pfa_mean"].iloc[0]),
                    "pfa_ceiling": float(pfa) * pfa_tolerance + 1e-7,
                    "proposed_pfa_calibrated": float(proposed["empirical_pfa_mean"].iloc[0]) <= float(pfa) * pfa_tolerance + 1e-7,
                    "learned_pfa_calibrated": float(learned_row["empirical_pfa_mean"].iloc[0]) <= float(pfa) * pfa_tolerance + 1e-7,
                    "proposed_beats_learned": proposed_pd > learned_pd,
                }
            )
    comparisons = pd.DataFrame(comparison_rows)

    rng = np.random.default_rng(seed)
    pivot = (
        combined_df.pivot_table(
            index=["asset", "item_id", "pfa_target"],
            columns="method",
            values="pd",
            aggfunc="mean",
        )
        .reset_index()
        .dropna(subset=["tpsscs_finished_detector", "loso_supervised_raw_feature_logreg"])
    )
    ci_rows: list[dict[str, Any]] = []
    for pfa in sorted(pivot["pfa_target"].unique()):
        sub = pivot[np.isclose(pivot["pfa_target"], pfa)]
        values = (
            sub["tpsscs_finished_detector"].astype(float)
            - sub["loso_supervised_raw_feature_logreg"].astype(float)
        ).to_numpy()
        ci = bootstrap_ci(values, rng, n_boot)
        ci_rows.append(
            {
                "pfa": float(pfa),
                "n_items": int(values.size),
                "mean_delta_pd": ci["mean"],
                "ci95_low": ci["ci_low"],
                "ci95_high": ci["ci_high"],
                "positive_fraction": float(np.mean(values > 0)) if values.size else float("nan"),
                "nonnegative_fraction": float(np.mean(values >= 0)) if values.size else float("nan"),
            }
        )
    ci_df = pd.DataFrame(ci_rows)

    real_assets = sorted(a for a in comparisons["asset"].unique() if a != "combined")
    asset_rows = comparisons[comparisons["asset"].isin(real_assets)]
    combined_rows = comparisons[comparisons["asset"] == "combined"]
    passed = (
        len(real_assets) >= 2
        and not comparisons.empty
        and bool(asset_rows["proposed_pfa_calibrated"].all())
        and bool(asset_rows["learned_pfa_calibrated"].all())
        and bool(combined_rows["proposed_pfa_calibrated"].all())
        and bool(combined_rows["learned_pfa_calibrated"].all())
        and bool(asset_rows["proposed_beats_learned"].all())
        and bool(combined_rows["proposed_beats_learned"].all())
    )
    payload = {
        "learned_method": "loso_supervised_raw_feature_logreg",
        "proposed_method": "tpsscs_finished_detector",
        "lowrank_method": lowrank_method,
        "assets": real_assets,
        "heldout_target_bearing_items": int(learned["item_id"].nunique()),
        "pfa_points": int(combined_rows["pfa"].nunique()),
        "asset_level_comparisons": int(len(asset_rows)),
        "combined_comparisons": int(len(combined_rows)),
        "asset_level_wins_vs_learned": int(asset_rows["proposed_beats_learned"].sum()),
        "combined_wins_vs_learned": int(combined_rows["proposed_beats_learned"].sum()),
        "min_combined_delta_vs_learned": float(combined_rows["delta_vs_learned_logreg"].min()) if not combined_rows.empty else float("nan"),
        "min_asset_delta_vs_learned": float(asset_rows["delta_vs_learned_logreg"].min()) if not asset_rows.empty else float("nan"),
        "all_pfa_calibrated": bool(
            comparisons["proposed_pfa_calibrated"].all() and comparisons["learned_pfa_calibrated"].all()
        )
        if not comparisons.empty
        else False,
        "passed": bool(passed),
    }
    return comparisons, ci_df, payload


def write_markdown(path: Path, date_tag: str, payload: dict[str, Any], train_infos: list[dict[str, Any]], comparisons: pd.DataFrame, ci_df: pd.DataFrame) -> None:
    lines = [
        "# AISTAP Full-Asset LOSO Learned Raw-Feature Baseline",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Passed: `{str(payload['passed']).lower()}`",
        f"- Learned baseline: `{payload['learned_method']}`",
        f"- Proposed method: `{payload['proposed_method']}`",
        f"- Held-out target-bearing items: `{payload['heldout_target_bearing_items']}`",
        f"- Asset-level wins vs learned baseline: `{payload['asset_level_wins_vs_learned']}/{payload['asset_level_comparisons']}`",
        f"- Combined wins vs learned baseline: `{payload['combined_wins_vs_learned']}/{payload['combined_comparisons']}`",
        f"- Minimum combined delta vs learned baseline: `{payload['min_combined_delta_vs_learned']:.4f}`",
        f"- Minimum asset-level delta vs learned baseline: `{payload['min_asset_delta_vs_learned']:.4f}`",
        f"- All Pfa calibrated: `{str(payload['all_pfa_calibrated']).lower()}`",
        "",
        "## Protocol",
        "",
        "- Train a supervised logistic detector on raw-score local features from one official full asset.",
        "- Test it on the other official full asset, then swap train/test assets.",
        "- Score calibration uses the same conservative per-frame background thresholding policy as the TP-SSCS full-asset protocol.",
        "- The learned baseline uses only raw-score derived local features; it does not use TP-SSCS residuals or target coordinates.",
        "",
        "## Training Directions",
        "",
        "| Train asset | Test asset | Frames | Positive frames | Positive pixels | Background pixels |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for info in train_infos:
        lines.append(
            f"| `{info['train_asset']}` | `{info['test_asset']}` | {info['frames_seen']} | "
            f"{info['positive_frames_seen']} | {info['positive_pixels']} | {info['background_pixels']} |"
        )
    lines.extend(
        [
            "",
            "## Combined Comparisons",
            "",
            "| Pfa | TP-SSCS Pd | Learned Pd | Raw Pd | Low-rank Pd | Delta vs learned | Learned empirical Pfa |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    combined = comparisons[comparisons["asset"] == "combined"].sort_values("pfa")
    for _, row in combined.iterrows():
        lines.append(
            f"| {row['pfa']:.0e} | {row['proposed_pd']:.4f} | {row['learned_logreg_pd']:.4f} | "
            f"{row['raw_pd']:.4f} | {row['lowrank_pd']:.4f} | {row['delta_vs_learned_logreg']:.4f} | "
            f"{row['learned_empirical_pfa']:.6g} |"
        )
    lines.extend(
        [
            "",
            "## Bootstrap CI",
            "",
            "| Pfa | n | Mean TP-SSCS minus learned Pd | 95% CI | Positive fraction |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in ci_df.iterrows():
        lines.append(
            f"| {row['pfa']:.0e} | {int(row['n_items'])} | {row['mean_delta_pd']:.4f} | "
            f"[{row['ci95_low']:.4f}, {row['ci95_high']:.4f}] | {row['positive_fraction']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is not a benchmark against large pretrained radar detectors; it is a supervised, leave-one-condition-out learned detector baseline using the official AISTAP-SIM full assets.",
            "- The test asset is never used to fit the learned baseline in its corresponding direction.",
            "- The result addresses the narrow criticism that the paper only beats hand-designed CFAR variants on the official full assets.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--candidate-date", default="20260715")
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--background-per-frame", type=int, default=2048)
    parser.add_argument("--max-iter", type=int, default=300)
    parser.add_argument("--c", type=float, default=1.0)
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--max-train-frames", type=int, default=None)
    parser.add_argument("--max-test-positive", type=int, default=None)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    full_dir = root / "data" / "downloads" / "aistap_sim" / "full"
    assets = sorted(full_dir.glob("sim*_test.mat"))
    if len(assets) < 2:
        raise FileNotFoundError(f"Need at least two full assets under {full_dir}")
    asset_by_name = {p.name: p for p in assets}
    directions = [("simMed_test.mat", "simWind_test.mat"), ("simWind_test.mat", "simMed_test.mat")]
    pfas = parse_floats(args.pfas)
    rng = np.random.default_rng(args.seed)

    learned_frames: list[pd.DataFrame] = []
    train_infos: list[dict[str, Any]] = []
    for train_name, test_name in directions:
        train_path = asset_by_name[train_name]
        test_path = asset_by_name[test_name]
        x, y, train_info = collect_training_samples(
            train_path,
            rng,
            background_per_frame=args.background_per_frame,
            max_frames=args.max_train_frames,
        )
        model = train_logreg(x, y, max_iter=args.max_iter, c_value=args.c)
        learned_df, test_info = evaluate_model(
            model,
            train_asset_name=train_name,
            asset_path=test_path,
            pfas=pfas,
            max_positive=args.max_test_positive,
        )
        train_info.test_asset = test_name
        info = train_info.__dict__.copy()
        info.update(test_info)
        train_infos.append(info)
        learned_frames.append(learned_df)

    learned = pd.concat(learned_frames, ignore_index=True)
    existing = load_existing_candidate_rows(root, args.candidate_date)
    comparisons, ci_df, payload = compare_to_existing(
        learned,
        existing,
        pfa_tolerance=args.pfa_tolerance,
        n_boot=args.boot,
        seed=args.seed,
    )
    payload.update(
        {
            "date": args.date,
            "candidate_date": args.candidate_date,
            "features": FEATURE_NAMES,
            "background_per_frame": args.background_per_frame,
            "max_iter": args.max_iter,
            "c": args.c,
            "bootstrap_replicates": args.boot,
            "train_infos": train_infos,
        }
    )

    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    learned_csv = result_dir / f"aistap_full_asset_loso_learned_raw_baseline_{args.date}.csv"
    comparison_csv = result_dir / f"aistap_full_asset_loso_learned_raw_baseline_comparison_{args.date}.csv"
    ci_csv = result_dir / f"aistap_full_asset_loso_learned_raw_baseline_bootstrap_ci_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_loso_learned_raw_baseline_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_loso_learned_raw_baseline_{args.date}.md"

    learned.to_csv(learned_csv, index=False)
    comparisons.to_csv(comparison_csv, index=False)
    ci_df.to_csv(ci_csv, index=False)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(md_path, args.date, payload, train_infos, comparisons, ci_df)

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
