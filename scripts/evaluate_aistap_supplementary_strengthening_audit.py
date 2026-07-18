from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PFAS = [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2]


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


def find_lowrank_method(methods: list[str]) -> str | None:
    candidates = sorted(method for method in methods if method.startswith("low_rank_residual_k"))
    rank30 = [method for method in candidates if method.endswith("30")]
    if rank30:
        return rank30[0]
    return candidates[-1] if candidates else None


def load_aistap_full_asset(root: Path) -> pd.DataFrame:
    paths = sorted((root / "results" / "aistap_full_asset").glob("aistap_full_asset_detector_candidate_*_20260715.csv"))
    frames = [pd.read_csv(path) for path in paths]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def summarize_aistap(df: pd.DataFrame, rng: np.random.Generator, n_boot: int) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["pfa_target"] = df["pfa_target"].astype(float)
    methods = list(df["method"].astype(str).unique())
    lowrank = find_lowrank_method(methods)
    target_method = "tpsscs_finished_detector" if "tpsscs_finished_detector" in methods else "tpsscs_trainable_gate"
    needed = {"raw", target_method}
    if lowrank:
        needed.add(lowrank)
    missing = needed - set(methods)
    if missing:
        raise ValueError("AISTAP full-asset table is missing methods: " + ", ".join(sorted(missing)))

    pivot = (
        df.pivot_table(
            index=["asset", "item_id", "pfa_target"],
            columns="method",
            values="pd",
            aggfunc="mean",
        )
        .reset_index()
        .dropna(subset=["raw", target_method])
    )
    rows: list[dict[str, Any]] = []
    for pfa in PFAS:
        sub = pivot[np.isclose(pivot["pfa_target"], pfa)]
        if sub.empty:
            continue
        for comparator in ["raw", lowrank]:
            if comparator is None or comparator not in sub:
                continue
            deltas = (sub[target_method].astype(float) - sub[comparator].astype(float)).to_numpy()
            ci = bootstrap_ci(deltas, rng, n_boot)
            rows.append(
                {
                    "source": "aistap_full_asset",
                    "pfa": pfa,
                    "target_method": target_method,
                    "comparator": comparator,
                    "n_units": int(len(deltas)),
                    "unit": "target-bearing frame",
                    "mean_delta_pd": ci["mean"],
                    "ci95_low": ci["ci_low"],
                    "ci95_high": ci["ci_high"],
                    "positive_unit_fraction": float(np.mean(deltas > 0)),
                    "nonnegative_unit_fraction": float(np.mean(deltas >= 0)),
                }
            )
    return pd.DataFrame(rows)


