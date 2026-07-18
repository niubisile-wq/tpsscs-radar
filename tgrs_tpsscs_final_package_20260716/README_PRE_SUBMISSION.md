# TP-SSCS TGRS Manuscript Final Package

Package date: 2026-07-16

2026-07-17 supplement: the package now also includes the full-asset seed-sensitivity outputs, strengthened classical CFAR baseline audit, parameter-swept CFAR audit, leave-one-condition-out learned-baseline audit, stronger supervised HGB feature-ensemble boundary audit, TP-SSCS-feature HGB audit, positive-target-pixel label-efficiency audit, label-cost Pareto audit, target-free calibration boundary audit, frame-level robustness audit, paired-significance audit, log-Pfa AUC operating-surface audit, component-attribution audit, runtime/complexity profile, claim-consistency audit, refreshed top-readiness check, experimental-quality assessment, submission-readiness audit, and metadata fill-in template. The main manuscript PDF/TEX has been rewritten and recompiled to cite the seed-sensitivity, parameter-swept classical-baseline, LOSO learned-baseline, HGB boundary, positive-pixel label-efficiency, label-cost Pareto, target-free calibration, frame-level robustness, paired-significance, log-Pfa AUC, component-attribution, and runtime/complexity supplements.

## Main manuscript

- `manuscript/tgrs_tpsscs_nofig_20260715.pdf`
- `manuscript/tgrs_tpsscs_nofig_20260715.tex`
- `manuscript/tgrs_tpsscs_nofig_20260715.log`

Current compiled length: 12 pages.

## Figures used in the manuscript

- `figures/submitted/figure1_paradigm_shift.png`
- `figures/submitted/figure7_official_full_asset_validation_20260716.pdf`
- `figures/submitted/figure7_official_full_asset_validation_20260716.png`
- `figures/submitted/figure7_official_full_asset_validation_20260716.svg`

The manuscript currently imports:

- `../figures/submitted/figure1_paradigm_shift.png`
- `../figures/submitted/figure7_official_full_asset_validation_20260716.pdf`

## Source data included

- `source_data/aistap_full_asset/aistap_combined_full_asset_protocol_20260715.csv`
- `source_data/aistap_full_asset/aistap_combined_full_asset_bootstrap_ci_20260715.csv`
- `source_data/aistap_sample/aistap_lowrank_k1_2_3_5_8_10_15_20_30_baseline.csv`
- `source_data/aistap_sample/aistap_target_preservation_ablation_20260713.csv`
- `source_data/ipix_external/ipix_validated_residual_fusion_test_20260715.csv`
- `source_data/ipix_external/ipix_heldout_bootstrap_delta_ci_20260715.csv`
- `source_data/ssdd_external/ssdd_external_trainable_gate_20260715.csv`
- `source_data/ssdd_external/ssdd_image_annotation_bootstrap_ci_20260715.csv`
- `source_data/aistap_full_asset/aistap_full_asset_seed_sensitivity_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_seed_sensitivity_summary_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_seed_sensitivity_by_pfa_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_seed_sensitivity_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_classical_cfar_baselines_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_classical_cfar_baselines_summary_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_classical_cfar_best_comparison_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_classical_cfar_baselines_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_classical_cfar_param_sweep_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_classical_cfar_param_sweep_summary_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_classical_cfar_param_sweep_best_comparison_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_classical_cfar_param_sweep_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_loso_learned_raw_baseline_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_learned_raw_baseline_comparison_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_learned_raw_baseline_bootstrap_ci_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_learned_raw_baseline_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_comparison_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_bootstrap_ci_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_comparison_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_bootstrap_ci_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_comparison_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_bootstrap_ci_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_label_cost_pareto_frame_auc_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_label_cost_pareto_budget_auc_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_label_cost_pareto_points_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_label_cost_pareto_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_target_free_calibration_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_target_free_calibration_comparison_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_target_free_calibration_bootstrap_ci_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_target_free_calibration_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_frame_level_robustness_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_frame_level_robustness_summary_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_frame_level_robustness_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_paired_significance_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_paired_significance_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_log_pfa_auc_frames_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_log_pfa_auc_deltas_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_log_pfa_auc_summary_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_log_pfa_auc_20260717.json`
- `source_data/aistap_full_asset/aistap_full_asset_component_attribution_operating_summary_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_component_attribution_pfa_deltas_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_component_attribution_pfa_summary_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_component_attribution_frame_auc_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_component_attribution_auc_deltas_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_component_attribution_auc_summary_20260717.csv`
- `source_data/aistap_full_asset/aistap_full_asset_component_attribution_20260717.json`
- `source_data/aistap_full_asset/aistap_runtime_profile_components_20260717.csv`
- `source_data/aistap_full_asset/aistap_runtime_profile_totals_20260717.csv`
- `source_data/aistap_full_asset/aistap_runtime_profile_frames_20260717.csv`
- `source_data/aistap_full_asset/aistap_runtime_profile_summary_20260717.csv`
- `source_data/aistap_full_asset/aistap_runtime_profile_20260717.json`

