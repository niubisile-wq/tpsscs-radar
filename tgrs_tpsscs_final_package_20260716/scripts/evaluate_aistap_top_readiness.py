from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class Gate:
    name: str
    status: str
    evidence: str
    detail: str
    hard: bool = False


def exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def latest(paths: list[Path]) -> Path | None:
    existing = [p for p in paths if p.exists()]
    if not existing:
        return None
    return max(existing, key=lambda p: p.stat().st_mtime)


def read_csv(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def fmt_bool(ok: bool) -> str:
    return "pass" if ok else "fail"


def gate_reproducibility(root: Path) -> Gate:
    required = [
        root / "claim_matrix.md",
        root / "README.md",
        root / "STATUS.md",
        root / "logs" / "aistap_final_go_no_go_gate_20260713.md",
        root / "logs" / "aistap_top_ready_completion_audit_20260715.md",
        root / "logs" / "aistap_final_comparison_scorecard_20260713.md",
        root / "logs" / "aistap_manuscript_final_draft_20260715.md",
        root / "logs" / "aistap_figure_table_final_pack_20260715.md",
        root / "logs" / "aistap_manuscript_submission_package_20260715.md",
        root / "results" / "aistap_sample" / "aistap_operating_surface_20260713.csv",
    ]
    missing = [str(p.relative_to(root)) for p in required if not exists(p)]
    return Gate(
        name="reproducibility_package",
        status=fmt_bool(not missing),
        evidence=", ".join(str(p.relative_to(root)) for p in required if exists(p)),
        detail="all core package artifacts exist" if not missing else "missing: " + ", ".join(missing),
    )


def gate_deployable_candidate(root: Path) -> Gate:
    states = sorted((root / "results" / "aistap_sample").glob("tpsscs_minimal_train_state_*.pt"))
    preferred = [p for p in states if "rank30_hidden16_steps150_lr0p02" in p.name]
    selected = latest(preferred or states)
    return Gate(
        name="deployable_candidate_artifact",
        status=fmt_bool(selected is not None),
        evidence=str(selected.relative_to(root)) if selected else "no saved trainable-gate state artifact",
        detail=(
            "saved trainable-gate state exists; this supports reproducibility of the candidate branch"
            if selected
            else "current evidence has trainable-gate summaries but no reusable model state in results/aistap_sample"
        ),
        hard=True,
    )


def gate_target_frontier(root: Path) -> Gate:
    paths = sorted((root / "results" / "aistap_sample").glob("aistap_target_preservation_ablation_*.csv"))
    df = read_csv(latest(paths))
    if df.empty or "method" not in df.columns:
        return Gate(
            name="target_preservation_frontier",
            status="fail",
            evidence="no target-preservation ablation CSV",
            detail="cannot verify the trainable branch frontier",
            hard=True,
        )
    trainable = df[df["method"] == "trainable_gate"].copy()
    lowrank = df[df["method"] == "low_rank_residual"].copy()
    if trainable.empty or lowrank.empty:
        return Gate(
            name="target_preservation_frontier",
            status="fail",
            evidence=str(latest(paths).relative_to(root)),
            detail="trainable_gate or low_rank_residual rows are missing",
            hard=True,
        )

    rows: list[dict[str, Any]] = []
    for pfa in sorted(set(trainable["pfa_target"]).intersection(set(lowrank["pfa_target"]))):
        t = trainable[trainable["pfa_target"] == pfa].sort_values(["pd", "target_loss_db"], ascending=[False, True]).iloc[0]
        l = lowrank[lowrank["pfa_target"] == pfa].sort_values(["pd", "target_loss_db"], ascending=[False, True]).iloc[0]
        rows.append(
            {
                "pfa": float(pfa),
                "trainable_pd": float(t["pd"]),
                "lowrank_pd": float(l["pd"]),
                "trainable_target_loss": float(t["target_loss_db"]),
                "lowrank_target_loss": float(l["target_loss_db"]),
            }
        )

    improved = [
        r
        for r in rows
        if r["trainable_pd"] + 1e-9 >= r["lowrank_pd"]
        and r["trainable_target_loss"] + 1e-9 < r["lowrank_target_loss"]
    ]
    loose = [r for r in improved if r["pfa"] >= 0.003]
    if loose:
        best = loose[-1]
        return Gate(
            name="target_preservation_frontier",
            status="pass",
            evidence=str(latest(paths).relative_to(root)),
            detail=(
                f"trainable gate improves the low-rank frontier at pfa={best['pfa']:g}: "
                f"Pd {best['trainable_pd']:.4f} vs {best['lowrank_pd']:.4f}, "
                f"target loss {best['trainable_target_loss']:.3f} vs {best['lowrank_target_loss']:.3f} dB"
            ),
        )
    return Gate(
        name="target_preservation_frontier",
        status="partial",
        evidence=str(latest(paths).relative_to(root)),
        detail="trainable gate reduces target loss, but does not dominate the low-rank frontier on the checked operating points",
        hard=True,
    )


def gate_sample_size(root: Path) -> Gate:
    full_paths = sorted((root / "results" / "aistap_full_asset").glob("aistap_full_asset_detector_candidate_*.csv"))
    full_frames = [read_csv(p) for p in full_paths]
    full_frames = [df for df in full_frames if not df.empty]
    if full_frames:
        full_df = pd.concat(full_frames, ignore_index=True)
    else:
        full_df = pd.DataFrame()
    if not full_df.empty and "item_id" in full_df.columns:
        if "asset" in full_df.columns:
            target_items = int(full_df[["asset", "item_id"]].drop_duplicates().shape[0])
            asset_count = int(full_df["asset"].nunique())
        else:
            target_items = int(full_df["item_id"].nunique())
            asset_count = 1
        ok = target_items >= 100
        cross_condition_json = latest(sorted((root / "logs").glob("aistap_cross_condition_full_asset_validation_*.json")))
        evidence_path = cross_condition_json if cross_condition_json is not None else latest(full_paths)
        return Gate(
            name="top_tier_sample_scale",
            status=fmt_bool(ok),
            evidence=str(evidence_path.relative_to(root)) if evidence_path is not None else "no full-asset detector CSV",
            detail=f"{target_items} target-bearing full-asset items evaluated across {asset_count} official assets; top-tier gate requires >=100 or an independent external dataset",
            hard=True,
        )

    paths = sorted((root / "results" / "aistap_sample").glob("aistap_target_preservation_ablation_*.csv"))
    df = read_csv(latest(paths))
    if df.empty:
        return Gate(
            name="top_tier_sample_scale",
            status="fail",
            evidence="no target-preservation ablation CSV",
            detail="sample scale cannot be verified",
            hard=True,
        )
    target_items = df[["path", "image_index"]].drop_duplicates().shape[0] if {"path", "image_index"} <= set(df.columns) else 0
    ok = target_items >= 100
    return Gate(
        name="top_tier_sample_scale",
        status=fmt_bool(ok),
        evidence=str(latest(paths).relative_to(root)),
        detail=f"{target_items} target-bearing evaluated public-sample items; top-tier gate requires >=100 or an independent external dataset",
        hard=True,
    )


def gate_cross_condition(root: Path) -> Gate:
    paths = sorted((root / "results" / "aistap_sample").glob("aistap_subset_loso_cross_condition_*_summary.csv"))
    df = read_csv(latest(paths))
    if df.empty:
        return Gate(
            name="cross_condition_holdout",
            status="fail",
            evidence="no subset LOSO summary CSV",
            detail="cannot verify cross-condition behavior",
        )
    if "holdout" not in df.columns and "held_out_subset" in df.columns:
        df = df.rename(columns={"held_out_subset": "holdout"})
    needed = {"holdout", "method", "pfa_target", "pd_mean"}
    if not needed <= set(df.columns):
        return Gate(
            name="cross_condition_holdout",
            status="partial",
            evidence=str(latest(paths).relative_to(root)),
            detail="summary exists but lacks expected columns",
        )
    train = df[(df["method"] == "trainable_gate") & (df["pfa_target"].round(8) == 0.01)]
    low = df[(df["method"] == "low_rank_residual") & (df["pfa_target"].round(8) == 0.01)]
    finite = not train.empty and train["pd_mean"].notna().all()
    wins = 0
    for holdout in sorted(set(train["holdout"]).intersection(set(low["holdout"]))):
        tp = float(train[train["holdout"] == holdout]["pd_mean"].iloc[0])
        lp = float(low[low["holdout"] == holdout]["pd_mean"].iloc[0])
        if tp >= lp:
            wins += 1
    status = "pass" if finite and wins >= 2 else "partial" if finite else "fail"
    return Gate(
        name="cross_condition_holdout",
        status=status,
        evidence=str(latest(paths).relative_to(root)),
        detail=f"trainable gate finite on {train['holdout'].nunique() if finite else 0} holdouts; wins/ties low-rank on {wins} holdouts at Pfa=1e-2",
    )


def gate_external_aistap(root: Path) -> Gate:
    claim = (root / "claim_matrix.md").read_text(encoding="utf-8", errors="replace")
    cross_condition_json = latest(sorted((root / "logs").glob("aistap_cross_condition_full_asset_validation_*.json")))
    combined_full_asset_json = latest(sorted((root / "results" / "aistap_full_asset").glob("aistap_combined_full_asset_protocol_*.json")))
    ipix_validated_json = latest(sorted((root / "results" / "ipix_external").glob("ipix_validated_residual_fusion_*.json")))
    ipix_json = latest(sorted((root / "results" / "ipix_external").glob("ipix_external_detector_transfer_*.json")))
    ssdd_json = latest(sorted((root / "results" / "ssdd_external").glob("ssdd_external_trainable_gate_*.json")))
    ssdd_ci_json = latest(sorted((root / "results" / "ssdd_external").glob("ssdd_image_level_bootstrap_ci_*.json")))
    ssdd_log = latest(sorted((root / "logs").glob("ssdd_external_trainable_gate_*.md")))
    ssdd_ci_log = latest(sorted((root / "logs").glob("ssdd_image_level_bootstrap_ci_*.md")))
    ipix_audit = latest(sorted((root / "logs").glob("external_access_and_ipix_transfer_audit_*.md")))
    external_logs = [
        cross_condition_json,
        combined_full_asset_json,
        ipix_validated_json,
        ipix_json,
        ssdd_json,
        ssdd_ci_json,
        ssdd_log,
        ssdd_ci_log,
        ipix_audit,
        root / "logs" / "aistap_external_radar_validation_audit_20260713.md",
        root / "logs" / "sevir_year_holdout_external_radar_validation_20260713.md",
        root / "logs" / "nexrad_public_window_leaderboard_20260714.md",
    ]
    evidence = [str(p.relative_to(root)) for p in external_logs if p is not None and exists(p)]
    cross_condition_passed = False
    cross_detail = ""
    if cross_condition_json is not None and cross_condition_json.exists():
        try:
            data = json.loads(cross_condition_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        cross_condition_passed = data.get("passed") is True
        assets = data.get("criteria", {}).get("assets", [])
        if cross_condition_passed:
            cross_detail = f"AISTAP-SIM cross-condition full-asset validation passed on {len(assets)} official assets"
    combined_full_asset_passed = False
    combined_detail = ""
    if combined_full_asset_json is not None and combined_full_asset_json.exists():
        try:
            combined_full_asset = json.loads(combined_full_asset_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            combined_full_asset = {}
        combined_full_asset_passed = combined_full_asset.get("passed") is True
        if combined_full_asset_passed:
            combined_detail = (
                "combined official full-asset protocol passed "
                f"on {combined_full_asset.get('combined_target_bearing_items', 'unknown')} target-bearing items "
                f"({combined_full_asset.get('combined_wins_vs_raw', 'unknown')}/"
                f"{combined_full_asset.get('combined_comparisons', 'unknown')} combined Pfa wins vs raw and low-rank)"
            )
    ipix_validated_passed = False
    ipix_validated_detail = ""
    if ipix_validated_json is not None and ipix_validated_json.exists():
        try:
            ipix_validated = json.loads(ipix_validated_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ipix_validated = {}
        ipix_validated_passed = ipix_validated.get("passed") is True
        if ipix_validated_passed:
            stats = ipix_validated.get("test_stats", {})
            test_file_count = len(ipix_validated.get("test_files", [])) or "unknown"
            ipix_validated_detail = (
                "independent IPIX validated residual-aware fusion passed "
                f"on {test_file_count} held-out recordings "
                f"({stats.get('wins_raw', 'unknown')}/"
                f"{len(stats.get('comparisons', [])) or 'unknown'} Pfa wins vs raw)"
            )
    ssdd_passed = False
    ssdd_detail = ""
    if ssdd_json is not None and ssdd_json.exists():
        try:
            ssdd = json.loads(ssdd_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ssdd = {}
        ssdd_passed = ssdd.get("passed") is True
        if ssdd_passed:
            stats = ssdd.get("test_stats", {})
            meta = ssdd.get("test_meta", {})
            ssdd_detail = (
                "official SSDD SAR external trainable-gate validation passed "
                f"on {meta.get('images', 'unknown')} test images/"
                f"{meta.get('annotations', 'unknown')} ship annotations "
                f"({stats.get('wins_raw', 'unknown')} wins, "
                f"{stats.get('ties_raw', 'unknown')} ties, "
                f"{stats.get('losses_raw', 'unknown')} losses vs raw)"
            )
    ssdd_ci_passed = False
    ssdd_ci_detail = ""
    if ssdd_ci_json is not None and ssdd_ci_json.exists():
        try:
            ssdd_ci = json.loads(ssdd_ci_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ssdd_ci = {}
        ssdd_ci_passed = ssdd_ci.get("passed") is True
        if ssdd_ci_passed:
            meta = ssdd_ci.get("test_meta", {})
            ssdd_ci_detail = (
                "SSDD image/annotation-level bootstrap CI supplement passed "
                f"on {meta.get('images', 'unknown')} images/"
                f"{meta.get('annotations', 'unknown')} annotations"
            )
    not_retrained = "does not by itself mean the AISTAP method has been re-trained" in claim
    if cross_condition_passed and ipix_validated_passed and ssdd_passed:
        return Gate(
            name="aistap_external_method_validation",
            status="pass",
            evidence=", ".join(evidence),
            detail=(
                cross_detail
                + ("; " + combined_detail if combined_full_asset_passed else "")
                + "; "
                + ipix_validated_detail
                + "; "
                + ssdd_detail
                + ("; " + ssdd_ci_detail if ssdd_ci_passed else "")
                + "; this gives one official in-domain full-asset layer and two independent external radar dataset families"
            ),
            hard=True,
        )
    if cross_condition_passed and ipix_validated_passed:
        return Gate(
            name="aistap_external_method_validation",
            status="pass",
            evidence=", ".join(evidence),
            detail=(
                cross_detail
                + "; "
                + ipix_validated_detail
                + "; this closes the method-level external-validation gate, but breadth relative to the battery package is evaluated separately"
            ),
            hard=True,
        )
    if cross_condition_passed:
        ipix_detail = ""
        if ipix_json is not None and ipix_json.exists():
            ipix_detail = "; an independent IPIX zero-shot transfer smoke test exists, but it is not a passing external-validation result"
        return Gate(
            name="aistap_external_method_validation",
            status="partial",
            evidence=", ".join(evidence),
            detail=(
                cross_detail
                + "; this is method-level official cross-condition evidence, but independent non-AISTAP external validation remains unproven"
                + ipix_detail
            ),
            hard=True,
        )
    return Gate(
        name="aistap_external_method_validation",
        status="fail" if not_retrained else "partial",
        evidence=", ".join(evidence) if evidence else "no external radar validation logs",
        detail=(
            "external radar audits exist, but claim_matrix states they are not AISTAP retraining/transfer results"
            if not_retrained
            else "external logs exist, but method-level transfer still needs manual confirmation"
        ),
        hard=True,
    )


def gate_reference_superiority(root: Path, power_root: Path, battery_root: Path) -> Gate:
    power_status = power_root / "STATUS.md"
    battery_note = battery_root / "BATTERY_EXTERNAL_VALIDATION_ONE_PAGER_20260713.md"
    local_scorecard = root / "logs" / "aistap_cross_paper_scorecard_20260713.md"
    ipix_validated_json = latest(sorted((root / "results" / "ipix_external").glob("ipix_validated_residual_fusion_*.json")))
    ssdd_json = latest(sorted((root / "results" / "ssdd_external").glob("ssdd_external_trainable_gate_*.json")))
    ssdd_ci_json = latest(sorted((root / "results" / "ssdd_external").glob("ssdd_image_level_bootstrap_ci_*.json")))
    missing = [str(p) for p in [power_status, battery_note, local_scorecard] if not exists(p)]
    if missing:
        return Gate(
            name="local_reference_superiority",
            status="fail",
            evidence="missing: " + "; ".join(missing),
            detail="cannot compare against both local reference papers",
            hard=True,
        )
    score = local_scorecard.read_text(encoding="utf-8", errors="replace")
    battery = battery_note.read_text(encoding="utf-8", errors="replace")
    beats_power_inside_boundary = "operating-policy evidence density" in score
    battery_has_external_depth = "Validation hierarchy" in battery and "2026 millions-scale open archive" in battery
    ipix_suite_passed = False
    ipix_test_files = 0
    ipix_wins_raw: int | str = "unknown"
    ipix_wins_lowrank: int | str = "unknown"
    ipix_comparisons = 0
    ssdd_suite_passed = False
    ssdd_test_images: int | str = "unknown"
    ssdd_test_annotations: int | str = "unknown"
    ssdd_wins_raw: int | str = "unknown"
    ssdd_ties_raw: int | str = "unknown"
    ssdd_losses_raw: int | str = "unknown"
    ssdd_wins_lowrank: int | str = "unknown"
    ssdd_comparisons: int | str = "unknown"
    ssdd_ci_passed = False
    if ipix_validated_json is not None and ipix_validated_json.exists():
        try:
            ipix_validated = json.loads(ipix_validated_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ipix_validated = {}
        stats = ipix_validated.get("test_stats", {})
        comparisons = stats.get("comparisons", [])
        ipix_test_files = len(ipix_validated.get("test_files", []))
        ipix_wins_raw = stats.get("wins_raw", "unknown")
        ipix_wins_lowrank = stats.get("wins_lowrank", "unknown")
        ipix_comparisons = len(comparisons)
        ipix_suite_passed = (
            ipix_validated.get("passed") is True
            and ipix_test_files >= 10
            and ipix_wins_raw == ipix_comparisons
            and ipix_wins_lowrank == ipix_comparisons
            and ipix_comparisons > 0
        )
    if ssdd_json is not None and ssdd_json.exists():
        try:
            ssdd = json.loads(ssdd_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ssdd = {}
        stats = ssdd.get("test_stats", {})
        meta = ssdd.get("test_meta", {})
        ssdd_test_images = meta.get("images", "unknown")
        ssdd_test_annotations = meta.get("annotations", "unknown")
        ssdd_wins_raw = stats.get("wins_raw", "unknown")
        ssdd_ties_raw = stats.get("ties_raw", "unknown")
        ssdd_losses_raw = stats.get("losses_raw", "unknown")
        ssdd_wins_lowrank = stats.get("wins_lowrank", "unknown")
        ssdd_comparisons = stats.get("comparisons", "unknown")
        ssdd_suite_passed = (
            ssdd.get("passed") is True
            and isinstance(ssdd_test_images, int)
            and ssdd_test_images >= 200
            and isinstance(ssdd_test_annotations, int)
            and ssdd_test_annotations >= 500
            and ssdd_losses_raw == 0
            and isinstance(ssdd_wins_raw, int)
            and ssdd_wins_raw >= 3
            and ssdd_wins_lowrank == ssdd_comparisons
        )
    if ssdd_ci_json is not None and ssdd_ci_json.exists():
        try:
            ssdd_ci = json.loads(ssdd_ci_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ssdd_ci = {}
        ssdd_ci_passed = ssdd_ci.get("passed") is True
    ok = beats_power_inside_boundary and not battery_has_external_depth
    evidence_parts = [
        str(local_scorecard.relative_to(root)),
        "power_se/STATUS.md",
        "battery/BATTERY_EXTERNAL_VALIDATION_ONE_PAGER_20260713.md",
    ]
    if ipix_validated_json is not None and ipix_validated_json.exists():
        evidence_parts.append(str(ipix_validated_json.relative_to(root)))
    if ssdd_json is not None and ssdd_json.exists():
        evidence_parts.append(str(ssdd_json.relative_to(root)))
    if ssdd_ci_json is not None and ssdd_ci_json.exists():
        evidence_parts.append(str(ssdd_ci_json.relative_to(root)))
    if battery_has_external_depth and beats_power_inside_boundary and ipix_suite_passed and ssdd_suite_passed:
        status = "pass"
        detail = (
            "AISTAP is ahead on detector operating-policy density and now has two positive independent external radar families: "
            f"IPIX over {ipix_test_files} disjoint held-out recordings "
            f"({ipix_wins_raw}/{ipix_comparisons} Pfa wins vs raw, {ipix_wins_lowrank}/{ipix_comparisons} vs low-rank) "
            f"and official SSDD over {ssdd_test_images} test images/{ssdd_test_annotations} ship annotations "
            f"({ssdd_wins_raw} wins, {ssdd_ties_raw} ties, {ssdd_losses_raw} losses vs raw; "
            f"{ssdd_wins_lowrank}/{ssdd_comparisons} wins vs low-rank). "
            + ("The SSDD image/annotation-level CI supplement also passes. " if ssdd_ci_passed else "")
            +
            "This closes the local reference superiority gate against the selected power and battery packages"
        )
    elif battery_has_external_depth and ipix_suite_passed:
        status = "partial"
        detail = (
            "AISTAP is ahead on internal detector operating-policy density and now has "
            f"a positive IPIX single-family external layer over {ipix_test_files} disjoint held-out recordings "
            f"({ipix_wins_raw}/{ipix_comparisons} Pfa wins vs raw, "
            f"{ipix_wins_lowrank}/{ipix_comparisons} vs low-rank), "
            "but the battery package still has broader multi-tier external-validation breadth"
        )
    elif battery_has_external_depth:
        status = "fail"
        detail = (
            "AISTAP is ahead on internal detector operating-policy density, "
            "but battery still has stronger external-validation breadth"
        )
    else:
        status = fmt_bool(ok)
        detail = "local scorecard supports superiority over both selected references"
    return Gate(
        name="local_reference_superiority",
        status=status,
        evidence="; ".join(evidence_parts),
        detail=detail,
        hard=True,
    )


def gate_classical_cfar_baseline_strength(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_full_asset_classical_cfar_baselines_*.json")))
    comparison_path = latest(sorted(result_dir.glob("aistap_full_asset_classical_cfar_best_comparison_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_full_asset_classical_cfar_baselines_*.md")))
    if json_path is None or comparison_path is None:
        return Gate(
            name="classical_cfar_baseline_strength",
            status="fail",
            evidence="no full-asset classical CFAR baseline audit",
            detail="top-tier baseline-strength gate requires raw/residual global top-k plus local CA/GOCA/SOCA/OS-CFAR comparisons on official full assets",
            hard=True,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="classical_cfar_baseline_strength",
            status="fail",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse classical CFAR audit JSON: {exc}",
            hard=True,
        )
    comparison = read_csv(comparison_path)
    combined_rows = comparison[comparison["asset"] == "combined"] if "asset" in comparison.columns else pd.DataFrame()
    asset_rows = comparison[comparison["asset"] != "combined"] if "asset" in comparison.columns else pd.DataFrame()
    ok = (
        data.get("passed_strict_best_classical") is True
        and data.get("all_proposed_pfa_calibrated") is True
        and int(data.get("target_bearing_items", 0)) >= 200
        and int(data.get("combined_wins_vs_best_classical", 0)) == int(data.get("combined_comparisons", -1))
        and int(data.get("asset_level_wins_vs_best_classical", 0)) == int(data.get("asset_level_comparisons", -1))
        and int(data.get("combined_comparisons", 0)) >= 7
        and int(data.get("asset_level_comparisons", 0)) >= 14
        and len(data.get("candidate_methods", [])) >= 10
        and not combined_rows.empty
        and not asset_rows.empty
        and bool(combined_rows["beats_best_classical"].all())
        and bool(asset_rows["beats_best_classical"].all())
    )
    evidence = [str(json_path.relative_to(root)), str(comparison_path.relative_to(root))]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    return Gate(
        name="classical_cfar_baseline_strength",
        status=fmt_bool(ok),
        evidence=", ".join(evidence),
        detail=(
            f"TP-SSCS wins {data.get('combined_wins_vs_best_classical', 0)}/"
            f"{data.get('combined_comparisons', 0)} combined and "
            f"{data.get('asset_level_wins_vs_best_classical', 0)}/"
            f"{data.get('asset_level_comparisons', 0)} asset-level comparisons "
            f"against the best of {len(data.get('candidate_methods', []))} global/local CFAR baselines; "
            f"minimum combined delta {float(data.get('combined_min_delta_vs_best_classical', float('nan'))):.4f}"
        ),
        hard=True,
    )


def gate_classical_cfar_parameter_sensitivity(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_full_asset_classical_cfar_param_sweep_*.json")))
    comparison_path = latest(sorted(result_dir.glob("aistap_full_asset_classical_cfar_param_sweep_best_comparison_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_full_asset_classical_cfar_param_sweep_*.md")))
    if json_path is None or comparison_path is None:
        return Gate(
            name="classical_cfar_parameter_sensitivity",
            status="fail",
            evidence="no full-asset classical CFAR parameter-sweep audit",
            detail="top-tier baseline-strength gate requires a multi-parameter local CFAR sweep, not only one fixed CFAR setting",
            hard=True,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="classical_cfar_parameter_sensitivity",
            status="fail",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse classical CFAR parameter-sweep JSON: {exc}",
            hard=True,
        )
    comparison = read_csv(comparison_path)
    combined_rows = comparison[comparison["asset"] == "combined"] if "asset" in comparison.columns else pd.DataFrame()
    asset_rows = comparison[comparison["asset"] != "combined"] if "asset" in comparison.columns else pd.DataFrame()
    training_grid = data.get("training_grid", [])
    guard_grid = data.get("guard_grid", [])
    os_percentiles = data.get("os_percentiles", [])
    ok = (
        data.get("passed_strict_best_swept_classical") is True
        and data.get("all_proposed_pfa_calibrated") is True
        and int(data.get("target_bearing_items", 0)) >= 200
        and int(data.get("candidate_method_count", 0)) >= 50
        and len(training_grid) >= 3
        and len(guard_grid) >= 2
        and len(os_percentiles) >= 3
        and int(data.get("combined_wins_vs_best_swept_classical", 0)) == int(data.get("combined_comparisons", -1))
        and int(data.get("asset_level_wins_vs_best_swept_classical", 0)) == int(data.get("asset_level_comparisons", -1))
        and int(data.get("combined_comparisons", 0)) >= 7
        and int(data.get("asset_level_comparisons", 0)) >= 14
        and float(data.get("combined_min_delta_vs_best_swept_classical", -1.0)) > 0.0
        and not combined_rows.empty
        and not asset_rows.empty
        and bool(combined_rows["beats_best_classical"].all())
        and bool(asset_rows["beats_best_classical"].all())
    )
    evidence = [str(json_path.relative_to(root)), str(comparison_path.relative_to(root))]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    return Gate(
        name="classical_cfar_parameter_sensitivity",
        status=fmt_bool(ok),
        evidence=", ".join(evidence),
        detail=(
            f"TP-SSCS wins {data.get('combined_wins_vs_best_swept_classical', 0)}/"
            f"{data.get('combined_comparisons', 0)} combined and "
            f"{data.get('asset_level_wins_vs_best_swept_classical', 0)}/"
            f"{data.get('asset_level_comparisons', 0)} asset-level comparisons "
            f"against the best of {data.get('candidate_method_count', 0)} CFAR methods/configurations; "
            f"training grid {training_grid}, guard grid {guard_grid}, OS percentiles {os_percentiles}; "
            f"minimum combined delta {float(data.get('combined_min_delta_vs_best_swept_classical', float('nan'))):.4f}"
        ),
        hard=True,
    )


def gate_loso_learned_baseline(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_full_asset_loso_learned_raw_baseline_*.json")))
    comparison_path = latest(sorted(result_dir.glob("aistap_full_asset_loso_learned_raw_baseline_comparison_*.csv")))
    ci_path = latest(sorted(result_dir.glob("aistap_full_asset_loso_learned_raw_baseline_bootstrap_ci_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_full_asset_loso_learned_raw_baseline_*.md")))
    if json_path is None or comparison_path is None or ci_path is None:
        return Gate(
            name="loso_learned_baseline_strength",
            status="fail",
            evidence="no full-asset leave-one-condition-out learned-baseline audit",
            detail="top-tier learned-baseline gate requires a supervised held-out learned comparator on the official AISTAP-SIM full assets",
            hard=True,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="loso_learned_baseline_strength",
            status="fail",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse learned-baseline audit JSON: {exc}",
            hard=True,
        )
    comparison = read_csv(comparison_path)
    ci_df = read_csv(ci_path)
    combined_rows = comparison[comparison["asset"] == "combined"] if "asset" in comparison.columns else pd.DataFrame()
    asset_rows = comparison[comparison["asset"] != "combined"] if "asset" in comparison.columns else pd.DataFrame()
    ci_positive = (not ci_df.empty and "ci95_low" in ci_df.columns and bool((ci_df["ci95_low"].astype(float) > 0.0).all()))
    ok = (
        data.get("passed") is True
        and data.get("all_pfa_calibrated") is True
        and int(data.get("heldout_target_bearing_items", 0)) >= 200
        and int(data.get("combined_wins_vs_learned", 0)) == int(data.get("combined_comparisons", -1))
        and int(data.get("asset_level_wins_vs_learned", 0)) == int(data.get("asset_level_comparisons", -1))
        and int(data.get("combined_comparisons", 0)) >= 7
        and int(data.get("asset_level_comparisons", 0)) >= 14
        and float(data.get("min_combined_delta_vs_learned", -1.0)) > 0.0
        and float(data.get("min_asset_delta_vs_learned", -1.0)) > 0.0
        and not combined_rows.empty
        and not asset_rows.empty
        and bool(combined_rows["proposed_beats_learned"].all())
        and bool(asset_rows["proposed_beats_learned"].all())
        and ci_positive
    )
    evidence = [str(json_path.relative_to(root)), str(comparison_path.relative_to(root)), str(ci_path.relative_to(root))]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    return Gate(
        name="loso_learned_baseline_strength",
        status=fmt_bool(ok),
        evidence=", ".join(evidence),
        detail=(
            f"TP-SSCS wins {data.get('combined_wins_vs_learned', 0)}/"
            f"{data.get('combined_comparisons', 0)} combined and "
            f"{data.get('asset_level_wins_vs_learned', 0)}/"
            f"{data.get('asset_level_comparisons', 0)} asset-level comparisons "
            f"against the leave-one-condition-out supervised raw-feature logistic baseline; "
            f"held-out items {data.get('heldout_target_bearing_items', 0)}, "
            f"minimum combined delta {float(data.get('min_combined_delta_vs_learned', float('nan'))):.4f}, "
            f"bootstrap CI lower bounds positive={ci_positive}"
        ),
        hard=True,
    )


def gate_feature_ensemble_boundary(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    raw_hgb_json = latest(sorted(result_dir.glob("aistap_full_asset_loso_feature_ensemble_baseline_*.json")))
    tpsscs_hgb_json = latest(sorted(result_dir.glob("aistap_full_asset_loso_tpsscs_feature_ensemble_*.json")))
    raw_hgb_log = latest(sorted((root / "logs").glob("aistap_full_asset_loso_feature_ensemble_baseline_*.md")))
    tpsscs_hgb_log = latest(sorted((root / "logs").glob("aistap_full_asset_loso_tpsscs_feature_ensemble_*.md")))
    if raw_hgb_json is None or tpsscs_hgb_json is None:
        return Gate(
            name="feature_ensemble_boundary",
            status="partial",
            evidence="no strong feature-ensemble learned-baseline boundary audit",
            detail="strong supervised raw/residual HGB and TP-SSCS-feature HGB boundary checks are not both present",
            hard=False,
        )
    try:
        raw_data = json.loads(raw_hgb_json.read_text(encoding="utf-8"))
        tpsscs_data = json.loads(tpsscs_hgb_json.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="feature_ensemble_boundary",
            status="partial",
            evidence=", ".join(str(p.relative_to(root)) for p in [raw_hgb_json, tpsscs_hgb_json]),
            detail=f"could not parse feature-ensemble boundary JSON: {exc}",
            hard=False,
        )
    status = "pass" if tpsscs_data.get("passed_gain_vs_raw_residual_hgb") is True else "partial"
    evidence = [str(raw_hgb_json.relative_to(root)), str(tpsscs_hgb_json.relative_to(root))]
    for path in [raw_hgb_log, tpsscs_hgb_log]:
        if path is not None:
            evidence.append(str(path.relative_to(root)))
    return Gate(
        name="feature_ensemble_boundary",
        status=status,
        evidence=", ".join(evidence),
        detail=(
            "strong supervised raw/residual HGB beats compact TP-SSCS "
            f"({raw_data.get('combined_wins_vs_learned', 0)}/"
            f"{raw_data.get('combined_comparisons', 0)} compact wins; "
            f"minimum compact-minus-HGB delta {float(raw_data.get('min_combined_delta_vs_learned', float('nan'))):.4f}); "
            "TP-SSCS-feature HGB improves over compact TP-SSCS and nearly matches the raw/residual HGB "
            f"({tpsscs_data.get('combined_wins_vs_raw_residual_hgb', 0)}/"
            f"{tpsscs_data.get('combined_comparisons', 0)} combined wins vs raw/residual HGB; "
            f"minimum delta {float(tpsscs_data.get('min_combined_delta_vs_raw_residual_hgb', float('nan'))):.4f})"
        ),
        hard=False,
    )


def gate_positive_pixel_label_efficiency(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_full_asset_loso_low_positive_pixel_hgb_*.json")))
    comparison_path = latest(sorted(result_dir.glob("aistap_full_asset_loso_low_positive_pixel_hgb_comparison_*.csv")))
    ci_path = latest(sorted(result_dir.glob("aistap_full_asset_loso_low_positive_pixel_hgb_bootstrap_ci_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_full_asset_loso_low_positive_pixel_hgb_*.md")))
    if json_path is None or comparison_path is None or ci_path is None:
        return Gate(
            name="positive_pixel_label_efficiency",
            status="partial",
            evidence="no positive-pixel low-label HGB audit",
            detail="label-efficiency evidence is optional but useful after the supervised HGB boundary",
            hard=False,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="positive_pixel_label_efficiency",
            status="partial",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse positive-pixel low-label audit JSON: {exc}",
            hard=False,
        )
    needed = {"1", "2", "4", "8"}
    win_budgets = {str(x) for x in data.get("compact_all_pfa_win_budgets", [])}
    ci_budgets = {str(x) for x in data.get("compact_all_pfa_positive_ci_budgets", [])}
    ok = (
        data.get("budget_unit") == "positive_pixels"
        and data.get("all_methods_pfa_calibrated") is True
        and int(data.get("heldout_target_bearing_items", 0)) >= 200
        and needed <= win_budgets
        and needed <= ci_budgets
    )
    evidence = [str(json_path.relative_to(root)), str(comparison_path.relative_to(root)), str(ci_path.relative_to(root))]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    return Gate(
        name="positive_pixel_label_efficiency",
        status="pass" if ok else "partial",
        evidence=", ".join(evidence),
        detail=(
            "compact TP-SSCS beats low-label raw/residual HGB at all seven Pfa points "
            f"for positive-pixel budgets {', '.join(sorted(win_budgets, key=lambda x: int(x) if x.isdigit() else 10**9))}; "
            f"positive-CI all-Pfa budgets {', '.join(sorted(ci_budgets, key=lambda x: int(x) if x.isdigit() else 10**9))}; "
            f"HGB first catches/exceeds compact at any Pfa at budget {data.get('first_budget_where_hgb_catches_or_exceeds_compact_at_any_pfa')}"
        ),
        hard=False,
    )


def gate_label_cost_pareto(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_full_asset_label_cost_pareto_*.json")))
    frame_path = latest(sorted(result_dir.glob("aistap_full_asset_label_cost_pareto_frame_auc_*.csv")))
    budget_path = latest(sorted(result_dir.glob("aistap_full_asset_label_cost_pareto_budget_auc_*.csv")))
    points_path = latest(sorted(result_dir.glob("aistap_full_asset_label_cost_pareto_points_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_full_asset_label_cost_pareto_*.md")))
    if json_path is None or frame_path is None or budget_path is None or points_path is None:
        return Gate(
            name="label_cost_pareto",
            status="partial",
            evidence="no label-cost Pareto audit",
            detail="label-cost evidence is optional but useful for bounding the supervised HGB comparison by annotation cost",
            hard=False,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="label_cost_pareto",
            status="partial",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse label-cost Pareto JSON: {exc}",
            hard=False,
        )

    needed = {"1", "2", "4", "8", "16"}
    dominated = {str(x) for x in data.get("compact_dominates_low_label_hgb_budgets_auc_runtime_labels", [])}
    ci_budgets = {str(x) for x in data.get("compact_auc_positive_ci_budgets", [])}
    boundary = set(data.get("boundary", []))
    compact_auc = float(data.get("compact_auc", float("nan")))
    full_hgb_auc = float(data.get("raw_residual_hgb_full_auc", float("nan")))
    ratio = float(data.get("hgb_over_compact_runtime_ratio", float("nan")))
    first_exceed = str(data.get("first_budget_hgb_auc_exceeds_compact"))
    target_items = int(data.get("target_bearing_items", 0))
    ok = (
        target_items >= 200
        and ratio > 1.0
        and needed <= dominated
        and needed <= ci_budgets
        and first_exceed == "64"
        and full_hgb_auc > compact_auc
        and "does_not_claim_superiority_over_full_label_hgb_boundary" in boundary
    )

    def sort_budget(values: set[str]) -> list[str]:
        return sorted(values, key=lambda x: int(x) if x.isdigit() else 10**9)

    evidence = [
        str(json_path.relative_to(root)),
        str(frame_path.relative_to(root)),
        str(budget_path.relative_to(root)),
        str(points_path.relative_to(root)),
    ]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    return Gate(
        name="label_cost_pareto",
        status="pass" if ok else "partial",
        evidence=", ".join(evidence),
        detail=(
            f"{target_items} target-bearing frames; compact TP-SSCS AUC {compact_auc:.4f} with zero official "
            f"full-asset positive-target labels and local CPU median {float(data.get('compact_runtime_ms', float('nan'))):.2f} ms/frame; "
            f"raw/residual HGB runtime ratio {ratio:.2f}x and full-label AUC {full_hgb_auc:.4f}; "
            f"compact Pareto-dominates low-label HGB budgets {', '.join(sort_budget(dominated))} in AUC/labels/runtime; "
            f"positive-CI AUC budgets {', '.join(sort_budget(ci_budgets))}; "
            f"HGB first exceeds compact AUC at budget {first_exceed}; full-label HGB remains an upper boundary"
        ),
        hard=False,
    )


def gate_target_free_calibration_boundary(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_full_asset_target_free_calibration_*.json")))
    comparison_path = latest(sorted(result_dir.glob("aistap_full_asset_target_free_calibration_comparison_*.csv")))
    ci_path = latest(sorted(result_dir.glob("aistap_full_asset_target_free_calibration_bootstrap_ci_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_full_asset_target_free_calibration_*.md")))
    if json_path is None or comparison_path is None or ci_path is None:
        return Gate(
            name="target_free_calibration_boundary",
            status="partial",
            evidence="no target-free calibration audit",
            detail="target-free calibration robustness evidence is optional but useful for claim control",
            hard=False,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="target_free_calibration_boundary",
            status="partial",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse target-free calibration JSON: {exc}",
            hard=False,
        )
    positive_modes = data.get("positive_delta_modes", [])
    calibrated_modes = data.get("pfa_calibrated_modes", [])
    passed_modes = data.get("passed_modes", [])
    status = "pass" if passed_modes else "partial" if positive_modes else "fail"
    evidence = [str(json_path.relative_to(root)), str(comparison_path.relative_to(root)), str(ci_path.relative_to(root))]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    summaries = data.get("mode_summary", [])
    summary_text = "; ".join(
        f"{item.get('calibration_mode')}: wins raw {item.get('combined_wins_vs_raw')}/{item.get('combined_comparisons')}, "
        f"wins low-rank {item.get('combined_wins_vs_lowrank')}/{item.get('combined_comparisons')}, "
        f"min delta low-rank {float(item.get('min_combined_delta_vs_lowrank', float('nan'))):.4f}, "
        f"Pfa calibrated={item.get('all_tpsscs_pfa_calibrated')}"
        for item in summaries
    )
    return Gate(
        name="target_free_calibration_boundary",
        status=status,
        evidence=", ".join(evidence),
        detail=(
            f"positive-delta modes={positive_modes}; fully Pfa-calibrated modes={calibrated_modes}; "
            f"passed modes={passed_modes}; {summary_text}"
        ),
        hard=False,
    )


def gate_frame_level_robustness(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_full_asset_frame_level_robustness_*.json")))
    summary_path = latest(sorted(result_dir.glob("aistap_full_asset_frame_level_robustness_summary_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_full_asset_frame_level_robustness_*.md")))
    if json_path is None or summary_path is None:
        return Gate(
            name="frame_level_robustness",
            status="partial",
            evidence="no frame-level robustness audit",
            detail="frame-level distribution evidence is optional but useful for ruling out few-frame aggregate gains",
            hard=False,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="frame_level_robustness",
            status="partial",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse frame-level robustness JSON: {exc}",
            hard=False,
        )
    target_items = int(data.get("target_bearing_items", 0))
    lowrank_losses = int(data.get("lowrank_loss_item_pfa_pairs", -1))
    lowrank_nonnegative = int(data.get("lowrank_nonnegative_item_pfa_pairs", 0))
    pairs = int(data.get("item_pfa_pairs_per_comparator", 0))
    raw_min_win = float(data.get("combined_raw_min_win_fraction", float("nan")))
    raw_losses = int(data.get("raw_loss_item_pfa_pairs", 0))
    ok = (
        data.get("broad_frame_level_support") is True
        and target_items >= 200
        and pairs >= 1400
        and lowrank_losses == 0
        and lowrank_nonnegative == pairs
        and raw_min_win >= 0.85
        and raw_losses > 0
    )
    evidence = [str(json_path.relative_to(root)), str(summary_path.relative_to(root))]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    return Gate(
        name="frame_level_robustness",
        status="pass" if ok else "partial",
        evidence=", ".join(evidence),
        detail=(
            f"{target_items} target-bearing frames x {data.get('pfa_points', 0)} Pfa points; "
            f"low-rank nonnegative item-Pfa pairs {lowrank_nonnegative}/{pairs}, low-rank losses {lowrank_losses}; "
            f"raw minimum combined win fraction {raw_min_win:.3f}, raw-favorable item-Pfa pairs {raw_losses}; "
            "raw comparison remains broad but not universal"
        ),
        hard=False,
    )


def gate_paired_significance_audit(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_full_asset_paired_significance_*.json")))
    csv_path = latest(sorted(result_dir.glob("aistap_full_asset_paired_significance_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_full_asset_paired_significance_*.md")))
    if json_path is None or csv_path is None:
        return Gate(
            name="paired_significance_audit",
            status="partial",
            evidence="no paired significance audit",
            detail="paired nonparametric significance evidence is optional but useful for top-tier statistical reporting",
            hard=False,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="paired_significance_audit",
            status="partial",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse paired significance JSON: {exc}",
            hard=False,
        )
    target_items = int(data.get("target_bearing_items", 0))
    combined_tests = int(data.get("combined_tests_total", 0))
    max_q = float(data.get("max_combined_bh_q", float("nan")))
    min_effect = float(data.get("min_combined_matched_sign_effect", float("nan")))
    ok = (
        data.get("all_combined_significant_bh_0p05") is True
        and data.get("lowrank_all_combined_significant_bh_0p05") is True
        and data.get("raw_all_combined_significant_bh_0p05") is True
        and target_items >= 200
        and combined_tests >= 14
        and max_q < 0.05
        and min_effect >= 0.75
    )
    evidence = [str(json_path.relative_to(root)), str(csv_path.relative_to(root))]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    return Gate(
        name="paired_significance_audit",
        status="pass" if ok else "partial",
        evidence=", ".join(evidence),
        detail=(
            f"{combined_tests} combined exact sign tests over {target_items} target-bearing frames; "
            f"all combined BH-FDR significant={data.get('all_combined_significant_bh_0p05')}, "
            f"worst combined q={max_q:.3e}, minimum matched sign effect={min_effect:.3f}; "
            "ties are excluded from the sign test and this is not a new dataset"
        ),
        hard=False,
    )


def gate_log_pfa_auc_surface(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_full_asset_log_pfa_auc_*.json")))
    summary_path = latest(sorted(result_dir.glob("aistap_full_asset_log_pfa_auc_summary_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_full_asset_log_pfa_auc_*.md")))
    if json_path is None or summary_path is None:
        return Gate(
            name="log_pfa_auc_surface",
            status="partial",
            evidence="no log-Pfa AUC operating-surface audit",
            detail="whole-operating-surface evidence is optional but useful for avoiding single-Pfa claims",
            hard=False,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="log_pfa_auc_surface",
            status="partial",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse log-Pfa AUC JSON: {exc}",
            hard=False,
        )
    target_items = int(data.get("target_bearing_items", 0))
    pfa_points = int(data.get("pfa_points", 0))
    min_delta = float(data.get("min_combined_delta_auc", float("nan")))
    min_ci_low = float(data.get("min_combined_ci95_low", float("nan")))
    max_q = float(data.get("max_combined_bh_q", float("nan")))
    ok = (
        data.get("combined_auc_positive_vs_all") is True
        and data.get("combined_bootstrap_ci_positive_vs_all") is True
        and data.get("combined_significant_bh_vs_all") is True
        and target_items >= 200
        and pfa_points >= 7
        and min_delta > 0.0
        and min_ci_low > 0.0
        and max_q < 0.05
    )
    evidence = [str(json_path.relative_to(root)), str(summary_path.relative_to(root))]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    return Gate(
        name="log_pfa_auc_surface",
        status="pass" if ok else "partial",
        evidence=", ".join(evidence),
        detail=(
            f"log-Pfa AUC over {pfa_points} checked Pfa points and {target_items} target-bearing frames; "
            f"minimum combined AUC delta {min_delta:.4f}, minimum CI95 low {min_ci_low:.4f}, "
            f"worst combined BH-FDR q={max_q:.3e}; checked Pfa range only"
        ),
        hard=False,
    )


def gate_component_attribution(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_full_asset_component_attribution_*.json")))
    auc_summary_path = latest(sorted(result_dir.glob("aistap_full_asset_component_attribution_auc_summary_*.csv")))
    pfa_summary_path = latest(sorted(result_dir.glob("aistap_full_asset_component_attribution_pfa_summary_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_full_asset_component_attribution_*.md")))
    if json_path is None or auc_summary_path is None or pfa_summary_path is None:
        return Gate(
            name="component_attribution_audit",
            status="partial",
            evidence="no component-attribution audit",
            detail="component-attribution evidence is optional but useful for mechanism and policy-boundary claims",
            hard=False,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="component_attribution_audit",
            status="partial",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse component-attribution JSON: {exc}",
            hard=False,
        )
    auc_summary = read_csv(auc_summary_path)
    combined = auc_summary[auc_summary["asset"] == "combined"] if "asset" in auc_summary.columns else pd.DataFrame()
    raw_row = combined[combined["comparator"] == "raw"] if "comparator" in combined.columns else pd.DataFrame()
    lowrank_row = combined[combined["comparator"] == "low_rank_residual_k30"] if "comparator" in combined.columns else pd.DataFrame()
    gate_row = combined[combined["comparator"] == "tpsscs_trainable_gate"] if "comparator" in combined.columns else pd.DataFrame()
    raw_delta = float(raw_row["mean_delta_auc"].iloc[0]) if not raw_row.empty else float("nan")
    lowrank_delta = float(lowrank_row["mean_delta_auc"].iloc[0]) if not lowrank_row.empty else float("nan")
    lowrank_losses = int(lowrank_row["losses"].iloc[0]) if not lowrank_row.empty else -1
    gate_ci_positive = bool(gate_row["positive_bootstrap_ci"].iloc[0]) if not gate_row.empty else True
    target_items = int(data.get("target_bearing_items", 0))
    boundary = set(data.get("boundary", []))
    ok = (
        data.get("raw_auc_delta_positive") is True
        and data.get("lowrank_auc_nonnegative_all_frames") is True
        and data.get("gate_only_boundary_present") is True
        and target_items >= 200
        and raw_delta > 0.0
        and lowrank_delta > 0.0
        and lowrank_losses == 0
        and gate_ci_positive is False
        and "gate_only_is_relaxed_endpoint_not_selected_low_false_alarm_policy" in boundary
    )
    evidence = [str(json_path.relative_to(root)), str(auc_summary_path.relative_to(root)), str(pfa_summary_path.relative_to(root))]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    return Gate(
        name="component_attribution_audit",
        status="pass" if ok else "partial",
        evidence=", ".join(evidence),
        detail=(
            f"component attribution over {target_items} target-bearing frames: finished-detector AUC delta "
            f"{raw_delta:.4f} vs raw and {lowrank_delta:.4f} vs low-rank; "
            f"low-rank losses={lowrank_losses}; gate-only boundary present={data.get('gate_only_boundary_present')} "
            f"with gate-only CI-positive={gate_ci_positive}"
        ),
        hard=False,
    )


def gate_runtime_complexity_profile(root: Path) -> Gate:
    result_dir = root / "results" / "aistap_full_asset"
    json_path = latest(sorted(result_dir.glob("aistap_runtime_profile_*.json")))
    summary_path = latest(sorted(result_dir.glob("aistap_runtime_profile_summary_*.csv")))
    components_path = latest(sorted(result_dir.glob("aistap_runtime_profile_components_*.csv")))
    log_path = latest(sorted((root / "logs").glob("aistap_runtime_profile_*.md")))
    if json_path is None or summary_path is None or components_path is None:
        return Gate(
            name="runtime_complexity_profile",
            status="partial",
            evidence="no runtime/complexity profile",
            detail="runtime evidence is optional but useful for deployment-cost claim control",
            hard=False,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="runtime_complexity_profile",
            status="partial",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse runtime profile JSON: {exc}",
            hard=False,
        )
    frames = int(data.get("timed_target_frames_total", 0))
    ratio = float(data.get("hgb_over_compact_runtime_ratio", float("nan")))
    compact_ms = float(data.get("compact_tpsscs_finished_detector_median_ms", float("nan")))
    hgb_ms = float(data.get("raw_residual_hgb_inference_median_ms", float("nan")))
    params = int(data.get("tpsscs_parameter_count", 0))
    ok = frames >= 10 and params > 0 and ratio >= 1.0
    evidence = [str(json_path.relative_to(root)), str(summary_path.relative_to(root)), str(components_path.relative_to(root))]
    if log_path is not None:
        evidence.append(str(log_path.relative_to(root)))
    return Gate(
        name="runtime_complexity_profile",
        status="pass" if ok else "partial",
        evidence=", ".join(evidence),
        detail=(
            f"local CPU profile over {frames} target-bearing frames: compact TP-SSCS median {compact_ms:.2f} ms/frame, "
            f"raw/residual HGB median {hgb_ms:.2f} ms/frame, HGB/compact ratio {ratio:.2f}x, "
            f"TP-SSCS parameters {params}; hardware-independent speed claims remain out of scope"
        ),
        hard=False,
    )


def gate_claim_consistency(root: Path) -> Gate:
    json_path = latest(sorted((root / "logs").glob("aistap_claim_consistency_audit_*.json")))
    md_path = latest(sorted((root / "logs").glob("aistap_claim_consistency_audit_*.md")))
    if json_path is None:
        return Gate(
            name="claim_consistency_audit",
            status="fail",
            evidence="no claim consistency audit",
            detail="top-tier package requires automated claim-boundary consistency checks",
            hard=True,
        )
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Gate(
            name="claim_consistency_audit",
            status="fail",
            evidence=str(json_path.relative_to(root)),
            detail=f"could not parse claim consistency audit JSON: {exc}",
            hard=True,
        )
    ok = data.get("verdict") == "claim_consistent" and int(data.get("hard_failure_count", -1)) == 0
    evidence = [str(json_path.relative_to(root))]
    if md_path is not None:
        evidence.append(str(md_path.relative_to(root)))
    return Gate(
        name="claim_consistency_audit",
        status="pass" if ok else "fail",
        evidence=", ".join(evidence),
        detail=(
            f"verdict={data.get('verdict')}; hard_failure_count={data.get('hard_failure_count')}; "
            f"warning_count={data.get('warning_count')}"
        ),
        hard=True,
    )


def gate_finished_detector(root: Path) -> Gate:
    protocol_json = latest(sorted((root / "logs").glob("aistap_finished_detector_protocol_*.json")))
    if protocol_json is not None:
        try:
            data = json.loads(protocol_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        if data.get("passed") is True:
            criteria = data.get("criteria", {})
            return Gate(
                name="finished_detector_result",
                status="pass",
                evidence=str(protocol_json.relative_to(root)),
                detail=(
                    "finished-detector protocol gate passed on "
                    f"{criteria.get('target_bearing_items', 'unknown')} target-bearing full-asset items"
                ),
                hard=True,
            )
        return Gate(
            name="finished_detector_result",
            status="fail",
            evidence=str(protocol_json.relative_to(root)),
            detail="finished-detector protocol gate exists but did not pass",
            hard=True,
        )

    indicators = list((root / "logs").glob("*finished*detector*.md")) + list((root / "results").glob("**/*finished*detector*"))
    candidates = list((root / "logs").glob("tpsscs_detector_candidate_*.md")) + list(
        (root / "results").glob("**/tpsscs_detector_candidate_*.csv")
    )
    if candidates and not indicators:
        return Gate(
            name="finished_detector_result",
            status="partial",
            evidence=", ".join(str(p.relative_to(root)) for p in sorted(candidates)[:4]),
            detail="detector-candidate evaluation exists, but it is still public-sample bounded and not a finished detector result",
            hard=True,
        )
    return Gate(
        name="finished_detector_result",
        status=fmt_bool(bool(indicators)),
        evidence=", ".join(str(p.relative_to(root)) for p in indicators) if indicators else "no finished-detector artifact",
        detail=(
            "finished-detector artifact exists"
            if indicators
            else "current evidence is still trainable-scaffold / candidate-branch evidence"
        ),
        hard=True,
    )


def write_outputs(root: Path, gates: list[Gate], date_tag: str) -> tuple[Path, Path]:
    hard_failures = [g for g in gates if g.hard and g.status != "pass"]
    overall = "not_top_ready" if hard_failures else "top_ready"

    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    json_path = log_dir / f"aistap_top_readiness_self_check_{date_tag}.json"
    md_path = log_dir / f"aistap_top_readiness_self_check_{date_tag}.md"

    payload = {
        "date": date_tag,
        "overall": overall,
        "hard_failure_count": len(hard_failures),
        "gates": [asdict(g) for g in gates],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# AISTAP Top-Readiness Self Check",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Overall: `{overall}`",
        f"- Hard failures: `{len(hard_failures)}`",
        "",
        "## Gate Table",
        "",
        "| Gate | Status | Hard | Evidence | Detail |",
        "|---|---:|---:|---|---|",
    ]
    for g in gates:
        evidence = g.evidence.replace("|", "/")
        detail = g.detail.replace("|", "/")
        lines.append(f"| {g.name} | `{g.status}` | `{str(g.hard).lower()}` | {evidence} | {detail} |")

    lines.extend(
        [
            "",
            "## CAS Q1 Top Interpretation",
            "",
        ]
    )
    if hard_failures:
        lines.append(
            "The current package is not yet at the CAS Q1 top threshold because at least one hard gate remains unproven."
        )
        lines.append(
            "Current hard failures: "
            + ", ".join(f"`{g.name}`" for g in hard_failures)
            + "."
        )
    else:
        lines.append("All hard gates passed. The package can be treated as top-readiness candidate evidence, pending manuscript-level review.")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "绗笁鎵?"))
    parser.add_argument("--power-root", default=str(Path.home() / "Desktop" / "power_se"))
    parser.add_argument("--battery-root", default=str(Path.home() / "Desktop" / "宸插畬鎴愰」鐩? / "閿傜數姹犳晠闅滄娴嬭鏂?))
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    root = Path(args.root)
    power_root = Path(args.power_root)
    battery_root = Path(args.battery_root)

    gates = [
        gate_reproducibility(root),
        gate_deployable_candidate(root),
        gate_target_frontier(root),
        gate_sample_size(root),
        gate_cross_condition(root),
        gate_external_aistap(root),
        gate_reference_superiority(root, power_root, battery_root),
        gate_classical_cfar_baseline_strength(root),
        gate_classical_cfar_parameter_sensitivity(root),
        gate_loso_learned_baseline(root),
        gate_feature_ensemble_boundary(root),
        gate_positive_pixel_label_efficiency(root),
        gate_label_cost_pareto(root),
        gate_target_free_calibration_boundary(root),
        gate_frame_level_robustness(root),
        gate_paired_significance_audit(root),
        gate_log_pfa_auc_surface(root),
        gate_component_attribution(root),
        gate_runtime_complexity_profile(root),
        gate_claim_consistency(root),
        gate_finished_detector(root),
    ]
    json_path, md_path = write_outputs(root, gates, args.date)
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

