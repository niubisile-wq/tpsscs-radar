from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
import torch

import evaluate_aistap_full_asset_classical_cfar_baselines as base


def parse_ints(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def parse_floats(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def local_cfar_score_maps_multi_os(
    score: np.ndarray, training: int, guard: int, os_percentiles: list[float], eps: float
) -> dict[str, np.ndarray]:
    score = np.asarray(score, dtype=float)
    annulus = base.annulus_footprint(training, guard)
    ca_ref = base.mean_from_kernel(score, annulus.astype(float))
    side_refs = [base.mean_from_kernel(score, kernel) for kernel in base.side_footprints(training, guard)]
    side_stack = np.stack(side_refs, axis=0)
    maps = {
        f"ca_t{training}_g{guard}": score / np.maximum(ca_ref, eps),
        f"goca_t{training}_g{guard}": score / np.maximum(np.max(side_stack, axis=0), eps),
        f"soca_t{training}_g{guard}": score / np.maximum(np.min(side_stack, axis=0), eps),
    }
    for percentile in os_percentiles:
        os_ref = base.os_annulus_reference(score, annulus, percentile)
        maps[f"os{int(percentile)}_t{training}_g{guard}"] = score / np.maximum(os_ref, eps)
    return maps


def append_summary_rows(
    rows: list[dict[str, Any]],
    score: np.ndarray,
    mask: np.ndarray,
    pfas: list[float],
    asset_name: str,
    image_index: int,
    item_id: str,
    method: str,
    family: str,
    training: int | None,
    guard: int | None,
    os_percentile: float | None,
    policy: str,
) -> None:
    for row in base.summarize(score, mask, pfas, policy):
        row.update(
            {
                "asset": asset_name,
                "image_index": image_index,
                "item_id": item_id,
                "method": method,
                "method_family": family,
                "training_cells": training,
                "guard_cells": guard,
                "os_percentile": os_percentile,
            }
        )
        rows.append(row)


def evaluate_asset(
    asset_path: Path,
    model: torch.nn.Module,
    state_path: Path,
    pfas: list[float],
    training_grid: list[int],
    guard_grid: list[int],
    os_percentiles: list[float],
    max_positive: int | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total_frames = 0
    positive_frames = 0
    evaluated_positive = 0

    with h5py.File(asset_path, "r") as f, torch.no_grad():
        refs = f["meta_per_image"][()].reshape(-1)
        total_frames = int(len(refs))
        for idx, ref in enumerate(refs):
            meta = base.read_meta(f, ref)
            x_np = base.to_complex(f["rd_img"][idx])
            raw_score = base.score_map(x_np)
            mask = base.target_mask(meta, raw_score.shape)
            if not mask.any():
                continue
            positive_frames += 1
            if max_positive is not None and evaluated_positive >= max_positive:
                break

            x = torch.from_numpy(x_np).to(torch.complex128)
            out = model(x)
            residual_score = base.score_map(out["residual"].detach().cpu().numpy())
            gate_score = out["score"].detach().cpu().numpy()
            item_id = f"{asset_path.name}#{idx}"

            append_summary_rows(
                rows,
                raw_score,
                mask,
                pfas,
                asset_path.name,
                idx,
                item_id,
                "raw_global_topk",
                "global",
                None,
                None,
                None,
                "conservative_topk_strict_gt",
            )
            append_summary_rows(
                rows,
                residual_score,
                mask,
                pfas,
                asset_path.name,
                idx,
                item_id,
                f"low_rank_residual_k{model.rank}_global_topk",
                "global",
                None,
                None,
                None,
                "conservative_topk_strict_gt",
            )
            for row in base.summarize_finished_detector(residual_score, gate_score, mask, pfas):
                row.update(
                    {
                        "asset": asset_path.name,
                        "image_index": idx,
                        "item_id": item_id,
                        "method": "tpsscs_finished_detector",
                        "method_family": "proposed",
                        "training_cells": None,
                        "guard_cells": None,
                        "os_percentile": None,
                    }
                )
                rows.append(row)

            for training in training_grid:
                for guard in guard_grid:
                    raw_maps = local_cfar_score_maps_multi_os(raw_score, training, guard, os_percentiles, eps=1e-12)
                    residual_maps = local_cfar_score_maps_multi_os(
                        residual_score, training, guard, os_percentiles, eps=1e-12
                    )
                    for suffix, score in raw_maps.items():
                        os_value = float(suffix.split("_", 1)[0][2:]) if suffix.startswith("os") else None
                        append_summary_rows(
                            rows,
                            score,
                            mask,
                            pfas,
                            asset_path.name,
                            idx,
                            item_id,
                            f"raw_{suffix}_cfar_local",
                            "classical_local_cfar_param_sweep",
                            training,
                            guard,
                            os_value,
                            "local_cfar_param_sweep_score_conservative_topk_strict_gt",
                        )
                    for suffix, score in residual_maps.items():
                        os_value = float(suffix.split("_", 1)[0][2:]) if suffix.startswith("os") else None
                        append_summary_rows(
                            rows,
                            score,
                            mask,
                            pfas,
                            asset_path.name,
                            idx,
                            item_id,
                            f"low_rank_residual_k{model.rank}_{suffix}_cfar_local",
                            "classical_local_cfar_param_sweep",
                            training,
                            guard,
                            os_value,
                            "local_cfar_param_sweep_score_conservative_topk_strict_gt",
                        )
            evaluated_positive += 1

    info = {
        "asset": str(asset_path),
        "state": str(state_path),
        "total_frames": total_frames,
        "positive_frames": positive_frames,
        "evaluated_positive_frames": evaluated_positive,
    }
    return pd.DataFrame(rows), info


def summarize_sweep(df: pd.DataFrame, pfa_tolerance: float) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    summary = (
        df.groupby(["asset", "pfa_target", "method", "method_family", "training_cells", "guard_cells", "os_percentile"], dropna=False)
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined = (
        df.groupby(["pfa_target", "method", "method_family", "training_cells", "guard_cells", "os_percentile"], dropna=False)
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
            classical = sub[sub["method_family"].isin(["global", "classical_local_cfar_param_sweep"])]
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
                    "best_training_cells": None if pd.isna(best["training_cells"]) else int(best["training_cells"]),
                    "best_guard_cells": None if pd.isna(best["guard_cells"]) else int(best["guard_cells"]),
                    "best_os_percentile": None if pd.isna(best["os_percentile"]) else float(best["os_percentile"]),
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
        "candidate_method_count": int(df["method"].nunique()),
        "asset_level_comparisons": int(len(asset_rows)),
        "asset_level_wins_vs_best_swept_classical": int(asset_rows["beats_best_classical"].sum())
        if not asset_rows.empty
        else 0,
        "asset_level_ties_vs_best_swept_classical": int(asset_rows["ties_best_classical"].sum())
        if not asset_rows.empty
        else 0,
        "combined_comparisons": int(len(combined_rows)),
        "combined_wins_vs_best_swept_classical": int(combined_rows["beats_best_classical"].sum())
        if not combined_rows.empty
        else 0,
        "combined_ties_vs_best_swept_classical": int(combined_rows["ties_best_classical"].sum())
        if not combined_rows.empty
        else 0,
        "combined_min_delta_vs_best_swept_classical": float(combined_rows["delta_vs_best_classical"].min())
        if not combined_rows.empty
        else float("nan"),
        "all_proposed_pfa_calibrated": bool(comparisons["pfa_calibrated"].all()) if not comparisons.empty else False,
    }
    payload["passed_strict_best_swept_classical"] = bool(
        payload["asset_level_comparisons"] > 0
        and payload["combined_comparisons"] > 0
        and payload["asset_level_wins_vs_best_swept_classical"] == payload["asset_level_comparisons"]
        and payload["combined_wins_vs_best_swept_classical"] == payload["combined_comparisons"]
        and payload["all_proposed_pfa_calibrated"]
    )
    payload["passed_noninferior_best_swept_classical"] = bool(
        payload["asset_level_comparisons"] > 0
        and payload["combined_comparisons"] > 0
        and (
            payload["asset_level_wins_vs_best_swept_classical"]
            + payload["asset_level_ties_vs_best_swept_classical"]
            == payload["asset_level_comparisons"]
        )
        and (
            payload["combined_wins_vs_best_swept_classical"]
            + payload["combined_ties_vs_best_swept_classical"]
            == payload["combined_comparisons"]
        )
        and payload["all_proposed_pfa_calibrated"]
    )
    return summary, comparisons, payload


def write_markdown(path: Path, date_tag: str, payload: dict[str, Any], comparisons: pd.DataFrame) -> None:
    combined = comparisons[comparisons["asset"] == "combined"].sort_values("pfa")
    lines = [
        "# AISTAP Full-Asset Classical CFAR Parameter-Sweep Audit",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Strict wins vs best swept classical baseline: `{payload['passed_strict_best_swept_classical']}`",
        f"- Non-inferior vs best swept classical baseline: `{payload['passed_noninferior_best_swept_classical']}`",
        f"- Assets: `{', '.join(payload['assets'])}`",
        f"- Combined target-bearing items: `{payload['target_bearing_items']}`",
        f"- Candidate methods/configurations: `{payload['candidate_method_count']}`",
        f"- Training grid: `{', '.join(map(str, payload['training_grid']))}`",
        f"- Guard grid: `{', '.join(map(str, payload['guard_grid']))}`",
        f"- OS percentiles: `{', '.join(str(int(x)) for x in payload['os_percentiles'])}`",
        f"- Asset-level wins/ties vs best swept classical: `{payload['asset_level_wins_vs_best_swept_classical']}/{payload['asset_level_ties_vs_best_swept_classical']}/{payload['asset_level_comparisons']}`",
        f"- Combined wins/ties vs best swept classical: `{payload['combined_wins_vs_best_swept_classical']}/{payload['combined_ties_vs_best_swept_classical']}/{payload['combined_comparisons']}`",
        f"- Combined minimum delta vs best swept classical: `{payload['combined_min_delta_vs_best_swept_classical']:.4f}`",
        "",
        "## Combined Best-Swept-Classical Comparison",
        "",
        "| Pfa | TP-SSCS Pd | Best swept classical method | Best Pd | Delta |",
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
            "## Boundary",
            "",
            "- This audit gives the classical CFAR baselines multiple local-window settings rather than a single fixed setting.",
            "- The result is still an official AISTAP-SIM full-asset baseline-strength audit, not a new external dataset.",
            "- All score families remain calibrated with the same conservative empirical-Pfa thresholding rule.",
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
    parser.add_argument("--training-grid", default="4,6,8")
    parser.add_argument("--guard-grid", default="1,2")
    parser.add_argument("--os-percentiles", default="60,75,90")
    parser.add_argument("--max-positive", type=int, default=0)
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    state = Path(args.state)
    if not state.is_absolute():
        state = root / state
    pfas = parse_floats(args.pfas)
    training_grid = parse_ints(args.training_grid)
    guard_grid = parse_ints(args.guard_grid)
    os_percentiles = parse_floats(args.os_percentiles)
    max_positive = None if args.max_positive <= 0 else args.max_positive
    asset_paths = []
    for item in args.assets.split(","):
        path = Path(item.strip())
        if not path.is_absolute():
            path = root / path
        asset_paths.append(path)

    model = base.load_trainable_model(state)
    model.eval()
    frames: list[pd.DataFrame] = []
    infos: list[dict[str, Any]] = []
    for asset in asset_paths:
        print(f"evaluating {asset.name}", flush=True)
        df, info = evaluate_asset(
            asset,
            model,
            state,
            pfas,
            training_grid=training_grid,
            guard_grid=guard_grid,
            os_percentiles=os_percentiles,
            max_positive=max_positive,
        )
        frames.append(df)
        infos.append(info)
    all_rows = pd.concat(frames, ignore_index=True)
    summary, comparisons, payload = summarize_sweep(all_rows, args.pfa_tolerance)
    payload.update(
        {
            "date": args.date,
            "state": str(state),
            "asset_info": infos,
            "training_grid": training_grid,
            "guard_grid": guard_grid,
            "os_percentiles": os_percentiles,
            "pfa_tolerance": float(args.pfa_tolerance),
        }
    )

    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    detail_csv = result_dir / f"aistap_full_asset_classical_cfar_param_sweep_{args.date}.csv"
    summary_csv = result_dir / f"aistap_full_asset_classical_cfar_param_sweep_summary_{args.date}.csv"
    comparison_csv = result_dir / f"aistap_full_asset_classical_cfar_param_sweep_best_comparison_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_classical_cfar_param_sweep_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_classical_cfar_param_sweep_{args.date}.md"
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
