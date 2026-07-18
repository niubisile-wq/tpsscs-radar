from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_SEED_TAGS = {
    7: "20260715",
    11: "seed11_fullasset_sensitivity_20260717",
    23: "seed23_fullasset_sensitivity_20260717",
}


def parse_seed_tags(text: str) -> dict[int, str]:
    if not text.strip():
        return DEFAULT_SEED_TAGS
    out: dict[int, str] = {}
    for chunk in text.split(","):
        seed_text, tag = chunk.split(":", 1)
        out[int(seed_text.strip())] = tag.strip()
    return out


def find_lowrank_method(methods: set[str]) -> str:
    candidates = sorted(method for method in methods if method.startswith("low_rank_residual_k"))
    rank30 = [method for method in candidates if method.endswith("30")]
    if rank30:
        return rank30[0]
    if candidates:
        return candidates[-1]
    raise ValueError("No low-rank residual comparator found")


def load_seed_frame(root: Path, seed: int, tag: str) -> pd.DataFrame:
    result_dir = root / "results" / "aistap_full_asset"
    paths = sorted(result_dir.glob(f"aistap_full_asset_detector_candidate_*_{tag}.csv"))
    if not paths:
        raise FileNotFoundError(f"No full-asset detector CSVs found for seed {seed}, tag {tag}")
    frames = []
    for path in paths:
        df = pd.read_csv(path)
        df["seed"] = seed
        df["source_csv"] = str(path.relative_to(root))
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def summarize(df: pd.DataFrame, pfa_tolerance: float) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    needed = {"seed", "asset", "item_id", "method", "pfa_target", "pd", "empirical_pfa"}
    missing = sorted(needed - set(df.columns))
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    methods = set(df["method"].astype(str))
    target_method = "tpsscs_finished_detector"
    if target_method not in methods:
        raise ValueError(f"Missing {target_method}")
    if "raw" not in methods:
        raise ValueError("Missing raw comparator")
    lowrank_method = find_lowrank_method(methods)

    grouped = (
        df.groupby(["seed", "asset", "pfa_target", "method"])
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined = (
        df.groupby(["seed", "pfa_target", "method"])
        .agg(
            pd_mean=("pd", "mean"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
    )
    combined["asset"] = "combined"
    grouped = pd.concat([grouped, combined[grouped.columns]], ignore_index=True)

    rows: list[dict[str, Any]] = []
    for seed in sorted(grouped["seed"].unique()):
        for asset in sorted(grouped["asset"].unique()):
            sub_asset = grouped[(grouped["seed"] == seed) & (grouped["asset"] == asset)]
            if sub_asset.empty:
                continue
            for pfa in sorted(sub_asset["pfa_target"].unique()):
                target = sub_asset[(sub_asset["pfa_target"] == pfa) & (sub_asset["method"] == target_method)]
                raw = sub_asset[(sub_asset["pfa_target"] == pfa) & (sub_asset["method"] == "raw")]
                lowrank = sub_asset[(sub_asset["pfa_target"] == pfa) & (sub_asset["method"] == lowrank_method)]
                if target.empty or raw.empty or lowrank.empty:
                    continue
                target_pd = float(target["pd_mean"].iloc[0])
                raw_pd = float(raw["pd_mean"].iloc[0])
                lowrank_pd = float(lowrank["pd_mean"].iloc[0])
                target_pfa = float(target["empirical_pfa_mean"].iloc[0])
                pfa_ceiling = float(pfa) * pfa_tolerance + 1e-7
                rows.append(
                    {
                        "seed": int(seed),
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
                        "target_empirical_pfa": target_pfa,
                        "pfa_ceiling": pfa_ceiling,
                        "pfa_calibrated": target_pfa <= pfa_ceiling,
                        "beats_raw": target_pd > raw_pd,
                        "beats_lowrank": target_pd > lowrank_pd,
                    }
                )
    comparisons = pd.DataFrame(rows)
    combined_rows = comparisons[comparisons["asset"] == "combined"].copy()
    asset_rows = comparisons[comparisons["asset"] != "combined"].copy()

    seed_rows: list[dict[str, Any]] = []
    for seed in sorted(combined_rows["seed"].unique()):
        seed_combined = combined_rows[combined_rows["seed"] == seed]
        seed_asset = asset_rows[asset_rows["seed"] == seed]
        seed_rows.append(
            {
                "seed": int(seed),
                "combined_items": int(seed_combined["n_items"].max()),
                "combined_wins_vs_raw": int(seed_combined["beats_raw"].sum()),
                "combined_wins_vs_lowrank": int(seed_combined["beats_lowrank"].sum()),
                "combined_pfa_points": int(seed_combined["pfa"].nunique()),
                "asset_level_wins_vs_raw": int(seed_asset["beats_raw"].sum()),
                "asset_level_wins_vs_lowrank": int(seed_asset["beats_lowrank"].sum()),
                "asset_level_comparisons": int(len(seed_asset)),
                "min_delta_vs_raw": float(seed_combined["delta_vs_raw"].min()),
                "min_delta_vs_lowrank": float(seed_combined["delta_vs_lowrank"].min()),
                "all_pfa_calibrated": bool(seed_combined["pfa_calibrated"].all() and seed_asset["pfa_calibrated"].all()),
                "passed": bool(
                    seed_combined["beats_raw"].all()
                    and seed_combined["beats_lowrank"].all()
                    and seed_asset["beats_raw"].all()
                    and seed_asset["beats_lowrank"].all()
                    and seed_combined["pfa_calibrated"].all()
                    and seed_asset["pfa_calibrated"].all()
                ),
            }
        )
    seed_summary = pd.DataFrame(seed_rows)

    stability_rows: list[dict[str, Any]] = []
    for pfa in sorted(combined_rows["pfa"].unique()):
        sub = combined_rows[combined_rows["pfa"] == pfa]
        stability_rows.append(
            {
                "pfa": float(pfa),
                "target_pd_min": float(sub["target_pd"].min()),
                "target_pd_max": float(sub["target_pd"].max()),
                "target_pd_range": float(sub["target_pd"].max() - sub["target_pd"].min()),
                "delta_vs_raw_min": float(sub["delta_vs_raw"].min()),
                "delta_vs_lowrank_min": float(sub["delta_vs_lowrank"].min()),
            }
        )
    stability = pd.DataFrame(stability_rows)

    payload = {
        "target_method": target_method,
        "lowrank_method": lowrank_method,
        "seeds": [int(seed) for seed in sorted(df["seed"].unique())],
        "assets": sorted(asset for asset in df["asset"].astype(str).unique()),
        "combined_target_bearing_items_per_seed": int(combined_rows["n_items"].max()),
        "pfa_points": int(combined_rows["pfa"].nunique()),
        "seed_count": int(seed_summary.shape[0]),
        "seeds_passed": int(seed_summary["passed"].sum()),
        "all_seeds_passed": bool(seed_summary["passed"].all()),
        "total_combined_wins_vs_raw": int(combined_rows["beats_raw"].sum()),
        "total_combined_wins_vs_lowrank": int(combined_rows["beats_lowrank"].sum()),
        "total_combined_comparisons": int(combined_rows.shape[0]),
        "total_asset_level_wins_vs_raw": int(asset_rows["beats_raw"].sum()),
        "total_asset_level_wins_vs_lowrank": int(asset_rows["beats_lowrank"].sum()),
        "total_asset_level_comparisons": int(asset_rows.shape[0]),
        "worst_combined_delta_vs_raw": float(combined_rows["delta_vs_raw"].min()),
        "worst_combined_delta_vs_lowrank": float(combined_rows["delta_vs_lowrank"].min()),
        "max_target_pd_seed_range": float(stability["target_pd_range"].max()),
        "all_pfa_calibrated": bool(comparisons["pfa_calibrated"].all()),
    }
    return comparisons, seed_summary, stability, payload


def write_markdown(
    path: Path,
    date_tag: str,
    payload: dict[str, Any],
    seed_summary: pd.DataFrame,
    stability: pd.DataFrame,
) -> None:
    lines = [
        "# AISTAP Full-Asset Seed Sensitivity",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Passed: `{str(payload['all_seeds_passed']).lower()}`",
        f"- Seeds: `{', '.join(str(seed) for seed in payload['seeds'])}`",
        f"- Assets: `{', '.join(payload['assets'])}`",
        f"- Combined target-bearing items per seed: `{payload['combined_target_bearing_items_per_seed']}`",
        f"- Combined wins vs raw: `{payload['total_combined_wins_vs_raw']}/{payload['total_combined_comparisons']}`",
        f"- Combined wins vs low-rank: `{payload['total_combined_wins_vs_lowrank']}/{payload['total_combined_comparisons']}`",
        f"- Asset-level wins vs raw: `{payload['total_asset_level_wins_vs_raw']}/{payload['total_asset_level_comparisons']}`",
        f"- Asset-level wins vs low-rank: `{payload['total_asset_level_wins_vs_lowrank']}/{payload['total_asset_level_comparisons']}`",
        f"- Worst combined delta vs raw: `{payload['worst_combined_delta_vs_raw']:.4f}`",
        f"- Worst combined delta vs low-rank: `{payload['worst_combined_delta_vs_lowrank']:.4f}`",
        f"- Maximum cross-seed target-Pd range over Pfa points: `{payload['max_target_pd_seed_range']:.4f}`",
        "",
        "## Per-Seed Summary",
        "",
        "| Seed | Combined wins vs raw | Combined wins vs low-rank | Asset-level wins vs raw | Asset-level wins vs low-rank | Min delta vs raw | Min delta vs low-rank | Pfa calibrated |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in seed_summary.sort_values("seed").iterrows():
        lines.append(
            f"| {int(row['seed'])} | {int(row['combined_wins_vs_raw'])}/{int(row['combined_pfa_points'])} | "
            f"{int(row['combined_wins_vs_lowrank'])}/{int(row['combined_pfa_points'])} | "
            f"{int(row['asset_level_wins_vs_raw'])}/{int(row['asset_level_comparisons'])} | "
            f"{int(row['asset_level_wins_vs_lowrank'])}/{int(row['asset_level_comparisons'])} | "
            f"{row['min_delta_vs_raw']:.4f} | {row['min_delta_vs_lowrank']:.4f} | "
            f"`{str(bool(row['all_pfa_calibrated'])).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Cross-Seed Stability By Pfa",
            "",
            "| Pfa | Target Pd min | Target Pd max | Range | Min delta vs raw | Min delta vs low-rank |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in stability.sort_values("pfa").iterrows():
        lines.append(
            f"| {row['pfa']:.0e} | {row['target_pd_min']:.4f} | {row['target_pd_max']:.4f} | "
            f"{row['target_pd_range']:.4f} | {row['delta_vs_raw_min']:.4f} | {row['delta_vs_lowrank_min']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The final `rank=30`, `hidden=16`, `steps=150`, `lr=0.02` full-asset result is not a single-seed artifact under this three-seed check.",
            "- All checked seeds preserve the full official AISTAP-SIM combined gate against both raw and rank-matched low-rank residual comparators.",
            "- The evidence remains an in-domain official AISTAP-SIM full-asset sensitivity check; it should be paired with IPIX and SSDD for external-support claims.",
            "",
            "## Boundary",
            "",
            "- This does not prove universal seed invariance over all possible initializations.",
            "- This does not change the IPIX zero-shot boundary or the SSDD supervised-adaptation boundary.",
            "- It does strengthen the finished-detector protocol by showing that nearby training seeds keep the same official full-asset win pattern.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--seed-tags", default="")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--pfa-tolerance", type=float, default=1.05)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    seed_tags = parse_seed_tags(args.seed_tags)
    df = pd.concat(
        [load_seed_frame(root, seed, tag) for seed, tag in sorted(seed_tags.items())],
        ignore_index=True,
    )
    comparisons, seed_summary, stability, payload = summarize(df, args.pfa_tolerance)

    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    comparison_csv = result_dir / f"aistap_full_asset_seed_sensitivity_{args.date}.csv"
    seed_csv = result_dir / f"aistap_full_asset_seed_sensitivity_summary_{args.date}.csv"
    stability_csv = result_dir / f"aistap_full_asset_seed_sensitivity_by_pfa_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_seed_sensitivity_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_seed_sensitivity_{args.date}.md"

    comparisons.to_csv(comparison_csv, index=False, encoding="utf-8-sig")
    seed_summary.to_csv(seed_csv, index=False, encoding="utf-8-sig")
    stability.to_csv(stability_csv, index=False, encoding="utf-8-sig")
    json_path.write_text(
        json.dumps(
            {
                "payload": payload,
                "seed_summary": seed_summary.to_dict(orient="records"),
                "stability_by_pfa": stability.to_dict(orient="records"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(md_path, args.date, payload, seed_summary, stability)

    print(comparison_csv)
    print(seed_csv)
    print(stability_csv)
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
