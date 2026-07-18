from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def find_lowrank_method(methods: set[str]) -> str | None:
    candidates = sorted(method for method in methods if method.startswith("low_rank_residual_k"))
    rank30 = [method for method in candidates if method.endswith("30")]
    if rank30:
        return rank30[0]
    return candidates[-1] if candidates else None


def find_target_method(methods: set[str]) -> str | None:
    for method in ["tpsscs_finished_detector", "tpsscs_trainable_gate"]:
        if method in methods:
            return method
    return None


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


def load_full_asset_rows(root: Path, date_tag: str) -> pd.DataFrame:
    result_dir = root / "results" / "aistap_full_asset"
    paths = sorted(result_dir.glob(f"aistap_full_asset_detector_candidate_*_{date_tag}.csv"))
    if not paths:
        raise FileNotFoundError(f"No full-asset detector-candidate CSVs found for {date_tag}")
    frames = [pd.read_csv(path) for path in paths]
    return pd.concat(frames, ignore_index=True)


def summarize_gate(df: pd.DataFrame, pfa_tolerance: float, n_boot: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    needed = {"asset", "item_id", "method", "pfa_target", "pd", "empirical_pfa"}
    missing = sorted(needed - set(df.columns))
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    df = df.copy()
    df["pfa_target"] = df["pfa_target"].astype(float)
    methods = set(df["method"].astype(str))
    target_method = find_target_method(methods)
    lowrank_method = find_lowrank_method(methods)
    if target_method is None:
        raise ValueError("Missing TP-SSCS target method")
    if lowrank_method is None:
        raise ValueError("Missing low-rank comparator")
    if "raw" not in methods:
        raise ValueError("Missing raw comparator")

    summary = (
        df.groupby(["asset", "pfa_target", "method"])
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined = (
        df.groupby(["pfa_target", "method"])
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
            target = asset_summary[(asset_summary["pfa_target"] == pfa) & (asset_summary["method"] == target_method)]
            raw = asset_summary[(asset_summary["pfa_target"] == pfa) & (asset_summary["method"] == "raw")]
            lowrank = asset_summary[(asset_summary["pfa_target"] == pfa) & (asset_summary["method"] == lowrank_method)]
            if target.empty or raw.empty or lowrank.empty:
                continue
            target_pd = float(target["pd_mean"].iloc[0])
            raw_pd = float(raw["pd_mean"].iloc[0])
            lowrank_pd = float(lowrank["pd_mean"].iloc[0])
            observed_pfa = float(target["empirical_pfa_mean"].iloc[0])
            pfa_ceiling = float(pfa) * pfa_tolerance + 1e-7
            comparison_rows.append(
                {
                    "asset": asset,
                    "pfa": float(pfa),
                    "target_method": target_method,
                    "lowrank_method": lowrank_method,
                    "n_items": int(target["n_items"].iloc[0]),
                    "target_pd": target_pd,
                    "raw_pd": raw_pd,
                    "lowrank_pd": lowrank_pd,
                    "delta_vs_raw": target_pd - raw_pd,
                    "delta_vs_lowrank": target_pd - lowrank_pd,
                    "target_empirical_pfa": observed_pfa,
                    "pfa_ceiling": pfa_ceiling,
                    "pfa_calibrated": observed_pfa <= pfa_ceiling,
                    "beats_raw": target_pd > raw_pd,
                    "beats_lowrank": target_pd > lowrank_pd,
                }
            )
    comparisons = pd.DataFrame(comparison_rows)

    rng = np.random.default_rng(seed)
    pivot = (
        df.pivot_table(
            index=["asset", "item_id", "pfa_target"],
            columns="method",
            values="pd",
            aggfunc="mean",
        )
        .reset_index()
        .dropna(subset=[target_method, "raw", lowrank_method])
    )
    ci_rows: list[dict[str, Any]] = []
    for pfa in sorted(pivot["pfa_target"].unique()):
        sub = pivot[np.isclose(pivot["pfa_target"], pfa)]
        for comparator in ["raw", lowrank_method]:
            values = (sub[target_method].astype(float) - sub[comparator].astype(float)).to_numpy()
            ci = bootstrap_ci(values, rng, n_boot)
            ci_rows.append(
                {
                    "pfa": float(pfa),
                    "target_method": target_method,
                    "comparator": comparator,
                    "n_items": int(len(values)),
                    "mean_delta_pd": ci["mean"],
                    "ci95_low": ci["ci_low"],
                    "ci95_high": ci["ci_high"],
                    "positive_fraction": float(np.mean(values > 0)),
                    "nonnegative_fraction": float(np.mean(values >= 0)),
                }
            )
    ci_df = pd.DataFrame(ci_rows)

    real_assets = sorted(asset for asset in comparisons["asset"].unique() if asset != "combined")
    combined_rows = comparisons[comparisons["asset"] == "combined"]
    asset_rows = comparisons[comparisons["asset"].isin(real_assets)]
    passed = (
        len(real_assets) >= 2
        and not comparisons.empty
        and bool(asset_rows["pfa_calibrated"].all())
        and bool(combined_rows["pfa_calibrated"].all())
        and bool(asset_rows["beats_raw"].all())
        and bool(asset_rows["beats_lowrank"].all())
        and bool(combined_rows["beats_raw"].all())
        and bool(combined_rows["beats_lowrank"].all())
    )
    payload = {
        "target_method": target_method,
        "lowrank_method": lowrank_method,
        "assets": real_assets,
        "combined_target_bearing_items": int(df["item_id"].nunique()),
        "pfa_points": int(combined_rows["pfa"].nunique()),
        "asset_level_comparisons": int(len(asset_rows)),
        "combined_comparisons": int(len(combined_rows)),
        "asset_level_wins_vs_raw": int(asset_rows["beats_raw"].sum()),
        "asset_level_wins_vs_lowrank": int(asset_rows["beats_lowrank"].sum()),
        "combined_wins_vs_raw": int(combined_rows["beats_raw"].sum()),
        "combined_wins_vs_lowrank": int(combined_rows["beats_lowrank"].sum()),
        "all_pfa_calibrated": bool(comparisons["pfa_calibrated"].all()),
        "passed": bool(passed),
    }
    return comparisons, ci_df, payload


def write_markdown(path: Path, date_tag: str, payload: dict[str, Any], comparisons: pd.DataFrame, ci_df: pd.DataFrame) -> None:
    lines = [
        "# AISTAP Combined Full-Asset Protocol Gate",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Passed: `{str(payload['passed']).lower()}`",
        f"- Assets: `{', '.join(payload['assets'])}`",
        f"- Combined target-bearing items: `{payload['combined_target_bearing_items']}`",
        f"- Asset-level wins vs raw: `{payload['asset_level_wins_vs_raw']}/{payload['asset_level_comparisons']}`",
        f"- Asset-level wins vs low-rank: `{payload['asset_level_wins_vs_lowrank']}/{payload['asset_level_comparisons']}`",
        f"- Combined wins vs raw: `{payload['combined_wins_vs_raw']}/{payload['combined_comparisons']}`",
        f"- Combined wins vs low-rank: `{payload['combined_wins_vs_lowrank']}/{payload['combined_comparisons']}`",
        f"- All Pfa calibrated: `{str(payload['all_pfa_calibrated']).lower()}`",
        "",
        "## Combined Comparisons",
        "",
        "| Pfa | TP-SSCS Pd | Raw Pd | Low-rank Pd | Delta vs raw | Delta vs low-rank | Empirical Pfa |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    combined = comparisons[comparisons["asset"] == "combined"].sort_values("pfa")
    for _, row in combined.iterrows():
        lines.append(
            f"| {row['pfa']:.0e} | {row['target_pd']:.4f} | {row['raw_pd']:.4f} | {row['lowrank_pd']:.4f} | "
            f"{row['delta_vs_raw']:.4f} | {row['delta_vs_lowrank']:.4f} | {row['target_empirical_pfa']:.6g} |"
        )
    lines.extend(
        [
            "",
            "## Combined Bootstrap CI",
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
            "- This gate consolidates `simMed_test.mat` and `simWind_test.mat` into one in-domain official full-asset protocol artifact.",
            "- It is an in-domain official AISTAP-SIM gate, not an independent external-dataset result.",
            "- Independent external support remains IPIX held-out validation and SSDD SAR adaptation.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260715)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    df = load_full_asset_rows(root, args.date)
    comparisons, ci_df, payload = summarize_gate(df, args.pfa_tolerance, args.boot, args.seed)
    payload.update({"date": args.date, "pfa_tolerance": args.pfa_tolerance, "bootstrap_replicates": args.boot})

    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    comparison_csv = result_dir / f"aistap_combined_full_asset_protocol_{args.date}.csv"
    ci_csv = result_dir / f"aistap_combined_full_asset_bootstrap_ci_{args.date}.csv"
    json_path = result_dir / f"aistap_combined_full_asset_protocol_{args.date}.json"
    md_path = log_dir / f"aistap_combined_full_asset_protocol_{args.date}.md"

    comparisons.to_csv(comparison_csv, index=False)
    ci_df.to_csv(ci_csv, index=False)
    payload["artifacts"] = {
        "comparison_csv": str(comparison_csv),
        "ci_csv": str(ci_csv),
        "markdown_log": str(md_path),
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_path, args.date, payload, comparisons, ci_df)

    print(json_path)
    print(comparison_csv)
    print(ci_csv)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
