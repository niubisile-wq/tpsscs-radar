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

import evaluate_aistap_full_asset_classical_cfar_baselines as base

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evaluate_aistap_target_preservation_ablation import load_trainable_model


METHODS = ["raw", "low_rank_residual_k30", "tpsscs_finished_detector"]


@dataclass
class FrameScores:
    asset: str
    image_index: int
    item_id: str
    has_target: bool
    raw: np.ndarray
    residual: np.ndarray
    gate: np.ndarray
    mask: np.ndarray


def parse_floats(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def ntrue_from_meta(meta: dict[str, Any]) -> float:
    try:
        return float(np.asarray(meta.get("Ntrue", 0.0)).reshape(-1)[0])
    except Exception:
        return 0.0


def load_asset_scores(asset_path: Path, model: torch.nn.Module, max_frames: int | None = None) -> list[FrameScores]:
    rows: list[FrameScores] = []
    with h5py.File(asset_path, "r") as f, torch.no_grad():
        refs = f["meta_per_image"][()].reshape(-1)
        for idx, ref in enumerate(refs):
            if max_frames is not None and len(rows) >= max_frames:
                break
            meta = base.read_meta(f, ref)
            x_np = base.to_complex(f["rd_img"][idx])
            raw_score = base.score_map(x_np)
            x = torch.from_numpy(x_np).to(torch.complex128)
            out = model(x)
            residual_score = base.score_map(out["residual"].detach().cpu().numpy())
            gate_score = out["score"].detach().cpu().numpy()
            mask = base.target_mask(meta, raw_score.shape)
            rows.append(
                FrameScores(
                    asset=asset_path.name,
                    image_index=idx,
                    item_id=f"{asset_path.name}#{idx}",
                    has_target=ntrue_from_meta(meta) > 0.0 and bool(mask.any()),
                    raw=raw_score.astype(np.float64, copy=False),
                    residual=residual_score.astype(np.float64, copy=False),
                    gate=gate_score.astype(np.float64, copy=False),
                    mask=mask,
                )
            )
    return rows


def concatenate_background(frames: list[FrameScores], score_name: str) -> np.ndarray:
    parts: list[np.ndarray] = []
    for frame in frames:
        score = getattr(frame, score_name)
        if frame.has_target:
            parts.append(score[~frame.mask].reshape(-1))
        else:
            parts.append(score.reshape(-1))
    if not parts:
        return np.asarray([], dtype=float)
    return np.concatenate(parts).astype(float, copy=False)


def thresholds_from_frames(frames: list[FrameScores], pfas: list[float]) -> dict[str, dict[float, float]]:
    raw_bg = concatenate_background(frames, "raw")
    residual_bg = concatenate_background(frames, "residual")
    gate_bg = concatenate_background(frames, "gate")
    if raw_bg.size == 0 or residual_bg.size == 0 or gate_bg.size == 0:
        raise ValueError("Calibration frames have no background pixels.")
    thresholds: dict[str, dict[float, float]] = {
        "raw": {},
        "low_rank_residual_k30": {},
        "tpsscs_residual": {},
        "tpsscs_gate": {},
    }
    gate_threshold, _ = base.conservative_cfar_threshold(gate_bg, 0.0)
    for pfa in pfas:
        thresholds["raw"][float(pfa)] = base.conservative_cfar_threshold(raw_bg, pfa)[0]
        residual_threshold = base.conservative_cfar_threshold(residual_bg, pfa)[0]
        thresholds["low_rank_residual_k30"][float(pfa)] = residual_threshold
        thresholds["tpsscs_residual"][float(pfa)] = residual_threshold
        thresholds["tpsscs_gate"][float(pfa)] = gate_threshold
    return thresholds


def evaluate_frame(frame: FrameScores, thresholds: dict[str, dict[float, float]], pfas: list[float], calibration_mode: str, calibration_asset: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pfa in pfas:
        pfa = float(pfa)
        method_detections = {
            "raw": frame.raw > thresholds["raw"][pfa],
            "low_rank_residual_k30": frame.residual > thresholds["low_rank_residual_k30"][pfa],
            "tpsscs_finished_detector": (frame.residual > thresholds["tpsscs_residual"][pfa])
            | (frame.gate > thresholds["tpsscs_gate"][pfa]),
        }
        for method, det in method_detections.items():
            bg = ~frame.mask
            rows.append(
                {
                    "calibration_mode": calibration_mode,
                    "calibration_asset": calibration_asset,
                    "asset": frame.asset,
                    "image_index": frame.image_index,
                    "item_id": frame.item_id,
                    "method": method,
                    "pfa_target": pfa,
                    "pd": float(det[frame.mask].mean()) if frame.mask.any() else float("nan"),
                    "empirical_pfa": float(det[bg].mean()) if bg.any() else float("nan"),
                    "target_count": int(frame.mask.sum()),
                    "background_count": int(bg.sum()),
                    "false_alarms": int(det[bg].sum()) if bg.any() else 0,
                    "detections": int(det.sum()),
                    "threshold_policy": "target_free_background_fixed_threshold",
                }
            )
    return rows


def summarize_methods(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["calibration_mode", "asset", "pfa_target", "method"], dropna=False)
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined = (
        df.groupby(["calibration_mode", "pfa_target", "method"], dropna=False)
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


def compare_methods(df: pd.DataFrame, pfa_tolerance: float, n_boot: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    summary = summarize_methods(df)
    comparison_rows: list[dict[str, Any]] = []
    for mode in sorted(summary["calibration_mode"].unique()):
        mode_summary = summary[summary["calibration_mode"] == mode]
        for asset in sorted(mode_summary["asset"].unique()):
            asset_summary = mode_summary[mode_summary["asset"] == asset]
            for pfa in sorted(asset_summary["pfa_target"].unique()):
                sub = asset_summary[np.isclose(asset_summary["pfa_target"].astype(float), float(pfa))]
                proposed = sub[sub["method"] == "tpsscs_finished_detector"]
                raw = sub[sub["method"] == "raw"]
                lowrank = sub[sub["method"] == "low_rank_residual_k30"]
                if proposed.empty or raw.empty or lowrank.empty:
                    continue
                proposed_pd = float(proposed["pd_mean"].iloc[0])
                raw_pd = float(raw["pd_mean"].iloc[0])
                lowrank_pd = float(lowrank["pd_mean"].iloc[0])
                proposed_pfa = float(proposed["empirical_pfa_mean"].iloc[0])
                pfa_ceiling = float(pfa) * pfa_tolerance + 1e-7
                comparison_rows.append(
                    {
                        "calibration_mode": mode,
                        "asset": asset,
                        "pfa": float(pfa),
                        "n_items": int(proposed["n_items"].iloc[0]),
                        "tpsscs_pd": proposed_pd,
                        "raw_pd": raw_pd,
                        "lowrank_pd": lowrank_pd,
                        "delta_vs_raw": proposed_pd - raw_pd,
                        "delta_vs_lowrank": proposed_pd - lowrank_pd,
                        "tpsscs_empirical_pfa": proposed_pfa,
                        "raw_empirical_pfa": float(raw["empirical_pfa_mean"].iloc[0]),
                        "lowrank_empirical_pfa": float(lowrank["empirical_pfa_mean"].iloc[0]),
                        "pfa_ceiling": pfa_ceiling,
                        "tpsscs_pfa_calibrated": proposed_pfa <= pfa_ceiling,
                        "beats_raw": proposed_pd > raw_pd,
                        "beats_lowrank": proposed_pd > lowrank_pd,
                    }
                )
    comparisons = pd.DataFrame(comparison_rows)

    rng = np.random.default_rng(seed)
    pivot = (
        df.pivot_table(
            index=["calibration_mode", "asset", "item_id", "pfa_target"],
            columns="method",
            values="pd",
            aggfunc="mean",
        )
        .reset_index()
        .dropna(subset=METHODS)
    )
    ci_rows: list[dict[str, Any]] = []
    for mode in sorted(pivot["calibration_mode"].unique()):
        mode_rows = pivot[pivot["calibration_mode"] == mode]
        for pfa in sorted(mode_rows["pfa_target"].unique()):
            sub = mode_rows[np.isclose(mode_rows["pfa_target"].astype(float), float(pfa))]
            for comparator in ["raw", "low_rank_residual_k30"]:
                values = (sub["tpsscs_finished_detector"].astype(float) - sub[comparator].astype(float)).to_numpy()
                ci = bootstrap_ci(values, rng, n_boot)
                ci_rows.append(
                    {
                        "calibration_mode": mode,
                        "pfa": float(pfa),
                        "comparator": comparator,
                        "n_items": int(values.size),
                        "mean_delta_pd": ci["mean"],
                        "ci95_low": ci["ci_low"],
                        "ci95_high": ci["ci_high"],
                        "positive_fraction": float(np.mean(values > 0.0)) if values.size else float("nan"),
                    }
                )
    ci_df = pd.DataFrame(ci_rows)

    mode_payload: list[dict[str, Any]] = []
    for mode in sorted(comparisons["calibration_mode"].unique()):
        sub = comparisons[comparisons["calibration_mode"] == mode]
        combined = sub[sub["asset"] == "combined"]
        asset_rows = sub[sub["asset"] != "combined"]
        ci_sub = ci_df[ci_df["calibration_mode"] == mode]
        raw_ci = ci_sub[ci_sub["comparator"] == "raw"]
        lowrank_ci = ci_sub[ci_sub["comparator"] == "low_rank_residual_k30"]
        mode_payload.append(
            {
                "calibration_mode": mode,
                "asset_level_comparisons": int(len(asset_rows)),
                "combined_comparisons": int(len(combined)),
                "asset_level_wins_vs_raw": int(asset_rows["beats_raw"].sum()),
                "asset_level_wins_vs_lowrank": int(asset_rows["beats_lowrank"].sum()),
                "combined_wins_vs_raw": int(combined["beats_raw"].sum()),
                "combined_wins_vs_lowrank": int(combined["beats_lowrank"].sum()),
                "min_combined_delta_vs_raw": float(combined["delta_vs_raw"].min()) if not combined.empty else float("nan"),
                "min_combined_delta_vs_lowrank": float(combined["delta_vs_lowrank"].min()) if not combined.empty else float("nan"),
                "all_tpsscs_pfa_calibrated": bool(sub["tpsscs_pfa_calibrated"].all()) if not sub.empty else False,
                "ci_lower_bounds_positive_vs_raw": bool((raw_ci["ci95_low"].astype(float) > 0.0).all()) if not raw_ci.empty else False,
                "ci_lower_bounds_positive_vs_lowrank": bool((lowrank_ci["ci95_low"].astype(float) > 0.0).all()) if not lowrank_ci.empty else False,
            }
        )
    positive_delta_modes = [
        item["calibration_mode"]
        for item in mode_payload
        if item["combined_wins_vs_raw"] == item["combined_comparisons"]
        and item["combined_wins_vs_lowrank"] == item["combined_comparisons"]
        and item["ci_lower_bounds_positive_vs_raw"]
        and item["ci_lower_bounds_positive_vs_lowrank"]
    ]
    pfa_calibrated_modes = [
        item["calibration_mode"] for item in mode_payload if item["all_tpsscs_pfa_calibrated"]
    ]
    passed_modes = [mode for mode in positive_delta_modes if mode in pfa_calibrated_modes]
    payload = {
        "methods": METHODS,
        "target_bearing_items": int(df["item_id"].nunique()),
        "calibration_modes": [item["calibration_mode"] for item in mode_payload],
        "positive_delta_modes": positive_delta_modes,
        "pfa_calibrated_modes": pfa_calibrated_modes,
        "passed_modes": passed_modes,
        "mode_summary": mode_payload,
    }
    return comparisons, ci_df, payload


def write_markdown(path: Path, date_tag: str, payload: dict[str, Any], calibration_counts: dict[str, Any], comparisons: pd.DataFrame, ci_df: pd.DataFrame) -> None:
    lines = [
        "# AISTAP Full-Asset Target-Free Calibration Audit",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Target-bearing items: `{payload['target_bearing_items']}`",
        f"- Calibration modes: `{', '.join(payload['calibration_modes'])}`",
        f"- Positive-delta modes: `{', '.join(payload['positive_delta_modes']) if payload['positive_delta_modes'] else 'none'}`",
        f"- Fully Pfa-calibrated modes: `{', '.join(payload['pfa_calibrated_modes']) if payload['pfa_calibrated_modes'] else 'none'}`",
        f"- Passed modes: `{', '.join(payload['passed_modes']) if payload['passed_modes'] else 'none'}`",
        "",
        "## Calibration Support",
        "",
        "| Asset | Target-free frames | Target-bearing frames |",
        "|---|---:|---:|",
    ]
    for asset, counts in calibration_counts.items():
        lines.append(f"| `{asset}` | {counts['target_free_frames']} | {counts['target_bearing_frames']} |")
    lines.extend(["", "## Mode Summary", "", "| Mode | Combined wins vs raw | Combined wins vs low-rank | Min delta vs raw | Min delta vs low-rank | CI positive vs raw | CI positive vs low-rank |", "|---|---:|---:|---:|---:|---:|---:|"])
    for item in payload["mode_summary"]:
        lines.append(
            f"| `{item['calibration_mode']}` | {item['combined_wins_vs_raw']}/{item['combined_comparisons']} | "
            f"{item['combined_wins_vs_lowrank']}/{item['combined_comparisons']} | "
            f"{item['min_combined_delta_vs_raw']:.4f} | {item['min_combined_delta_vs_lowrank']:.4f} | "
            f"{str(item['ci_lower_bounds_positive_vs_raw']).lower()} | {str(item['ci_lower_bounds_positive_vs_lowrank']).lower()} |"
        )
    lines.extend(["", "## Combined Operating Points", "", "| Mode | Pfa | TP-SSCS Pd | Raw Pd | Low-rank Pd | Delta vs raw | Delta vs low-rank | TP-SSCS empirical Pfa |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    combined = comparisons[comparisons["asset"] == "combined"].sort_values(["calibration_mode", "pfa"])
    for _, row in combined.iterrows():
        lines.append(
            f"| `{row['calibration_mode']}` | {row['pfa']:.0e} | {row['tpsscs_pd']:.4f} | "
            f"{row['raw_pd']:.4f} | {row['lowrank_pd']:.4f} | {row['delta_vs_raw']:.4f} | "
            f"{row['delta_vs_lowrank']:.4f} | {row['tpsscs_empirical_pfa']:.6g} |"
        )
    lines.extend(["", "## Bootstrap CI", "", "| Mode | Pfa | Comparator | n | Mean delta | 95% CI | Positive fraction |", "|---|---:|---|---:|---:|---:|---:|"])
    for _, row in ci_df.iterrows():
        lines.append(
            f"| `{row['calibration_mode']}` | {row['pfa']:.0e} | `{row['comparator']}` | {int(row['n_items'])} | "
            f"{row['mean_delta_pd']:.4f} | [{row['ci95_low']:.4f}, {row['ci95_high']:.4f}] | {row['positive_fraction']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This audit replaces per-target-frame background thresholding with thresholds estimated only from target-free frames.",
            "- `same_asset_target_free` calibrates each asset from its own target-free frames.",
            "- `cross_asset_target_free` calibrates each asset from the other official full asset's target-free frames.",
            "- This is a calibration-robustness audit, not a new dataset or a fully blind deployment test.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--state", default="results/aistap_sample/tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt")
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--max-frames", type=int, default=None)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    state_path = root / args.state
    model = load_trainable_model(state_path)
    model.eval()
    full_dir = root / "data" / "downloads" / "aistap_sim" / "full"
    asset_paths = sorted(full_dir.glob("sim*_test.mat"))
    if len(asset_paths) < 2:
        raise FileNotFoundError(f"Need at least two full assets under {full_dir}")
    pfas = parse_floats(args.pfas)

    by_asset = {path.name: load_asset_scores(path, model, max_frames=args.max_frames) for path in asset_paths}
    calibration_counts = {
        asset: {
            "target_free_frames": sum(not frame.has_target for frame in frames),
            "target_bearing_frames": sum(frame.has_target for frame in frames),
        }
        for asset, frames in by_asset.items()
    }

    rows: list[dict[str, Any]] = []
    for asset, frames in by_asset.items():
        target_frames = [frame for frame in frames if frame.has_target]
        same_calibration = [frame for frame in frames if not frame.has_target]
        if not same_calibration:
            raise ValueError(f"No target-free frames available for {asset}")
        same_thresholds = thresholds_from_frames(same_calibration, pfas)
        for frame in target_frames:
            rows.extend(evaluate_frame(frame, same_thresholds, pfas, "same_asset_target_free", asset))

        other_assets = [name for name in by_asset if name != asset]
        for other in other_assets:
            cross_calibration = [frame for frame in by_asset[other] if not frame.has_target]
            if not cross_calibration:
                continue
            cross_thresholds = thresholds_from_frames(cross_calibration, pfas)
            for frame in target_frames:
                rows.extend(evaluate_frame(frame, cross_thresholds, pfas, "cross_asset_target_free", other))

    result = pd.DataFrame(rows)
    comparisons, ci_df, payload = compare_methods(result, args.pfa_tolerance, args.boot, args.seed)
    payload.update(
        {
            "date": args.date,
            "state": str(state_path.relative_to(root)),
            "pfa_tolerance": args.pfa_tolerance,
            "bootstrap_replicates": args.boot,
            "calibration_counts": calibration_counts,
        }
    )

    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    rows_csv = result_dir / f"aistap_full_asset_target_free_calibration_{args.date}.csv"
    comparison_csv = result_dir / f"aistap_full_asset_target_free_calibration_comparison_{args.date}.csv"
    ci_csv = result_dir / f"aistap_full_asset_target_free_calibration_bootstrap_ci_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_target_free_calibration_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_target_free_calibration_{args.date}.md"

    result.to_csv(rows_csv, index=False)
    comparisons.to_csv(comparison_csv, index=False)
    ci_df.to_csv(ci_csv, index=False)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(md_path, args.date, payload, calibration_counts, comparisons, ci_df)

    print(json.dumps({k: payload[k] for k in ["target_bearing_items", "calibration_modes", "positive_delta_modes", "pfa_calibrated_modes", "passed_modes", "mode_summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