## Scripts included

- `scripts/plot_submission_figures_20260715.py`
- `scripts/evaluate_aistap_combined_full_asset_protocol.py`
- `scripts/evaluate_aistap_target_preservation_ablation.py`
- `scripts/evaluate_aistap_sample_cfar.py`
- `scripts/evaluate_aistap_lowrank_baseline.py`
- `scripts/evaluate_ssdd_image_level_bootstrap_ci.py`
- `scripts/evaluate_aistap_full_asset_seed_sensitivity.py`
- `scripts/evaluate_aistap_full_asset_classical_cfar_baselines.py`
- `scripts/evaluate_aistap_full_asset_classical_cfar_param_sweep.py`
- `scripts/evaluate_aistap_full_asset_loso_learned_raw_baseline.py`
- `scripts/evaluate_aistap_full_asset_loso_feature_ensemble_baseline.py`
- `scripts/evaluate_aistap_full_asset_loso_tpsscs_feature_ensemble.py`
- `scripts/evaluate_aistap_full_asset_loso_low_label_hgb.py`
- `scripts/evaluate_aistap_full_asset_label_cost_pareto.py`
- `scripts/evaluate_aistap_full_asset_target_free_calibration.py`
- `scripts/evaluate_aistap_full_asset_frame_level_robustness.py`
- `scripts/evaluate_aistap_full_asset_paired_significance.py`
- `scripts/evaluate_aistap_full_asset_operating_surface_auc.py`
- `scripts/evaluate_aistap_full_asset_component_attribution.py`
- `scripts/evaluate_aistap_runtime_profile.py`
- `scripts/evaluate_aistap_top_readiness.py`
- `scripts/audit_aistap_claim_consistency.py`

## Logs and notes included

- `logs/aistap_submission_figures_20260715.md`
- `logs/tgrs_quant_table_figure_insertion_20260716.md`
- `logs/aistap_combined_full_asset_protocol_20260715.md`
- `logs/aistap_results_methods_discussion_insert_20260715.md`
- `logs/aistap_manuscript_submission_package_20260715.md`
- `logs/aistap_target_preservation_ablation_20260713.md`
- `logs/aistap_full_asset_seed_sensitivity_20260717.md`
- `logs/aistap_top_readiness_self_check_20260717.md`
- `logs/aistap_top_readiness_self_check_20260717.json`
- `logs/aistap_experimental_quality_assessment_20260717.md`
- `logs/aistap_full_asset_classical_cfar_baselines_20260717.md`
- `logs/aistap_full_asset_classical_cfar_param_sweep_20260717.md`
- `logs/aistap_full_asset_loso_learned_raw_baseline_20260717.md`
- `logs/aistap_full_asset_loso_feature_ensemble_baseline_20260717.md`
- `logs/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.md`
- `logs/aistap_full_asset_loso_low_positive_pixel_hgb_20260717.md`
- `logs/aistap_full_asset_label_cost_pareto_20260717.md`
- `logs/aistap_full_asset_target_free_calibration_20260717.md`
- `logs/aistap_full_asset_frame_level_robustness_20260717.md`
- `logs/aistap_full_asset_paired_significance_20260717.md`
- `logs/aistap_full_asset_log_pfa_auc_20260717.md`
- `logs/aistap_full_asset_component_attribution_20260717.md`
- `logs/aistap_runtime_profile_20260717.md`
- `logs/aistap_claim_consistency_audit_20260717.md`
- `logs/aistap_claim_consistency_audit_20260717.json`
- `logs/aistap_supplementary_experiment_priority_20260715.md`
- `logs/aistap_20260717_top_tier_manuscript_insert.md`
- `logs/tgrs_submission_readiness_audit_20260717.md`
- `logs/tgrs_submission_readiness_audit_20260717.json`
- `logs/tgrs_submission_metadata_fillin_template_20260717.md`

## Final technical checks completed

