from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
import torch
from scipy import ndimage
from numpy.lib.stride_tricks import sliding_window_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evaluate_aistap_target_preservation_ablation import load_trainable_model


def to_complex(arr: np.ndarray) -> np.ndarray:
    if arr.dtype.fields and {"real", "imag"} <= set(arr.dtype.fields):
        return arr["real"] + 1j * arr["imag"]
    return np.asarray(arr)


def decode_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.ndarray):
        if value.size == 1:
            return decode_value(value.reshape(-1)[0])
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def read_meta(f: h5py.File, ref: Any) -> dict[str, Any]:
    grp = f[ref]
    return {key: decode_value(grp[key][()]) for key in grp.keys()}


def score_map(x: np.ndarray) -> np.ndarray:
    return np.sum(np.abs(x) ** 2, axis=0)


def target_mask(meta: dict[str, Any], shape: tuple[int, int]) -> np.ndarray:
    try:
        ntrue = float(np.asarray(meta.get("Ntrue", 0.0)).reshape(-1)[0])
    except Exception:
        ntrue = 0.0
    if ntrue <= 0:
        return np.zeros(shape, dtype=bool)

    dop_axis = np.asarray(meta["truth_pix_dop_axis"]).reshape(-1)
    range_axis = np.asarray(meta["truth_pix_range_axis"]).reshape(-1)
    dop_vals = np.rint(np.asarray(meta["targ_pix_dop"]).reshape(-1)).astype(int)
    range_vals = np.rint(np.asarray(meta["targ_pix_range"]).reshape(-1)).astype(int)
    dop_min = int(dop_axis.min())
    range_min = int(range_axis.min())
    mask = np.zeros(shape, dtype=bool)
    for d, r in zip(dop_vals, range_vals):
        di = d - dop_min
        ri = r - range_min
        if 0 <= di < shape[0] and 0 <= ri < shape[1]:
            mask[di, ri] = True
    return mask


def conservative_cfar_threshold(bg: np.ndarray, pfa: float) -> tuple[float, int]:
    bg = np.asarray(bg, dtype=float).reshape(-1)
    bg = bg[np.isfinite(bg)]
    if bg.size == 0:
        return float("nan"), 0
    max_false_alarms = int(np.floor(float(pfa) * bg.size))
    if max_false_alarms <= 0:
        return float(np.max(bg)), 0
    if max_false_alarms >= bg.size:
        return float(np.nextafter(np.min(bg), -np.inf)), int(bg.size)
    threshold_index = bg.size - max_false_alarms - 1
    threshold = float(np.partition(bg, threshold_index)[threshold_index])
    return threshold, max_false_alarms


def summarize(score: np.ndarray, mask: np.ndarray, pfas: list[float], policy: str) -> list[dict[str, Any]]:
    score = np.asarray(score, dtype=float)
    bg = score[~mask]
    tgt = score[mask]
    rows: list[dict[str, Any]] = []
    for pfa in pfas:
        threshold, max_false_alarms = conservative_cfar_threshold(bg, pfa)
        det = np.isfinite(score) & (score > threshold)
        rows.append(
            {
                "pfa_target": float(pfa),
                "threshold": threshold,
                "pd": float(det[mask].mean()) if tgt.size else float("nan"),
                "empirical_pfa": float(det[~mask].mean()) if bg.size else float("nan"),
                "target_count": int(tgt.size),
                "background_count": int(bg.size),
                "max_false_alarms": int(max_false_alarms),
                "false_alarms": int(det[~mask].sum()) if bg.size else 0,
                "detections": int(det.sum()),
                "threshold_policy": policy,
            }
        )
    return rows


