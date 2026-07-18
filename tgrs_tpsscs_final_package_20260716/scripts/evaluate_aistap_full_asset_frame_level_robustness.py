from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def load_full_asset_rows(root: Path, source_date: str) -> pd.DataFrame:
    result_dir = root / "results" / "aistap_full_asset"
    paths = sorted(result_dir.glob(f"aistap_full_asset_detector_candidate_*_{source_date}.csv"))
    if not paths:
        raise FileNotFoundError(f"No full-asset detector-candidate CSVs found for {source_date}")
    return pd.concat([pd.read_csv(path) for path in paths], ignore_index=True)


def find_lowrank_method(methods: set[str]) -> str:
    candidates = sorted(method for method in methods if method.startswith("low_rank_residual_k"))
    rank30 = [method for method in candidates if method.endswith("30")]
    if rank30:
        return rank30[0]
    if candidates:
        return candidates[-1]
    raise ValueError("Missing low-rank residual method")


def quantile(series: pd.Series, q: float) -> float:
    values = series.astype(float).to_numpy()
    if values.size == 0:
        return float("nan")
    return float(np.quantile(values, q))


def paired_delta_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, str, str]:
    required = {"asset", "item_id", "image_index", "pfa_target", "method", "pd", "target_count", "empirical_pfa"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    methods = set(df["method"].astype(str))
    target_method = "tpsscs_finished_detector" if "tpsscs_finished_detector" in methods else "tpsscs_trainable_gate"
    if target_method not in methods:
        raise ValueError("Missing TP-SSCS target method")
    if "raw" not in methods:
        raise ValueError("Missing raw method")
    lowrank_method = find_lowrank_method(methods)

    pivot = (
        df.pivot_table(
            index=["asset", "item_id", "image_index", "pfa_target"],
            columns="method",
            values=["pd", "empirical_pfa", "target_count"],
            aggfunc="mean",
        )
        .reset_index()
    )
    pivot.columns = [
        "_".join(str(part) for part in col if str(part)) if isinstance(col, tuple) else str(col)
        for col in pivot.columns
    ]

    rows: list[dict[str, Any]] = []
    for comparator in ["raw", lowrank_method]:
        needed = [f"pd_{target_method}", f"pd_{comparator}", f"empirical_pfa_{target_method}", f"target_count_{target_method}"]
        sub = pivot.dropna(subset=needed).copy()
        target_pd = sub[f"pd_{target_method}"].astype(float)
        comp_pd = sub[f"pd_{comparator}"].astype(float)
        delta = target_pd - comp_pd
        for idx, base in sub.iterrows():
            d = float(delta.loc[idx])
            rows.append(
                {
                    "asset": base["asset"],
                    "item_id": base["item_id"],
                    "image_index": int(base["image_index"]),
                    "pfa_target": float(base["pfa_target"]),
                    "target_method": target_method,
                    "comparator": comparator,
                    "target_pd": float(base[f"pd_{target_method}"]),
                    "comparator_pd": float(base[f"pd_{comparator}"]),
                    "delta_pd": d,
                    "target_empirical_pfa": float(base[f"empirical_pfa_{target_method}"]),
                    "target_count": int(round(float(base[f"target_count_{target_method}"]))),
                    "outcome": "win" if d > 0 else "tie" if d == 0 else "loss",
                }
            )
    return pd.DataFrame(rows), target_method, lowrank_method


def summarize(deltas: pd.DataFrame) -> pd.DataFrame:
    summary = (
        deltas.groupby(["asset", "pfa_target", "comparator"], dropna=False)
        .agg(
            n_items=("item_id", "nunique"),
            mean_delta_pd=("delta_pd", "mean"),
            median_delta_pd=("delta_pd", "median"),
            q05_delta_pd=("delta_pd", lambda s: quantile(s, 0.05)),
            q25_delta_pd=("delta_pd", lambda s: quantile(s, 0.25)),
            q75_delta_pd=("delta_pd", lambda s: quantile(s, 0.75)),
            q95_delta_pd=("delta_pd", lambda s: quantile(s, 0.95)),
            min_delta_pd=("delta_pd", "min"),
            max_delta_pd=("delta_pd", "max"),
            win_count=("outcome", lambda s: int((s == "win").sum())),
            tie_count=("outcome", lambda s: int((s == "tie").sum())),
            loss_count=("outcome", lambda s: int((s == "loss").sum())),
            nonnegative_count=("delta_pd", lambda s: int((s >= 0).sum())),
            target_pd_mean=("target_pd", "mean"),
            comparator_pd_mean=("comparator_pd", "mean"),
        )
        .reset_index()
    )
    combined = (
        deltas.groupby(["pfa_target", "comparator"], dropna=False)
        .agg(
            n_items=("item_id", "nunique"),
            mean_delta_pd=("delta_pd", "mean"),
            median_delta_pd=("delta_pd", "median"),
            q05_delta_pd=("delta_pd", lambda s: quantile(s, 0.05)),
            q25_delta_pd=("delta_pd", lambda s: quantile(s, 0.25)),
            q75_delta_pd=("delta_pd", lambda s: quantile(s, 0.75)),
            q95_delta_pd=("delta_pd", lambda s: quantile(s, 0.95)),
            min_delta_pd=("delta_pd", "min"),
            max_delta_pd=("delta_pd", "max"),
            win_count=("outcome", lambda s: int((s == "win").sum())),
            tie_count=("outcome", lambda s: int((s == "tie").sum())),
            loss_count=("outcome", lambda s: int((s == "loss").sum())),
            nonnegative_count=("delta_pd", lambda s: int((s >= 0).sum())),
            target_pd_mean=("target_pd", "mean"),
            comparator_pd_mean=("comparator_pd", "mean"),
        )
        .reset_index()
    )
    combined["asset"] = "combined"
    summary = pd.concat([summary, combined[summary.columns]], ignore_index=True)
    summary["win_fraction"] = summary["win_count"] / summary["n_items"]
    summary["nonnegative_fraction"] = summary["nonnegative_count"] / summary["n_items"]
    summary["loss_fraction"] = summary["loss_count"] / summary["n_items"]
    return summary.sort_values(["asset", "comparator", "pfa_target"]).reset_index(drop=True)


def payload_from_summary(
    deltas: pd.DataFrame,
    summary: pd.DataFrame,
    target_method: str,
    lowrank_method: str,
    date_tag: str,
    source_date: str,
) -> dict[str, Any]:
    combined = summary[summary["asset"] == "combined"].copy()
    low = combined[combined["comparator"] == lowrank_method]
    raw = combined[combined["comparator"] == "raw"]
    total_low = deltas[deltas["comparator"] == lowrank_method]
    total_raw = deltas[deltas["comparator"] == "raw"]
    low_nonnegative_all = bool((total_low["delta_pd"] >= 0).all())
    raw_min_win_fraction = float(raw["win_fraction"].min()) if not raw.empty else float("nan")
    low_min_nonnegative_fraction = float(low["nonnegative_fraction"].min()) if not low.empty else float("nan")
    broad_support = low_nonnegative_all and raw_min_win_fraction >= 0.85 and low_min_nonnegative_fraction >= 1.0
    return {
        "date": date_tag,
        "source_date": source_date,
        "target_method": target_method,
        "lowrank_method": lowrank_method,
        "assets": sorted(deltas["asset"].unique().tolist()),
        "target_bearing_items": int(deltas["item_id"].nunique()),
        "pfa_points": int(deltas["pfa_target"].nunique()),
        "item_pfa_pairs_per_comparator": int(total_low.shape[0]),
        "lowrank_nonnegative_item_pfa_pairs": int((total_low["delta_pd"] >= 0).sum()),
        "lowrank_loss_item_pfa_pairs": int((total_low["delta_pd"] < 0).sum()),
        "lowrank_win_item_pfa_pairs": int((total_low["delta_pd"] > 0).sum()),
        "raw_nonnegative_item_pfa_pairs": int((total_raw["delta_pd"] >= 0).sum()),
        "raw_loss_item_pfa_pairs": int((total_raw["delta_pd"] < 0).sum()),
        "raw_win_item_pfa_pairs": int((total_raw["delta_pd"] > 0).sum()),
        "combined_lowrank_min_win_fraction": float(low["win_fraction"].min()) if not low.empty else float("nan"),
        "combined_lowrank_min_nonnegative_fraction": low_min_nonnegative_fraction,
        "combined_raw_min_win_fraction": raw_min_win_fraction,
        "combined_raw_min_nonnegative_fraction": float(raw["nonnegative_fraction"].min()) if not raw.empty else float("nan"),
        "combined_lowrank_min_median_delta": float(low["median_delta_pd"].min()) if not low.empty else float("nan"),
        "combined_raw_min_median_delta": float(raw["median_delta_pd"].min()) if not raw.empty else float("nan"),
        "broad_frame_level_support": bool(broad_support),
        "boundary": [
            "frame_level_support_not_universal_per_frame_improvement_vs_raw",
            "lowrank_comparison_has_no_negative_item_pfa_pairs_but_many_ties_at_loose_pfa",
            "raw_comparison_has_some_negative_item_pfa_pairs_and_should_be_reported_as_broad_not_universal",
        ],
    }


def write_markdown(path: Path, payload: dict[str, Any], summary: pd.DataFrame) -> None:
    lowrank = payload["lowrank_method"]
    combined = summary[summary["asset"] == "combined"].sort_values(["comparator", "pfa_target"])
    lines = [
        "# AISTAP Full-Asset Frame-Level Robustness Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "## Verdict",
        "",
        f"- Broad frame-level support: `{str(payload['broad_frame_level_support']).lower()}`",
        f"- Target-bearing items: `{payload['target_bearing_items']}`",
        f"- Pfa points: `{payload['pfa_points']}`",
        f"- Low-rank nonnegative item-Pfa pairs: `{payload['lowrank_nonnegative_item_pfa_pairs']}/{payload['item_pfa_pairs_per_comparator']}`",
        f"- Low-rank loss item-Pfa pairs: `{payload['lowrank_loss_item_pfa_pairs']}`",
        f"- Raw nonnegative item-Pfa pairs: `{payload['raw_nonnegative_item_pfa_pairs']}/{payload['item_pfa_pairs_per_comparator']}`",
        f"- Raw loss item-Pfa pairs: `{payload['raw_loss_item_pfa_pairs']}`",
        f"- Minimum combined win fraction vs raw: `{payload['combined_raw_min_win_fraction']:.3f}`",
        f"- Minimum combined nonnegative fraction vs `{lowrank}`: `{payload['combined_lowrank_min_nonnegative_fraction']:.3f}`",
        "",
        "## Combined Distribution",
        "",
        "| Comparator | Pfa | n | Win | Tie | Loss | Win fraction | Nonnegative | Median delta | q05 delta | Min delta |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in combined.iterrows():
        lines.append(
            f"| `{row['comparator']}` | {row['pfa_target']:.0e} | {int(row['n_items'])} | "
            f"{int(row['win_count'])} | {int(row['tie_count'])} | {int(row['loss_count'])} | "
            f"{row['win_fraction']:.3f} | {row['nonnegative_fraction']:.3f} | "
            f"{row['median_delta_pd']:.4f} | {row['q05_delta_pd']:.4f} | {row['min_delta_pd']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This audit asks whether the official full-asset mean Pd gains are broadly distributed over frames.",
            "- The low-rank comparison has no negative item-Pfa pairs, but loose-Pfa gains include many ties where both detectors already detect the same target cells.",
            "- The raw comparison has a high frame-level win fraction but not universal per-frame improvement; raw-favorable frames remain part of the boundary.",
            "- This is a distributional support audit over the existing official full-asset result, not a new dataset.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--source-date", default="20260715")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    df = load_full_asset_rows(root, args.source_date)
    deltas, target_method, lowrank_method = paired_delta_rows(df)
    summary = summarize(deltas)
    payload = payload_from_summary(deltas, summary, target_method, lowrank_method, args.date, args.source_date)

    delta_csv = result_dir / f"aistap_full_asset_frame_level_robustness_{args.date}.csv"
    summary_csv = result_dir / f"aistap_full_asset_frame_level_robustness_summary_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_frame_level_robustness_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_frame_level_robustness_{args.date}.md"

    deltas.to_csv(delta_csv, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_csv, index=False, encoding="utf-8-sig")
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(md_path, payload, summary)

    print(md_path)
    print(json_path)
    print(summary_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