- LaTeX build completed successfully.
- Final PDF length is 12 pages.
- No undefined references or citations were found in the final log.
- No `Float too large`, `Overfull`, or `Underfull \vbox` warnings were found in the final log scan.
- Figure files imported by the manuscript exist.
- Figure 2 internal title mismatch was fixed.
- Figure 2 panel-c heatmap colors were changed for readable numeric labels.
- All bibliography entries are cited, and all cited keys have bibliography entries.
- Page-level visual inspection found no blank pages, orphan section headings, or misplaced Fig. 1/Fig. 2 blocks.
- The 2026-07-17 seed-sensitivity supplement passes across seeds `7`, `11`, and `23` with 21/21 combined wins vs raw, 21/21 combined wins vs low-rank, and maximum cross-seed target-Pd range `0.0079`.
- The 2026-07-17 strengthened classical-baseline supplement passes against the best of 11 global/local CFAR methods with 7/7 combined wins, 14/14 asset-level wins, and minimum combined delta `0.0205`.
- The 2026-07-17 parameter-swept classical-baseline supplement passes against the best of 75 global/local CFAR method/configuration candidates with 7/7 combined wins, 14/14 asset-level wins, and minimum combined delta `0.0162`.
- The 2026-07-17 LOSO learned-baseline supplement passes against a supervised raw-feature logistic detector trained on the opposite official full asset, with 7/7 combined wins, 14/14 asset-level wins, minimum combined delta `0.0596`, and positive bootstrap CI lower bounds at all Pfa points.
- The 2026-07-17 stronger supervised raw/residual HGB boundary audit is an informative negative: the HGB feature ensemble beats compact TP-SSCS on the official full-asset protocol, so the manuscript should not claim dominance over all supervised learned detectors.
- The 2026-07-17 TP-SSCS-feature HGB audit shows TP-SSCS features are useful in a supervised ensemble: it beats compact TP-SSCS at 7/7 combined operating points and 14/14 asset-level operating points, and nearly matches the raw/residual HGB boundary with 6/7 combined wins but not a strict all-Pfa win.
- The 2026-07-17 positive-target-pixel label-efficiency audit shows compact zero-target-label TP-SSCS beats low-label raw/residual HGB at all seven combined Pfa points for `1`, `2`, `4`, and `8` positive-pixel budgets with positive bootstrap CI lower bounds; the HGB first catches or exceeds compact at budget `16`.
- The 2026-07-17 label-cost Pareto audit shows compact TP-SSCS AUC `0.5313`, zero official full-asset positive-target labels, and `133.66` ms/frame local CPU median inference; it Pareto-dominates low-label raw/residual HGB budgets `1`, `2`, `4`, `8`, and `16` in AUC, label cost, and measured runtime with positive bootstrap CI support. HGB first exceeds compact AUC at budget `64`; this is not a full-label HGB superiority claim.
- The 2026-07-17 target-free calibration boundary audit shows same-asset and cross-asset target-free thresholds preserve TP-SSCS positive Pd margins over raw and low-rank at all seven combined Pfa points with positive bootstrap support; fixed threshold transfer is not fully empirical-Pfa calibrated, so this is not a replacement for the main calibrated protocol.
- The 2026-07-17 frame-level robustness audit shows TP-SSCS has `1470/1470` nonnegative item-Pfa pairs versus `low_rank_residual_k30`; versus raw, the support is broad but not universal, with minimum combined win fraction `0.890` and `61` raw-favorable item-Pfa pairs.
- The 2026-07-17 paired-significance audit shows all `14` combined comparator/Pfa exact sign tests remain significant after BH-FDR correction, with worst combined q-value `2.945e-29` and minimum matched sign effect `0.816`; the sign test ignores ties and should not be read as pixel-level independence or universal raw-frame dominance.
- The 2026-07-17 log-Pfa AUC audit shows whole-operating-surface support over the checked `1e-5` to `1e-2` Pfa grid: TP-SSCS AUC `0.5313` vs low-rank `0.4760` and raw `0.3085`, minimum combined delta `0.0553`, minimum frame-bootstrap CI lower bound `0.0491`, and worst combined BH-FDR q-value `1.464e-55`.
- The 2026-07-17 component-attribution audit shows the finished detector's log-Pfa AUC gain is `+0.2228` over raw and `+0.0553` over low-rank residual, with `195/15/0` frame-level AUC wins/ties/losses versus low-rank; gate-only is reported as a relaxed learned-score boundary rather than a uniformly dominated endpoint.
- The 2026-07-17 runtime/complexity profile reports local CPU compact TP-SSCS finished-detector median inference `133.66` ms/frame versus `608.99` ms/frame for the checked raw/residual HGB inference stack over 12 deterministic target-bearing official full-asset frames; this is not a hardware-independent real-time claim.
- The 2026-07-17 claim-consistency audit reports verdict `claim_consistent` with `0` hard failures and `0` warnings across manuscript, README, STATUS, claim matrix, and top-tier insert text.
- The refreshed 2026-07-17 top-readiness check reports `overall=top_ready` with `0` hard failures, while retaining non-hard partial items for the HGB feature-ensemble boundary and target-free calibration boundary, non-hard pass items for positive-pixel label efficiency, label-cost Pareto, frame-level robustness, paired significance, log-Pfa AUC, component attribution, and runtime/complexity, and a hard pass item for claim consistency.
- The 2026-07-17 submission-readiness audit reports verdict `technically_complete_metadata_blocked`: `0` hard file/build failures, `0` warnings, `12` compiled pages, and `6` remaining submission metadata blockers.

## Not yet ready for formal submission until these are filled

The current manuscript still contains submission metadata placeholders:

- Real author names and IEEE membership status.
- Author affiliations.
- Corresponding author name and email.
- ORCID identifiers required by IEEE submission workflow.
- Funding information.
- Final acknowledgment text.
- Public repository, DOI, or access statement for data/code availability.

These placeholders should be replaced before formal TGRS submission.

Use `logs/tgrs_submission_metadata_fillin_template_20260717.md` for fill-in text, then rerun the root-level audit script:

```powershell
py scripts\audit_tgrs_submission_readiness.py
```
