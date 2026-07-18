from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


def exact_one_sided_sign_pvalue(wins: int, losses: int) -> float:
    n = int(wins) + int(losses)
    if n <= 0:
        return 1.0
    if wins <= losses:
        return 1.0
    numerator = sum(math.comb(n, k) for k in range(int(wins), n + 1))
    return float(numerator / (2 ** n))


def benjamini_hochberg(pvalues: list[float]) -> list[float]:
    m = len(pvalues)
    if not m:
        return []
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [1.0] * m
    running = 1.0
    for reverse_rank, idx in enumerate(reversed(order), start=1):
        rank = m - reverse_rank + 1
        q = min(running, pvalues[idx] * m / rank)
        running = q
        adjusted[idx] = min(1.0, q)
    return adjusted


def auc_over_log_pfa(curve: pd.DataFrame) -> float:
    ordered = curve.sort_values("pfa_target")
    x = np.log10(ordered["pfa_target"].astype(float).to_numpy())
    y = ordered["pd"].astype(float).to_numpy()
    if len(x) < 2:
        return float("nan")
    return float(np.trapezoid(y, x) / (x.max() - x.min()))


def reconstruct_method_curves(df: pd.DataFrame) -> pd.DataFrame:
    needed = {"asset", "item_id", "image_index", "pfa_target", "comparator", "target_pd", "comparator_pd", "target_count"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"input is missing required columns: {sorted(missing)}")

    id_cols = ["asset", "item_id", "image_index", "pfa_target", "target_count"]
    target = df[id_cols + ["target_pd"]].drop_duplicates().rename(columns={"target_pd": "pd"})
    target["method"] = "tpsscs_finished_detector"

    comp = df[id_cols + ["comparator", "comparator_pd"]].copy()
    comp = comp.rename(columns={"comparator": "method", "comparator_pd": "pd"})

    curves = pd.concat([target, comp], ignore_index=True)
    curves = curves.drop_duplicates(subset=id_cols + ["method"])
    return curves


