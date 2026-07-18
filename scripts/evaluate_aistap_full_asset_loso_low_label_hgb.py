from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

import evaluate_aistap_full_asset_classical_cfar_baselines as base
import evaluate_aistap_full_asset_loso_feature_ensemble_baseline as hgb


METHOD_NAME = "loso_low_label_raw_residual_hgb"
COMPACT_METHOD = "tpsscs_finished_detector"


@dataclass
class FrameRecord:
    asset: str
    image_index: int
    item_id: str
    features: np.ndarray
    mask_flat: np.ndarray
    shape: tuple[int, int]


def parse_floats(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def parse_ints_or_all(text: str) -> list[int | str]:
    values: list[int | str] = []
    for raw in text.split(","):
        item = raw.strip().lower()
        if not item:
            continue
        if item == "all":
            values.append("all")
        else:
            value = int(item)
            if value <= 0:
                raise ValueError("Label budgets must be positive integers or `all`.")
            values.append(value)
    return values


def parse_ints(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def budget_label(value: int | str) -> str:
    return "all" if value == "all" else str(int(value))


def budget_sort_key(label: str) -> int:
    return 10**9 if label == "all" else int(label)


def load_positive_records(asset_path: Path, rank: int, max_positive: int | None) -> list[FrameRecord]:
    records: list[FrameRecord] = []
    for idx, raw_score, residual_score, mask in hgb.frame_iter(asset_path, rank):
        if not mask.any():
            continue
        if max_positive is not None and len(records) >= max_positive:
            break
        features = hgb.feature_cube(raw_score, residual_score).reshape(-1, len(hgb.FEATURE_NAMES))
        records.append(
            FrameRecord(
                asset=asset_path.name,
                image_index=idx,
                item_id=f"{asset_path.name}#{idx}",
                features=np.ascontiguousarray(features, dtype=np.float32),
                mask_flat=mask.reshape(-1).astype(bool),
                shape=raw_score.shape,
            )
        )
    if not records:
        raise ValueError(f"No positive frames found in {asset_path}")
    return records


def select_budget_records(records: list[FrameRecord], budget: int | str, seed: int) -> list[FrameRecord]:
    if budget == "all" or int(budget) >= len(records):
        return list(records)
    rng = np.random.default_rng(seed)
    indices = np.sort(rng.choice(len(records), size=int(budget), replace=False))
    return [records[int(i)] for i in indices]


def collect_training_samples(
    records: list[FrameRecord],
    rng: np.random.Generator,
    background_per_frame: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    positive_pixels = 0
    background_pixels = 0

    for record in records:
        pos_idx = np.flatnonzero(record.mask_flat)
        bg_idx = np.flatnonzero(~record.mask_flat)
        if pos_idx.size:
            x_parts.append(record.features[pos_idx])
            y_parts.append(np.ones(pos_idx.size, dtype=np.int8))
            positive_pixels += int(pos_idx.size)
        n_bg = min(background_per_frame, bg_idx.size)
        if n_bg:
            sample_bg = rng.choice(bg_idx, size=n_bg, replace=False)
            x_parts.append(record.features[sample_bg])
            y_parts.append(np.zeros(n_bg, dtype=np.int8))
            background_pixels += int(n_bg)

    if not x_parts or positive_pixels == 0:
        raise ValueError("Selected label budget did not include positive training pixels.")
    x = np.vstack(x_parts)
    y = np.concatenate(y_parts)
    pos = int(np.sum(y == 1))
    neg = int(np.sum(y == 0))
    weights = np.where(y == 1, 0.5 / max(pos, 1), 0.5 / max(neg, 1)).astype(np.float64)
    weights *= float(y.size)
    info = {
        "positive_frames": len(records),
        "positive_pixels": positive_pixels,
        "background_pixels": background_pixels,
        "training_samples": int(y.size),
    }
    return x, y, weights, info


def collect_training_pixel_samples(
    records: list[FrameRecord],
    budget: int | str,
    rng: np.random.Generator,
    background_per_positive_pixel: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    positive_locations: list[tuple[int, int]] = []
    for record_idx, record in enumerate(records):
        for pixel_idx in np.flatnonzero(record.mask_flat):
            positive_locations.append((record_idx, int(pixel_idx)))
    if not positive_locations:
        raise ValueError("No positive pixels available for target-pixel budget.")

    if budget == "all" or int(budget) >= len(positive_locations):
        selected_locations = positive_locations
    else:
        selected_indices = rng.choice(len(positive_locations), size=int(budget), replace=False)
        selected_locations = [positive_locations[int(i)] for i in selected_indices]

    by_record: dict[int, list[int]] = {}
    for record_idx, pixel_idx in selected_locations:
        by_record.setdefault(record_idx, []).append(pixel_idx)

    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    positive_pixels = 0
    background_pixels = 0
    for record_idx, pos_indices in sorted(by_record.items()):
        record = records[record_idx]
        pos = np.asarray(pos_indices, dtype=int)
        x_parts.append(record.features[pos])
        y_parts.append(np.ones(pos.size, dtype=np.int8))
        positive_pixels += int(pos.size)

        bg_idx = np.flatnonzero(~record.mask_flat)
        n_bg = min(bg_idx.size, max(1, int(pos.size) * background_per_positive_pixel))
        sample_bg = rng.choice(bg_idx, size=n_bg, replace=False)
        x_parts.append(record.features[sample_bg])
        y_parts.append(np.zeros(n_bg, dtype=np.int8))
        background_pixels += int(n_bg)

    x = np.vstack(x_parts)
    y = np.concatenate(y_parts)
    pos = int(np.sum(y == 1))
    neg = int(np.sum(y == 0))
    weights = np.where(y == 1, 0.5 / max(pos, 1), 0.5 / max(neg, 1)).astype(np.float64)
    weights *= float(y.size)
    info = {
        "positive_frames": len(by_record),
        "positive_pixels": positive_pixels,
        "background_pixels": background_pixels,
        "training_samples": int(y.size),
    }
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
    model: HistGradientBoostingClassifier,
    test_records: list[FrameRecord],
    train_asset: str,
    budget: int | str,
    budget_unit: str,
    selected_positive_frames: int,
    selected_positive_pixels: int,
    seed: int,
    pfas: list[float],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    label = budget_label(budget)
    positive_frame_count = len(test_records)
    for record in test_records:
        score = model.predict_proba(record.features)[:, 1].reshape(record.shape)
        mask = record.mask_flat.reshape(record.shape)
        for row in base.summarize(score, mask, pfas, "low_label_hgb_conservative_topk_strict_gt"):
            row.update(
                {
                    "asset": record.asset,
                    "image_index": record.image_index,
                    "item_id": record.item_id,
                    "method": METHOD_NAME,
                    "method_family": "low_label_learned_raw_residual_feature_ensemble",
                    "train_asset": train_asset,
                    "test_asset": record.asset,
                    "label_budget": label,
                    "label_budget_unit": budget_unit,
                    "selected_positive_frames": selected_positive_frames,
                    "selected_positive_pixels": selected_positive_pixels,
                    "seed": seed,
                    "test_positive_frames": positive_frame_count,
                }
            )
            rows.append(row)
    return pd.DataFrame(rows)


def load_existing_candidate_rows(root: Path, date_tag: str) -> pd.DataFrame:
    paths = sorted((root / "results" / "aistap_full_asset").glob(f"aistap_full_asset_detector_candidate_*_{date_tag}.csv"))
    if not paths:
        raise FileNotFoundError(f"No detector-candidate rows found for date {date_tag}")
    return pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)


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


def compare_low_label_to_compact(
    learned: pd.DataFrame,
    compact_source: pd.DataFrame,
    pfa_tolerance: float,
    n_boot: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    compact = compact_source[compact_source["method"] == COMPACT_METHOD].copy()
    compact = compact[
        [
            "asset",
            "item_id",
            "pfa_target",
            "pd",
            "empirical_pfa",
            "method",
        ]
    ].rename(
        columns={
            "pd": "compact_pd",
            "empirical_pfa": "compact_empirical_pfa",
            "method": "compact_method",
        }
    )
    paired = learned.merge(compact, on=["asset", "item_id", "pfa_target"], how="inner")
    paired["delta_compact_minus_low_label_hgb"] = paired["compact_pd"].astype(float) - paired["pd"].astype(float)
    paired["compact_beats_low_label_hgb_item"] = paired["delta_compact_minus_low_label_hgb"] > 0.0
    paired["low_label_hgb_empirical_pfa"] = paired["empirical_pfa"].astype(float)
    paired["compact_pfa_calibrated"] = paired["compact_empirical_pfa"].astype(float) <= paired["pfa_target"].astype(float) * pfa_tolerance + 1e-7
    paired["low_label_hgb_pfa_calibrated"] = paired["low_label_hgb_empirical_pfa"].astype(float) <= paired["pfa_target"].astype(float) * pfa_tolerance + 1e-7

    group_cols = ["label_budget", "asset", "pfa_target"]
    asset_summary = (
        paired.groupby(group_cols, dropna=False)
        .agg(
            compact_pd=("compact_pd", "mean"),
            low_label_hgb_pd=("pd", "mean"),
            delta_compact_minus_low_label_hgb=("delta_compact_minus_low_label_hgb", "mean"),
            compact_empirical_pfa=("compact_empirical_pfa", "mean"),
            low_label_hgb_empirical_pfa=("low_label_hgb_empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
            n_pair_observations=("item_id", "size"),
            n_seeds=("seed", "nunique"),
            compact_item_win_fraction=("compact_beats_low_label_hgb_item", "mean"),
            compact_pfa_calibrated=("compact_pfa_calibrated", "all"),
            low_label_hgb_pfa_calibrated=("low_label_hgb_pfa_calibrated", "all"),
        )
        .reset_index()
    )
    combined_summary = (
        paired.groupby(["label_budget", "pfa_target"], dropna=False)
        .agg(
            compact_pd=("compact_pd", "mean"),
            low_label_hgb_pd=("pd", "mean"),
            delta_compact_minus_low_label_hgb=("delta_compact_minus_low_label_hgb", "mean"),
            compact_empirical_pfa=("compact_empirical_pfa", "mean"),
            low_label_hgb_empirical_pfa=("low_label_hgb_empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
            n_pair_observations=("item_id", "size"),
            n_seeds=("seed", "nunique"),
            compact_item_win_fraction=("compact_beats_low_label_hgb_item", "mean"),
            compact_pfa_calibrated=("compact_pfa_calibrated", "all"),
            low_label_hgb_pfa_calibrated=("low_label_hgb_pfa_calibrated", "all"),
        )
        .reset_index()
    )
    combined_summary["asset"] = "combined"
    comparisons = pd.concat([asset_summary, combined_summary[asset_summary.columns]], ignore_index=True)
    comparisons["compact_beats_low_label_hgb"] = comparisons["delta_compact_minus_low_label_hgb"] > 0.0
    comparisons["pfa"] = comparisons["pfa_target"].astype(float)
    comparisons = comparisons.sort_values(
        by=["label_budget"],
        key=lambda s: s.map(lambda x: budget_sort_key(str(x))) if s.name == "label_budget" else s,
    ).reset_index(drop=True)

    rng = np.random.default_rng(seed)
    ci_rows: list[dict[str, Any]] = []
    for label in sorted(paired["label_budget"].astype(str).unique(), key=budget_sort_key):
        budget_rows = paired[paired["label_budget"].astype(str) == label]
        for pfa in sorted(budget_rows["pfa_target"].unique()):
            sub = budget_rows[np.isclose(budget_rows["pfa_target"].astype(float), float(pfa))]
            values = sub["delta_compact_minus_low_label_hgb"].astype(float).to_numpy()
            ci = bootstrap_ci(values, rng, n_boot)
            ci_rows.append(
                {
                    "label_budget": label,
                    "pfa": float(pfa),
                    "n_pair_observations": int(values.size),
                    "n_items": int(sub["item_id"].nunique()),
                    "n_seeds": int(sub["seed"].nunique()),
                    "mean_delta_compact_minus_low_label_hgb": ci["mean"],
                    "ci95_low": ci["ci_low"],
                    "ci95_high": ci["ci_high"],
                    "positive_fraction": float(np.mean(values > 0.0)) if values.size else float("nan"),
                    "nonnegative_fraction": float(np.mean(values >= 0.0)) if values.size else float("nan"),
                }
            )
    ci_df = pd.DataFrame(ci_rows)

    combined = comparisons[comparisons["asset"] == "combined"].copy()
    budget_payload: list[dict[str, Any]] = []
    all_win_budgets: list[str] = []
    positive_ci_budgets: list[str] = []
    for label in sorted(combined["label_budget"].astype(str).unique(), key=budget_sort_key):
        sub = combined[combined["label_budget"].astype(str) == label]
        ci_sub = ci_df[ci_df["label_budget"].astype(str) == label]
        all_wins = bool(sub["compact_beats_low_label_hgb"].all()) if not sub.empty else False
        all_ci_positive = bool((ci_sub["ci95_low"].astype(float) > 0.0).all()) if not ci_sub.empty else False
        if all_wins:
            all_win_budgets.append(label)
        if all_ci_positive:
            positive_ci_budgets.append(label)
        budget_payload.append(
            {
                "label_budget": label,
                "combined_wins_for_compact": int(sub["compact_beats_low_label_hgb"].sum()),
                "combined_comparisons": int(len(sub)),
                "min_combined_delta_compact_minus_low_label_hgb": float(sub["delta_compact_minus_low_label_hgb"].min()) if not sub.empty else float("nan"),
                "mean_combined_delta_compact_minus_low_label_hgb": float(sub["delta_compact_minus_low_label_hgb"].mean()) if not sub.empty else float("nan"),
                "ci_lower_bounds_positive_all_pfa": all_ci_positive,
                "compact_item_win_fraction_mean": float(sub["compact_item_win_fraction"].mean()) if not sub.empty else float("nan"),
            }
        )

    hgb_catchup = None
    for entry in budget_payload:
        if entry["combined_wins_for_compact"] < entry["combined_comparisons"]:
            hgb_catchup = entry["label_budget"]
            break

    payload = {
        "method": METHOD_NAME,
        "compact_method": COMPACT_METHOD,
        "label_budgets": [entry["label_budget"] for entry in budget_payload],
        "seeds": sorted(int(x) for x in learned["seed"].unique()),
        "assets": sorted(x for x in learned["asset"].astype(str).unique()),
        "heldout_target_bearing_items": int(learned["item_id"].nunique()),
        "pair_observations": int(len(paired)),
        "pfa_points": int(combined["pfa"].nunique()),
        "budget_summary": budget_payload,
        "compact_all_pfa_win_budgets": all_win_budgets,
        "compact_all_pfa_positive_ci_budgets": positive_ci_budgets,
        "largest_budget_with_compact_all_pfa_win": all_win_budgets[-1] if all_win_budgets else None,
        "first_budget_where_hgb_catches_or_exceeds_compact_at_any_pfa": hgb_catchup,
        "all_methods_pfa_calibrated": bool(
            comparisons["compact_pfa_calibrated"].all() and comparisons["low_label_hgb_pfa_calibrated"].all()
        )
        if not comparisons.empty
        else False,
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
        "# AISTAP Full-Asset LOSO Low-Label HGB Label-Efficiency Audit",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Compact zero-target-label method: `{payload['compact_method']}`",
        f"- Low-label learned method: `{payload['method']}`",
        f"- Held-out target-bearing items: `{payload['heldout_target_bearing_items']}`",
        f"- Seeds: `{', '.join(str(s) for s in payload['seeds'])}`",
        f"- Budget unit: `{payload.get('budget_unit', 'positive_frames')}`",
        f"- Label budgets: `{', '.join(payload['label_budgets'])}`",
        f"- Compact all-Pfa win budgets: `{', '.join(payload['compact_all_pfa_win_budgets']) if payload['compact_all_pfa_win_budgets'] else 'none'}`",
        f"- Compact all-Pfa positive-CI budgets: `{', '.join(payload['compact_all_pfa_positive_ci_budgets']) if payload['compact_all_pfa_positive_ci_budgets'] else 'none'}`",
        f"- First budget where HGB catches or exceeds compact at any Pfa: `{payload['first_budget_where_hgb_catches_or_exceeds_compact_at_any_pfa']}`",
        f"- All methods Pfa calibrated: `{str(payload['all_methods_pfa_calibrated']).lower()}`",
        "",
        "## Protocol",
        "",
        "- Cache the same raw/residual feature cube used by the full LOSO HGB boundary audit for every target-bearing frame in each official full asset.",
        "- For each train/test direction, randomly select the requested source-domain positive-frame or positive-pixel budget and train a raw/residual HGB only from those labeled examples.",
        "- Test on every target-bearing frame in the opposite official full asset; repeat for each seed and label budget.",
        "- Compare the low-label HGB to compact TP-SSCS, which uses no target labels from either official full asset at this stage.",
        "",
        "## Budget Summary",
        "",
        "| Label budget | Compact wins / Pfa | Min compact-HGB delta | Mean compact-HGB delta | All CI lows positive | Mean item win fraction |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for entry in payload["budget_summary"]:
        lines.append(
            f"| {entry['label_budget']} | {entry['combined_wins_for_compact']}/{entry['combined_comparisons']} | "
            f"{entry['min_combined_delta_compact_minus_low_label_hgb']:.4f} | "
            f"{entry['mean_combined_delta_compact_minus_low_label_hgb']:.4f} | "
            f"{str(entry['ci_lower_bounds_positive_all_pfa']).lower()} | "
            f"{entry['compact_item_win_fraction_mean']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Combined Operating Points",
            "",
            "| Budget | Pfa | Compact Pd | Low-label HGB Pd | Compact-HGB delta | Compact item win fraction |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )
    combined = comparisons[comparisons["asset"] == "combined"].copy()
    combined = combined.sort_values(
        ["label_budget", "pfa"],
        key=lambda s: s.map(lambda x: budget_sort_key(str(x))) if s.name == "label_budget" else s,
    )
    for _, row in combined.iterrows():
        lines.append(
            f"| {row['label_budget']} | {row['pfa']:.0e} | {row['compact_pd']:.4f} | "
            f"{row['low_label_hgb_pd']:.4f} | {row['delta_compact_minus_low_label_hgb']:.4f} | "
            f"{row['compact_item_win_fraction']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Bootstrap CI",
            "",
            "| Budget | Pfa | n pairs | Mean compact-HGB delta | 95% CI | Positive fraction |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in ci_df.iterrows():
        lines.append(
            f"| {row['label_budget']} | {row['pfa']:.0e} | {int(row['n_pair_observations'])} | "
            f"{row['mean_delta_compact_minus_low_label_hgb']:.4f} | "
            f"[{row['ci95_low']:.4f}, {row['ci95_high']:.4f}] | {row['positive_fraction']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Training Sample Audit",
            "",
            "| Seed | Budget | Train asset | Test asset | Selected positive frames | Positive pixels | Background pixels | Training samples |",
            "|---:|---:|---|---|---:|---:|---:|---:|",
        ]
    )
    for info in train_infos:
        lines.append(
            f"| {info['seed']} | {info['label_budget']} | `{info['train_asset']}` | `{info['test_asset']}` | "
            f"{info['selected_positive_frames']} | {info['positive_pixels']} | {info['background_pixels']} | {info['training_samples']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "- A compact win at small budgets supports a label-efficiency claim, not a universal superiority claim over fully supervised learned detectors.",
            "- If the HGB catches up at larger budgets, that should be reported as a supervised-data boundary rather than hidden.",
            "- This audit directly complements the full-label HGB boundary audit by separating zero-label structural robustness from supervised feature-ensemble capacity.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    global METHOD_NAME

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--candidate-date", default="20260715")
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--budgets", default="1,2,4,8,16,32,64,all")
    parser.add_argument("--budget-unit", choices=["positive_frames", "positive_pixels"], default="positive_frames")
    parser.add_argument("--seeds", default="20260717,20260718,20260719")
    parser.add_argument("--rank", type=int, default=30)
    parser.add_argument("--background-per-frame", type=int, default=4096)
    parser.add_argument("--background-per-positive-pixel", type=int, default=128)
    parser.add_argument("--max-iter", type=int, default=160)
    parser.add_argument("--learning-rate", type=float, default=0.06)
    parser.add_argument("--max-leaf-nodes", type=int, default=31)
    parser.add_argument("--l2", type=float, default=1e-3)
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--boot", type=int, default=2000)
    parser.add_argument("--max-positive-cache", type=int, default=None)
    args = parser.parse_args()

    output_prefix = "aistap_full_asset_loso_low_label_hgb"
    if args.budget_unit == "positive_pixels":
        METHOD_NAME = "loso_low_positive_pixel_raw_residual_hgb"
        output_prefix = "aistap_full_asset_loso_low_positive_pixel_hgb"

    root = Path(args.root).resolve()
    full_dir = root / "data" / "downloads" / "aistap_sim" / "full"
    assets = sorted(full_dir.glob("sim*_test.mat"))
    if len(assets) < 2:
        raise FileNotFoundError(f"Need at least two full assets under {full_dir}")
    asset_by_name = {p.name: p for p in assets}
    directions = [("simMed_test.mat", "simWind_test.mat"), ("simWind_test.mat", "simMed_test.mat")]
    pfas = parse_floats(args.pfas)
    budgets = parse_ints_or_all(args.budgets)
    seeds = parse_ints(args.seeds)

    cache: dict[str, list[FrameRecord]] = {}
    for asset_name in sorted({name for pair in directions for name in pair}):
        cache[asset_name] = load_positive_records(asset_by_name[asset_name], rank=args.rank, max_positive=args.max_positive_cache)

    learned_frames: list[pd.DataFrame] = []
    train_infos: list[dict[str, Any]] = []
    for seed in seeds:
        for budget in budgets:
            label = budget_label(budget)
            for direction_idx, (train_name, test_name) in enumerate(directions):
                selection_seed = seed + 1009 * (direction_idx + 1) + 7919 * budget_sort_key(label)
                rng = np.random.default_rng(seed + 104729 * (direction_idx + 1) + 17 * budget_sort_key(label))
                if args.budget_unit == "positive_frames":
                    selected = select_budget_records(cache[train_name], budget, seed=selection_seed)
                    x, y, weights, info = collect_training_samples(selected, rng, args.background_per_frame)
                else:
                    x, y, weights, info = collect_training_pixel_samples(
                        cache[train_name],
                        budget,
                        rng,
                        args.background_per_positive_pixel,
                    )
                model = train_hgb(
                    x,
                    y,
                    weights,
                    max_iter=args.max_iter,
                    learning_rate=args.learning_rate,
                    max_leaf_nodes=args.max_leaf_nodes,
                    l2_regularization=args.l2,
                    seed=seed + direction_idx,
                )
                learned = evaluate_model(
                    model,
                    cache[test_name],
                    train_asset=train_name,
                    budget=budget,
                    budget_unit=args.budget_unit,
                    selected_positive_frames=int(info["positive_frames"]),
                    selected_positive_pixels=int(info["positive_pixels"]),
                    seed=seed,
                    pfas=pfas,
                )
                learned_frames.append(learned)
                train_infos.append(
                    {
                        "seed": seed,
                        "label_budget": label,
                        "label_budget_unit": args.budget_unit,
                        "train_asset": train_name,
                        "test_asset": test_name,
                        "selected_positive_frames": int(info["positive_frames"]),
                        **info,
                    }
                )

    learned_all = pd.concat(learned_frames, ignore_index=True)
    compact_rows = load_existing_candidate_rows(root, args.candidate_date)
    comparisons, ci_df, payload = compare_low_label_to_compact(
        learned_all,
        compact_rows,
        pfa_tolerance=args.pfa_tolerance,
        n_boot=args.boot,
        seed=min(seeds),
    )
    payload.update(
        {
            "date": args.date,
            "candidate_date": args.candidate_date,
            "budget_unit": args.budget_unit,
            "features": hgb.FEATURE_NAMES,
            "rank": args.rank,
            "background_per_frame": args.background_per_frame,
            "background_per_positive_pixel": args.background_per_positive_pixel,
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

    learned_csv = result_dir / f"{output_prefix}_{args.date}.csv"
    comparison_csv = result_dir / f"{output_prefix}_comparison_{args.date}.csv"
    ci_csv = result_dir / f"{output_prefix}_bootstrap_ci_{args.date}.csv"
    json_path = result_dir / f"{output_prefix}_{args.date}.json"
    md_path = log_dir / f"{output_prefix}_{args.date}.md"

    learned_all.to_csv(learned_csv, index=False)
    comparisons.to_csv(comparison_csv, index=False)
    ci_df.to_csv(ci_csv, index=False)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(md_path, args.date, payload, train_infos, comparisons, ci_df)

    print(json.dumps({k: payload[k] for k in [
        "method",
        "compact_method",
        "label_budgets",
        "seeds",
        "heldout_target_bearing_items",
        "compact_all_pfa_win_budgets",
        "compact_all_pfa_positive_ci_budgets",
        "first_budget_where_hgb_catches_or_exceeds_compact_at_any_pfa",
        "all_methods_pfa_calibrated",
    ]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
