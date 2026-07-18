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
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evaluate_aistap_target_preservation_ablation import load_trainable_model
from evaluate_ipix_external_detector_transfer import (
    low_rank_residual,
    read_ipix_windows,
    score_map,
    summarize_finished_detector,
    summarize_score,
)
from evaluate_ipix_file_holdout_adaptation import masks_for_file, robust_z


def load_items(
    root: Path,
    files: list[str],
    model: torch.nn.Module,
    window: int,
    stride: int,
    max_windows_per_file: int | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    file_info: list[dict[str, Any]] = []
    with torch.no_grad():
        for filename in files:
            path = root / "data" / "downloads" / "ipix" / filename
            windows, info = read_ipix_windows(path, window=window, stride=stride, max_windows=max_windows_per_file)
            file_info.append(info)
            for window_index, x_np in enumerate(windows):
                target_mask, background_mask, primary_bin, guard_bins = masks_for_file(filename, x_np.shape[1:])
                x = torch.from_numpy(x_np).to(torch.complex128)
                out = model(x)
                raw_score = score_map(x_np)
                low_score = score_map(low_rank_residual(x_np, model.rank))
                residual_score = score_map(out["residual"].detach().cpu().numpy())
                gate_score = out["score"].detach().cpu().numpy()
                raw_z = robust_z(raw_score, background_mask)
                residual_z = robust_z(residual_score, background_mask)
                items.append(
                    {
                        "file": filename,
                        "window_index": window_index,
                        "item_id": f"{filename}#{window_index}",
                        "raw_score": raw_score,
                        "low_score": low_score,
                        "residual_score": residual_score,
                        "gate_score": gate_score,
                        "raw_z": raw_z,
                        "residual_z": residual_z,
                        "target_mask": target_mask,
                        "background_mask": background_mask,
                        "primary_bin": primary_bin,
                        "guard_bins": guard_bins,
                    }
                )
    return items, file_info


def fusion_score(item: dict[str, Any], beta: float) -> np.ndarray:
    return item["raw_z"] + beta * (item["raw_z"] - item["residual_z"])


def evaluate_method_items(items: list[dict[str, Any]], pfas: list[float], rank: int, beta: float) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for item in items:
        adapted_score = fusion_score(item, beta)
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
                "tpsscs_finished_detector",
                summarize_finished_detector(
                    item["residual_score"],
                    item["gate_score"],
                    item["target_mask"],
                    item["background_mask"],
                    pfas,
                ),
            ),
            (
                "ipix_validated_residual_fusion",
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
                        "beta": beta if method == "ipix_validated_residual_fusion" else np.nan,
                        "primary_target_bin_1indexed": item["primary_bin"],
                        "guard_bins_1indexed": ",".join(str(b) for b in item["guard_bins"]),
                    }
                )
                rows.append(row)
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["method", "pfa_target"])
        .agg(
            pd_mean=("pd", "mean"),
            pd_std=("pd", "std"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_windows=("item_id", "nunique"),
        )
        .reset_index()
    )


def score_against_raw(summary: pd.DataFrame, method: str, pfas: list[float]) -> dict[str, Any]:
    comparisons: list[dict[str, Any]] = []
    wins_raw = 0
    wins_low = 0
    deltas: list[float] = []
    lowrank_methods = sorted(m for m in summary["method"].astype(str).unique() if m.startswith("low_rank_residual_k"))
    lowrank_method = lowrank_methods[0] if lowrank_methods else ""
    for pfa in pfas:
        cand = summary[(summary["method"] == method) & (summary["pfa_target"] == pfa)]
        raw = summary[(summary["method"] == "raw") & (summary["pfa_target"] == pfa)]
        low = summary[(summary["method"] == lowrank_method) & (summary["pfa_target"] == pfa)]
        if cand.empty or raw.empty or low.empty:
            continue
        cand_pd = float(cand["pd_mean"].iloc[0])
        raw_pd = float(raw["pd_mean"].iloc[0])
        low_pd = float(low["pd_mean"].iloc[0])
        wins_raw += int(cand_pd >= raw_pd)
        wins_low += int(cand_pd >= low_pd)
        deltas.append(cand_pd - raw_pd)
        comparisons.append(
            {
                "pfa": float(pfa),
                "candidate_pd": cand_pd,
                "raw_pd": raw_pd,
                "lowrank_pd": low_pd,
                "candidate_empirical_pfa": float(cand["empirical_pfa_mean"].iloc[0]),
                "beats_raw": cand_pd >= raw_pd,
                "beats_lowrank": cand_pd >= low_pd,
            }
        )
    return {
        "wins_raw": wins_raw,
        "wins_lowrank": wins_low,
        "mean_delta_vs_raw": float(np.mean(deltas)) if deltas else float("nan"),
        "comparisons": comparisons,
    }


