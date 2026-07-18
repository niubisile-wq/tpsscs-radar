from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


MANUSCRIPT = Path("tgrs_tpsscs_final_package_20260716/manuscript/tgrs_tpsscs_nofig_20260715.tex")
CLAIM_FILES = [
    Path("README.md"),
    Path("STATUS.md"),
    Path("claim_matrix.md"),
    Path("logs/aistap_experimental_quality_assessment_20260717.md"),
    Path("logs/aistap_20260717_top_tier_manuscript_insert.md"),
    MANUSCRIPT,
]


@dataclass
class Check:
    name: str
    status: str
    severity: str
    detail: str
    evidence: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def normalize(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def context(text: str, start: int, end: int, width: int = 110) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    return text[left:right].strip()


def is_negated_or_bounded(snippet: str) -> bool:
    s = snippet.lower()
    boundary_terms = [
        "not ",
        "negative",
        "unsupported",
        "not justified",
        "should not",
        "cannot",
        "no ",
        "bounded",
        "boundary",
        "rather than",
        "instead of",
        "not as",
        "not a",
        "fails",
        "loses",
        "does not",
        "not fully",
        "without",
        "partial",
        "limited",
        "claims that",
        "needed before",
        "still needs",
        "different question",
        "failure",
        "low-label",
        "label-cost",
        "positive-pixel",
        "target pixels",
    ]
    return any(term in s for term in boundary_terms)


def required_phrase_check(name: str, files: list[Path], patterns: list[str], root: Path, detail: str) -> Check:
    found: list[str] = []
    missing: list[str] = []
    for pattern in patterns:
        matched = False
        for rel in files:
            text = read_text(root / rel)
            if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL):
                found.append(f"{rel}:{pattern}")
                matched = True
                break
        if not matched:
            missing.append(pattern)
    if missing:
        return Check(name, "fail", "hard", detail + "; missing patterns: " + " | ".join(missing), ", ".join(found))
    return Check(name, "pass", "info", detail, ", ".join(found))


def forbidden_overclaim_check(root: Path) -> Check:
    # These are only failures when they appear outside a negated/bounded context.
    forbidden_patterns = {
        "universal_or_sensor_agnostic_detector": r"\b(universal|sensor-agnostic|cross-sensor|cross-dataset)\b.{0,80}\b(detector|superiority|dominance|wins?)\b",
        "all_supervised_learned_dominance": r"\b(beat|beats|outperform|outperforms|dominates?|superior)\b.{0,120}\b(all|every)\s+(supervised|learned|HGB|detectors?)\b",
        "hgb_dominance_overclaim": r"\bcompact\s+TP-SSCS\b.{0,80}\b(beat|beats|outperform|outperforms|dominates?|superior)\b.{0,80}\b(raw/residual\s+HGB|HGB feature ensemble|strong supervised)\b",
        "target_free_full_calibration_overclaim": r"\btarget-free\b.{0,120}\b(fully|all|complete|guaranteed)\b.{0,80}\b(Pfa|P_FA|false-alarm|calibrat)",
        "universal_frame_level_raw_win": r"\b(every|all|universal)\b.{0,120}\b(frame|item-Pfa|target-bearing frame)\b.{0,120}\b(raw|raw maps)\b",
        "universal_gate_only_dominance": r"\b(finished detector|tpsscs_finished_detector|selected detector)\b.{0,120}\b(dominates|beats|outperforms)\b.{0,120}\b(gate-only|trainable gate)\b.{0,120}\b(all|every|universal)\b",
        "ipix_zero_shot_positive_overclaim": r"\bIPIX\b.{0,100}\b(zero-shot|direct transfer)\b.{0,80}\b(pass|passes|positive|wins?|successful)\b",
        "production_ready_overclaim": r"\b(production-ready|deployment-ready|deployable)\b.{0,80}\b(detector|system|claim|calibration)\b",
        "runtime_speed_overclaim": r"\b(real-time|hardware-independent|speed superiority)\b.{0,100}\b(proves|guarantees|universal|all hardware|claim)\b",
    }
    suspicious: list[dict[str, str]] = []
    for rel in CLAIM_FILES:
        text = normalize(read_text(root / rel))
        if not text:
            continue
        for name, pattern in forbidden_patterns.items():
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                snippet = context(text, match.start(), match.end())
                if is_negated_or_bounded(snippet):
                    continue
                suspicious.append({"file": str(rel), "pattern": name, "context": snippet})
    if suspicious:
        detail = "; ".join(f"{x['file']} [{x['pattern']}]: {x['context']}" for x in suspicious[:8])
        if len(suspicious) > 8:
            detail += f"; ... {len(suspicious) - 8} more"
        return Check("forbidden_overclaims", "fail", "hard", detail)
    return Check("forbidden_overclaims", "pass", "info", "no unbounded overclaim patterns found")