def summarize_finished_detector(
    residual_score: np.ndarray, gate_score: np.ndarray, mask: np.ndarray, pfas: list[float]
) -> list[dict[str, Any]]:
    residual_bg = residual_score[~mask]
    gate_bg = gate_score[~mask]
    gate_threshold, gate_max_false_alarms = conservative_cfar_threshold(gate_bg, 0.0)
    gate_det = gate_score > gate_threshold
    rows: list[dict[str, Any]] = []
    for pfa in pfas:
        residual_threshold, residual_max_false_alarms = conservative_cfar_threshold(residual_bg, pfa)
        residual_det = residual_score > residual_threshold
        det = residual_det | gate_det
        rows.append(
            {
                "pfa_target": float(pfa),
                "threshold": float("nan"),
                "residual_threshold": residual_threshold,
                "gate_threshold": gate_threshold,
                "pd": float(det[mask].mean()) if mask.any() else float("nan"),
                "empirical_pfa": float(det[~mask].mean()) if residual_bg.size else float("nan"),
                "target_count": int(mask.sum()),
                "background_count": int((~mask).sum()),
                "max_false_alarms": int(residual_max_false_alarms + gate_max_false_alarms),
                "false_alarms": int(det[~mask].sum()) if residual_bg.size else 0,
                "detections": int(det.sum()),
                "threshold_policy": "residual_cfar_plus_zero_false_gate_union",
            }
        )
    return rows


def annulus_footprint(training: int, guard: int) -> np.ndarray:
    radius = training + guard
    yy, xx = np.mgrid[-radius : radius + 1, -radius : radius + 1]
    full = (np.abs(yy) <= radius) & (np.abs(xx) <= radius)
    guard_zone = (np.abs(yy) <= guard) & (np.abs(xx) <= guard)
    fp = full & ~guard_zone
    return fp.astype(bool)


def side_footprints(training: int, guard: int) -> list[np.ndarray]:
    radius = training + guard
    yy, xx = np.mgrid[-radius : radius + 1, -radius : radius + 1]
    not_guard = ~((np.abs(yy) <= guard) & (np.abs(xx) <= guard))
    return [
        ((xx < -guard) & (np.abs(yy) <= radius) & not_guard).astype(float),
        ((xx > guard) & (np.abs(yy) <= radius) & not_guard).astype(float),
        ((yy < -guard) & (np.abs(xx) <= radius) & not_guard).astype(float),
        ((yy > guard) & (np.abs(xx) <= radius) & not_guard).astype(float),
    ]