def frame_auc_table(curves: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (asset, item_id, image_index, target_count, method), group in curves.groupby(
        ["asset", "item_id", "image_index", "target_count", "method"], sort=True
    ):
        rows.append(
            {
                "asset": asset,
                "item_id": item_id,
                "image_index": int(image_index),
                "target_count": int(target_count),
                "method": method,
                "log_pfa_auc_pd": auc_over_log_pfa(group),
                "pfa_points": int(group["pfa_target"].nunique()),
            }
        )
    return pd.DataFrame(rows)


def paired_auc_deltas(frame_auc: pd.DataFrame) -> pd.DataFrame:
    pivot = frame_auc.pivot_table(
        index=["asset", "item_id", "image_index", "target_count"],
        columns="method",
        values="log_pfa_auc_pd",
        aggfunc="first",
    ).reset_index()
    target_col = "tpsscs_finished_detector"
    rows: list[dict[str, object]] = []
    for comparator in ["raw", "low_rank_residual_k30"]:
        if comparator not in pivot.columns or target_col not in pivot.columns:
            continue
        tmp = pivot[["asset", "item_id", "image_index", "target_count", target_col, comparator]].dropna().copy()
        tmp = tmp.rename(columns={target_col: "tpsscs_auc", comparator: "comparator_auc"})
        tmp["comparator"] = comparator
        tmp["delta_auc"] = tmp["tpsscs_auc"] - tmp["comparator_auc"]
        rows.append(tmp)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_bootstrap: int) -> tuple[float, float]:
    if len(values) == 0:
        return float("nan"), float("nan")
    samples = rng.choice(values, size=(n_bootstrap, len(values)), replace=True).mean(axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def summarize_deltas(deltas: pd.DataFrame, n_bootstrap: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    groups: list[tuple[str, str, pd.DataFrame]] = []
    for (asset, comparator), group in deltas.groupby(["asset", "comparator"], sort=True):
        groups.append((str(asset), str(comparator), group))
    for comparator, group in deltas.groupby("comparator", sort=True):
        groups.append(("combined", str(comparator), group))

    rng = np.random.default_rng(seed)
    for asset, comparator, group in groups:
        vals = group["delta_auc"].astype(float).to_numpy()
        wins = int((vals > 0.0).sum())
        ties = int((vals == 0.0).sum())
        losses = int((vals < 0.0).sum())
        ci_low, ci_high = bootstrap_ci(vals, rng, n_bootstrap)
        nonzero = wins + losses
        rows.append(
            {
                "asset": asset,
                "comparator": comparator,
                "n_items": int(len(vals)),
                "tpsscs_auc_mean": float(group["tpsscs_auc"].mean()),
                "comparator_auc_mean": float(group["comparator_auc"].mean()),
                "mean_delta_auc": float(vals.mean()),
                "median_delta_auc": float(np.median(vals)),
                "q05_delta_auc": float(np.quantile(vals, 0.05)),
                "min_delta_auc": float(vals.min()),
                "max_delta_auc": float(vals.max()),
                "bootstrap_ci95_low": ci_low,
                "bootstrap_ci95_high": ci_high,
                "wins": wins,
                "ties": ties,
                "losses": losses,
                "win_fraction": wins / len(vals),
                "nonnegative_fraction": (wins + ties) / len(vals),
                "matched_sign_effect": (wins - losses) / nonzero if nonzero else 0.0,
                "one_sided_sign_p": exact_one_sided_sign_pvalue(wins, losses),
            }
        )
    out = pd.DataFrame(rows).sort_values(["asset", "comparator"]).reset_index(drop=True)
    out["bh_fdr_q_all_tests"] = benjamini_hochberg(out["one_sided_sign_p"].astype(float).tolist())
    out["positive_bootstrap_ci"] = out["bootstrap_ci95_low"].astype(float) > 0.0
    out["significant_bh_0p05"] = out["bh_fdr_q_all_tests"].astype(float) < 0.05
    return out


def write_markdown(path: Path, payload: dict[str, object], summary: pd.DataFrame) -> None:
    combined = summary[summary["asset"] == "combined"].copy()
    lines = [
        "# AISTAP Full-Asset Log-Pfa AUC Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "## Verdict",
        "",
        f"- Target-bearing items: `{payload['target_bearing_items']}`",
        f"- Pfa points: `{payload['pfa_points']}`",
        f"- Combined AUC wins vs raw and low-rank: `{str(payload['combined_auc_positive_vs_all']).lower()}`",
        f"- Combined bootstrap CI lower bounds positive: `{str(payload['combined_bootstrap_ci_positive_vs_all']).lower()}`",
        f"- Combined BH-FDR significant sign tests: `{str(payload['combined_significant_bh_vs_all']).lower()}`",
        f"- Minimum combined AUC delta: `{float(payload['min_combined_delta_auc']):.4f}`",
        f"- Worst combined BH-FDR q-value: `{float(payload['max_combined_bh_q']):.3e}`",
        "",
        "## Combined Log-Pfa AUC",
        "",
        "| Comparator | n | TP-SSCS AUC | Comparator AUC | Delta | CI95 low | CI95 high | Win/Tie/Loss | BH q |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in combined.iterrows():
        lines.append(
            "| "
            + f"`{row['comparator']}` | {int(row['n_items'])} | "
            + f"{float(row['tpsscs_auc_mean']):.4f} | {float(row['comparator_auc_mean']):.4f} | "
            + f"{float(row['mean_delta_auc']):.4f} | {float(row['bootstrap_ci95_low']):.4f} | "
            + f"{float(row['bootstrap_ci95_high']):.4f} | "
            + f"{int(row['wins'])}/{int(row['ties'])}/{int(row['losses'])} | "
            + f"{float(row['bh_fdr_q_all_tests']):.3e} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- AUC is the normalized trapezoidal integral of Pd over log10(Pfa) from 1e-5 to 1e-2.",
            "- This audit summarizes the existing seven operating points; it does not add a new dataset.",
            "- The paired bootstrap unit is the target-bearing frame, not pixels.",
            "- The result supports whole-operating-surface robustness under the official Pfa grid, not performance outside the checked Pfa range.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--source-date", default=None)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260717)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    source_date = args.source_date or args.date
    source_path = result_dir / f"aistap_full_asset_frame_level_robustness_{source_date}.csv"
    if not source_path.exists():
        raise FileNotFoundError(f"missing frame-level robustness CSV: {source_path}")

    df = pd.read_csv(source_path)
    curves = reconstruct_method_curves(df)
    frame_auc = frame_auc_table(curves)
    deltas = paired_auc_deltas(frame_auc)
    summary = summarize_deltas(deltas, args.bootstrap, args.seed)

    combined = summary[summary["asset"] == "combined"].copy()
    payload = {
        "date": args.date,
        "source_date": source_date,
        "source_csv": str(source_path.relative_to(root)),
        "target_bearing_items": int(deltas[["asset", "item_id"]].drop_duplicates().shape[0]),
        "pfa_points": int(df["pfa_target"].nunique()),
        "comparators": sorted(deltas["comparator"].dropna().unique().tolist()),
        "bootstrap_replicates": int(args.bootstrap),
        "bootstrap_seed": int(args.seed),
        "combined_auc_positive_vs_all": bool((combined["mean_delta_auc"].astype(float) > 0.0).all()),
        "combined_bootstrap_ci_positive_vs_all": bool(combined["positive_bootstrap_ci"].all()),
        "combined_significant_bh_vs_all": bool(combined["significant_bh_0p05"].all()),
        "min_combined_delta_auc": float(combined["mean_delta_auc"].min()),
        "max_combined_bh_q": float(combined["bh_fdr_q_all_tests"].max()),
        "min_combined_ci95_low": float(combined["bootstrap_ci95_low"].min()),
        "boundary": [
            "auc_integrates_checked_pfa_grid_only",
            "paired_bootstrap_unit_is_target_bearing_frame",
            "not_new_dataset",
            "does_not_claim_performance_outside_checked_pfa_range",
        ],
    }

    frame_path = result_dir / f"aistap_full_asset_log_pfa_auc_frames_{args.date}.csv"
    delta_path = result_dir / f"aistap_full_asset_log_pfa_auc_deltas_{args.date}.csv"
    summary_path = result_dir / f"aistap_full_asset_log_pfa_auc_summary_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_log_pfa_auc_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_log_pfa_auc_{args.date}.md"
    frame_auc.to_csv(frame_path, index=False)
    deltas.to_csv(delta_path, index=False)
    summary.to_csv(summary_path, index=False)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(md_path, payload, summary)
    print(md_path)
    print(json_path)
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