def json_gate_check(root: Path) -> list[Check]:
    checks: list[Check] = []
    paths = {
        "hgb_boundary": root / "results/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_20260717.json",
        "tpsscs_feature_hgb": root / "results/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.json",
        "low_positive_pixel": root / "results/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_20260717.json",
        "label_cost_pareto": root / "results/aistap_full_asset/aistap_full_asset_label_cost_pareto_20260717.json",
        "target_free_calibration": root / "results/aistap_full_asset/aistap_full_asset_target_free_calibration_20260717.json",
        "frame_level_robustness": root / "results/aistap_full_asset/aistap_full_asset_frame_level_robustness_20260717.json",
        "paired_significance": root / "results/aistap_full_asset/aistap_full_asset_paired_significance_20260717.json",
        "log_pfa_auc": root / "results/aistap_full_asset/aistap_full_asset_log_pfa_auc_20260717.json",
        "component_attribution": root / "results/aistap_full_asset/aistap_full_asset_component_attribution_20260717.json",
        "runtime_profile": root / "results/aistap_full_asset/aistap_runtime_profile_20260717.json",
        "top_readiness": root / "logs/aistap_top_readiness_self_check_20260717.json",
    }
    data: dict[str, Any] = {}
    for key, path in paths.items():
        if not path.exists():
            checks.append(Check(f"json:{key}", "fail", "hard", "missing JSON", str(path.relative_to(root))))
            continue
        try:
            data[key] = json.loads(path.read_text(encoding="utf-8"))
            checks.append(Check(f"json:{key}", "pass", "info", "JSON parsed", str(path.relative_to(root))))
        except Exception as exc:
            checks.append(Check(f"json:{key}", "fail", "hard", f"JSON parse error: {exc}", str(path.relative_to(root))))

    hgb = data.get("hgb_boundary", {})
    if hgb:
        ok = hgb.get("passed") is False and int(hgb.get("combined_wins_vs_learned", -1)) == 0
        checks.append(
            Check(
                "evidence:hgb_boundary_negative",
                "pass" if ok else "fail",
                "hard",
                f"raw/residual HGB boundary must be recorded as compact TP-SSCS loss; passed={hgb.get('passed')}, compact wins={hgb.get('combined_wins_vs_learned')}",
                "results/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_20260717.json",
            )
        )
    tps = data.get("tpsscs_feature_hgb", {})
    if tps:
        ok = (
            int(tps.get("combined_wins_vs_compact_tpsscs", 0)) == int(tps.get("combined_comparisons", -1))
            and tps.get("passed_gain_vs_raw_residual_hgb") is False
        )
        checks.append(
            Check(
                "evidence:tpsscs_feature_hgb_bounded",
                "pass" if ok else "fail",
                "hard",
                f"TP-SSCS-feature HGB must beat compact but not claim strict raw/residual HGB win; compact wins={tps.get('combined_wins_vs_compact_tpsscs')}, passed vs HGB={tps.get('passed_gain_vs_raw_residual_hgb')}",
                "results/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.json",
            )
        )
    low = data.get("low_positive_pixel", {})
    if low:
        needed = {"1", "2", "4", "8"}
        wins = {str(x) for x in low.get("compact_all_pfa_win_budgets", [])}
        first_catch = str(low.get("first_budget_where_hgb_catches_or_exceeds_compact_at_any_pfa"))
        ok = needed <= wins and first_catch == "16"
        checks.append(
            Check(
                "evidence:positive_pixel_boundary",
                "pass" if ok else "fail",
                "hard",
                f"low-label claim must be limited to budgets 1/2/4/8 with HGB catch at 16; wins={sorted(wins)}, first_catch={first_catch}",
                "results/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_20260717.json",
            )
        )
    pareto = data.get("label_cost_pareto", {})
    if pareto:
        needed = {"1", "2", "4", "8", "16"}
        dominated = {str(x) for x in pareto.get("compact_dominates_low_label_hgb_budgets_auc_runtime_labels", [])}
        ci_budgets = {str(x) for x in pareto.get("compact_auc_positive_ci_budgets", [])}
        boundary = set(pareto.get("boundary", []))
        first_exceed = str(pareto.get("first_budget_hgb_auc_exceeds_compact"))
        ratio = float(pareto.get("hgb_over_compact_runtime_ratio", float("nan")))
        compact_auc = float(pareto.get("compact_auc", float("nan")))
        full_hgb_auc = float(pareto.get("raw_residual_hgb_full_auc", float("nan")))
        ok = (
            int(pareto.get("target_bearing_items", 0)) >= 200
            and needed <= dominated
            and needed <= ci_budgets
            and first_exceed == "64"
            and ratio > 1.0
            and full_hgb_auc > compact_auc
            and "does_not_claim_superiority_over_full_label_hgb_boundary" in boundary
        )
        checks.append(
            Check(
                "evidence:label_cost_pareto_boundary",
                "pass" if ok else "fail",
                "hard",
                f"label-cost Pareto claim must be limited to low-label HGB budgets 1/2/4/8/16 and keep full-label HGB as boundary; dominated={sorted(dominated)}, ci_budgets={sorted(ci_budgets)}, first_exceed={first_exceed}, ratio={ratio}, compact_auc={compact_auc}, full_hgb_auc={full_hgb_auc}, boundary={sorted(boundary)}",
                "results/aistap_full_asset/aistap_full_asset_label_cost_pareto_20260717.json",
            )
        )
    tf = data.get("target_free_calibration", {})
    if tf:
        positive = set(tf.get("positive_delta_modes", []))
        calibrated = set(tf.get("pfa_calibrated_modes", []))
        passed = set(tf.get("passed_modes", []))
        ok = {"same_asset_target_free", "cross_asset_target_free"} <= positive and not calibrated and not passed
        checks.append(
            Check(
                "evidence:target_free_boundary",
                "pass" if ok else "fail",
                "hard",
                f"target-free audit must be positive-delta but not fully calibrated; positive={sorted(positive)}, calibrated={sorted(calibrated)}, passed={sorted(passed)}",
                "results/aistap_full_asset/aistap_full_asset_target_free_calibration_20260717.json",
            )
        )
    frame = data.get("frame_level_robustness", {})
    if frame:
        pairs = int(frame.get("item_pfa_pairs_per_comparator", 0))
        lowrank_losses = int(frame.get("lowrank_loss_item_pfa_pairs", -1))
        lowrank_nonnegative = int(frame.get("lowrank_nonnegative_item_pfa_pairs", 0))
        raw_losses = int(frame.get("raw_loss_item_pfa_pairs", 0))
        raw_min_win = float(frame.get("combined_raw_min_win_fraction", float("nan")))
        boundary = set(frame.get("boundary", []))
        ok = (
            frame.get("broad_frame_level_support") is True
            and pairs >= 1400
            and lowrank_losses == 0
            and lowrank_nonnegative == pairs
            and raw_losses > 0
            and raw_min_win >= 0.85
            and "raw_comparison_has_some_negative_item_pfa_pairs_and_should_be_reported_as_broad_not_universal" in boundary
        )
        checks.append(
            Check(
                "evidence:frame_level_robustness_boundary",
                "pass" if ok else "fail",
                "hard",
                f"frame-level audit must show no low-rank losses and bounded raw support; pairs={pairs}, lowrank_losses={lowrank_losses}, raw_losses={raw_losses}, raw_min_win={raw_min_win}, boundary={sorted(boundary)}",
                "results/aistap_full_asset/aistap_full_asset_frame_level_robustness_20260717.json",
            )
        )
    paired = data.get("paired_significance", {})
    if paired:
        max_q = float(paired.get("max_combined_bh_q", float("nan")))
        min_effect = float(paired.get("min_combined_matched_sign_effect", float("nan")))
        boundary = set(paired.get("boundary", []))
        ok = (
            paired.get("all_combined_significant_bh_0p05") is True
            and paired.get("lowrank_all_combined_significant_bh_0p05") is True
            and paired.get("raw_all_combined_significant_bh_0p05") is True
            and int(paired.get("target_bearing_items", 0)) >= 200
            and int(paired.get("combined_tests_total", 0)) >= 14
            and max_q < 0.05
            and min_effect >= 0.75
            and "paired_sign_test_excludes_ties" in boundary
            and "does_not_claim_universal_per_frame_raw_dominance" in boundary
        )
        checks.append(
            Check(
                "evidence:paired_significance_boundary",
                "pass" if ok else "fail",
                "hard",
                f"paired significance audit must pass all combined BH-FDR tests and keep sign-test boundaries; max_q={max_q}, min_effect={min_effect}, boundary={sorted(boundary)}",
                "results/aistap_full_asset/aistap_full_asset_paired_significance_20260717.json",
            )
        )
    auc = data.get("log_pfa_auc", {})
    if auc:
        min_delta = float(auc.get("min_combined_delta_auc", float("nan")))
        min_ci_low = float(auc.get("min_combined_ci95_low", float("nan")))
        max_q = float(auc.get("max_combined_bh_q", float("nan")))
        boundary = set(auc.get("boundary", []))
        ok = (
            auc.get("combined_auc_positive_vs_all") is True
            and auc.get("combined_bootstrap_ci_positive_vs_all") is True
            and auc.get("combined_significant_bh_vs_all") is True
            and int(auc.get("target_bearing_items", 0)) >= 200
            and int(auc.get("pfa_points", 0)) >= 7
            and min_delta > 0.0
            and min_ci_low > 0.0
            and max_q < 0.05
            and "auc_integrates_checked_pfa_grid_only" in boundary
            and "paired_bootstrap_unit_is_target_bearing_frame" in boundary
        )
        checks.append(
            Check(
                "evidence:log_pfa_auc_boundary",
                "pass" if ok else "fail",
                "hard",
                f"log-Pfa AUC audit must show positive whole-surface deltas with frame-level CI and checked-range boundary; min_delta={min_delta}, min_ci_low={min_ci_low}, max_q={max_q}, boundary={sorted(boundary)}",
                "results/aistap_full_asset/aistap_full_asset_log_pfa_auc_20260717.json",
            )
        )
    component = data.get("component_attribution", {})
    if component:
        boundary = set(component.get("boundary", []))
        auc_rows = component.get("auc_summary", [])
        combined = {row.get("comparator"): row for row in auc_rows if row.get("asset") == "combined"}
        raw_delta = float(combined.get("raw", {}).get("mean_delta_auc", float("nan")))
        lowrank_delta = float(combined.get("low_rank_residual_k30", {}).get("mean_delta_auc", float("nan")))
        lowrank_losses = int(combined.get("low_rank_residual_k30", {}).get("losses", -1))
        gate_ci_positive = bool(combined.get("tpsscs_trainable_gate", {}).get("positive_bootstrap_ci", True))
        ok = (
            component.get("raw_auc_delta_positive") is True
            and component.get("lowrank_auc_nonnegative_all_frames") is True
            and component.get("gate_only_boundary_present") is True
            and int(component.get("target_bearing_items", 0)) >= 200
            and raw_delta > 0.0
            and lowrank_delta > 0.0
            and lowrank_losses == 0
            and gate_ci_positive is False
            and "gate_only_is_relaxed_endpoint_not_selected_low_false_alarm_policy" in boundary
        )
        checks.append(
            Check(
                "evidence:component_attribution_boundary",
                "pass" if ok else "fail",
                "hard",
                f"component attribution must show raw/low-rank AUC gains and keep gate-only as a bounded relaxed endpoint; raw_delta={raw_delta}, lowrank_delta={lowrank_delta}, lowrank_losses={lowrank_losses}, gate_ci_positive={gate_ci_positive}, boundary={sorted(boundary)}",
                "results/aistap_full_asset/aistap_full_asset_component_attribution_20260717.json",
            )
        )
    runtime = data.get("runtime_profile", {})
    if runtime:
        frames = int(runtime.get("timed_target_frames_total", 0))
        ratio = float(runtime.get("hgb_over_compact_runtime_ratio", float("nan")))
        boundary = set(runtime.get("boundary", []))
        ok = frames >= 10 and ratio >= 1.0 and "does_not_claim_universal_real_time_performance" in boundary
        checks.append(
            Check(
                "evidence:runtime_profile_boundary",
                "pass" if ok else "fail",
                "hard",
                f"runtime claim must be local CPU and bounded; frames={frames}, ratio={ratio}, boundary={sorted(boundary)}",
                "results/aistap_full_asset/aistap_runtime_profile_20260717.json",
            )
        )
    top = data.get("top_readiness", {})
    if top:
        gates = {g.get("name"): g for g in top.get("gates", [])}
        expected = {
            "feature_ensemble_boundary": "partial",
            "positive_pixel_label_efficiency": "pass",
            "label_cost_pareto": "pass",
            "target_free_calibration_boundary": "partial",
            "frame_level_robustness": "pass",
            "paired_significance_audit": "pass",
            "log_pfa_auc_surface": "pass",
            "component_attribution_audit": "pass",
            "runtime_complexity_profile": "pass",
        }
        missing_or_wrong = [
            f"{name}={gates.get(name, {}).get('status')}" for name, status in expected.items() if gates.get(name, {}).get("status") != status
        ]
        ok = top.get("overall") == "top_ready" and int(top.get("hard_failure_count", -1)) == 0 and not missing_or_wrong
        checks.append(
            Check(
                "evidence:top_readiness_gate_status",
                "pass" if ok else "fail",
                "hard",
                f"overall={top.get('overall')}; hard_failure_count={top.get('hard_failure_count')}; gate mismatches={missing_or_wrong}",
                "logs/aistap_top_readiness_self_check_20260717.json",
            )
        )
    return checks


