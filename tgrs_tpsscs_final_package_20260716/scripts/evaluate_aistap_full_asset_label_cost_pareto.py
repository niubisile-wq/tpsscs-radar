from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def auc_over_log_pfa(curve: pd.DataFrame, pd_col: str = "pd") -> float:
    ordered = curve.sort_values("pfa_target")
    x = np.log10(ordered["pfa_target"].astype(float).to_numpy())
    y = ordered[pd_col].astype(float).to_numpy()
    if len(x) < 2:
        return float("nan")
    return float(np.trapezoid(y, x) / (x.max() - x.min()))


def label_sort_key(label: str) -> tuple[int, int]:
    if str(label) == "all":
        return (1, 10**9)
    return (0, int(label))


def label_value(label: str, all_positive_pixels: int) -> int:
    return all_positive_pixels if str(label) == "all" else int(label)


def bootstrap_ci(values: np.ndarray, n_bootstrap: int, seed: int) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(int(n_bootstrap), values.size), replace=True).mean(axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def load_compact_frame_auc(result_dir: Path, candidate_date: str) -> pd.DataFrame:
    paths = sorted(result_dir.glob(f"aistap_full_asset_detector_candidate_*_{candidate_date}.csv"))
    frames = [pd.read_csv(path) for path in paths]
    if not frames:
        raise FileNotFoundError(f"missing detector candidate CSVs for {candidate_date}")
    df = pd.concat(frames, ignore_index=True)
    compact = df[df["method"] == "tpsscs_finished_detector"].copy()
    rows: list[dict[str, Any]] = []
    for (asset, item_id, image_index), group in compact.groupby(["asset", "item_id", "image_index"], sort=True):
        rows.append(
            {
                "asset": asset,
                "item_id": item_id,
                "image_index": int(image_index),
                "compact_auc": auc_over_log_pfa(group, "pd"),
                "pfa_points": int(group["pfa_target"].nunique()),
            }
        )
    return pd.DataFrame(rows)


def low_label_budget_auc(low_label_rows: pd.DataFrame, compact_auc: pd.DataFrame, n_bootstrap: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    frame_rows: list[dict[str, Any]] = []
    budgets = sorted(low_label_rows["label_budget"].astype(str).unique(), key=label_sort_key)
    for budget in budgets:
        sub = low_label_rows[low_label_rows["label_budget"].astype(str) == budget].copy()
        for (asset, item_id, image_index, seed_value), group in sub.groupby(["asset", "item_id", "image_index", "seed"], sort=True):
            frame_rows.append(
                {
                    "label_budget": budget,
                    "asset": asset,
                    "item_id": item_id,
                    "image_index": int(image_index),
                    "seed": int(seed_value),
                    "low_label_hgb_auc": auc_over_log_pfa(group, "pd"),
                }
            )
    frame_auc = pd.DataFrame(frame_rows)
    merged = frame_auc.merge(compact_auc, on=["asset", "item_id", "image_index"], how="left")
    merged["delta_compact_minus_low_label_hgb_auc"] = merged["compact_auc"] - merged["low_label_hgb_auc"]

    for budget in budgets:
        sub = merged[merged["label_budget"] == budget].copy()
        deltas = sub["delta_compact_minus_low_label_hgb_auc"].astype(float).to_numpy()
        ci_low, ci_high = bootstrap_ci(deltas, n_bootstrap, seed + label_sort_key(budget)[1])
        rows.append(
            {
                "label_budget": budget,
                "n_pair_observations": int(sub.shape[0]),
                "n_items": int(sub[["asset", "item_id"]].drop_duplicates().shape[0]),
                "n_seeds": int(sub["seed"].nunique()),
                "compact_auc_mean": float(sub["compact_auc"].mean()),
                "low_label_hgb_auc_mean": float(sub["low_label_hgb_auc"].mean()),
                "mean_delta_compact_minus_low_label_hgb_auc": float(np.mean(deltas)),
                "ci95_low": ci_low,
                "ci95_high": ci_high,
                "positive_fraction": float(np.mean(deltas > 0.0)),
                "nonnegative_fraction": float(np.mean(deltas >= 0.0)),
                "compact_auc_ci_positive": bool(ci_low > 0.0),
            }
        )
    return merged.sort_values(["label_budget", "asset", "item_id", "seed"]).reset_index(drop=True), pd.DataFrame(rows)


def aggregate_auc_from_comparison(path: Path, method_col: str) -> float:
    df = pd.read_csv(path)
    combined = df[df["asset"] == "combined"].copy()
    if "pfa" in combined.columns and "pfa_target" not in combined.columns:
        combined = combined.rename(columns={"pfa": "pfa_target"})
    return auc_over_log_pfa(combined, method_col)


def pareto_points(
    budget_auc: pd.DataFrame,
    runtime: dict[str, Any],
    raw_residual_hgb_auc: float,
    all_positive_pixels: int,
) -> pd.DataFrame:
    compact_runtime = float(runtime["compact_tpsscs_finished_detector_median_ms"])
    hgb_runtime = float(runtime["raw_residual_hgb_inference_median_ms"])
    compact_auc = float(budget_auc["compact_auc_mean"].iloc[0])
    rows: list[dict[str, Any]] = [
        {
            "method": "compact_tpsscs",
            "label_budget": "0",
            "positive_target_pixels": 0,
            "runtime_ms": compact_runtime,
            "log_pfa_auc": compact_auc,
            "source": "finished_detector",
            "description": "zero official full-asset positive target pixels; compact finished detector",
        }
    ]
    for _, row in budget_auc.iterrows():
        budget = str(row["label_budget"])
        rows.append(
            {
                "method": f"low_label_raw_residual_hgb_budget_{budget}",
                "label_budget": budget,
                "positive_target_pixels": label_value(budget, all_positive_pixels),
                "runtime_ms": hgb_runtime,
                "log_pfa_auc": float(row["low_label_hgb_auc_mean"]),
                "source": "low_positive_pixel_hgb",
                "description": f"raw/residual HGB with {budget} source-domain positive target pixels",
            }
        )
    rows.append(
        {
            "method": "raw_residual_hgb_full_boundary",
            "label_budget": "all_boundary",
            "positive_target_pixels": all_positive_pixels,
            "runtime_ms": hgb_runtime,
            "log_pfa_auc": raw_residual_hgb_auc,
            "source": "full_feature_ensemble_boundary",
            "description": "strong raw/residual HGB boundary from the LOSO feature-ensemble audit",
        }
    )
    points = pd.DataFrame(rows)
    dominated = []
    dominator = []
    for i, row in points.iterrows():
        is_dominated = False
        dom = ""
        for j, other in points.iterrows():
            if i == j:
                continue
            no_worse = (
                float(other["positive_target_pixels"]) <= float(row["positive_target_pixels"])
                and float(other["runtime_ms"]) <= float(row["runtime_ms"])
                and float(other["log_pfa_auc"]) >= float(row["log_pfa_auc"])
            )
            strict = (
                float(other["positive_target_pixels"]) < float(row["positive_target_pixels"])
                or float(other["runtime_ms"]) < float(row["runtime_ms"])
                or float(other["log_pfa_auc"]) > float(row["log_pfa_auc"])
            )
            if no_worse and strict:
                is_dominated = True
                dom = str(other["method"])
                break
        dominated.append(is_dominated)
        dominator.append(dom)
    points["pareto_dominated"] = dominated
    points["dominated_by"] = dominator
    return points.sort_values(["pareto_dominated", "positive_target_pixels", "runtime_ms"]).reset_index(drop=True)


def write_markdown(path: Path, payload: dict[str, Any], budget_auc: pd.DataFrame, points: pd.DataFrame) -> None:
    compact = points[points["method"] == "compact_tpsscs"].iloc[0]
    dominated_budgets = budget_auc[
        (budget_auc["mean_delta_compact_minus_low_label_hgb_auc"] > 0.0)
        & (budget_auc["compact_auc_ci_positive"])
    ]["label_budget"].astype(str).tolist()
    lines = [
        "# AISTAP Label-Cost Pareto Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "## Verdict",
        "",
        f"- Compact TP-SSCS AUC: `{float(compact['log_pfa_auc']):.4f}` with `0` official full-asset positive target labels.",
        f"- Compact TP-SSCS runtime: `{float(payload['compact_runtime_ms']):.2f}` ms/frame.",
        f"- Raw/residual HGB runtime: `{float(payload['hgb_runtime_ms']):.2f}` ms/frame (`{float(payload['hgb_over_compact_runtime_ratio']):.2f}x` compact).",
        f"- Low-label HGB budgets dominated by compact TP-SSCS in AUC, labels, and runtime with positive AUC bootstrap CI: `{dominated_budgets}`.",
        f"- First positive-pixel budget where low-label HGB exceeds compact AUC: `{payload['first_budget_hgb_auc_exceeds_compact']}`.",
        f"- Strong full-label raw/residual HGB boundary AUC: `{float(payload['raw_residual_hgb_full_auc']):.4f}`.",
        "",
        "## Budget AUC",
        "",
        "| HGB positive-pixel budget | Compact AUC | HGB AUC | Delta | CI95 low | CI95 high | Positive fraction |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in budget_auc.iterrows():
        lines.append(
            f"| `{row['label_budget']}` | {float(row['compact_auc_mean']):.4f} | "
            f"{float(row['low_label_hgb_auc_mean']):.4f} | "
            f"{float(row['mean_delta_compact_minus_low_label_hgb_auc']):.4f} | "
            f"{float(row['ci95_low']):.4f} | {float(row['ci95_high']):.4f} | "
            f"{float(row['positive_fraction']):.3f} |"
        )
    lines.extend(
        [
            "",
            "## Pareto Points",
            "",
            "| Method | Positive target pixels | Runtime ms/frame | AUC | Dominated | Dominated by |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in points.iterrows():
        lines.append(
            f"| `{row['method']}` | {int(row['positive_target_pixels'])} | "
            f"{float(row['runtime_ms']):.2f} | {float(row['log_pfa_auc']):.4f} | "
            f"{str(bool(row['pareto_dominated'])).lower()} | `{row['dominated_by']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This audit combines already-frozen low-label HGB, full HGB-boundary, and runtime outputs; it does not retrain a new detector.",
            "- Runtime is the local CPU profile already reported for compact TP-SSCS and the checked raw/residual HGB inference stack; it is not hardware-independent.",
            "- The Pareto claim is scoped to official AISTAP-SIM full assets, the checked Pfa grid, positive-target-pixel supervision, and the measured local implementation.",
            "- Full-label HGB remains the supervised in-domain upper boundary; this audit strengthens the low-target-label/low-cost positioning, not universal superiority.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--candidate-date", default="20260715")
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260717)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    low_label_rows = pd.read_csv(result_dir / f"aistap_full_asset_loso_low_positive_pixel_hgb_{args.date}.csv")
    compact_auc = load_compact_frame_auc(result_dir, args.candidate_date)
    frame_auc, budget_auc = low_label_budget_auc(low_label_rows, compact_auc, args.bootstrap, args.seed)

    runtime = json.loads((result_dir / f"aistap_runtime_profile_{args.date}.json").read_text(encoding="utf-8"))
    raw_residual_hgb_auc = aggregate_auc_from_comparison(
        result_dir / f"aistap_full_asset_loso_feature_ensemble_baseline_comparison_{args.date}.csv",
        "learned_hgb_pd",
    )
    all_positive_pixels = int(low_label_rows[low_label_rows["label_budget"].astype(str) == "all"]["selected_positive_pixels"].max())
    points = pareto_points(budget_auc, runtime, raw_residual_hgb_auc, all_positive_pixels)

    compact_auc_mean = float(budget_auc["compact_auc_mean"].iloc[0])
    hgb_exceeds = budget_auc[budget_auc["low_label_hgb_auc_mean"].astype(float) > compact_auc_mean]["label_budget"].astype(str).tolist()
    first_exceeds = sorted(hgb_exceeds, key=label_sort_key)[0] if hgb_exceeds else "none"
    auc_ci_positive_budgets = budget_auc[budget_auc["compact_auc_ci_positive"]]["label_budget"].astype(str).tolist()
    dominated_positive_ci_budgets = [
        str(row["label_budget"])
        for _, row in budget_auc.iterrows()
        if bool(row["compact_auc_ci_positive"])
        and float(row["mean_delta_compact_minus_low_label_hgb_auc"]) > 0.0
        and label_value(str(row["label_budget"]), all_positive_pixels) > 0
    ]

    payload = {
        "date": args.date,
        "candidate_date": args.candidate_date,
        "target_bearing_items": int(frame_auc[["asset", "item_id"]].drop_duplicates().shape[0]),
        "pair_observations": int(frame_auc.shape[0]),
        "seeds": sorted(frame_auc["seed"].dropna().astype(int).unique().tolist()),
        "compact_auc": compact_auc_mean,
        "compact_runtime_ms": float(runtime["compact_tpsscs_finished_detector_median_ms"]),
        "hgb_runtime_ms": float(runtime["raw_residual_hgb_inference_median_ms"]),
        "hgb_over_compact_runtime_ratio": float(runtime["hgb_over_compact_runtime_ratio"]),
        "raw_residual_hgb_full_auc": raw_residual_hgb_auc,
        "all_positive_pixels": all_positive_pixels,
        "compact_auc_positive_ci_budgets": auc_ci_positive_budgets,
        "compact_dominates_low_label_hgb_budgets_auc_runtime_labels": dominated_positive_ci_budgets,
        "largest_positive_ci_auc_budget": sorted(auc_ci_positive_budgets, key=label_sort_key)[-1],
        "first_budget_hgb_auc_exceeds_compact": first_exceeds,
        "pareto_front_methods": points[points["pareto_dominated"] == False]["method"].astype(str).tolist(),
        "bootstrap_replicates": int(args.bootstrap),
        "bootstrap_seed": int(args.seed),
        "boundary": [
            "uses_existing_frozen_low_label_hgb_outputs",
            "local_cpu_runtime_not_hardware_independent",
            "pareto_scope_official_aistap_full_assets_checked_pfa_grid",
            "does_not_claim_superiority_over_full_label_hgb_boundary",
        ],
    }

    frame_auc_path = result_dir / f"aistap_full_asset_label_cost_pareto_frame_auc_{args.date}.csv"
    budget_auc_path = result_dir / f"aistap_full_asset_label_cost_pareto_budget_auc_{args.date}.csv"
    points_path = result_dir / f"aistap_full_asset_label_cost_pareto_points_{args.date}.csv"
    json_path = result_dir / f"aistap_full_asset_label_cost_pareto_{args.date}.json"
    md_path = log_dir / f"aistap_full_asset_label_cost_pareto_{args.date}.md"

    frame_auc.to_csv(frame_auc_path, index=False)
    budget_auc.to_csv(budget_auc_path, index=False)
    points.to_csv(points_path, index=False)
    json_path.write_text(
        json.dumps(
            {
                **payload,
                "budget_auc": budget_auc.to_dict(orient="records"),
                "pareto_points": points.to_dict(orient="records"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(md_path, payload, budget_auc, points)

    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")
    print(
        "label_cost_pareto: "
        f"dominated_budgets={dominated_positive_ci_budgets} "
        f"first_hgb_auc_exceeds={first_exceeds} "
        f"front={payload['pareto_front_methods']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
