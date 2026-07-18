from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


DATE = "20260717"
PACKAGE_NAME = "tgrs_tpsscs_final_package_20260716"
MANUSCRIPT_STEM = "tgrs_tpsscs_nofig_20260715"


EXPECTED_FIGURES = [
    "figures/submitted/figure1_paradigm_shift.png",
    "figures/submitted/figure7_official_full_asset_validation_20260716.pdf",
    "figures/submitted/figure7_official_full_asset_validation_20260716.png",
    "figures/submitted/figure7_official_full_asset_validation_20260716.svg",
]

EXPECTED_SOURCE_DATA = [
    "source_data/aistap_full_asset/aistap_combined_full_asset_protocol_20260715.csv",
    "source_data/aistap_full_asset/aistap_combined_full_asset_bootstrap_ci_20260715.csv",
    "source_data/aistap_sample/aistap_lowrank_k1_2_3_5_8_10_15_20_30_baseline.csv",
    "source_data/aistap_sample/aistap_target_preservation_ablation_20260713.csv",
    "source_data/ipix_external/ipix_validated_residual_fusion_test_20260715.csv",
    "source_data/ipix_external/ipix_heldout_bootstrap_delta_ci_20260715.csv",
    "source_data/ssdd_external/ssdd_external_trainable_gate_20260715.csv",
    "source_data/ssdd_external/ssdd_image_annotation_bootstrap_ci_20260715.csv",
    "source_data/aistap_full_asset/aistap_full_asset_seed_sensitivity_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_seed_sensitivity_summary_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_seed_sensitivity_by_pfa_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_seed_sensitivity_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_classical_cfar_baselines_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_classical_cfar_baselines_summary_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_classical_cfar_best_comparison_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_classical_cfar_baselines_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_classical_cfar_param_sweep_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_classical_cfar_param_sweep_summary_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_classical_cfar_param_sweep_best_comparison_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_classical_cfar_param_sweep_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_loso_learned_raw_baseline_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_learned_raw_baseline_comparison_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_learned_raw_baseline_bootstrap_ci_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_learned_raw_baseline_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_comparison_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_bootstrap_ci_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_comparison_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_bootstrap_ci_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_comparison_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_bootstrap_ci_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_label_cost_pareto_frame_auc_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_label_cost_pareto_budget_auc_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_label_cost_pareto_points_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_label_cost_pareto_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_target_free_calibration_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_target_free_calibration_comparison_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_target_free_calibration_bootstrap_ci_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_target_free_calibration_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_frame_level_robustness_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_frame_level_robustness_summary_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_frame_level_robustness_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_paired_significance_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_paired_significance_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_log_pfa_auc_frames_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_log_pfa_auc_deltas_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_log_pfa_auc_summary_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_log_pfa_auc_20260717.json",
    "source_data/aistap_full_asset/aistap_full_asset_component_attribution_operating_summary_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_component_attribution_pfa_deltas_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_component_attribution_pfa_summary_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_component_attribution_frame_auc_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_component_attribution_auc_deltas_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_component_attribution_auc_summary_20260717.csv",
    "source_data/aistap_full_asset/aistap_full_asset_component_attribution_20260717.json",
    "source_data/aistap_full_asset/aistap_runtime_profile_components_20260717.csv",
    "source_data/aistap_full_asset/aistap_runtime_profile_totals_20260717.csv",
    "source_data/aistap_full_asset/aistap_runtime_profile_frames_20260717.csv",
    "source_data/aistap_full_asset/aistap_runtime_profile_summary_20260717.csv",
    "source_data/aistap_full_asset/aistap_runtime_profile_20260717.json",
]

