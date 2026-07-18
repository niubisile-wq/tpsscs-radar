from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
import torch
from scipy import ndimage
from sklearn.ensemble import HistGradientBoostingClassifier

import evaluate_aistap_full_asset_classical_cfar_baselines as base

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evaluate_aistap_target_preservation_ablation import load_trainable_model


METHOD_NAME = "loso_supervised_tpsscs_feature_hgb"
BASELINE_METHOD = "loso_supervised_raw_residual_hgb"
MAP_PREFIXES = ["raw", "residual", "tpsscs", "gate"]
FEATURE_NAMES = (
    [f"{prefix}_{suffix}" for prefix in MAP_PREFIXES for suffix in ["frame_z", "local_z_5", "local_z_17", "contrast_5", "contrast_17", "gradient_mag"]]
    + [
        "tpsscs_minus_raw_z",
        "tpsscs_minus_residual_z",
        "residual_minus_raw_z",
        "max_raw_residual_tpsscs_z",
        "gate_times_tpsscs_z",
    ]
)


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


def one_map_features(score: np.ndarray, prefix: str) -> tuple[list[np.ndarray], list[str], np.ndarray, np.ndarray]:
    score = np.asarray(score, dtype=np.float64)
    log_score = np.log1p(np.maximum(score, 0.0))
    frame_z = robust_scale(log_score)
    feats = [frame_z]
    names = [f"{prefix}_frame_z"]
    for size in (5, 17):
        local_mean = ndimage.uniform_filter(log_score, size=size, mode="reflect")
        local_sq = ndimage.uniform_filter(log_score * log_score, size=size, mode="reflect")
        local_std = np.sqrt(np.maximum(local_sq - local_mean * local_mean, 1e-8))
        feats.append((log_score - local_mean) / local_std)
        names.append(f"{prefix}_local_z_{size}")
    for size in (5, 17):
        local_mean = ndimage.uniform_filter(log_score, size=size, mode="reflect")
        feats.append(log_score - local_mean)
        names.append(f"{prefix}_contrast_{size}")
    gy, gx = np.gradient(log_score)
    feats.append(np.sqrt(gx * gx + gy * gy))
    names.append(f"{prefix}_gradient_mag")
    return feats, names, frame_z, log_score


def feature_cube(raw_score: np.ndarray, residual_score: np.ndarray, tpsscs_score: np.ndarray, gate: np.ndarray) -> np.ndarray:
    maps = {
        "raw": raw_score,
        "residual": residual_score,
        "tpsscs": tpsscs_score,
        "gate": gate,
    }
    feats: list[np.ndarray] = []
    names: list[str] = []
    z_maps: dict[str, np.ndarray] = {}
    log_maps: dict[str, np.ndarray] = {}
    for prefix in MAP_PREFIXES:
        f, n, z, log_score = one_map_features(maps[prefix], prefix)
        feats.extend(f)
        names.extend(n)
        z_maps[prefix] = z
        log_maps[prefix] = log_score
    if names != FEATURE_NAMES[: len(names)]:
        raise RuntimeError("feature name order mismatch")

    cross = [
        robust_scale(log_maps["tpsscs"] - log_maps["raw"]),
        robust_scale(log_maps["tpsscs"] - log_maps["residual"]),
        robust_scale(log_maps["residual"] - log_maps["raw"]),
        np.maximum.reduce([z_maps["raw"], z_maps["residual"], z_maps["tpsscs"]]),
        robust_scale(np.asarray(gate, dtype=float) * z_maps["tpsscs"]),
    ]
    feats.extend(cross)
    return np.stack(feats, axis=-1).astype(np.float32)


def frame_iter(asset_path: Path, model: torch.nn.Module):
    with h5py.File(asset_path, "r") as f, torch.no_grad():
        refs = f["meta_per_image"][()].reshape(-1)
        for idx, ref in enumerate(refs):
            meta = base.read_meta(f, ref)
            x_np = base.to_complex(f["rd_img"][idx])
            raw_score = base.score_map(x_np)
            x = torch.from_numpy(x_np).to(torch.complex128)
            out = model(x)
            residual_score = base.score_map(out["residual"].detach().cpu().numpy())
            tpsscs_score = out["score"].detach().cpu().numpy()
            gate = out["gate"].detach().cpu().numpy()
            mask = base.target_mask(meta, raw_score.shape)
            yield idx, raw_score, residual_score, tpsscs_score, gate, mask


