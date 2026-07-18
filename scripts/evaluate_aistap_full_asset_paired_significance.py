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
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [1.0] * m
    running = 1.0
    for rank_from_end, idx in enumerate(reversed(order), start=1):
        rank = m - rank_from_end + 1
        q = min(running, pvalues[idx] * m / rank)
        running = q
        adjusted[idx] = min(1.0, q)
    return adjusted


def summarize_group(frame: pd.DataFrame, asset: str, comparator: str, pfa: float) -> dict[str, float | int | str]:
    deltas = frame["delta_pd"].astype(float).to_numpy()
    wins = int((deltas > 0.0).sum())
    ties = int((deltas == 0.0).sum())
    losses = int((deltas < 0.0).sum())
    nonzero = wins + losses
    sign_effect = (wins - losses) / nonzero if nonzero else 0.0
    return {
        "asset": asset,
        "comparator": comparator,
        "pfa_target": float(pfa),
        "n_items": int(len(frame)),
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "nonzero_pairs": nonzero,
        "win_fraction": wins / len(frame) if len(frame) else float("nan"),
        "nonnegative_fraction": (wins + ties) / len(frame) if len(frame) else float("nan"),
        "loss_fraction": losses / len(frame) if len(frame) else float("nan"),
        "mean_delta_pd": float(np.mean(deltas)) if len(deltas) else float("nan"),
        "median_delta_pd": float(np.median(deltas)) if len(deltas) else float("nan"),
        "q05_delta_pd": float(np.quantile(deltas, 0.05)) if len(deltas) else float("nan"),
        "min_delta_pd": float(np.min(deltas)) if len(deltas) else float("nan"),
        "max_delta_pd": float(np.max(deltas)) if len(deltas) else float("nan"),
        "matched_sign_effect": float(sign_effect),
        "one_sided_sign_p": exact_one_sided_sign_pvalue(wins, losses),
    }


def make_summaries(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    needed = {"asset", "pfa_target", "comparator", "delta_pd"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"input is missing required columns: {sorted(missing)}")
    for (asset, comparator, pfa), group in df.groupby(["asset", "comparator", "pfa_target"], sort=True):
        rows.append(summarize_group(group, str(asset), str(comparator), float(pfa)))
    for (comparator, pfa), group in df.groupby(["comparator", "pfa_target"], sort=True):
        rows.append(summarize_group(group, "combined", str(comparator), float(pfa)))
    out = pd.DataFrame(rows)
    out = out.sort_values(["asset", "comparator", "pfa_target"]).reset_index(drop=True)
    out["bh_fdr_q_all_tests"] = benjamini_hochberg(out["one_sided_sign_p"].astype(float).tolist())
    out["significant_bh_0p05"] = out["bh_fdr_q_all_tests"].astype(float) < 0.05
    return out


def write_markdown(path: Path, payload: dict[str, object], table: pd.DataFrame) -> None:
    combined = table[table["asset"] == "combined"].copy()
    lines = [
        "# AISTAP Full-Asset Paired Significance Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "## Verdict",
        "",
        f"- Target-bearing items: `{payload['target_bearing_items']}`",
        f"- Pfa points: `{payload['pfa_points']}`",
        f"- Combined tests significant after BH-FDR: `{str(payload['all_combined_significant_bh_0p05']).lower()}`",
        f"- Low-rank combined significant after BH-FDR: `{str(payload['lowrank_all_combined_significant_bh_0p05']).lower()}`",
        f"- Raw combined significant after BH-FDR: `{str(payload['raw_all_combined_significant_bh_0p05']).lower()}`",
        f"- Worst combined BH-FDR q-value: `{float(payload['max_combined_bh_q']):.3e}`",
        f"- Minimum combined matched sign effect: `{float(payload['min_combined_matched_sign_effect']):.3f}`",
        "",
        "## Combined Paired Tests",
        "",
        "| Comparator | Pfa | n | Win | Tie | Loss | Sign effect | one-sided sign p | BH q | Significant |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in combined.iterrows():
        lines.append(
            "| "
            + f"`{row['comparator']}` | {float(row['pfa_target']):g} | {int(row['n_items'])} | "
            + f"{int(row['wins'])} | {int(row['ties'])} | {int(row['losses'])} | "
            + f"{float(row['matched_sign_effect']):.3f} | {float(row['one_sided_sign_p']):.3e} | "
            + f"{float(row['bh_fdr_q_all_tests']):.3e} | `{str(bool(row['significant_bh_0p05'])).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is a paired nonparametric audit over the frozen official full-asset frame-level rows.",
            "- The one-sided exact sign test ignores ties and tests whether positive TP-SSCS-minus-comparator deltas outnumber negative deltas.",
            "- BH-FDR is applied across all asset-level and combined comparator/Pfa tests in this audit.",
            "- This strengthens statistical reporting for the official AISTAP-SIM result; it is not a new dataset or a universal per-frame dominance claim.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--source-date", default=None)
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
    table = make_summaries(df)
    combined = table[table["asset"] == "combined"].copy()
    lowrank = combined[combined["comparator"] == "low_rank_residual_k30"]
    raw = combined[combined["comparator"] == "raw"]

    all_combined_sig = bool(combined["significant_bh_0p05"].all())
    lowrank_sig = bool((not lowrank.empty) and lowrank["significant_bh_0p05"].all())
    raw_sig = bool((not raw.empty) and raw["significant_bh_0p05"].all())
    payload = {
        "date": args.date,
        "source_date": source_date,
        "source_csv": str(source_path.relative_to(root)),
        "target_bearing_items": int(df[["asset", "item_id"]].drop_duplicates().shape[0]),
        "pfa_points": int(df["pfa_target"].nunique()),
        "comparators": sorted(df["comparator"].dropna().unique().tolist()),
        "tests_total": int(table.shape[0]),
        "combined_tests_total": int(combined.shape[0]),
        "all_combined_significant_bh_0p05": all_combined_sig,
        "lowrank_all_combined_significant_bh_0p05": lowrank_sig,
        "raw_all_combined_significant_bh_0p05": raw_sig,
        "max_combined_bh_q": float(combined["bh_fdr_q_all_tests"].max()),
        "max_lowrank_combined_bh_q": float(lowrank["bh_fdr_q_all_tests"].max()),
        "max_raw_combined_bh_q": float(raw["bh_fdr_q_all_tests"].max()),
        "min_combined_matched_sign_effect": float(combined["matched_sign_effect"].min()),
        "min_lowrank_combined_matched_sign_effect": float(lowrank["matched_sign_effect"].min()),
        "min_raw_combined_matched_sign_effect": float(raw["matched_sign_effect"].min()),
        "boundary": [
            "paired_sign_test_excludes_ties",
            "bh_fdr_applied_across_all_asset_and_combined_tests",
            "statistical_audit_over_existing_official_full_asset_rows_not_new_dataset",
            "does_not_claim_universal_per_frame_raw_dominance",
        ],
    }

    csv_path = result_dir / f"aistap_full_asset_paired_significance_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_paired_significance_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_paired_significance_{args.date}.md"
    table.to_csv(csv_path, index=False)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(md_path, payload, table)
    print(md_path)
    print(json_path)
    print(csv_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