def run_audit(root: Path) -> dict[str, Any]:
    checks: list[Check] = []
    for rel in CLAIM_FILES:
        path = root / rel
        checks.append(
            Check(
                f"file:{rel.as_posix()}",
                "pass" if path.exists() and path.stat().st_size > 0 else "fail",
                "hard",
                f"{path.stat().st_size} bytes" if path.exists() else "missing",
                rel.as_posix(),
            )
        )

    checks.append(
        required_phrase_check(
            "required:hgb_negative_boundary",
            [MANUSCRIPT, Path("README.md"), Path("claim_matrix.md")],
            [r"raw/residual\s+HGB.*(exceeds|beats).*compact\s+TP-SSCS", r"not\s+(be\s+)?(described|claim(ed)?)\s+as\s+superior\s+to\s+all\s+supervised|not\s+a\s+blanket\s+replacement"],
            root,
            "HGB upper-bound failure must be stated and bounded",
        )
    )
    checks.append(
        required_phrase_check(
            "required:positive_pixel_label_boundary",
            [MANUSCRIPT, Path("README.md"), Path("claim_matrix.md")],
            [r"1,?\s*2,?\s*4,?\s*(and|or|,)\s*8\s+positive|1`,\s*`2`,\s*`4`,?\s*(and|,)\s*`8`", r"16\s+positive\s+(target\s+)?pixels?.*(catch|exceed|competitive)"],
            root,
            "positive-pixel label-efficiency claim must include winning and catch-up budgets",
        )
    )
    checks.append(
        required_phrase_check(
            "required:label_cost_pareto_boundary",
            [MANUSCRIPT, Path("README.md"), Path("claim_matrix.md")],
            [
                r"label-cost\s+Pareto.*(1/2/4/8/16|1,?\s*2,?\s*4,?\s*8,?\s*(and|,)?\s*16|1`,\s*`2`,\s*`4`,\s*`8`,?\s*(and|,)\s*`16`)",
                r"HGB.*64.*(exceeds|exceed|higher|above).*compact|64.*HGB.*(exceeds|exceed|higher|above).*compact",
                r"full-label\s+HGB.*(boundary|not)|not.*full-label\s+HGB|does\s+not\s+claim.*full-label",
            ],
            root,
            "label-cost Pareto claim must report low-label budgets, HGB crossover budget, and full-label HGB boundary",
        )
    )
    checks.append(
        required_phrase_check(
            "required:target_free_calibration_boundary",
            [MANUSCRIPT, Path("README.md"), Path("claim_matrix.md")],
            [r"target-free.*(positive|preserve).*margin|target-free.*7/7", r"not\s+fully\s+.*(Pfa|P_FA|false-alarm).*calibrat|do\s+not\s+fully\s+preserve\s+empirical"],
            root,
            "target-free calibration must be framed as ordering robustness plus Pfa-transfer boundary",
        )
    )
    checks.append(
        required_phrase_check(
            "required:frame_level_robustness_boundary",
            [MANUSCRIPT, Path("README.md"), Path("claim_matrix.md")],
            [
                r"1470/1470.*(low_rank_residual_k30|low-rank|rank-matched)|((low_rank_residual_k30|low-rank|rank-matched).*)1470/1470",
                r"raw.*(broad\s+but\s+not\s+universal|raw-favorable|61)|not\s+universal.*raw",
            ],
            root,
            "frame-level robustness must include low-rank no-loss evidence and bounded raw-frame wording",
        )
    )
    checks.append(
        required_phrase_check(
            "required:paired_significance_boundary",
            [MANUSCRIPT, Path("README.md"), Path("claim_matrix.md")],
            [
                r"(BH-FDR|FDR).*2\.945e-29|2\.945e-29.*(BH-FDR|FDR)",
                r"(sign\s+test|matched\s+sign).*0\.816|0\.816.*(sign\s+effect|matched\s+sign)",
                r"sign\s+test.*(excludes|ignores)\s+ties|ties.*(excluded|ignored).*sign\s+test",
            ],
            root,
            "paired significance audit must report corrected significance, effect size, and tie-handling boundary",
        )
    )
    checks.append(
        required_phrase_check(
            "required:log_pfa_auc_boundary",
            [MANUSCRIPT, Path("README.md"), Path("claim_matrix.md")],
            [
                r"log-Pfa\s+AUC.*0\.0553|0\.0553.*log-Pfa\s+AUC",
                r"(CI|bootstrap).*0\.0491|0\.0491.*(CI|bootstrap)",
                r"checked\s+Pfa\s+range|checked\s+Pfa\s+grid|1e-5\s+to\s+1e-2",
            ],
            root,
            "log-Pfa AUC audit must report whole-surface delta, CI, and checked-Pfa boundary",
        )
    )
    checks.append(
        required_phrase_check(
            "required:component_attribution_boundary",
            [MANUSCRIPT, Path("README.md"), Path("claim_matrix.md")],
            [
                r"component-attribution.*0\.0553|0\.0553.*component-attribution|AUC.*0\.0553.*low-rank",
                r"gate-only.*(boundary|relaxed|looser Pfa|not.*universal)|trainable gate.*(boundary|relaxed|looser Pfa|not.*universal)",
            ],
            root,
            "component attribution must report low-rank AUC gain and gate-only boundary",
        )
    )
    checks.append(
        required_phrase_check(
            "required:runtime_boundary",
            [MANUSCRIPT, Path("README.md"), Path("claim_matrix.md")],
            [r"(CPU|runtime).*133\.66|133\.66.*(CPU|runtime)", r"not\s+(a\s+)?hardware-independent|not\s+(a\s+)?real-time|hardware-independent\s+speed\s+claims?\s+remain\s+out\s+of\s+scope"],
            root,
            "runtime/complexity claim must include local CPU evidence and hardware-independent boundary",
        )
    )
    checks.append(
        required_phrase_check(
            "required:external_boundary",
            [MANUSCRIPT, Path("README.md"), Path("claim_matrix.md")],
            [r"IPIX.*zero-shot.*negative|negative\s+IPIX\s+zero-shot", r"SSDD.*supervised.*adaptation|supervised\s+SSDD\s+adaptation"],
            root,
            "external results must separate negative zero-shot IPIX from supervised/validated adaptation",
        )
    )

    checks.append(forbidden_overclaim_check(root))
    checks.extend(json_gate_check(root))

    hard_failures = [c for c in checks if c.status == "fail" and c.severity == "hard"]
    warnings = [c for c in checks if c.status == "warn"]
    verdict = "claim_consistent" if not hard_failures else "claim_inconsistent"
    return {
        "date": datetime.now().strftime("%Y%m%d"),
        "verdict": verdict,
        "hard_failure_count": len(hard_failures),
        "warning_count": len(warnings),
        "checks": [asdict(c) for c in checks],
    }