EXPECTED_SCRIPTS = [
    "scripts/plot_submission_figures_20260715.py",
    "scripts/evaluate_aistap_combined_full_asset_protocol.py",
    "scripts/evaluate_aistap_target_preservation_ablation.py",
    "scripts/evaluate_aistap_sample_cfar.py",
    "scripts/evaluate_aistap_lowrank_baseline.py",
    "scripts/evaluate_ssdd_image_level_bootstrap_ci.py",
    "scripts/evaluate_aistap_full_asset_seed_sensitivity.py",
    "scripts/evaluate_aistap_full_asset_classical_cfar_baselines.py",
    "scripts/evaluate_aistap_full_asset_classical_cfar_param_sweep.py",
    "scripts/evaluate_aistap_full_asset_loso_learned_raw_baseline.py",
    "scripts/evaluate_aistap_full_asset_loso_feature_ensemble_baseline.py",
    "scripts/evaluate_aistap_full_asset_loso_tpsscs_feature_ensemble.py",
    "scripts/evaluate_aistap_full_asset_loso_low_label_hgb.py",
    "scripts/evaluate_aistap_full_asset_label_cost_pareto.py",
    "scripts/evaluate_aistap_full_asset_target_free_calibration.py",
    "scripts/evaluate_aistap_full_asset_frame_level_robustness.py",
    "scripts/evaluate_aistap_full_asset_paired_significance.py",
    "scripts/evaluate_aistap_full_asset_operating_surface_auc.py",
    "scripts/evaluate_aistap_full_asset_component_attribution.py",
    "scripts/evaluate_aistap_runtime_profile.py",
    "scripts/evaluate_aistap_top_readiness.py",
    "scripts/audit_aistap_claim_consistency.py",
]

EXPECTED_LOGS = [
    "logs/aistap_submission_figures_20260715.md",
    "logs/tgrs_quant_table_figure_insertion_20260716.md",
    "logs/aistap_combined_full_asset_protocol_20260715.md",
    "logs/aistap_results_methods_discussion_insert_20260715.md",
    "logs/aistap_manuscript_submission_package_20260715.md",
    "logs/aistap_target_preservation_ablation_20260713.md",
    "logs/aistap_full_asset_seed_sensitivity_20260717.md",
    "logs/aistap_top_readiness_self_check_20260717.md",
    "logs/aistap_top_readiness_self_check_20260717.json",
    "logs/aistap_experimental_quality_assessment_20260717.md",
    "logs/aistap_full_asset_classical_cfar_baselines_20260717.md",
    "logs/aistap_full_asset_classical_cfar_param_sweep_20260717.md",
    "logs/aistap_full_asset_loso_learned_raw_baseline_20260717.md",
    "logs/aistap_full_asset_loso_feature_ensemble_baseline_20260717.md",
    "logs/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.md",
    "logs/aistap_full_asset_loso_low_positive_pixel_hgb_20260717.md",
    "logs/aistap_full_asset_label_cost_pareto_20260717.md",
    "logs/aistap_full_asset_target_free_calibration_20260717.md",
    "logs/aistap_full_asset_frame_level_robustness_20260717.md",
    "logs/aistap_full_asset_paired_significance_20260717.md",
    "logs/aistap_full_asset_log_pfa_auc_20260717.md",
    "logs/aistap_full_asset_component_attribution_20260717.md",
    "logs/aistap_runtime_profile_20260717.md",
    "logs/aistap_claim_consistency_audit_20260717.md",
    "logs/aistap_claim_consistency_audit_20260717.json",
    "logs/aistap_supplementary_experiment_priority_20260715.md",
    "logs/aistap_20260717_top_tier_manuscript_insert.md",
]

PLACEHOLDER_PATTERNS = {
    "author_name_placeholder": r"\bAuthor~?Name\b",
    "email_placeholder": r"author@example\.com",
    "journal_issue_placeholder": r"Vol\.~XX|No\.~XX",
    "insert_before_submission": r"inserted before submission|insert .* before submission|should insert",
    "generic_data_availability": r"Local outputs and logs are stored under the project",
    "generic_code_availability": r"Scripts for AISTAP-SIM validation.*project README",
}

LATEX_BLOCKERS = {
    "undefined_references": r"undefined references|undefined citations|Citation .* undefined|Reference .* undefined",
    "overfull_boxes": r"Overfull",
    "float_too_large": r"Float too large",
    "underfull_vbox": r"Underfull \\vbox",
}


@dataclass
class Check:
    name: str
    status: str
    detail: str
    severity: str = "info"


def exists_nonempty(base: Path, rel_path: str) -> Check:
    path = base / rel_path
    if path.exists() and path.is_file() and path.stat().st_size > 0:
        return Check(rel_path, "pass", f"{path.stat().st_size} bytes")
    if path.exists() and path.is_file():
        return Check(rel_path, "fail", "file exists but is empty", "hard")
    return Check(rel_path, "fail", "missing", "hard")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def imported_graphics(tex: str) -> list[str]:
    matches = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex)
    return [m.replace("\\", "/") for m in matches if "#" not in m]


def relative_to_package(path: Path, package_dir: Path) -> str:
    try:
        return path.relative_to(package_dir).as_posix()
    except ValueError:
        return path.as_posix()