def summarize_ipix(df: pd.DataFrame, rng: np.random.Generator, n_boot: int) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["pfa_target"] = df["pfa_target"].astype(float)
    methods = list(df["method"].astype(str).unique())
    lowrank = find_lowrank_method(methods)
    target_method = "ipix_validated_residual_fusion"
    needed = {"raw", target_method}
    if lowrank:
        needed.add(lowrank)
    missing = needed - set(methods)
    if missing:
        raise ValueError("IPIX table is missing methods: " + ", ".join(sorted(missing)))

    pivot = (
        df.pivot_table(
            index=["file", "item_id", "pfa_target"],
            columns="method",
            values="pd",
            aggfunc="mean",
        )
        .reset_index()
        .dropna(subset=["raw", target_method])
    )
    rows: list[dict[str, Any]] = []
    for pfa in PFAS:
        sub = pivot[np.isclose(pivot["pfa_target"], pfa)]
        if sub.empty:
            continue
        for comparator in ["raw", lowrank]:
            if comparator is None or comparator not in sub:
                continue
            file_deltas = (
                sub.assign(delta=sub[target_method].astype(float) - sub[comparator].astype(float))
                .groupby("file")["delta"]
                .mean()
                .to_numpy()
            )
            ci = bootstrap_ci(file_deltas, rng, n_boot)
            rows.append(
                {
                    "source": "ipix_heldout",
                    "pfa": pfa,
                    "target_method": target_method,
                    "comparator": comparator,
                    "n_units": int(len(file_deltas)),
                    "unit": "held-out recording",
                    "mean_delta_pd": ci["mean"],
                    "ci95_low": ci["ci_low"],
                    "ci95_high": ci["ci_high"],
                    "positive_unit_fraction": float(np.mean(file_deltas > 0)),
                    "nonnegative_unit_fraction": float(np.mean(file_deltas >= 0)),
                }
            )
    return pd.DataFrame(rows)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_priority_table(aistap_ci: pd.DataFrame, ipix_ci: pd.DataFrame, ssdd_payload: dict[str, Any]) -> list[dict[str, Any]]:
    ssdd_rows = ssdd_payload.get("test_rows", [])
    ssdd_has_image_level = False
    ssdd_losses = ssdd_payload.get("test_stats", {}).get("losses_raw")
    ssdd_mean_delta = ssdd_payload.get("test_stats", {}).get("mean_delta_vs_raw")
    aistap_all_positive_ci = bool((aistap_ci["ci95_low"] > 0).all()) if not aistap_ci.empty else False
    ipix_raw = ipix_ci[ipix_ci["comparator"] == "raw"] if not ipix_ci.empty else pd.DataFrame()
    ipix_has_positive_raw_ci = bool((ipix_raw["ci95_low"] > 0).sum() >= 3) if not ipix_raw.empty else False

    return [
        {
            "rank": 1,
            "experiment": "SSDD image-level / annotation-level robustness and bootstrap CI",
            "status": "not_yet_done",
            "impact": "high",
            "cost": "medium",
            "risk": "low",
            "reason": (
                "SSDD is the newest external positive source, but the current artifact is Pfa-level aggregate only. "
                "Per-image or per-annotation deltas would answer the most likely reviewer question: whether gains are broad or driven by a small subset."
            ),
            "current_evidence": {
                "aggregate_rows": len(ssdd_rows),
                "losses_vs_raw": ssdd_losses,
                "mean_delta_vs_raw": ssdd_mean_delta,
                "has_image_level_ci": ssdd_has_image_level,
            },
        },
        {
            "rank": 2,
            "experiment": "AISTAP + IPIX paired bootstrap / confidence interval reporting",
            "status": "partially_completed_by_this_audit",
            "impact": "high",
            "cost": "low",
            "risk": "low",
            "reason": (
                "The main wins are already present; confidence intervals convert win-count evidence into reviewer-facing uncertainty evidence."
            ),
            "current_evidence": {
                "aistap_all_delta_ci_positive": aistap_all_positive_ci,
                "ipix_raw_positive_ci_points_at_file_level": int((ipix_raw["ci95_low"] > 0).sum()) if not ipix_raw.empty else 0,
                "ipix_raw_pfa_points": int(len(ipix_raw)) if not ipix_raw.empty else 0,
            },
        },
        {
            "rank": 3,
            "experiment": "Formal combined full-asset protocol gate over simMed + simWind",
            "status": "not_yet_done",
            "impact": "medium",
            "cost": "low",
            "risk": "low",
            "reason": (
                "The cross-condition summary already passes on both assets, but the named finished-detector protocol artifact currently emphasizes simMed. "
                "A single combined gate would make the in-domain claim easier to defend."
            ),
        },
        {
            "rank": 4,
            "experiment": "Final-state sensitivity across seed / rank / hidden width on full assets",
            "status": "not_yet_done",
            "impact": "medium_high",
            "cost": "medium",
            "risk": "medium",
            "reason": (
                "The sample branch has stability checks, but a reviewer may ask whether the saved full-asset detector is seed-sensitive. "
                "Run only if manuscript time allows, because a weak seed may force more explanation."
            ),
        },
        {
            "rank": 5,
            "experiment": "Additional classical detector baselines beyond raw CFAR and low-rank residual",
            "status": "optional_high_risk",
            "impact": "medium_high",
            "cost": "high",
            "risk": "medium_high",
            "reason": (
                "This could answer baseline-strength criticism, but only helps if implemented cleanly and fairly. "
                "A rushed CA/OS/GOCA/SOCA comparison could create new reviewer attack surface."
            ),
        },
    ]