def collect_training_samples(
    asset_path: Path,
    model: torch.nn.Module,
    rng: np.random.Generator,
    background_per_frame: int,
    max_frames: int | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, TrainInfo]:
    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    frames_seen = 0
    positive_frames_seen = 0
    positive_pixels = 0
    background_pixels = 0

    for idx, raw_score, residual_score, tpsscs_score, gate, mask in frame_iter(asset_path, model):
        if max_frames is not None and frames_seen >= max_frames:
            break
        frames_seen += 1
        feats = feature_cube(raw_score, residual_score, tpsscs_score, gate).reshape(-1, len(FEATURE_NAMES))
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
    pos = int(np.sum(y == 1))
    neg = int(np.sum(y == 0))
    weights = np.where(y == 1, 0.5 / max(pos, 1), 0.5 / max(neg, 1)).astype(np.float64)
    weights *= float(y.size)
    info = TrainInfo(
        train_asset=asset_path.name,
        test_asset="",
        frames_seen=frames_seen,
        positive_frames_seen=positive_frames_seen,
        positive_pixels=positive_pixels,
        background_pixels=background_pixels,
    )
    return x, y, weights, info


def train_hgb(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    max_iter: int,
    learning_rate: float,
    max_leaf_nodes: int,
    l2_regularization: float,
    seed: int,
) -> HistGradientBoostingClassifier:
    model = HistGradientBoostingClassifier(
        max_iter=max_iter,
        learning_rate=learning_rate,
        max_leaf_nodes=max_leaf_nodes,
        l2_regularization=l2_regularization,
        early_stopping=False,
        random_state=seed,
    )
    model.fit(x, y, sample_weight=weights)
    return model


