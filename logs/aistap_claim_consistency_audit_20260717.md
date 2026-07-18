# AISTAP Claim Consistency Audit

Date: 20260717
Verdict: `claim_consistent`

## Summary

- Hard failures: `0`
- Warnings: `0`

## Failed Checks

- None.

## Passed Checks

- `file:README.md`: 41011 bytes
- `file:STATUS.md`: 43288 bytes
- `file:claim_matrix.md`: 26668 bytes
- `file:logs/aistap_experimental_quality_assessment_20260717.md`: 11051 bytes
- `file:logs/aistap_20260717_top_tier_manuscript_insert.md`: 26523 bytes
- `file:tgrs_tpsscs_final_package_20260716/manuscript/tgrs_tpsscs_nofig_20260715.tex`: 79792 bytes
- `required:hgb_negative_boundary`: HGB upper-bound failure must be stated and bounded
- `required:positive_pixel_label_boundary`: positive-pixel label-efficiency claim must include winning and catch-up budgets
- `required:label_cost_pareto_boundary`: label-cost Pareto claim must report low-label budgets, HGB crossover budget, and full-label HGB boundary
- `required:target_free_calibration_boundary`: target-free calibration must be framed as ordering robustness plus Pfa-transfer boundary
- `required:frame_level_robustness_boundary`: frame-level robustness must include low-rank no-loss evidence and bounded raw-frame wording
- `required:paired_significance_boundary`: paired significance audit must report corrected significance, effect size, and tie-handling boundary
- `required:log_pfa_auc_boundary`: log-Pfa AUC audit must report whole-surface delta, CI, and checked-Pfa boundary
- `required:component_attribution_boundary`: component attribution must report low-rank AUC gain and gate-only boundary
- `required:runtime_boundary`: runtime/complexity claim must include local CPU evidence and hardware-independent boundary
- `required:external_boundary`: external results must separate negative zero-shot IPIX from supervised/validated adaptation
- `forbidden_overclaims`: no unbounded overclaim patterns found
- `json:hgb_boundary`: JSON parsed
- `json:tpsscs_feature_hgb`: JSON parsed
- `json:low_positive_pixel`: JSON parsed
- `json:label_cost_pareto`: JSON parsed
- `json:target_free_calibration`: JSON parsed
- `json:frame_level_robustness`: JSON parsed
- `json:paired_significance`: JSON parsed
- `json:log_pfa_auc`: JSON parsed
- `json:component_attribution`: JSON parsed
- `json:runtime_profile`: JSON parsed
- `json:top_readiness`: JSON parsed
- `evidence:hgb_boundary_negative`: raw/residual HGB boundary must be recorded as compact TP-SSCS loss; passed=False, compact wins=0
- `evidence:tpsscs_feature_hgb_bounded`: TP-SSCS-feature HGB must beat compact but not claim strict raw/residual HGB win; compact wins=7, passed vs HGB=False
- `evidence:positive_pixel_boundary`: low-label claim must be limited to budgets 1/2/4/8 with HGB catch at 16; wins=['1', '2', '4', '8'], first_catch=16
- `evidence:label_cost_pareto_boundary`: label-cost Pareto claim must be limited to low-label HGB budgets 1/2/4/8/16 and keep full-label HGB as boundary; dominated=['1', '16', '2', '4', '8'], ci_budgets=['1', '16', '2', '4', '8'], first_exceed=64, ratio=4.556429818969869, compact_auc=0.5313080161181634, full_hgb_auc=0.7156040756556384, boundary=['does_not_claim_superiority_over_full_label_hgb_boundary', 'local_cpu_runtime_not_hardware_independent', 'pareto_scope_official_aistap_full_assets_checked_pfa_grid', 'uses_existing_frozen_low_label_hgb_outputs']
- `evidence:target_free_boundary`: target-free audit must be positive-delta but not fully calibrated; positive=['cross_asset_target_free', 'same_asset_target_free'], calibrated=[], passed=[]
- `evidence:frame_level_robustness_boundary`: frame-level audit must show no low-rank losses and bounded raw support; pairs=1470, lowrank_losses=0, raw_losses=61, raw_min_win=0.8904761904761904, boundary=['frame_level_support_not_universal_per_frame_improvement_vs_raw', 'lowrank_comparison_has_no_negative_item_pfa_pairs_but_many_ties_at_loose_pfa', 'raw_comparison_has_some_negative_item_pfa_pairs_and_should_be_reported_as_broad_not_universal']
- `evidence:paired_significance_boundary`: paired significance audit must pass all combined BH-FDR tests and keep sign-test boundaries; max_q=2.945080712825111e-29, min_effect=0.8164251207729468, boundary=['bh_fdr_applied_across_all_asset_and_combined_tests', 'does_not_claim_universal_per_frame_raw_dominance', 'paired_sign_test_excludes_ties', 'statistical_audit_over_existing_official_full_asset_rows_not_new_dataset']
- `evidence:log_pfa_auc_boundary`: log-Pfa AUC audit must show positive whole-surface deltas with frame-level CI and checked-range boundary; min_delta=0.055331964094430905, min_ci_low=0.049142001404955706, max_q=1.4636666117296334e-55, boundary=['auc_integrates_checked_pfa_grid_only', 'does_not_claim_performance_outside_checked_pfa_range', 'not_new_dataset', 'paired_bootstrap_unit_is_target_bearing_frame']
- `evidence:component_attribution_boundary`: component attribution must show raw/low-rank AUC gains and keep gate-only as a bounded relaxed endpoint; raw_delta=0.22279949628243312, lowrank_delta=0.055331964094430905, lowrank_losses=0, gate_ci_positive=False, boundary=['auc_integrates_checked_pfa_grid_only', 'gate_only_is_relaxed_endpoint_not_selected_low_false_alarm_policy', 'not_new_dataset', 'paired_unit_is_target_bearing_frame', 'reuses_frozen_detector_candidate_csvs']
- `evidence:runtime_profile_boundary`: runtime claim must be local CPU and bounded; frames=12, ratio=4.556429818969869, boundary=['does_not_claim_universal_real_time_performance', 'local_cpu_runtime_profile_not_hardware_independent_speed_benchmark', 'supports_bounded_deployment_cost_claim_only']
- `evidence:top_readiness_gate_status`: overall=top_ready; hard_failure_count=0; gate mismatches=[]