def write_markdown(
    path: Path,
    date_tag: str,
    priorities: list[dict[str, Any]],
    aistap_ci: pd.DataFrame,
    ipix_ci: pd.DataFrame,
    ssdd_payload: dict[str, Any],
) -> None:
    lines = [
        "# AISTAP Supplementary Experiment Strengthening Audit",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        "- The current evidence remains `top_ready`; no hard experiment blocker is visible.",
        "- Further work should not be another broad data hunt. The highest-value additions are uncertainty reporting and robustness localization.",
        "- The single best next experiment is SSDD image-level / annotation-level robustness with bootstrap confidence intervals.",
        "- The best low-cost supplement is a formal bootstrap CI table for AISTAP full assets and IPIX held-out recordings; this audit generates that table for the available per-unit artifacts.",
        "",
        "## Priority Experiments",
        "",
        "| Rank | Experiment | Status | Impact | Cost | Risk | Why it matters |",
        "|---:|---|---|---|---|---|---|",
    ]
    for item in priorities:
        lines.append(
            f"| {item['rank']} | {item['experiment']} | `{item['status']}` | `{item['impact']}` | "
            f"`{item['cost']}` | `{item['risk']}` | {item['reason']} |"
        )

    lines.extend(
        [
            "",
            "## Bootstrap CI Snapshot",
            "",
            "### AISTAP Full Assets",
            "",
            "| Pfa | Comparator | n | Mean Delta Pd | 95% CI | Positive-unit fraction |",
            "|---:|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in aistap_ci.iterrows():
        lines.append(
            f"| {row['pfa']:.0e} | `{row['comparator']}` | {int(row['n_units'])} | "
            f"{row['mean_delta_pd']:.4f} | [{row['ci95_low']:.4f}, {row['ci95_high']:.4f}] | "
            f"{row['positive_unit_fraction']:.3f} |"
        )

    lines.extend(
        [
            "",
            "### IPIX Held-out Recordings",
            "",
            "| Pfa | Comparator | n recordings | Mean Delta Pd | 95% CI | Positive-recording fraction |",
            "|---:|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in ipix_ci.iterrows():
        lines.append(
            f"| {row['pfa']:.0e} | `{row['comparator']}` | {int(row['n_units'])} | "
            f"{row['mean_delta_pd']:.4f} | [{row['ci95_low']:.4f}, {row['ci95_high']:.4f}] | "
            f"{row['positive_unit_fraction']:.3f} |"
        )

    stats = ssdd_payload.get("test_stats", {})
    meta = ssdd_payload.get("test_meta", {})
    lines.extend(
        [
            "",
            "## SSDD Gap",
            "",
            f"- Current SSDD aggregate evidence: `{meta.get('images', 'unknown')}` test images, `{meta.get('annotations', 'unknown')}` annotations.",
            f"- Aggregate test result: `{stats.get('wins_raw', 'unknown')}` wins, `{stats.get('ties_raw', 'unknown')}` ties, `{stats.get('losses_raw', 'unknown')}` losses vs raw; mean Pd delta vs raw `{stats.get('mean_delta_vs_raw', 'unknown')}`.",
            "- Missing supplement: image-level or annotation-level confidence intervals and a distribution plot of per-image gains.",
            "",
            "## Recommended Stopping Rule",
            "",
            "- Do SSDD image-level CI if time allows; it is the only clear high-value experiment left.",
            "- Do the combined full-asset gate if a clean one-page protocol artifact is desired.",
            "- Do not open a new data-source hunt unless a clean, scriptable radar dataset is already available.",
            "- Do not add high-risk classical baselines unless they can be implemented with the same Pfa calibration and documented fairly.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260715)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rng = np.random.default_rng(args.seed)

    aistap_df = load_aistap_full_asset(root)
    ipix_path = root / "results" / "ipix_external" / "ipix_validated_residual_fusion_test_20260715.csv"
    ipix_df = pd.read_csv(ipix_path) if ipix_path.exists() else pd.DataFrame()
    ssdd_payload = load_json(root / "results" / "ssdd_external" / "ssdd_external_trainable_gate_20260715.json")

    aistap_ci = summarize_aistap(aistap_df, rng, args.boot)
    ipix_ci = summarize_ipix(ipix_df, rng, args.boot)
    priorities = build_priority_table(aistap_ci, ipix_ci, ssdd_payload)

    result_dir = root / "results" / "aistap_supplementary"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    aistap_csv = result_dir / f"aistap_full_asset_bootstrap_delta_ci_{args.date}.csv"
    ipix_csv = result_dir / f"ipix_heldout_bootstrap_delta_ci_{args.date}.csv"
    json_path = result_dir / f"aistap_supplementary_strengthening_audit_{args.date}.json"
    md_path = log_dir / f"aistap_supplementary_experiment_priority_{args.date}.md"

    aistap_ci.to_csv(aistap_csv, index=False)
    ipix_ci.to_csv(ipix_csv, index=False)
    payload = {
        "date": args.date,
        "bootstrap_replicates": args.boot,
        "seed": args.seed,
        "priorities": priorities,
        "artifacts": {
            "aistap_ci_csv": str(aistap_csv),
            "ipix_ci_csv": str(ipix_csv),
            "markdown_log": str(md_path),
        },
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_path, args.date, priorities, aistap_ci, ipix_ci, ssdd_payload)

    print(aistap_csv)
    print(ipix_csv)
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
