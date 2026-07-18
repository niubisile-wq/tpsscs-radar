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

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SRC = ROOT / "src"
for path in [SCRIPTS, SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import evaluate_aistap_full_asset_target_free_calibration as tf
from evaluate_aistap_target_preservation_ablation import load_trainable_model


METHODS = ["raw", "low_rank_residual_k30", "tpsscs_finished_detector"]


def parse_floats(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def pfa_label(value: float) -> str:
    return f"{float(value):.0e}" if float(value) < 0.001 else f"{float(value):.3g}"


def background_for_frames(frames: list[tf.FrameScores], score_name: str) -> np.ndarray:
    return tf.concatenate_background(frames, score_name).astype(float, copy=False)


def tail_scale(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float).reshape(-1)
    if values.size == 0:
        return 1.0
    q999 = float(np.quantile(values, 0.999))
    q99 = float(np.quantile(values, 0.99))
    scale = q999 - q99
    if not np.isfinite(scale) or scale <= 0.0:
        scale = float(np.std(values))
    return max(scale, 1e-12)


def threshold(bg: np.ndarray, pfa: float) -> float:
    return tf.base.conservative_cfar_threshold(bg, float(pfa))[0]


def build_calibration_cache(frames_by_asset: dict[str, list[tf.FrameScores]]) -> dict[str, dict[str, np.ndarray]]:
    cache: dict[str, dict[str, np.ndarray]] = {}
    for asset, frames in frames_by_asset.items():
        target_free = [frame for frame in frames if not frame.has_target]
        if not target_free:
            raise ValueError(f"asset has no target-free frames: {asset}")
        gate_bg = background_for_frames(target_free, "gate")
        cache[asset] = {
            "raw": background_for_frames(target_free, "raw"),
            "residual": background_for_frames(target_free, "residual"),
            "gate": gate_bg,
            "gate_max": np.asarray([float(np.max(gate_bg))]),
            "gate_tail_scale": np.asarray([tail_scale(gate_bg)]),
            "target_free_frames": np.asarray([len(target_free)]),
        }
    return cache


def evaluate_configuration(
    frames_by_asset: dict[str, list[tf.FrameScores]],
    calibration_cache: dict[str, dict[str, np.ndarray]],
    pfas: list[float],
    mode: str,
    residual_safety_factor: float,
    gate_margin_scale: float,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    asset_names = sorted(frames_by_asset)
    for asset in asset_names:
        if mode == "same_asset_target_free_conservative":
            calibration_asset = asset
        elif mode == "cross_asset_target_free_conservative":
            calibration_asset = [name for name in asset_names if name != asset][0]
        else:
            raise ValueError(f"unknown calibration mode: {mode}")

        cal = calibration_cache[calibration_asset]
        gate_threshold = float(cal["gate_max"][0] + gate_margin_scale * cal["gate_tail_scale"][0])
        raw_thresholds = {pfa: threshold(cal["raw"], pfa / residual_safety_factor) for pfa in pfas}
        residual_thresholds = {pfa: threshold(cal["residual"], pfa / residual_safety_factor) for pfa in pfas}

        for frame in frames_by_asset[asset]:
            if not frame.has_target:
                continue
            bg = ~frame.mask
            for pfa in pfas:
                pfa = float(pfa)
                raw_det = frame.raw > raw_thresholds[pfa]
                residual_det = frame.residual > residual_thresholds[pfa]
                finished_det = residual_det | (frame.gate > gate_threshold)
                for method, det in [
                    ("raw", raw_det),
                    ("low_rank_residual_k30", residual_det),
                    ("tpsscs_finished_detector", finished_det),
                ]:
                    rows.append(
                        {
                            "calibration_mode": mode,
                            "calibration_asset": calibration_asset,
                            "asset": asset,
                            "image_index": int(frame.image_index),
                            "item_id": frame.item_id,
                            "method": method,
                            "pfa_target": pfa,
                            "residual_safety_factor": float(residual_safety_factor),
                            "gate_margin_scale": float(gate_margin_scale),
                            "gate_threshold": gate_threshold if method == "tpsscs_finished_detector" else float("nan"),
                            "pd": float(det[frame.mask].mean()),
                            "empirical_pfa": float(det[bg].mean()),
                            "target_count": int(frame.mask.sum()),
                            "background_count": int(bg.sum()),
                            "false_alarms": int(det[bg].sum()),
                            "detections": int(det.sum()),
                            "threshold_policy": "target_free_threshold_with_residual_safety_and_gate_margin",
                        }
                    )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    keys = ["calibration_mode", "residual_safety_factor", "gate_margin_scale", "asset", "pfa_target", "method"]
    summary = (
        df.groupby(keys, dropna=False)
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            empirical_pfa_max=("empirical_pfa", "max"),
            false_alarms_total=("false_alarms", "sum"),
            background_count_total=("background_count", "sum"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined_keys = ["calibration_mode", "residual_safety_factor", "gate_margin_scale", "pfa_target", "method"]
    combined = (
        df.groupby(combined_keys, dropna=False)
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            empirical_pfa_max=("empirical_pfa", "max"),
            false_alarms_total=("false_alarms", "sum"),
            background_count_total=("background_count", "sum"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined["asset"] = "combined"
    return pd.concat([summary, combined[summary.columns]], ignore_index=True).sort_values(keys).reset_index(drop=True)


def compare(summary: pd.DataFrame, pfa_tolerance: float) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_cols = ["calibration_mode", "residual_safety_factor", "gate_margin_scale", "asset", "pfa_target"]
    for keys, group in summary.groupby(group_cols, sort=True):
        mode, safety, margin, asset, pfa = keys
        lookup = {str(row["method"]): row for _, row in group.iterrows()}
        if not all(method in lookup for method in METHODS):
            continue
        t = lookup["tpsscs_finished_detector"]
        raw = lookup["raw"]
        low = lookup["low_rank_residual_k30"]
        ceiling = float(pfa) * float(pfa_tolerance) + 1e-7
        rows.append(
            {
                "calibration_mode": mode,
                "residual_safety_factor": float(safety),
                "gate_margin_scale": float(margin),
                "asset": asset,
                "pfa_target": float(pfa),
                "n_items": int(t["n_items"]),
                "tpsscs_pd": float(t["pd_mean"]),
                "raw_pd": float(raw["pd_mean"]),
                "lowrank_pd": float(low["pd_mean"]),
                "delta_vs_raw": float(t["pd_mean"]) - float(raw["pd_mean"]),
                "delta_vs_lowrank": float(t["pd_mean"]) - float(low["pd_mean"]),
                "tpsscs_empirical_pfa": float(t["empirical_pfa_mean"]),
                "raw_empirical_pfa": float(raw["empirical_pfa_mean"]),
                "lowrank_empirical_pfa": float(low["empirical_pfa_mean"]),
                "tpsscs_false_alarms_total": int(t["false_alarms_total"]),
                "background_count_total": int(t["background_count_total"]),
                "pfa_ceiling": ceiling,
                "tpsscs_pfa_calibrated": float(t["empirical_pfa_mean"]) <= ceiling,
                "raw_pfa_calibrated": float(raw["empirical_pfa_mean"]) <= ceiling,
                "lowrank_pfa_calibrated": float(low["empirical_pfa_mean"]) <= ceiling,
                "beats_raw": float(t["pd_mean"]) > float(raw["pd_mean"]),
                "beats_lowrank": float(t["pd_mean"]) > float(low["pd_mean"]),
            }
        )
    return pd.DataFrame(rows).sort_values(group_cols).reset_index(drop=True)


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_bootstrap: int) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return float("nan"), float("nan")
    samples = rng.choice(values, size=(int(n_bootstrap), values.size), replace=True).mean(axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def bootstrap_for_candidates(df: pd.DataFrame, candidates: pd.DataFrame, n_bootstrap: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(seed)
    if candidates.empty:
        return pd.DataFrame()
    for _, candidate in candidates.iterrows():
        mode = candidate["calibration_mode"]
        safety = float(candidate["residual_safety_factor"])
        margin = float(candidate["gate_margin_scale"])
        sub = df[
            (df["calibration_mode"] == mode)
            & np.isclose(df["residual_safety_factor"].astype(float), safety)
            & np.isclose(df["gate_margin_scale"].astype(float), margin)
        ]
        pivot = sub.pivot_table(
            index=["asset", "item_id", "pfa_target"],
            columns="method",
            values="pd",
            aggfunc="first",
        ).reset_index()
        for pfa in sorted(pivot["pfa_target"].unique()):
            pfa_sub = pivot[np.isclose(pivot["pfa_target"].astype(float), float(pfa))]
            for comparator in ["raw", "low_rank_residual_k30"]:
                values = (
                    pfa_sub["tpsscs_finished_detector"].astype(float) - pfa_sub[comparator].astype(float)
                ).to_numpy()
                ci_low, ci_high = bootstrap_ci(values, rng, n_bootstrap)
                rows.append(
                    {
                        "calibration_mode": mode,
                        "residual_safety_factor": safety,
                        "gate_margin_scale": margin,
                        "pfa_target": float(pfa),
                        "comparator": comparator,
                        "n_items": int(values.size),
                        "mean_delta_pd": float(values.mean()) if values.size else float("nan"),
                        "ci95_low": ci_low,
                        "ci95_high": ci_high,
                        "wins": int((values > 0).sum()),
                        "ties": int((values == 0).sum()),
                        "losses": int((values < 0).sum()),
                    }
                )
    return pd.DataFrame(rows)


def candidate_table(comparisons: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_cols = ["calibration_mode", "residual_safety_factor", "gate_margin_scale"]
    combined = comparisons[comparisons["asset"] == "combined"].copy()
    assets = comparisons[comparisons["asset"] != "combined"].copy()
    for keys, group in combined.groupby(group_cols, sort=True):
        mode, safety, margin = keys
        asset_group = assets[
            (assets["calibration_mode"] == mode)
            & np.isclose(assets["residual_safety_factor"].astype(float), float(safety))
            & np.isclose(assets["gate_margin_scale"].astype(float), float(margin))
        ]
        rows.append(
            {
                "calibration_mode": mode,
                "residual_safety_factor": float(safety),
                "gate_margin_scale": float(margin),
                "combined_pfa_calibrated": bool(group["tpsscs_pfa_calibrated"].all()),
                "asset_pfa_calibrated": bool(asset_group["tpsscs_pfa_calibrated"].all()),
                "all_methods_combined_pfa_calibrated": bool(
                    group[["tpsscs_pfa_calibrated", "raw_pfa_calibrated", "lowrank_pfa_calibrated"]].all().all()
                ),
                "combined_wins_vs_raw": int(group["beats_raw"].sum()),
                "combined_wins_vs_lowrank": int(group["beats_lowrank"].sum()),
                "asset_wins_vs_raw": int(asset_group["beats_raw"].sum()),
                "asset_wins_vs_lowrank": int(asset_group["beats_lowrank"].sum()),
                "combined_points": int(group.shape[0]),
                "asset_points": int(asset_group.shape[0]),
                "min_combined_delta_vs_raw": float(group["delta_vs_raw"].min()),
                "min_combined_delta_vs_lowrank": float(group["delta_vs_lowrank"].min()),
                "max_combined_tpsscs_pfa_ratio": float(
                    (group["tpsscs_empirical_pfa"].astype(float) / group["pfa_target"].astype(float)).max()
                ),
                "max_asset_tpsscs_pfa_ratio": float(
                    (asset_group["tpsscs_empirical_pfa"].astype(float) / asset_group["pfa_target"].astype(float)).max()
                )
                if not asset_group.empty
                else float("nan"),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["strict_pass"] = (
        out["combined_pfa_calibrated"]
        & out["asset_pfa_calibrated"]
        & (out["combined_wins_vs_raw"] == out["combined_points"])
        & (out["combined_wins_vs_lowrank"] == out["combined_points"])
        & (out["asset_wins_vs_raw"] == out["asset_points"])
        & (out["asset_wins_vs_lowrank"] == out["asset_points"])
        & (out["min_combined_delta_vs_lowrank"] > 0.0)
    )
    return out.sort_values(
        ["strict_pass", "max_combined_tpsscs_pfa_ratio", "min_combined_delta_vs_lowrank"],
        ascending=[False, True, False],
    ).reset_index(drop=True)


def write_markdown(path: Path, payload: dict[str, Any], candidates: pd.DataFrame, comparisons: pd.DataFrame, bootstrap: pd.DataFrame) -> None:
    passing = candidates[candidates["strict_pass"] == True].copy() if not candidates.empty else pd.DataFrame()
    best = passing.iloc[0] if not passing.empty else None
    lines = [
        "# AISTAP Conservative Target-Free Calibration Sweep",
        "",
        f"Date: {payload['date']}",
        "",
        "## Verdict",
        "",
        f"- Target-bearing items: `{payload['target_bearing_items']}`.",
        f"- Target-free support per asset: `{payload['target_free_frames_by_asset']}` frames.",
        f"- Residual safety factors: `{payload['residual_safety_factors']}`.",
        f"- Gate margin scales: `{payload['gate_margin_scales']}`.",
        f"- Strict passing configurations: `{payload['strict_passing_configurations']}`.",
    ]
    if best is not None:
        lines.extend(
            [
                f"- Best strict pass: mode `{best['calibration_mode']}`, residual safety `{best['residual_safety_factor']:.3g}`, gate margin `{best['gate_margin_scale']:.3g}`.",
                f"- Best strict pass max combined TP-SSCS Pfa ratio: `{float(best['max_combined_tpsscs_pfa_ratio']):.3f}`.",
                f"- Best strict pass minimum combined delta vs low-rank: `{float(best['min_combined_delta_vs_lowrank']):.4f}`.",
            ]
        )
    else:
        lines.append("- No strict configuration satisfied both empirical-Pfa calibration and all-Pfa TP-SSCS wins.")

    lines.extend(
        [
            "",
            "## Passing Configurations",
            "",
            "| Mode | Residual safety | Gate margin | Min delta raw | Min delta low-rank | Max Pfa ratio |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    if passing.empty:
        lines.append("| none | | | | | |")
    else:
        for _, row in passing.head(12).iterrows():
            lines.append(
                f"| `{row['calibration_mode']}` | {float(row['residual_safety_factor']):.3g} | "
                f"{float(row['gate_margin_scale']):.3g} | {float(row['min_combined_delta_vs_raw']):.4f} | "
                f"{float(row['min_combined_delta_vs_lowrank']):.4f} | {float(row['max_combined_tpsscs_pfa_ratio']):.3f} |"
            )

    if best is not None:
        mode = best["calibration_mode"]
        safety = float(best["residual_safety_factor"])
        margin = float(best["gate_margin_scale"])
        sub = comparisons[
            (comparisons["asset"] == "combined")
            & (comparisons["calibration_mode"] == mode)
            & np.isclose(comparisons["residual_safety_factor"].astype(float), safety)
            & np.isclose(comparisons["gate_margin_scale"].astype(float), margin)
        ].sort_values("pfa_target")
        lines.extend(
            [
                "",
                "## Best Strict-Pass Combined Operating Points",
                "",
                "| Pfa | TP-SSCS Pd | Raw Pd | Low-rank Pd | Delta raw | Delta low-rank | TP-SSCS empirical Pfa |",
                "|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for _, row in sub.iterrows():
            lines.append(
                f"| `{pfa_label(float(row['pfa_target']))}` | {float(row['tpsscs_pd']):.4f} | "
                f"{float(row['raw_pd']):.4f} | {float(row['lowrank_pd']):.4f} | "
                f"{float(row['delta_vs_raw']):.4f} | {float(row['delta_vs_lowrank']):.4f} | "
                f"{float(row['tpsscs_empirical_pfa']):.6g} |"
            )
        boot = bootstrap[
            (bootstrap["calibration_mode"] == mode)
            & np.isclose(bootstrap["residual_safety_factor"].astype(float), safety)
            & np.isclose(bootstrap["gate_margin_scale"].astype(float), margin)
        ]
        lines.extend(
            [
                "",
                "## Best Strict-Pass Bootstrap Deltas",
                "",
                "| Comparator | Pfa | Mean delta | CI95 low | CI95 high | Win/Tie/Loss |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for _, row in boot.sort_values(["comparator", "pfa_target"]).iterrows():
            lines.append(
                f"| `{row['comparator']}` | `{pfa_label(float(row['pfa_target']))}` | "
                f"{float(row['mean_delta_pd']):.4f} | {float(row['ci95_low']):.4f} | "
                f"{float(row['ci95_high']):.4f} | {int(row['wins'])}/{int(row['ties'])}/{int(row['losses'])} |"
            )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is a target-free calibration sensitivity sweep, not a new model-training result.",
            "- The sweep uses target-bearing backgrounds to audit empirical Pfa after applying target-free thresholds; selected conservative settings should therefore be described as diagnostic unless pre-registered on a future collection.",
            "- The result addresses whether a conservative target-free safety margin can recover empirical-Pfa control on the current official assets; it does not prove deployment-ready fixed calibration under arbitrary background shift.",
            "- The paired bootstrap unit is the target-bearing frame.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--assets", default="data/downloads/aistap_sim/full/simMed_test.mat,data/downloads/aistap_sim/full/simWind_test.mat")
    parser.add_argument("--state", default="results/aistap_sample/tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt")
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--residual-safety-factors", default="1,2,5,10,20,50,100,200,500,1000")
    parser.add_argument("--gate-margin-scales", default="0,0.25,0.5,1,2,4,8,16,32")
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260717)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    pfas = parse_floats(args.pfas)
    safety_factors = parse_floats(args.residual_safety_factors)
    gate_margins = parse_floats(args.gate_margin_scales)
    asset_paths = [root / item.strip() for item in args.assets.split(",") if item.strip()]
    state_path = root / args.state

    model = load_trainable_model(state_path)
    model.eval()

    frames_by_asset: dict[str, list[tf.FrameScores]] = {}
    with torch.no_grad():
        for asset_path in asset_paths:
            frames_by_asset[asset_path.name] = tf.load_asset_scores(asset_path, model)

    calibration_cache = build_calibration_cache(frames_by_asset)
    frames_total = sum(len(frames) for frames in frames_by_asset.values())
    target_items = sum(sum(1 for frame in frames if frame.has_target) for frames in frames_by_asset.values())
    target_free_by_asset = {
        asset: int(calibration_cache[asset]["target_free_frames"][0]) for asset in sorted(calibration_cache)
    }

    dfs: list[pd.DataFrame] = []
    for mode in ["same_asset_target_free_conservative", "cross_asset_target_free_conservative"]:
        for safety in safety_factors:
            for margin in gate_margins:
                dfs.append(evaluate_configuration(frames_by_asset, calibration_cache, pfas, mode, safety, margin))
    all_rows = pd.concat(dfs, ignore_index=True)
    summary = summarize(all_rows)
    comparisons = compare(summary, args.pfa_tolerance)
    candidates = candidate_table(comparisons)
    passing = candidates[candidates["strict_pass"] == True].copy() if not candidates.empty else pd.DataFrame()
    bootstrap = bootstrap_for_candidates(all_rows, passing.head(4), args.bootstrap, args.seed)

    payload: dict[str, Any] = {
        "date": args.date,
        "assets": [path.name for path in asset_paths],
        "state": str(Path(args.state)),
        "frames_total": int(frames_total),
        "target_bearing_items": int(target_items),
        "target_free_frames_by_asset": target_free_by_asset,
        "pfa_grid": [pfa_label(pfa) for pfa in pfas],
        "residual_safety_factors": safety_factors,
        "gate_margin_scales": gate_margins,
        "pfa_tolerance": float(args.pfa_tolerance),
        "bootstrap_replicates": int(args.bootstrap),
        "bootstrap_seed": int(args.seed),
        "strict_passing_configurations": int(passing.shape[0]),
        "best_strict_pass": passing.iloc[0].to_dict() if not passing.empty else None,
        "boundary": [
            "target_free_sensitivity_sweep_not_new_training",
            "uses_target_bearing_backgrounds_to_audit_empirical_pfa",
            "not_deployment_ready_fixed_calibration_claim",
            "paired_bootstrap_unit_is_target_bearing_frame",
        ],
    }

    all_rows_path = result_dir / f"aistap_full_asset_conservative_target_free_calibration_{args.date}.csv"
    summary_path = result_dir / f"aistap_full_asset_conservative_target_free_calibration_summary_{args.date}.csv"
    comparison_path = result_dir / f"aistap_full_asset_conservative_target_free_calibration_comparison_{args.date}.csv"
    candidate_path = result_dir / f"aistap_full_asset_conservative_target_free_calibration_candidates_{args.date}.csv"
    bootstrap_path = result_dir / f"aistap_full_asset_conservative_target_free_calibration_bootstrap_ci_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_conservative_target_free_calibration_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_conservative_target_free_calibration_{args.date}.md"

    all_rows.to_csv(all_rows_path, index=False)
    summary.to_csv(summary_path, index=False)
    comparisons.to_csv(comparison_path, index=False)
    candidates.to_csv(candidate_path, index=False)
    bootstrap.to_csv(bootstrap_path, index=False)
    json_path.write_text(
        json.dumps(
            {
                **payload,
                "candidate_summary": candidates.to_dict(orient="records"),
                "bootstrap_summary": bootstrap.to_dict(orient="records"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(md_path, payload, candidates, comparisons, bootstrap)

    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")
    print(
        "conservative_target_free: "
        f"strict_passing_configurations={payload['strict_passing_configurations']} "
        f"best={payload['best_strict_pass']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