def mean_from_kernel(score: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    score = np.asarray(score, dtype=float)
    count = ndimage.convolve(np.ones_like(score, dtype=float), kernel, mode="constant", cval=0.0)
    total = ndimage.convolve(score, kernel, mode="constant", cval=0.0)
    return total / np.maximum(count, 1.0)


def local_cfar_score_maps(
    score: np.ndarray, training: int, guard: int, os_percentile: float, eps: float
) -> dict[str, np.ndarray]:
    score = np.asarray(score, dtype=float)
    annulus = annulus_footprint(training, guard)
    ca_ref = mean_from_kernel(score, annulus.astype(float))
    side_refs = [mean_from_kernel(score, kernel) for kernel in side_footprints(training, guard)]
    side_stack = np.stack(side_refs, axis=0)
    goca_ref = np.max(side_stack, axis=0)
    soca_ref = np.min(side_stack, axis=0)
    os_ref = os_annulus_reference(score, annulus, os_percentile)
    return {
        "ca_cfar_local": score / np.maximum(ca_ref, eps),
        "goca_cfar_local": score / np.maximum(goca_ref, eps),
        "soca_cfar_local": score / np.maximum(soca_ref, eps),
        f"os{int(os_percentile)}_cfar_local": score / np.maximum(os_ref, eps),
    }


def os_annulus_reference(score: np.ndarray, footprint: np.ndarray, percentile: float) -> np.ndarray:
    radius_y = footprint.shape[0] // 2
    radius_x = footprint.shape[1] // 2
    padded = np.pad(score, ((radius_y, radius_y), (radius_x, radius_x)), mode="reflect")
    windows = sliding_window_view(padded, footprint.shape)
    refs = np.asarray(windows[..., footprint], dtype=float)
    kth = int(round((np.clip(percentile, 0.0, 100.0) / 100.0) * (refs.shape[-1] - 1)))
    return np.partition(refs, kth, axis=-1)[..., kth]


def evaluate_asset(
    asset_path: Path,
    state_path: Path,
    pfas: list[float],
    training: int,
    guard: int,
    os_percentile: float,
    max_positive: int | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    model = load_trainable_model(state_path)
    model.eval()
    rows: list[dict[str, Any]] = []
    total_frames = 0
    positive_frames = 0
    evaluated_positive = 0

    with h5py.File(asset_path, "r") as f, torch.no_grad():
        refs = f["meta_per_image"][()].reshape(-1)
        total_frames = int(len(refs))
        for idx, ref in enumerate(refs):
            meta = read_meta(f, ref)
            x_np = to_complex(f["rd_img"][idx])
            raw_score = score_map(x_np)
            mask = target_mask(meta, raw_score.shape)
            if not mask.any():
                continue
            positive_frames += 1
            if max_positive is not None and evaluated_positive >= max_positive:
                continue

            x = torch.from_numpy(x_np).to(torch.complex128)
            out = model(x)
            residual_score = score_map(out["residual"].detach().cpu().numpy())
            gate_score = out["score"].detach().cpu().numpy()

            method_scores: dict[str, tuple[np.ndarray, str, str]] = {
                "raw_global_topk": (raw_score, "global", "conservative_topk_strict_gt"),
                f"low_rank_residual_k{model.rank}_global_topk": (
                    residual_score,
                    "global",
                    "conservative_topk_strict_gt",
                ),
            }
            for suffix, cfar_score in local_cfar_score_maps(
                raw_score, training, guard, os_percentile, eps=1e-12
            ).items():
                method_scores[f"raw_{suffix}"] = (
                    cfar_score,
                    "classical_local_cfar",
                    "local_cfar_score_conservative_topk_strict_gt",
                )
            for suffix, cfar_score in local_cfar_score_maps(
                residual_score, training, guard, os_percentile, eps=1e-12
            ).items():
                method_scores[f"low_rank_residual_k{model.rank}_{suffix}"] = (
                    cfar_score,
                    "classical_local_cfar",
                    "local_cfar_score_conservative_topk_strict_gt",
                )

            item_id = f"{asset_path.name}#{idx}"
            for method, (score, family, policy) in method_scores.items():
                for row in summarize(score, mask, pfas, policy):
                    row.update(
                        {
                            "asset": asset_path.name,
                            "image_index": idx,
                            "item_id": item_id,
                            "method": method,
                            "method_family": family,
                            "training_cells": int(training),
                            "guard_cells": int(guard),
                            "os_percentile": float(os_percentile),
                        }
                    )
                    rows.append(row)

            for row in summarize_finished_detector(residual_score, gate_score, mask, pfas):
                row.update(
                    {
                        "asset": asset_path.name,
                        "image_index": idx,
                        "item_id": item_id,
                        "method": "tpsscs_finished_detector",
                        "method_family": "proposed",
                        "training_cells": int(training),
                        "guard_cells": int(guard),
                        "os_percentile": float(os_percentile),
                    }
                )
                rows.append(row)
            evaluated_positive += 1
            if max_positive is not None and evaluated_positive >= max_positive:
                break

    info = {
        "asset": str(asset_path),
        "state": str(state_path),
        "total_frames": total_frames,
        "positive_frames": positive_frames,
        "evaluated_positive_frames": evaluated_positive,
        "training_cells": int(training),
        "guard_cells": int(guard),
        "os_percentile": float(os_percentile),
    }
    return pd.DataFrame(rows), info


def summarize_combined(df: pd.DataFrame, pfa_tolerance: float) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    summary = (
        df.groupby(["asset", "pfa_target", "method", "method_family"])
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined = (
        df.groupby(["pfa_target", "method", "method_family"])
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined["asset"] = "combined"
    summary = pd.concat([summary, combined[summary.columns]], ignore_index=True)

    comparison_rows: list[dict[str, Any]] = []
    for asset in sorted(summary["asset"].unique()):
        asset_summary = summary[summary["asset"] == asset]
        for pfa in sorted(asset_summary["pfa_target"].unique()):
            sub = asset_summary[np.isclose(asset_summary["pfa_target"], pfa)].copy()
            proposed = sub[sub["method"] == "tpsscs_finished_detector"]
            classical = sub[sub["method_family"].isin(["global", "classical_local_cfar"])]
            if proposed.empty or classical.empty:
                continue
            best_idx = classical["pd_mean"].astype(float).idxmax()
            best = classical.loc[best_idx]
            proposed_pd = float(proposed["pd_mean"].iloc[0])
            best_pd = float(best["pd_mean"])
            observed_pfa = float(proposed["empirical_pfa_mean"].iloc[0])
            comparison_rows.append(
                {
                    "asset": asset,
                    "pfa": float(pfa),
                    "proposed_method": "tpsscs_finished_detector",
                    "proposed_pd": proposed_pd,
                    "proposed_empirical_pfa": observed_pfa,
                    "best_classical_method": str(best["method"]),
                    "best_classical_family": str(best["method_family"]),
                    "best_classical_pd": best_pd,
                    "best_classical_empirical_pfa": float(best["empirical_pfa_mean"]),
                    "delta_vs_best_classical": proposed_pd - best_pd,
                    "n_items": int(proposed["n_items"].iloc[0]),
                    "pfa_ceiling": float(pfa) * pfa_tolerance + 1e-7,
                    "pfa_calibrated": observed_pfa <= float(pfa) * pfa_tolerance + 1e-7,
                    "beats_best_classical": proposed_pd > best_pd,
                    "ties_best_classical": np.isclose(proposed_pd, best_pd),
                }
            )
    comparisons = pd.DataFrame(comparison_rows)
    combined_rows = comparisons[comparisons["asset"] == "combined"]
    asset_rows = comparisons[comparisons["asset"] != "combined"]
    payload = {
        "assets": sorted(asset for asset in summary["asset"].unique() if asset != "combined"),
        "target_bearing_items": int(df["item_id"].nunique()),
        "pfa_points": int(summary["pfa_target"].nunique()),
        "candidate_methods": sorted(df["method"].unique().tolist()),
        "asset_level_comparisons": int(len(asset_rows)),
        "asset_level_wins_vs_best_classical": int(asset_rows["beats_best_classical"].sum()) if not asset_rows.empty else 0,
        "asset_level_ties_vs_best_classical": int(asset_rows["ties_best_classical"].sum()) if not asset_rows.empty else 0,
        "combined_comparisons": int(len(combined_rows)),
        "combined_wins_vs_best_classical": int(combined_rows["beats_best_classical"].sum())
        if not combined_rows.empty
        else 0,
        "combined_ties_vs_best_classical": int(combined_rows["ties_best_classical"].sum())
        if not combined_rows.empty
        else 0,
        "combined_min_delta_vs_best_classical": float(combined_rows["delta_vs_best_classical"].min())
        if not combined_rows.empty
        else float("nan"),
        "all_proposed_pfa_calibrated": bool(comparisons["pfa_calibrated"].all()) if not comparisons.empty else False,
    }
    payload["passed_strict_best_classical"] = bool(
        payload["asset_level_comparisons"] > 0
        and payload["combined_comparisons"] > 0
        and payload["asset_level_wins_vs_best_classical"] == payload["asset_level_comparisons"]
        and payload["combined_wins_vs_best_classical"] == payload["combined_comparisons"]
        and payload["all_proposed_pfa_calibrated"]
    )
    payload["passed_noninferior_best_classical"] = bool(
        payload["asset_level_comparisons"] > 0
        and payload["combined_comparisons"] > 0
        and (
            payload["asset_level_wins_vs_best_classical"] + payload["asset_level_ties_vs_best_classical"]
            == payload["asset_level_comparisons"]
        )
        and (
            payload["combined_wins_vs_best_classical"] + payload["combined_ties_vs_best_classical"]
            == payload["combined_comparisons"]
        )
        and payload["all_proposed_pfa_calibrated"]
    )
    return summary, comparisons, payload


def write_markdown(path: Path, date_tag: str, payload: dict[str, Any], comparisons: pd.DataFrame) -> None:
    combined = comparisons[comparisons["asset"] == "combined"].sort_values("pfa")
    lines = [
        "# AISTAP Full-Asset Classical CFAR Baseline Audit",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Strict wins vs best classical baseline: `{payload['passed_strict_best_classical']}`",
        f"- Non-inferior vs best classical baseline: `{payload['passed_noninferior_best_classical']}`",
        f"- Assets: `{', '.join(payload['assets'])}`",
        f"- Combined target-bearing items: `{payload['target_bearing_items']}`",
        f"- Candidate methods: `{len(payload['candidate_methods'])}`",
        f"- Asset-level wins/ties vs best classical: `{payload['asset_level_wins_vs_best_classical']}/{payload['asset_level_ties_vs_best_classical']}/{payload['asset_level_comparisons']}`",
        f"- Combined wins/ties vs best classical: `{payload['combined_wins_vs_best_classical']}/{payload['combined_ties_vs_best_classical']}/{payload['combined_comparisons']}`",
        f"- Combined minimum delta vs best classical: `{payload['combined_min_delta_vs_best_classical']:.4f}`",
        f"- Proposed Pfa calibrated: `{payload['all_proposed_pfa_calibrated']}`",
        "",
        "## Combined Best-Classical Comparison",
        "",
        "| Pfa | TP-SSCS Pd | Best classical method | Best classical Pd | Delta |",
        "|---:|---:|---|---:|---:|",
    ]
    for _, row in combined.iterrows():
        lines.append(
            f"| {row['pfa']:.0e} | {row['proposed_pd']:.4f} | `{row['best_classical_method']}` | "
            f"{row['best_classical_pd']:.4f} | {row['delta_vs_best_classical']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Baseline Family",
            "",
            "- Global top-k empirical-Pfa baselines: raw power and rank-matched low-rank residual power.",
            "- Local CFAR score-map baselines: CA, GOCA, SOCA, and OS-CFAR scores on both raw power and low-rank residual power.",
            "- All methods are evaluated with the same conservative `score > threshold` empirical-Pfa cap on non-target pixels.",
            "",
            "## Boundary",
            "",
            "- This is a stronger classical-baseline audit, not a new dataset.",
            "- The local CFAR scores are locally normalized score maps followed by the same empirical-Pfa calibration used by the main protocol.",
            "- If strict wins are false, the result should be reported as a baseline-strength boundary rather than hidden.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--assets",
        default="data/downloads/aistap_sim/full/simMed_test.mat,data/downloads/aistap_sim/full/simWind_test.mat",
    )
    parser.add_argument(
        "--state",
        default="results/aistap_sample/tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt",
    )
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--training", type=int, default=6)
    parser.add_argument("--guard", type=int, default=2)
    parser.add_argument("--os-percentile", type=float, default=75.0)
    parser.add_argument("--max-positive", type=int, default=0)
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    state = Path(args.state)
    if not state.is_absolute():
        state = root / state
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]
    max_positive = None if args.max_positive <= 0 else args.max_positive
    asset_paths = []
    for item in args.assets.split(","):
        path = Path(item.strip())
        if not path.is_absolute():
            path = root / path
        asset_paths.append(path)

    frames: list[pd.DataFrame] = []
    infos: list[dict[str, Any]] = []
    for asset in asset_paths:
        df, info = evaluate_asset(
            asset,
            state,
            pfas,
            training=args.training,
            guard=args.guard,
            os_percentile=args.os_percentile,
            max_positive=max_positive,
        )
        frames.append(df)
        infos.append(info)
    all_rows = pd.concat(frames, ignore_index=True)
    summary, comparisons, payload = summarize_combined(all_rows, pfa_tolerance=args.pfa_tolerance)
    payload.update(
        {
            "date": args.date,
            "state": str(state),
            "asset_info": infos,
            "training_cells": int(args.training),
            "guard_cells": int(args.guard),
            "os_percentile": float(args.os_percentile),
            "pfa_tolerance": float(args.pfa_tolerance),
        }
    )

    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    detail_csv = result_dir / f"aistap_full_asset_classical_cfar_baselines_{args.date}.csv"
    summary_csv = result_dir / f"aistap_full_asset_classical_cfar_baselines_summary_{args.date}.csv"
    comparison_csv = result_dir / f"aistap_full_asset_classical_cfar_best_comparison_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_classical_cfar_baselines_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_classical_cfar_baselines_{args.date}.md"
    all_rows.to_csv(detail_csv, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_csv, index=False, encoding="utf-8-sig")
    comparisons.to_csv(comparison_csv, index=False, encoding="utf-8-sig")
    payload["artifacts"] = {
        "detail_csv": str(detail_csv),
        "summary_csv": str(summary_csv),
        "comparison_csv": str(comparison_csv),
        "json": str(json_path),
        "markdown": str(md_path),
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_path, args.date, payload, comparisons)

    print(detail_csv)
    print(summary_csv)
    print(comparison_csv)
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
