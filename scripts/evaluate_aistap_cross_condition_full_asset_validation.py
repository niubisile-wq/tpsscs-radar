from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


def find_lowrank_method(methods: set[str]) -> str | None:
    lowrank = sorted(m for m in methods if m.startswith("low_rank_residual_k"))
    if not lowrank:
        return None
    rank30 = [m for m in lowrank if m.endswith("30")]
    return rank30[0] if rank30 else lowrank[-1]


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["asset", "method", "pfa_target"])
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )


def evaluate(
    df: pd.DataFrame,
    min_assets: int,
    min_items_per_asset: int,
    pfa_tolerance: float,
) -> tuple[dict[str, Any], pd.DataFrame]:
    result: dict[str, Any] = {
        "passed": False,
        "criteria": {},
        "failures": [],
        "comparisons": [],
    }
    needed = {"asset", "method", "pfa_target", "pd", "empirical_pfa", "item_id"}
    missing = sorted(needed - set(df.columns))
    if missing:
        result["failures"].append("missing columns: " + ", ".join(missing))
        return result, pd.DataFrame()

    methods = set(df["method"].astype(str))
    lowrank_method = find_lowrank_method(methods)
    required_methods = {"raw", "tpsscs_finished_detector"}
    if lowrank_method:
        required_methods.add(lowrank_method)
    missing_methods = sorted(required_methods - methods)
    if missing_methods:
        result["failures"].append("missing methods: " + ", ".join(missing_methods))
        return result, pd.DataFrame()

    summary = summarize(df)
    assets = sorted(summary["asset"].astype(str).unique())
    result["criteria"]["asset_count"] = len(assets)
    result["criteria"]["assets"] = assets
    result["criteria"]["lowrank_method"] = lowrank_method
    result["criteria"]["min_items_per_asset"] = min_items_per_asset
    result["criteria"]["pfa_tolerance"] = pfa_tolerance

    if len(assets) < min_assets:
        result["failures"].append(f"only {len(assets)} full-test assets; require >= {min_assets}")

    comparison_rows: list[dict[str, Any]] = []
    for asset in assets:
        asset_summary = summary[summary["asset"] == asset]
        asset_items = int(asset_summary["n_items"].max()) if not asset_summary.empty else 0
        pfas = sorted(asset_summary["pfa_target"].unique())
        if asset_items < min_items_per_asset:
            result["failures"].append(f"{asset} has {asset_items} target-bearing items; require >= {min_items_per_asset}")
        if len(pfas) < 5:
            result["failures"].append(f"{asset} has only {len(pfas)} Pfa points; require >= 5")
        for pfa in pfas:
            tp = asset_summary[
                (asset_summary["method"] == "tpsscs_finished_detector")
                & (asset_summary["pfa_target"] == pfa)
            ]
            raw = asset_summary[(asset_summary["method"] == "raw") & (asset_summary["pfa_target"] == pfa)]
            low = asset_summary[
                (asset_summary["method"] == lowrank_method) & (asset_summary["pfa_target"] == pfa)
            ]
            if tp.empty or raw.empty or low.empty:
                result["failures"].append(f"{asset} missing comparison rows at Pfa {pfa:g}")
                continue
            tp_pd = float(tp["pd_mean"].iloc[0])
            raw_pd = float(raw["pd_mean"].iloc[0])
            low_pd = float(low["pd_mean"].iloc[0])
            observed_pfa = float(tp["empirical_pfa_mean"].iloc[0])
            ceiling = float(pfa) * pfa_tolerance + 1e-7
            row = {
                "asset": asset,
                "pfa": float(pfa),
                "tpsscs_pd": tp_pd,
                "raw_pd": raw_pd,
                "lowrank_pd": low_pd,
                "tpsscs_empirical_pfa": observed_pfa,
                "pfa_ceiling": ceiling,
                "beats_raw": tp_pd >= raw_pd,
                "beats_lowrank": tp_pd >= low_pd,
                "pfa_calibrated": observed_pfa <= ceiling,
                "n_items": asset_items,
            }
            comparison_rows.append(row)
            if not row["beats_raw"]:
                result["failures"].append(f"{asset} TP-SSCS does not beat raw at Pfa {pfa:g}")
            if not row["beats_lowrank"]:
                result["failures"].append(f"{asset} TP-SSCS does not beat {lowrank_method} at Pfa {pfa:g}")
            if not row["pfa_calibrated"]:
                result["failures"].append(
                    f"{asset} empirical Pfa {observed_pfa:.6g} exceeds ceiling {ceiling:.6g} at requested {pfa:.6g}"
                )

    result["comparisons"] = comparison_rows
    result["criteria"]["comparison_count"] = len(comparison_rows)
    result["passed"] = not result["failures"]
    return result, pd.DataFrame(comparison_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "绗笁鎵?"))
    parser.add_argument("--inputs", default="")
    parser.add_argument("--min-assets", type=int, default=2)
    parser.add_argument("--min-items-per-asset", type=int, default=100)
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    root = Path(args.root)
    if args.inputs.strip():
        paths = [Path(x.strip()) for x in args.inputs.split(",") if x.strip()]
        paths = [p if p.is_absolute() else root / p for p in paths]
    else:
        paths = sorted((root / "results" / "aistap_full_asset").glob("aistap_full_asset_detector_candidate_*_*.csv"))
    paths = [p for p in paths if p.exists()]
    if not paths:
        raise FileNotFoundError("No full-asset detector-candidate CSV files found")

    frames = [pd.read_csv(p) for p in paths]
    df = pd.concat(frames, ignore_index=True)
    result, comparison_df = evaluate(
        df,
        min_assets=args.min_assets,
        min_items_per_asset=args.min_items_per_asset,
        pfa_tolerance=args.pfa_tolerance,
    )
    result["inputs"] = [str(p) for p in paths]
    result["date"] = args.date
    result["boundary"] = (
        "This is AISTAP-SIM official cross-condition evidence. It is method-level transfer across official "
        "conditions, not independent non-AISTAP external-dataset validation."
    )

    log_dir = root / "logs"
    result_dir = root / "results" / "aistap_full_asset"
    log_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    json_path = log_dir / f"aistap_cross_condition_full_asset_validation_{args.date}.json"
    md_path = log_dir / f"aistap_cross_condition_full_asset_validation_{args.date}.md"
    csv_path = result_dir / f"aistap_cross_condition_full_asset_summary_{args.date}.csv"

    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    comparison_df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    lines = [
        "# AISTAP Cross-Condition Full-Asset Validation",
        "",
        f"Date: {args.date}",
        "",
        "## Verdict",
        "",
        f"- Passed: `{str(result['passed']).lower()}`",
        f"- Assets: `{result['criteria'].get('asset_count', 0)}`",
        f"- Low-rank comparator: `{result['criteria'].get('lowrank_method', 'missing')}`",
        f"- Minimum target-bearing items per asset: `{args.min_items_per_asset}`",
        "",
        "## Comparisons",
        "",
        "| Asset | Pfa | TP-SSCS Pd | Raw Pd | Low-rank Pd | Empirical Pfa | Beats raw | Beats low-rank |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["comparisons"]:
        lines.append(
            f"| {row['asset']} | {row['pfa']:.0e} | {row['tpsscs_pd']:.4f} | {row['raw_pd']:.4f} | {row['lowrank_pd']:.4f} | {row['tpsscs_empirical_pfa']:.6g} | `{str(row['beats_raw']).lower()}` | `{str(row['beats_lowrank']).lower()}` |"
        )
    lines.extend(["", "## Failures", ""])
    if result["failures"]:
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is AISTAP-SIM official cross-condition evidence.",
            "- It validates the same saved state and detector policy across official `simMed_test` and `simWind_test` full-test conditions.",
            "- It is not independent non-AISTAP external-dataset validation.",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json_path)
    print(md_path)
    print(csv_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