def evaluate_model(
    learned_model: HistGradientBoostingClassifier,
    train_asset_name: str,
    asset_path: Path,
    tpsscs_model: torch.nn.Module,
    pfas: list[float],
    max_positive: int | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    positive_frames = 0
    evaluated_positive = 0

    for idx, raw_score, residual_score, tpsscs_score, gate, mask in frame_iter(asset_path, tpsscs_model):
        if not mask.any():
            continue
        positive_frames += 1
        if max_positive is not None and evaluated_positive >= max_positive:
            break
        feats = feature_cube(raw_score, residual_score, tpsscs_score, gate).reshape(-1, len(FEATURE_NAMES))
        score = learned_model.predict_proba(feats)[:, 1].reshape(raw_score.shape)
        item_id = f"{asset_path.name}#{idx}"
        for row in base.summarize(score, mask, pfas, "loso_supervised_tpsscs_feature_hgb_conservative_topk_strict_gt"):
            row.update(
                {
                    "asset": asset_path.name,
                    "image_index": idx,
                    "item_id": item_id,
                    "method": METHOD_NAME,
                    "method_family": "learned_tpsscs_feature_ensemble",
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


def load_baseline_hgb_rows(root: Path, date_tag: str) -> pd.DataFrame:
    path = root / "results" / "aistap_full_asset" / f"aistap_full_asset_loso_feature_ensemble_baseline_{date_tag}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing baseline HGB rows: {path}")
    return pd.read_csv(path)


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


def compare_methods(
    tpsscs_feature_rows: pd.DataFrame,
    raw_residual_hgb_rows: pd.DataFrame,
    compact_rows: pd.DataFrame,
    pfa_tolerance: float,
    n_boot: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    compact_keep = compact_rows[compact_rows["method"] == "tpsscs_finished_detector"].copy()
    common_ids = set(tpsscs_feature_rows["item_id"].astype(str)).intersection(set(raw_residual_hgb_rows["item_id"].astype(str)))
    raw_residual_hgb_rows = raw_residual_hgb_rows[raw_residual_hgb_rows["item_id"].astype(str).isin(common_ids)]
    compact_keep = compact_keep[compact_keep["item_id"].astype(str).isin(common_ids)]
    tpsscs_feature_rows = tpsscs_feature_rows[tpsscs_feature_rows["item_id"].astype(str).isin(common_ids)]
    combined_df = pd.concat([compact_keep, raw_residual_hgb_rows, tpsscs_feature_rows], ignore_index=True)
    summary = summarize_methods(combined_df)

    comparison_rows: list[dict[str, Any]] = []
    for asset in sorted(summary["asset"].unique()):
        asset_summary = summary[summary["asset"] == asset]
        for pfa in sorted(asset_summary["pfa_target"].unique()):
            sub = asset_summary[np.isclose(asset_summary["pfa_target"], pfa)]
            compact = sub[sub["method"] == "tpsscs_finished_detector"]
            baseline = sub[sub["method"] == BASELINE_METHOD]
            enhanced = sub[sub["method"] == METHOD_NAME]
            if compact.empty or baseline.empty or enhanced.empty:
                continue
            enhanced_pd = float(enhanced["pd_mean"].iloc[0])
            baseline_pd = float(baseline["pd_mean"].iloc[0])
            compact_pd = float(compact["pd_mean"].iloc[0])
            comparison_rows.append(
                {
                    "asset": asset,
                    "pfa": float(pfa),
                    "n_items": int(enhanced["n_items"].iloc[0]),
                    "tpsscs_feature_hgb_pd": enhanced_pd,
                    "raw_residual_hgb_pd": baseline_pd,
                    "compact_tpsscs_pd": compact_pd,
                    "delta_vs_raw_residual_hgb": enhanced_pd - baseline_pd,
                    "delta_vs_compact_tpsscs": enhanced_pd - compact_pd,
                    "tpsscs_feature_hgb_empirical_pfa": float(enhanced["empirical_pfa_mean"].iloc[0]),
                    "raw_residual_hgb_empirical_pfa": float(baseline["empirical_pfa_mean"].iloc[0]),
                    "compact_tpsscs_empirical_pfa": float(compact["empirical_pfa_mean"].iloc[0]),
                    "pfa_ceiling": float(pfa) * pfa_tolerance + 1e-7,
                    "tpsscs_feature_hgb_pfa_calibrated": float(enhanced["empirical_pfa_mean"].iloc[0]) <= float(pfa) * pfa_tolerance + 1e-7,
                    "beats_raw_residual_hgb": enhanced_pd > baseline_pd,
                    "beats_or_ties_raw_residual_hgb": enhanced_pd >= baseline_pd,
                    "beats_compact_tpsscs": enhanced_pd > compact_pd,
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
        .dropna(subset=[METHOD_NAME, BASELINE_METHOD, "tpsscs_finished_detector"])
    )
    ci_rows: list[dict[str, Any]] = []
    for pfa in sorted(pivot["pfa_target"].unique()):
        sub = pivot[np.isclose(pivot["pfa_target"], pfa)]
        for comparator in [BASELINE_METHOD, "tpsscs_finished_detector"]:
            values = (sub[METHOD_NAME].astype(float) - sub[comparator].astype(float)).to_numpy()
            ci = bootstrap_ci(values, rng, n_boot)
            ci_rows.append(
                {
                    "pfa": float(pfa),
                    "comparator": comparator,
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
    hgb_ci = ci_df[ci_df["comparator"] == BASELINE_METHOD]
    compact_ci = ci_df[ci_df["comparator"] == "tpsscs_finished_detector"]
    ci_positive_vs_hgb = not hgb_ci.empty and bool((hgb_ci["ci95_low"].astype(float) > 0.0).all())
    ci_positive_vs_compact = not compact_ci.empty and bool((compact_ci["ci95_low"].astype(float) > 0.0).all())
    passed_gain_vs_hgb = (
        len(real_assets) >= 2
        and not comparisons.empty
        and bool(asset_rows["tpsscs_feature_hgb_pfa_calibrated"].all())
        and bool(combined_rows["tpsscs_feature_hgb_pfa_calibrated"].all())
        and bool(asset_rows["beats_raw_residual_hgb"].all())
        and bool(combined_rows["beats_raw_residual_hgb"].all())
        and ci_positive_vs_hgb
    )
    payload = {
        "learned_method": METHOD_NAME,
        "baseline_method": BASELINE_METHOD,
        "compact_method": "tpsscs_finished_detector",
        "assets": real_assets,
        "heldout_target_bearing_items": int(tpsscs_feature_rows["item_id"].nunique()),
        "pfa_points": int(combined_rows["pfa"].nunique()),
        "asset_level_comparisons": int(len(asset_rows)),
        "combined_comparisons": int(len(combined_rows)),
        "asset_level_wins_vs_raw_residual_hgb": int(asset_rows["beats_raw_residual_hgb"].sum()),
        "combined_wins_vs_raw_residual_hgb": int(combined_rows["beats_raw_residual_hgb"].sum()),
        "asset_level_wins_vs_compact_tpsscs": int(asset_rows["beats_compact_tpsscs"].sum()),
        "combined_wins_vs_compact_tpsscs": int(combined_rows["beats_compact_tpsscs"].sum()),
        "min_combined_delta_vs_raw_residual_hgb": float(combined_rows["delta_vs_raw_residual_hgb"].min()) if not combined_rows.empty else float("nan"),
        "min_asset_delta_vs_raw_residual_hgb": float(asset_rows["delta_vs_raw_residual_hgb"].min()) if not asset_rows.empty else float("nan"),
        "min_combined_delta_vs_compact_tpsscs": float(combined_rows["delta_vs_compact_tpsscs"].min()) if not combined_rows.empty else float("nan"),
        "ci_lower_bounds_positive_vs_raw_residual_hgb": bool(ci_positive_vs_hgb),
        "ci_lower_bounds_positive_vs_compact_tpsscs": bool(ci_positive_vs_compact),
        "all_pfa_calibrated": bool(comparisons["tpsscs_feature_hgb_pfa_calibrated"].all()) if not comparisons.empty else False,
        "passed_gain_vs_raw_residual_hgb": bool(passed_gain_vs_hgb),
    }
    return comparisons, ci_df, payload


def write_markdown(
    path: Path,
    date_tag: str,
    payload: dict[str, Any],
    train_infos: list[dict[str, Any]],
    comparisons: pd.DataFrame,
    ci_df: pd.DataFrame,
) -> None:
    lines = [
        "# AISTAP Full-Asset LOSO TP-SSCS-Feature Ensemble",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Passed gain vs raw/residual HGB: `{str(payload['passed_gain_vs_raw_residual_hgb']).lower()}`",
        f"- TP-SSCS-feature HGB: `{payload['learned_method']}`",
        f"- Baseline HGB: `{payload['baseline_method']}`",
        f"- Held-out target-bearing items: `{payload['heldout_target_bearing_items']}`",
        f"- Asset-level wins vs raw/residual HGB: `{payload['asset_level_wins_vs_raw_residual_hgb']}/{payload['asset_level_comparisons']}`",
        f"- Combined wins vs raw/residual HGB: `{payload['combined_wins_vs_raw_residual_hgb']}/{payload['combined_comparisons']}`",
        f"- Minimum combined delta vs raw/residual HGB: `{payload['min_combined_delta_vs_raw_residual_hgb']:.4f}`",
        f"- Minimum combined delta vs compact TP-SSCS: `{payload['min_combined_delta_vs_compact_tpsscs']:.4f}`",
        f"- CI lower bounds positive vs raw/residual HGB: `{str(payload['ci_lower_bounds_positive_vs_raw_residual_hgb']).lower()}`",
        f"- CI lower bounds positive vs compact TP-SSCS: `{str(payload['ci_lower_bounds_positive_vs_compact_tpsscs']).lower()}`",
        f"- All Pfa calibrated: `{str(payload['all_pfa_calibrated']).lower()}`",
        "",
        "## Protocol",
        "",
        "- Train a nonlinear histogram-gradient-boosting detector on one official full asset and test on the other.",
        "- Features include raw power, rank-30 low-rank residual power, compact TP-SSCS enhanced score, TP-SSCS gate map, local z-scores, local contrasts, gradients, and cross-features.",
        "- The baseline comparator is the raw/residual HGB trained and evaluated by the same LOSO protocol.",
        "- The test asset is not used for fitting in its corresponding direction.",
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
            "| Pfa | TP-SSCS-feature HGB Pd | Raw/residual HGB Pd | Compact TP-SSCS Pd | Delta vs HGB | Delta vs compact |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )
    combined = comparisons[comparisons["asset"] == "combined"].sort_values("pfa")
    for _, row in combined.iterrows():
        lines.append(
            f"| {row['pfa']:.0e} | {row['tpsscs_feature_hgb_pd']:.4f} | {row['raw_residual_hgb_pd']:.4f} | "
            f"{row['compact_tpsscs_pd']:.4f} | {row['delta_vs_raw_residual_hgb']:.4f} | "
            f"{row['delta_vs_compact_tpsscs']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Bootstrap CI",
            "",
            "| Pfa | Comparator | n | Mean Delta Pd | 95% CI | Positive fraction |",
            "|---:|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in ci_df.iterrows():
        lines.append(
            f"| {row['pfa']:.0e} | `{row['comparator']}` | {int(row['n_items'])} | "
            f"{row['mean_delta_pd']:.4f} | [{row['ci95_low']:.4f}, {row['ci95_high']:.4f}] | "
            f"{row['positive_fraction']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This audit tests whether TP-SSCS-derived features add value to a strong in-domain supervised HGB detector.",
            "- It does not establish zero-shot external transfer or replace the compact TP-SSCS fixed-detector result.",
            "- If positive, it supports TP-SSCS as a target-preserving feature construction as well as a compact detector policy.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--candidate-date", default="20260715")
    parser.add_argument("--baseline-date", default="20260717")
    parser.add_argument("--state", default="results/aistap_sample/tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt")
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--background-per-frame", type=int, default=4096)
    parser.add_argument("--max-iter", type=int, default=160)
    parser.add_argument("--learning-rate", type=float, default=0.06)
    parser.add_argument("--max-leaf-nodes", type=int, default=31)
    parser.add_argument("--l2", type=float, default=1e-3)
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--max-train-frames", type=int, default=None)
    parser.add_argument("--max-test-positive", type=int, default=None)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    state_path = root / args.state
    tpsscs_model = load_trainable_model(state_path)
    tpsscs_model.eval()

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
    for direction_idx, (train_name, test_name) in enumerate(directions):
        train_path = asset_by_name[train_name]
        test_path = asset_by_name[test_name]
        x, y, weights, train_info = collect_training_samples(
            train_path,
            tpsscs_model,
            rng,
            background_per_frame=args.background_per_frame,
            max_frames=args.max_train_frames,
        )
        model = train_hgb(
            x,
            y,
            weights,
            max_iter=args.max_iter,
            learning_rate=args.learning_rate,
            max_leaf_nodes=args.max_leaf_nodes,
            l2_regularization=args.l2,
            seed=args.seed + direction_idx,
        )
        learned_df, test_info = evaluate_model(
            model,
            train_asset_name=train_name,
            asset_path=test_path,
            tpsscs_model=tpsscs_model,
            pfas=pfas,
            max_positive=args.max_test_positive,
        )
        train_info.test_asset = test_name
        info = train_info.__dict__.copy()
        info.update(test_info)
        train_infos.append(info)
        learned_frames.append(learned_df)

    learned = pd.concat(learned_frames, ignore_index=True)
    baseline_hgb = load_baseline_hgb_rows(root, args.baseline_date)
    compact = load_existing_candidate_rows(root, args.candidate_date)
    comparisons, ci_df, payload = compare_methods(
        learned,
        baseline_hgb,
        compact,
        pfa_tolerance=args.pfa_tolerance,
        n_boot=args.boot,
        seed=args.seed,
    )
    payload.update(
        {
            "date": args.date,
            "candidate_date": args.candidate_date,
            "baseline_date": args.baseline_date,
            "state": str(state_path.relative_to(root)),
            "features": FEATURE_NAMES,
            "background_per_frame": args.background_per_frame,
            "max_iter": args.max_iter,
            "learning_rate": args.learning_rate,
            "max_leaf_nodes": args.max_leaf_nodes,
            "l2_regularization": args.l2,
            "bootstrap_replicates": args.boot,
            "train_infos": train_infos,
        }
    )

    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    learned_csv = result_dir / f"aistap_full_asset_loso_tpsscs_feature_ensemble_{args.date}.csv"
    comparison_csv = result_dir / f"aistap_full_asset_loso_tpsscs_feature_ensemble_comparison_{args.date}.csv"
    ci_csv = result_dir / f"aistap_full_asset_loso_tpsscs_feature_ensemble_bootstrap_ci_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_loso_tpsscs_feature_ensemble_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_loso_tpsscs_feature_ensemble_{args.date}.md"

    learned.to_csv(learned_csv, index=False)
    comparisons.to_csv(comparison_csv, index=False)
    ci_df.to_csv(ci_csv, index=False)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(md_path, args.date, payload, train_infos, comparisons, ci_df)

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