def write_outputs(root: Path, report: dict[str, Any], date_tag: str) -> tuple[Path, Path]:
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    json_path = log_dir / f"aistap_claim_consistency_audit_{date_tag}.json"
    md_path = log_dir / f"aistap_claim_consistency_audit_{date_tag}.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# AISTAP Claim Consistency Audit",
        "",
        f"Date: {date_tag}",
        f"Verdict: `{report['verdict']}`",
        "",
        "## Summary",
        "",
        f"- Hard failures: `{report['hard_failure_count']}`",
        f"- Warnings: `{report['warning_count']}`",
        "",
        "## Failed Checks",
        "",
    ]
    failed = [c for c in report["checks"] if c["status"] == "fail"]
    if failed:
        lines.extend(f"- `{c['name']}` ({c['severity']}): {c['detail']}" for c in failed)
    else:
        lines.append("- None.")
    lines.extend(["", "## Passed Checks", ""])
    passed = [c for c in report["checks"] if c["status"] == "pass"]
    lines.extend(f"- `{c['name']}`: {c['detail']}" for c in passed)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()
    root = Path(args.root).resolve()
    report = run_audit(root)
    report["date"] = args.date
    json_path, md_path = write_outputs(root, report, args.date)
    print(json.dumps({k: report[k] for k in ["verdict", "hard_failure_count", "warning_count"]}, indent=2))
    print(json_path)
    print(md_path)
    return 0 if report["hard_failure_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