def check_graphics(tex_path: Path, package_dir: Path, tex: str) -> list[Check]:
    checks: list[Check] = []
    for graphic in imported_graphics(tex):
        candidate = (tex_path.parent / graphic).resolve()
        rel = relative_to_package(candidate, package_dir)
        if candidate.exists() and candidate.stat().st_size > 0:
            checks.append(Check(f"imported_graphic:{graphic}", "pass", rel))
        elif candidate.exists():
            checks.append(Check(f"imported_graphic:{graphic}", "fail", f"{rel} is empty", "hard"))
        else:
            checks.append(Check(f"imported_graphic:{graphic}", "fail", f"{rel} missing", "hard"))
    return checks


def manuscript_page_count(log_text: str) -> int | None:
    match = re.search(r"Output written on .*?\((\d+) pages?,", log_text)
    if not match:
        return None
    return int(match.group(1))


def load_top_readiness(root: Path) -> Check:
    path = root / "logs/aistap_top_readiness_self_check_20260717.json"
    if not path.exists():
        return Check("top_readiness_json", "fail", "missing top-readiness JSON", "hard")
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        return Check("top_readiness_json", "fail", f"invalid JSON: {exc}", "hard")
    overall = data.get("overall")
    hard_failures = data.get("hard_failure_count")
    if overall == "top_ready" and hard_failures == 0:
        return Check("top_readiness_json", "pass", "overall=top_ready; hard_failure_count=0")
    return Check(
        "top_readiness_json",
        "fail",
        f"overall={overall}; hard_failure_count={hard_failures}",
        "hard",
    )


def audit() -> dict:
    root = Path(__file__).resolve().parents[1]
    package_dir = root / PACKAGE_NAME
    manuscript_dir = package_dir / "manuscript"
    tex_path = manuscript_dir / f"{MANUSCRIPT_STEM}.tex"
    pdf_path = manuscript_dir / f"{MANUSCRIPT_STEM}.pdf"
    log_path = manuscript_dir / f"{MANUSCRIPT_STEM}.log"

    checks: list[Check] = []
    checks.extend(
        [
            exists_nonempty(package_dir, "README_PRE_SUBMISSION.md"),
            exists_nonempty(package_dir, f"manuscript/{MANUSCRIPT_STEM}.tex"),
            exists_nonempty(package_dir, f"manuscript/{MANUSCRIPT_STEM}.pdf"),
            exists_nonempty(package_dir, f"manuscript/{MANUSCRIPT_STEM}.log"),
        ]
    )

    for rel_path in EXPECTED_FIGURES:
        checks.append(exists_nonempty(package_dir, rel_path))
    for rel_path in EXPECTED_SOURCE_DATA:
        checks.append(exists_nonempty(package_dir, rel_path))
    for rel_path in EXPECTED_SCRIPTS:
        checks.append(exists_nonempty(package_dir, rel_path))
    for rel_path in EXPECTED_LOGS:
        checks.append(exists_nonempty(package_dir, rel_path))

    tex = read_text(tex_path)
    log_text = read_text(log_path)

    checks.extend(check_graphics(tex_path, package_dir, tex))

    manuscript_extra_files = sorted(
        p.name
        for p in manuscript_dir.iterdir()
        if p.is_file() and p.suffix.lower() not in {".tex", ".pdf", ".log"}
    )
    if manuscript_extra_files:
        checks.append(
            Check(
                "manuscript_folder_cleanliness",
                "warn",
                "extra files: " + ", ".join(manuscript_extra_files),
                "soft",
            )
        )
    else:
        checks.append(Check("manuscript_folder_cleanliness", "pass", "only TEX/PDF/LOG files"))

    pages = manuscript_page_count(log_text)
    if pages is None:
        checks.append(Check("compiled_pdf_page_count", "warn", "page count not found in log", "soft"))
    elif pages <= 12:
        checks.append(Check("compiled_pdf_page_count", "pass", f"{pages} pages"))
    else:
        checks.append(Check("compiled_pdf_page_count", "warn", f"{pages} pages", "soft"))

    for name, pattern in LATEX_BLOCKERS.items():
        hit = re.search(pattern, log_text, flags=re.IGNORECASE)
        if hit:
            checks.append(Check(f"latex_log:{name}", "fail", f"matched `{hit.group(0)}`", "hard"))
        else:
            checks.append(Check(f"latex_log:{name}", "pass", "not found"))

    metadata_hits = []
    for name, pattern in PLACEHOLDER_PATTERNS.items():
        hits = re.findall(pattern, tex, flags=re.IGNORECASE | re.DOTALL)
        if hits:
            checks.append(
                Check(
                    f"metadata_placeholder:{name}",
                    "fail",
                    f"{len(hits)} match(es)",
                    "submission",
                )
            )
            metadata_hits.append(name)
        else:
            checks.append(Check(f"metadata_placeholder:{name}", "pass", "not found"))

    checks.append(load_top_readiness(root))

    hard_failures = [c for c in checks if c.status == "fail" and c.severity == "hard"]
    submission_blockers = [c for c in checks if c.status == "fail" and c.severity == "submission"]
    warnings = [c for c in checks if c.status == "warn"]

    if hard_failures:
        verdict = "not_submission_ready_hard_failures"
    elif submission_blockers:
        verdict = "technically_complete_metadata_blocked"
    elif warnings:
        verdict = "submission_ready_with_warnings"
    else:
        verdict = "submission_ready"

    return {
        "date": DATE,
        "root": str(root),
        "package": str(package_dir),
        "verdict": verdict,
        "hard_failure_count": len(hard_failures),
        "submission_blocker_count": len(submission_blockers),
        "warning_count": len(warnings),
        "page_count": pages,
        "metadata_blockers": metadata_hits,
        "checks": [c.__dict__ for c in checks],
    }


