from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


def latest(paths: list[Path]) -> Path | None:
    existing = [p for p in paths if p.exists()]
    if not existing:
        return None
    return max(existing, key=lambda p: p.stat().st_mtime)


def find_lowrank_method(methods: set[str]) -> str | None:
    lowrank = sorted(m for m in methods if m.startswith("low_rank_residual_k"))
    if not lowrank:
        return None
    rank30 = [m for m in lowrank if m.endswith("30")]
    return rank30[0] if rank30 else lowrank[-1]


def find_tpsscs_method(methods: set[str]) -> str | None:
    for method in ["tpsscs_finished_detector", "tpsscs_trainable_gate"]:
        if method in methods:
            return method
    return None


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["method", "pfa_target"])
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )


def evaluate_protocol(df: pd.DataFrame, min_items: int, pfa_tolerance: float) -> dict[str, Any]:
    result: dict[str, Any] = {
        "passed": False,
        "criteria": {},
        "failures": [],
    }
    if df.empty:
        result["failures"].append("input CSV is empty")
        return result

    needed = {"method", "pfa_target", "pd", "empirical_pfa", "item_id"}
    missing = sorted(needed - set(df.columns))
    if missing:
        result["failures"].append("missing columns: " + ", ".join(missing))
        return result

    methods = set(df["method"].astype(str))
    lowrank_method = find_lowrank_method(methods)
    tpsscs_method = find_tpsscs_method(methods)
    required_methods = {"raw"}
    if tpsscs_method:
        required_methods.add(tpsscs_method)
    if lowrank_method:
        required_methods.add(lowrank_method)
    missing_methods = sorted(required_methods - methods)
    if tpsscs_method is None:
        missing_methods.append("tpsscs_finished_detector or tpsscs_trainable_gate")
    if missing_methods:
        result["failures"].append("missing methods: " + ", ".join(missing_methods))
        return result

    summary = summarize(df)
    pfas = sorted(summary["pfa_target"].unique())
    n_items = int(df["item_id"].nunique())
    result["criteria"]["target_bearing_items"] = n_items
    result["criteria"]["pfa_count"] = len(pfas)
    result["criteria"]["lowrank_method"] = lowrank_method
    result["criteria"]["tpsscs_method"] = tpsscs_method

    if n_items < min_items:
        result["failures"].append(f"only {n_items} target-bearing items; require >= {min_items}")
    if len(pfas) < 5:
        result["failures"].append(f"only {len(pfas)} Pfa operating points; require >= 5")

    pfa_rows = summary[summary["method"] == tpsscs_method]
    pfa_ok = True
    for _, row in pfa_rows.iterrows():
        requested = float(row["pfa_target"])
        observed = float(row["empirical_pfa_mean"])
        ceiling = requested * pfa_tolerance + 1e-7
        if observed > ceiling:
            pfa_ok = False
            result["failures"].append(
                f"empirical Pfa {observed:.6g} exceeds ceiling {ceiling:.6g} at requested {requested:.6g}"
            )
    result["criteria"]["pfa_calibrated"] = pfa_ok

    wins_raw = 0
    wins_lowrank = 0
    comparisons: list[dict[str, Any]] = []
    for pfa in pfas:
        tp = summary[(summary["method"] == tpsscs_method) & (summary["pfa_target"] == pfa)]
        raw = summary[(summary["method"] == "raw") & (summary["pfa_target"] == pfa)]
        low = summary[(summary["method"] == lowrank_method) & (summary["pfa_target"] == pfa)]
        if tp.empty or raw.empty or low.empty:
            continue
        tp_pd = float(tp["pd_mean"].iloc[0])
        raw_pd = float(raw["pd_mean"].iloc[0])
        low_pd = float(low["pd_mean"].iloc[0])
        if tp_pd >= raw_pd:
            wins_raw += 1
        if tp_pd >= low_pd:
            wins_lowrank += 1
        comparisons.append(
            {
                "pfa": float(pfa),
                "tpsscs_pd": tp_pd,
                "raw_pd": raw_pd,
                "lowrank_pd": low_pd,
                "beats_raw": tp_pd >= raw_pd,
                "beats_lowrank": tp_pd >= low_pd,
            }
        )

    result["criteria"]["wins_vs_raw"] = wins_raw
    result["criteria"]["wins_vs_lowrank"] = wins_lowrank
    result["criteria"]["comparisons"] = comparisons

    if wins_raw < len(comparisons):
        result["failures"].append(f"TP-SSCS beats raw on {wins_raw}/{len(comparisons)} Pfa points; require all")
    if wins_lowrank < len(comparisons):
        result["failures"].append(
            f"TP-SSCS beats rank-matched low-rank on {wins_lowrank}/{len(comparisons)} Pfa points; require all"
        )

    result["passed"] = not result["failures"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "绗笁鎵?"))
    parser.add_argument("--input", default="")
    parser.add_argument("--min-items", type=int, default=100)
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    root = Path(args.root)
    input_path = Path(args.input) if args.input else None
    if input_path is not None and not input_path.is_absolute():
        input_path = root / input_path
    if input_path is None:
        input_path = latest(sorted((root / "results" / "aistap_full_asset").glob("aistap_full_asset_detector_candidate_*.csv")))
    if input_path is None or not input_path.exists():
        raise FileNotFoundError("No full-asset detector-candidate CSV found")

    df = pd.read_csv(input_path)
    result = evaluate_protocol(df, min_items=args.min_items, pfa_tolerance=args.pfa_tolerance)
    result["input"] = str(input_path)
    result["date"] = args.date

    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    json_path = log_dir / f"aistap_finished_detector_protocol_{args.date}.json"
    md_path = log_dir / f"aistap_finished_detector_protocol_{args.date}.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# AISTAP Finished Detector Protocol Gate",
        "",
        f"Date: {args.date}",
        "",
        "## Verdict",
        "",
        f"- Passed: `{str(result['passed']).lower()}`",
        f"- Input: `{input_path}`",
        f"- Target-bearing items: `{result['criteria'].get('target_bearing_items', 0)}`",
        f"- TP-SSCS method: `{result['criteria'].get('tpsscs_method', 'missing')}`",
        f"- Low-rank comparator: `{result['criteria'].get('lowrank_method', 'missing')}`",
        "",
        "## Criteria",
        "",
        f"- Minimum target-bearing items: `{args.min_items}`",
        f"- Pfa calibration tolerance: `{args.pfa_tolerance}`",
        f"- Wins vs raw: `{result['criteria'].get('wins_vs_raw', 0)}`",
        f"- Wins vs rank-matched low-rank: `{result['criteria'].get('wins_vs_lowrank', 0)}`",
        "",
        "## Pfa Comparisons",
        "",
        "| Pfa | TP-SSCS Pd | Raw Pd | Low-rank Pd | Beats raw | Beats low-rank |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["criteria"].get("comparisons", []):
        lines.append(
            f"| {row['pfa']:.0e} | {row['tpsscs_pd']:.4f} | {row['raw_pd']:.4f} | {row['lowrank_pd']:.4f} | `{str(row['beats_raw']).lower()}` | `{str(row['beats_lowrank']).lower()}` |"
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
            "- Passing this gate means the saved model state has a fixed, reproducible in-domain full-test detector protocol.",
            "- It does not by itself prove independent external validation or superiority over the local battery external-validation stack.",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