def select_beta(
    validation_items: list[dict[str, Any]],
    betas: list[float],
    pfas: list[float],
    rank: int,
) -> tuple[float, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    for beta in betas:
        df = evaluate_method_items(validation_items, pfas=pfas, rank=rank, beta=beta)
        stats = score_against_raw(summarize(df), "ipix_validated_residual_fusion", pfas)
        rows.append(
            {
                "beta": beta,
                "wins_raw": stats["wins_raw"],
                "wins_lowrank": stats["wins_lowrank"],
                "mean_delta_vs_raw": stats["mean_delta_vs_raw"],
            }
        )
    selected = sorted(rows, key=lambda r: (r["wins_raw"], r["mean_delta_vs_raw"]), reverse=True)[0]
    return float(selected["beta"]), rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "绗笁鎵?"))
    parser.add_argument("--state", default="results/aistap_sample/tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt")
    parser.add_argument("--development-files", default="19931107_135603_starea.cdf")
    parser.add_argument("--validation-files", default="19931107_141630_starea.cdf")
    parser.add_argument("--test-files", default="19931107_145028_starea.cdf")
    parser.add_argument("--betas", default="0,0.25,0.5,0.75,1,1.5,2")
    parser.add_argument("--window", type=int, default=1024)
    parser.add_argument("--stride", type=int, default=1024)
    parser.add_argument("--max-windows-per-file", type=int, default=128)
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    root = Path(args.root)
    state_path = Path(args.state)
    if not state_path.is_absolute():
        state_path = root / state_path
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]
    betas = [float(x) for x in args.betas.split(",") if x.strip()]
    development_files = [x.strip() for x in args.development_files.split(",") if x.strip()]
    validation_files = [x.strip() for x in args.validation_files.split(",") if x.strip()]
    test_files = [x.strip() for x in args.test_files.split(",") if x.strip()]
    max_windows = None if args.max_windows_per_file <= 0 else args.max_windows_per_file

    model = load_trainable_model(state_path)
    model.eval()
    development_items, development_info = load_items(root, development_files, model, args.window, args.stride, max_windows)
    validation_items, validation_info = load_items(root, validation_files, model, args.window, args.stride, max_windows)
    test_items, test_info = load_items(root, test_files, model, args.window, args.stride, max_windows)
    selected_beta, validation_grid = select_beta(validation_items, betas=betas, pfas=pfas, rank=int(model.rank))
    dev_df = evaluate_method_items(development_items, pfas=pfas, rank=int(model.rank), beta=selected_beta)
    validation_df = evaluate_method_items(validation_items, pfas=pfas, rank=int(model.rank), beta=selected_beta)
    test_df = evaluate_method_items(test_items, pfas=pfas, rank=int(model.rank), beta=selected_beta)
    test_summary = summarize(test_df)
    test_stats = score_against_raw(test_summary, "ipix_validated_residual_fusion", pfas)
    failures = []
    if test_stats["wins_raw"] < len(test_stats["comparisons"]):
        failures.append(
            f"validated residual fusion beats raw on {test_stats['wins_raw']}/{len(test_stats['comparisons'])} Pfa points"
        )
    if test_stats["wins_lowrank"] < len(test_stats["comparisons"]):
        failures.append(
            f"validated residual fusion beats low-rank on {test_stats['wins_lowrank']}/{len(test_stats['comparisons'])} Pfa points"
        )
    passed = not failures

    result_dir = root / "results" / "ipix_external"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    csv_path = result_dir / f"ipix_validated_residual_fusion_test_{args.date}.csv"
    dev_csv_path = result_dir / f"ipix_validated_residual_fusion_development_{args.date}.csv"
    validation_csv_path = result_dir / f"ipix_validated_residual_fusion_validation_{args.date}.csv"
    json_path = result_dir / f"ipix_validated_residual_fusion_{args.date}.json"
    md_path = log_dir / f"ipix_validated_residual_fusion_{args.date}.md"
    test_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    dev_df.to_csv(dev_csv_path, index=False, encoding="utf-8-sig")
    validation_df.to_csv(validation_csv_path, index=False, encoding="utf-8-sig")
    payload = {
        "date": args.date,
        "state": str(state_path),
        "development_files": development_files,
        "validation_files": validation_files,
        "test_files": test_files,
        "selected_beta": selected_beta,
        "validation_grid": validation_grid,
        "development_info": development_info,
        "validation_info": validation_info,
        "test_info": test_info,
        "test_stats": test_stats,
        "test_summary": test_summary.to_dict("records"),
        "passed": passed,
        "failures": failures,
        "boundary": "Independent IPIX validation-selected residual-aware fusion; beta selected on validation file and reported on disjoint test file.",
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# IPIX Validated Residual-Aware Fusion",
        "",
        f"Date: {args.date}",
        "",
        "## Setup",
        "",
        f"- Development files: `{', '.join(development_files)}`",
        f"- Validation files for beta selection: `{', '.join(validation_files)}`",
        f"- Held-out test files: `{', '.join(test_files)}`",
        f"- Selected beta: `{selected_beta:g}`",
        "- Score: `raw_z + beta * (raw_z - TPSSCS_residual_z)`.",
        "- The score uses raw evidence plus the saved TP-SSCS residual as a validation-selected external adaptation head; no range-bin index feature is used.",
        "",
        "## Verdict",
        "",
        f"- Passed: `{str(passed).lower()}`",
        f"- Test wins vs raw: `{test_stats['wins_raw']}/{len(test_stats['comparisons'])}`",
        f"- Test wins vs low-rank: `{test_stats['wins_lowrank']}/{len(test_stats['comparisons'])}`",
        f"- Mean Pd delta vs raw: `{test_stats['mean_delta_vs_raw']:.6f}`",
        "",
        "## Held-Out Test Comparisons",
        "",
        "| Pfa | Fusion Pd | Raw Pd | Low-rank Pd | Fusion empirical Pfa | Beats raw | Beats low-rank |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in test_stats["comparisons"]:
        lines.append(
            f"| {row['pfa']:.0e} | {row['candidate_pd']:.4f} | {row['raw_pd']:.4f} | {row['lowrank_pd']:.4f} | {row['candidate_empirical_pfa']:.6g} | `{str(row['beats_raw']).lower()}` | `{str(row['beats_lowrank']).lower()}` |"
        )
    lines.extend(["", "## Validation Grid", ""])
    for row in validation_grid:
        lines.append(
            f"- beta={row['beta']:g}: wins_vs_raw={row['wins_raw']}, wins_vs_lowrank={row['wins_lowrank']}, mean_delta_vs_raw={row['mean_delta_vs_raw']:.6f}"
        )
    lines.extend(["", "## Failures", ""])
    if failures:
        for failure in failures:
            lines.append(f"- {failure}")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is independent non-AISTAP IPIX file-level validation.",
            "- Beta is selected on a validation file and reported on a disjoint held-out test file.",
            "- This is stronger than the zero-shot smoke test, but it is still one external dataset family and does not by itself match the battery package's multi-tier external-validation breadth.",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(csv_path)
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