def write_outputs(report: dict) -> None:
    root = Path(report["root"])
    output_dirs = [root / "logs", root / PACKAGE_NAME / "logs"]
    for logs_dir in output_dirs:
        logs_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# TGRS Submission Readiness Audit",
        "",
        f"Date: {DATE}",
        f"Package: `{report['package']}`",
        f"Verdict: `{report['verdict']}`",
        "",
        "## Summary",
        "",
        f"- Hard file/build failures: {report['hard_failure_count']}",
        f"- Submission metadata blockers: {report['submission_blocker_count']}",
        f"- Warnings: {report['warning_count']}",
        f"- Compiled page count: {report['page_count']}",
        "",
        "## Interpretation",
        "",
    ]

    if report["verdict"] == "technically_complete_metadata_blocked":
        lines.extend(
            [
                "The experiment and manuscript package passes the technical file/build audit.",
                "Formal submission is still blocked by author, affiliation, funding, acknowledgment, and public data/code availability placeholders.",
            ]
        )
    elif report["verdict"] == "submission_ready":
        lines.append("The package has no detected hard, metadata, or warning blockers.")
    elif report["hard_failure_count"]:
        lines.append("The package is not ready because at least one required file/build check failed.")
    else:
        lines.append("The package has no hard failures but still has warnings to review.")

    lines.extend(
        [
            "",
            "## Submission Blockers",
            "",
        ]
    )
    blockers = [c for c in report["checks"] if c["status"] == "fail" and c["severity"] == "submission"]
    if blockers:
        lines.extend(f"- `{c['name']}`: {c['detail']}" for c in blockers)
    else:
        lines.append("- None detected.")

    lines.extend(["", "## Hard Failures", ""])
    hard_failures = [c for c in report["checks"] if c["status"] == "fail" and c["severity"] == "hard"]
    if hard_failures:
        lines.extend(f"- `{c['name']}`: {c['detail']}" for c in hard_failures)
    else:
        lines.append("- None detected.")

    lines.extend(["", "## Warnings", ""])
    warnings = [c for c in report["checks"] if c["status"] == "warn"]
    if warnings:
        lines.extend(f"- `{c['name']}`: {c['detail']}" for c in warnings)
    else:
        lines.append("- None detected.")

    lines.extend(["", "## Passed Evidence Checks", ""])
    passed = [c for c in report["checks"] if c["status"] == "pass"]
    lines.extend(f"- `{c['name']}`: {c['detail']}" for c in passed)

    for logs_dir in output_dirs:
        json_path = logs_dir / f"tgrs_submission_readiness_audit_{DATE}.json"
        md_path = logs_dir / f"tgrs_submission_readiness_audit_{DATE}.md"
        json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8-sig")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    report = audit()
    write_outputs(report)
    print(json.dumps({k: report[k] for k in ["verdict", "hard_failure_count", "submission_blocker_count", "warning_count", "page_count"]}, indent=2))


if __name__ == "__main__":
    main()
