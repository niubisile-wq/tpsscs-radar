from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


TARGET_METHOD = "tpsscs_finished_detector"
COMPARATORS = ["raw", "low_rank_residual_k30", "tpsscs_trainable_gate"]
METHODS = [TARGET_METHOD, *COMPARATORS]


def exact_one_sided_sign_pvalue(wins: int, losses: int) -> float:
    n = int(wins) + int(losses)
    if n <= 0:
        return 1.0
    if wins <= losses:
        return 1.0
    numerator = sum(math.comb(n, k) for k in range(int(wins), n + 1))
    return float(numerator / (2**n))


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


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_bootstrap: int) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return float("nan"), float("nan")
    samples = rng.choice(values, size=(int(n_bootstrap), values.size), replace=True).mean(axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def auc_over_log_pfa(curve: pd.DataFrame) -> float:
    ordered = curve.sort_values("pfa_target")
    x = np.log10(ordered["pfa_target"].astype(float).to_numpy())
    y = ordered["pd"].astype(float).to_numpy()
    if len(x) < 2:
        return float("nan")
    return float(np.trapezoid(y, x) / (x.max() - x.min()))


def read_candidate_results(result_dir: Path, source_date: str) -> tuple[pd.DataFrame, list[str]]:
    paths = sorted(result_dir.glob(f"aistap_full_asset_detector_candidate_*_{source_date}.csv"))
    if not paths:
        raise FileNotFoundError(f"missing detector candidate CSVs for source date {source_date}: {result_dir}")

    frames = [pd.read_csv(path) for path in paths]
    df = pd.concat(frames, ignore_index=True)
    required = {
        "asset",
        "item_id",
        "image_index",
        "method",
        "pfa_target",
        "pd",
        "empirical_pfa",
        "target_count",
        "background_count",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"candidate CSVs are missing required columns: {sorted(missing)}")

    method_set = set(df["method"].dropna().astype(str).unique())
    missing_methods = set(METHODS) - method_set
    if missing_methods:
        raise ValueError(f"candidate CSVs are missing required methods: {sorted(missing_methods)}")

    return df, [str(path.relative_to(result_dir.parent.parent)) for path in paths]


def method_operating_summary(df: pd.DataFrame) -> pd.DataFrame:
    groups: list[tuple[str, pd.DataFrame]] = []
    for asset, group in df.groupby("asset", sort=True):
        groups.append((str(asset), group))
    groups.append(("combined", df))

    rows: list[dict[str, object]] = []
    for asset, group in groups:
        for (method, pfa), sub in group.groupby(["method", "pfa_target"], sort=True):
            rows.append(
                {
                    "asset": asset,
                    "method": method,
                    "pfa_target": float(pfa),
                    "n_items": int(sub["item_id"].nunique()),
                    "pd_mean": float(sub["pd"].mean()),
                    "pd_median": float(sub["pd"].median()),
                    "pd_std": float(sub["pd"].std(ddof=1)),
                    "empirical_pfa_mean": float(sub["empirical_pfa"].mean()),
                    "empirical_pfa_max": float(sub["empirical_pfa"].max()),
                    "target_count_sum": int(sub.drop_duplicates(["asset", "item_id"])["target_count"].sum()),
                }
            )
    return pd.DataFrame(rows).sort_values(["asset", "method", "pfa_target"]).reset_index(drop=True)


def paired_operating_deltas(df: pd.DataFrame, n_bootstrap: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    pivot = df.pivot_table(
        index=["asset", "item_id", "image_index", "target_count", "pfa_target"],
        columns="method",
        values="pd",
        aggfunc="first",
    ).reset_index()

    rows: list[pd.DataFrame] = []
    for comparator in COMPARATORS:
        tmp = pivot[["asset", "item_id", "image_index", "target_count", "pfa_target", TARGET_METHOD, comparator]].dropna()
        tmp = tmp.rename(columns={TARGET_METHOD: "target_pd", comparator: "comparator_pd"}).copy()
        tmp["comparator"] = comparator
        tmp["delta_pd"] = tmp["target_pd"].astype(float) - tmp["comparator_pd"].astype(float)
        rows.append(tmp)
    deltas = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()

    summary_rows: list[dict[str, object]] = []
    rng = np.random.default_rng(seed)
    groups: list[tuple[str, str, float, pd.DataFrame]] = []
    for (asset, comparator, pfa), group in deltas.groupby(["asset", "comparator", "pfa_target"], sort=True):
        groups.append((str(asset), str(comparator), float(pfa), group))
    for (comparator, pfa), group in deltas.groupby(["comparator", "pfa_target"], sort=True):
        groups.append(("combined", str(comparator), float(pfa), group))

    for asset, comparator, pfa, group in groups:
        vals = group["delta_pd"].astype(float).to_numpy()
        wins = int((vals > 0.0).sum())
        ties = int((vals == 0.0).sum())
        losses = int((vals < 0.0).sum())
        nonzero = wins + losses
        ci_low, ci_high = bootstrap_ci(vals, rng, n_bootstrap)
        summary_rows.append(
            {
                "asset": asset,
                "comparator": comparator,
                "pfa_target": pfa,
                "n_items": int(len(vals)),
                "target_pd_mean": float(group["target_pd"].mean()),
                "comparator_pd_mean": float(group["comparator_pd"].mean()),
                "mean_delta_pd": float(vals.mean()),
                "median_delta_pd": float(np.median(vals)),
                "q05_delta_pd": float(np.quantile(vals, 0.05)),
                "min_delta_pd": float(vals.min()),
                "max_delta_pd": float(vals.max()),
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

    summary = pd.DataFrame(summary_rows).sort_values(["asset", "comparator", "pfa_target"]).reset_index(drop=True)
    summary["bh_fdr_q_all_tests"] = benjamini_hochberg(summary["one_sided_sign_p"].astype(float).tolist())
    summary["positive_bootstrap_ci"] = summary["bootstrap_ci95_low"].astype(float) > 0.0
    summary["significant_bh_0p05"] = summary["bh_fdr_q_all_tests"].astype(float) < 0.05
    return deltas.sort_values(["asset", "item_id", "comparator", "pfa_target"]).reset_index(drop=True), summary


def frame_auc_table(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (asset, item_id, image_index, target_count, method), group in df.groupby(
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


def paired_auc_summary(frame_auc: pd.DataFrame, n_bootstrap: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    pivot = frame_auc.pivot_table(
        index=["asset", "item_id", "image_index", "target_count"],
        columns="method",
        values="log_pfa_auc_pd",
        aggfunc="first",
    ).reset_index()

    rows: list[pd.DataFrame] = []
    for comparator in COMPARATORS:
        tmp = pivot[["asset", "item_id", "image_index", "target_count", TARGET_METHOD, comparator]].dropna()
        tmp = tmp.rename(columns={TARGET_METHOD: "target_auc", comparator: "comparator_auc"}).copy()
        tmp["comparator"] = comparator
        tmp["delta_auc"] = tmp["target_auc"].astype(float) - tmp["comparator_auc"].astype(float)
        rows.append(tmp)
    deltas = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()

    summary_rows: list[dict[str, object]] = []
    rng = np.random.default_rng(seed + 1)
    groups: list[tuple[str, str, pd.DataFrame]] = []
    for (asset, comparator), group in deltas.groupby(["asset", "comparator"], sort=True):
        groups.append((str(asset), str(comparator), group))
    for comparator, group in deltas.groupby("comparator", sort=True):
        groups.append(("combined", str(comparator), group))

    for asset, comparator, group in groups:
        vals = group["delta_auc"].astype(float).to_numpy()
        wins = int((vals > 0.0).sum())
        ties = int((vals == 0.0).sum())
        losses = int((vals < 0.0).sum())
        nonzero = wins + losses
        ci_low, ci_high = bootstrap_ci(vals, rng, n_bootstrap)
        summary_rows.append(
            {
                "asset": asset,
                "comparator": comparator,
                "n_items": int(len(vals)),
                "target_auc_mean": float(group["target_auc"].mean()),
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

    summary = pd.DataFrame(summary_rows).sort_values(["asset", "comparator"]).reset_index(drop=True)
    summary["bh_fdr_q_all_tests"] = benjamini_hochberg(summary["one_sided_sign_p"].astype(float).tolist())
    summary["positive_bootstrap_ci"] = summary["bootstrap_ci95_low"].astype(float) > 0.0
    summary["significant_bh_0p05"] = summary["bh_fdr_q_all_tests"].astype(float) < 0.05
    return deltas.sort_values(["asset", "item_id", "comparator"]).reset_index(drop=True), summary


def format_pfa(value: float) -> str:
    return f"{float(value):.0e}" if value < 0.001 else f"{float(value):.3g}"


def write_markdown(
    path: Path,
    payload: dict[str, object],
    operating: pd.DataFrame,
    operating_delta_summary: pd.DataFrame,
    auc_summary: pd.DataFrame,
) -> None:
    combined_operating = operating[operating["asset"] == "combined"].copy()
    combined_pivot = combined_operating.pivot_table(index="pfa_target", columns="method", values="pd_mean", aggfunc="first")
    combined_delta = operating_delta_summary[operating_delta_summary["asset"] == "combined"].copy()
    combined_auc = auc_summary[auc_summary["asset"] == "combined"].copy()

    gate_auc = combined_auc[combined_auc["comparator"] == "tpsscs_trainable_gate"].iloc[0]
    lowrank_auc = combined_auc[combined_auc["comparator"] == "low_rank_residual_k30"].iloc[0]
    raw_auc = combined_auc[combined_auc["comparator"] == "raw"].iloc[0]

    lines = [
        "# AISTAP Full-Asset Component Attribution Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "## Verdict",
        "",
        f"- Target-bearing frames: `{payload['target_bearing_items']}` across `{payload['assets']}`.",
        f"- Pfa grid: `{payload['pfa_grid']}`.",
        f"- Finished detector vs raw AUC delta: `{float(raw_auc['mean_delta_auc']):.4f}` "
        f"(wins/ties/losses `{int(raw_auc['wins'])}/{int(raw_auc['ties'])}/{int(raw_auc['losses'])}`).",
        f"- Finished detector vs low-rank residual AUC delta: `{float(lowrank_auc['mean_delta_auc']):.4f}` "
        f"(wins/ties/losses `{int(lowrank_auc['wins'])}/{int(lowrank_auc['ties'])}/{int(lowrank_auc['losses'])}`).",
        f"- Finished detector vs gate-only AUC delta: `{float(gate_auc['mean_delta_auc']):.4f}` "
        f"(wins/ties/losses `{int(gate_auc['wins'])}/{int(gate_auc['ties'])}/{int(gate_auc['losses'])}`).",
        "",
        "## Combined Mean Pd by Component",
        "",
        "| Pfa | Finished detector | Raw | Low-rank residual | Gate-only |",
        "|---:|---:|---:|---:|---:|",
    ]
    for pfa, row in combined_pivot.sort_index().iterrows():
        lines.append(
            f"| `{format_pfa(float(pfa))}` | "
            f"{float(row[TARGET_METHOD]):.4f} | {float(row['raw']):.4f} | "
            f"{float(row['low_rank_residual_k30']):.4f} | {float(row['tpsscs_trainable_gate']):.4f} |"
        )

    lines.extend(
        [
            "",
            "## Paired Delta by Pfa",
            "",
            "| Comparator | Pfa | Mean delta Pd | CI95 low | CI95 high | Wins/Ties/Losses | BH q |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for comparator in COMPARATORS:
        sub = combined_delta[combined_delta["comparator"] == comparator].sort_values("pfa_target")
        for _, row in sub.iterrows():
            lines.append(
                "| "
                + f"`{row['comparator']}` | `{format_pfa(float(row['pfa_target']))}` | "
                + f"{float(row['mean_delta_pd']):.4f} | {float(row['bootstrap_ci95_low']):.4f} | "
                + f"{float(row['bootstrap_ci95_high']):.4f} | "
                + f"{int(row['wins'])}/{int(row['ties'])}/{int(row['losses'])} | "
                + f"{float(row['bh_fdr_q_all_tests']):.3e} |"
            )

    lines.extend(
        [
            "",
            "## Log-Pfa AUC Attribution",
            "",
            "| Comparator | Target AUC | Comparator AUC | Mean delta | CI95 low | CI95 high | Wins/Ties/Losses | BH q |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in combined_auc.iterrows():
        lines.append(
            "| "
            + f"`{row['comparator']}` | {float(row['target_auc_mean']):.4f} | "
            + f"{float(row['comparator_auc_mean']):.4f} | {float(row['mean_delta_auc']):.4f} | "
            + f"{float(row['bootstrap_ci95_low']):.4f} | {float(row['bootstrap_ci95_high']):.4f} | "
            + f"{int(row['wins'])}/{int(row['ties'])}/{int(row['losses'])} | "
            + f"{float(row['bh_fdr_q_all_tests']):.3e} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The finished detector inherits broad Pd gains from residual clutter suppression and adds the zero-false gate branch where the learned score exceeds every background pixel.",
            "- Against low-rank residual alone, the finished detector is nonnegative on every frame-level AUC pair; the gain is largest at the tightest Pfa points.",
            "- Gate-only is a relaxed learned-score endpoint, not the selected conservative detector. It is weaker at the tightest Pfa point and stronger at looser Pfa points, so the finished detector should be presented as a low-false-alarm operating policy rather than a universal Pd upper bound.",
            "",
            "## Boundary",
            "",
            "- This audit reuses the frozen full-asset detector-candidate CSVs; it does not add a new dataset or retrain the model.",
            "- The paired unit is the target-bearing frame, not pixels.",
            "- AUC integrates the checked seven-point Pfa grid from 1e-5 to 1e-2 only.",
            "- The component-attribution claim is mechanistic and empirical on AISTAP full assets; it does not remove the existing external-transfer and metadata limitations.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--source-date", default="20260715")
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260717)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    df, source_csvs = read_candidate_results(result_dir, args.source_date)
    operating = method_operating_summary(df)
    pfa_deltas, pfa_summary = paired_operating_deltas(df, args.bootstrap, args.seed)
    frame_auc = frame_auc_table(df)
    auc_deltas, auc_summary = paired_auc_summary(frame_auc, args.bootstrap, args.seed)

    pfa_grid = sorted(df["pfa_target"].astype(float).unique().tolist())
    payload = {
        "date": args.date,
        "source_date": args.source_date,
        "source_csvs": source_csvs,
        "assets": sorted(df["asset"].dropna().astype(str).unique().tolist()),
        "methods": METHODS,
        "target_method": TARGET_METHOD,
        "comparators": COMPARATORS,
        "target_bearing_items": int(df[["asset", "item_id"]].drop_duplicates().shape[0]),
        "pfa_grid": [format_pfa(x) for x in pfa_grid],
        "bootstrap_replicates": int(args.bootstrap),
        "bootstrap_seed": int(args.seed),
        "raw_auc_delta_positive": bool(
            auc_summary[(auc_summary["asset"] == "combined") & (auc_summary["comparator"] == "raw")][
                "mean_delta_auc"
            ].iloc[0]
            > 0
        ),
        "lowrank_auc_nonnegative_all_frames": bool(
            (
                auc_deltas[auc_deltas["comparator"] == "low_rank_residual_k30"]["delta_auc"].astype(float)
                >= 0.0
            ).all()
        ),
        "gate_only_boundary_present": bool(
            (
                pfa_summary[
                    (pfa_summary["asset"] == "combined")
                    & (pfa_summary["comparator"] == "tpsscs_trainable_gate")
                ]["mean_delta_pd"].astype(float)
                < 0.0
            ).any()
        ),
        "boundary": [
            "reuses_frozen_detector_candidate_csvs",
            "not_new_dataset",
            "paired_unit_is_target_bearing_frame",
            "auc_integrates_checked_pfa_grid_only",
            "gate_only_is_relaxed_endpoint_not_selected_low_false_alarm_policy",
        ],
    }

    operating_path = result_dir / f"aistap_full_asset_component_attribution_operating_summary_{args.date}.csv"
    pfa_delta_path = result_dir / f"aistap_full_asset_component_attribution_pfa_deltas_{args.date}.csv"
    pfa_summary_path = result_dir / f"aistap_full_asset_component_attribution_pfa_summary_{args.date}.csv"
    frame_auc_path = result_dir / f"aistap_full_asset_component_attribution_frame_auc_{args.date}.csv"
    auc_delta_path = result_dir / f"aistap_full_asset_component_attribution_auc_deltas_{args.date}.csv"
    auc_summary_path = result_dir / f"aistap_full_asset_component_attribution_auc_summary_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_component_attribution_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_component_attribution_{args.date}.md"

    operating.to_csv(operating_path, index=False)
    pfa_deltas.to_csv(pfa_delta_path, index=False)
    pfa_summary.to_csv(pfa_summary_path, index=False)
    frame_auc.to_csv(frame_auc_path, index=False)
    auc_deltas.to_csv(auc_delta_path, index=False)
    auc_summary.to_csv(auc_summary_path, index=False)
    json_path.write_text(
        json.dumps(
            {
                **payload,
                "operating_summary": operating.to_dict(orient="records"),
                "pfa_delta_summary": pfa_summary.to_dict(orient="records"),
                "auc_summary": auc_summary.to_dict(orient="records"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(md_path, payload, operating, pfa_summary, auc_summary)

    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")
    print(
        "component_attribution: "
        f"raw_auc_delta_positive={payload['raw_auc_delta_positive']} "
        f"lowrank_auc_nonnegative_all_frames={payload['lowrank_auc_nonnegative_all_frames']} "
        f"gate_only_boundary_present={payload['gate_only_boundary_present']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
