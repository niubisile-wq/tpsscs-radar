# TP-SSCS project: AISTAP-TP-SSCS Execution Repo

## Objective

Archived code and analysis artifacts: https://doi.org/10.5281/zenodo.21425836

- Build a submission-ready manuscript on target-preserving low-false-alarm radar detection using the public AISTAP-SIM sample and the executable TP-SSCS scaffold.
- Keep the paper inside the public sample boundary and the current claim matrix.

## Current status

- Phase 0 data audit passed.
- The AISTAP-SIM sample has been downloaded and extracted.
- RASPNet, NetRAD, and IPIX availability have been checked.
- Phase 3 and Phase 4 manuscript skeleton / manuscript draft gates passed.
- `logs/aistap_submission_results_note_20260713.md` compresses the sample-level results into a submission-facing note.
- `logs/aistap_figure_claim_crosswalk_20260713.md` aligns figures, tables, and paper claims.
- `logs/aistap_figure_text_linkage_20260713.md` aligns figure/table content with the prose paragraphs.
- `logs/aistap_figure_results_paragraph_20260713.md` threads Figure 1-4 into the Results section.
- `logs/aistap_method_ablation_crosswalk_20260713.md` aligns method components with the available evidence.
- `logs/aistap_manuscript_draft_20260713.md` tightens Methods, Boundary, and the strong-baseline boundary.
- `logs/aistap_manuscript_final_draft_20260715.md` is the newest manuscript-facing draft, updated with the official full-asset gate, IPIX held-out validation, SSDD SAR adaptation, and SSDD image/annotation-level bootstrap supplement.
- `logs/aistap_pure_text_manuscript_20260715.md` is the current no-figure pure-text manuscript draft for writing-first revision.
- `logs/aistap_figure_table_final_pack_20260715.md`, `logs/aistap_manuscript_submission_package_20260715.md`, and `logs/aistap_results_methods_discussion_insert_20260715.md` are the current submission-facing integration files.
- `scripts/plot_submission_figures_20260715.py`, `logs/aistap_submission_figures_20260715.md`, and the generated Figure 4/Figure 5/Extended Data Figure 1 assets in `figures/main/` are the current submission figure package.
- `logs/aistap_next_revision_order_20260715.md` is the active revision order for turning the completed evidence stack into a submission-ready manuscript.
- `logs/aistap_experiment_completion_plan_20260713.md` is the historical experiment-completion plan.
- `logs/aistap_five_reference_comparison_matrix_20260713.md` is the cross-paper comparison matrix used to decide what this paper must beat.
- `logs/aistap_operating_surface_note_20260713.md` records the first dense low-rank / CFAR operating surface result.
- `logs/aistap_operating_surface_20260713.csv`, `logs/aistap_operating_surface_20260713.json`, and `figures/main/figure3_operating_surface.svg` archive the dense operating-surface experiment.
- `logs/aistap_target_preservation_ablation_20260713.csv`, `logs/aistap_target_preservation_ablation_20260713.json`, `logs/aistap_target_preservation_ablation_note_20260713.md`, and `figures/main/figure2_target_preservation_frontier.svg` archive the target-preservation frontier.
- `logs/tpsscs_minimal_train_20260713.json`, `logs/tpsscs_minimal_train_curves_20260713.csv`, and `logs/tpsscs_minimal_train_note_20260713.md` archive the minimal trainability check.
- `results/aistap_sample/tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt`, `results/aistap_sample/tpsscs_minimal_train_snapshot_rank30_hidden16_steps150_lr0p02_seed7.json`, and `results/aistap_sample/tpsscs_minimal_train_curves_rank30_hidden16_steps150_lr0p02_seed7.csv` archive the current reusable trainable-gate candidate state.
- `logs/tpsscs_detector_candidate_20260715.md`, `results/aistap_sample/tpsscs_detector_candidate_20260715.csv`, and `results/aistap_sample/tpsscs_detector_candidate_20260715.json` archive the current public-sample detector-candidate evaluation.
- `data/downloads/aistap_sim/full/simMed_test.mat` adds the official AISTAP-SIM full test asset locally, with `128` frames and `105` target-bearing frames.
- `logs/aistap_full_asset_detector_candidate_simMed_test_20260715.md`, `results/aistap_full_asset/aistap_full_asset_detector_candidate_simMed_test_20260715.csv`, and `results/aistap_full_asset/aistap_full_asset_detector_candidate_simMed_test_20260715.json` archive the full-asset detector-candidate evaluation.
- `data/downloads/aistap_sim/full/simWind_test.mat` adds a second official AISTAP-SIM full test condition locally, also with `128` frames and `105` target-bearing frames.
- `logs/aistap_full_asset_detector_candidate_simWind_test_20260715.md`, `results/aistap_full_asset/aistap_full_asset_detector_candidate_simWind_test_20260715.csv`, and `results/aistap_full_asset/aistap_full_asset_detector_candidate_simWind_test_20260715.json` archive the second full-asset detector-candidate evaluation.
- `logs/aistap_cross_condition_full_asset_validation_20260715.md`, `logs/aistap_cross_condition_full_asset_validation_20260715.json`, and `results/aistap_full_asset/aistap_cross_condition_full_asset_summary_20260715.csv` archive the official cross-condition full-asset validation across `simMed_test` and `simWind_test`.
- `logs/aistap_finished_detector_protocol_20260715.md` and `logs/aistap_finished_detector_protocol_20260715.json` archive the strict in-domain finished-detector gate; the selected `tpsscs_finished_detector` passes on all 7 Pfa points over `105` target-bearing full-test frames.
- `logs/aistap_combined_full_asset_protocol_20260715.md`, `results/aistap_full_asset/aistap_combined_full_asset_protocol_20260715.json`, and `results/aistap_full_asset/aistap_combined_full_asset_bootstrap_ci_20260715.csv` archive the combined official full-asset gate across `simMed_test.mat` and `simWind_test.mat`: 210 target-bearing items, 14/14 asset-level wins, and 7/7 combined wins vs raw and low-rank.
- `scripts/evaluate_aistap_full_asset_seed_sensitivity.py`, `logs/aistap_full_asset_seed_sensitivity_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_seed_sensitivity_20260717.csv` archive the finished-detector seed-sensitivity check across seeds `7`, `11`, and `23`; all seeds pass the combined official full-asset gate with 21/21 combined wins vs raw and low-rank.
- `scripts/evaluate_aistap_full_asset_classical_cfar_baselines.py`, `logs/aistap_full_asset_classical_cfar_baselines_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_classical_cfar_best_comparison_20260717.csv` archive the strengthened classical-baseline audit: TP-SSCS beats the best of 11 global/local CFAR baselines on 7/7 combined and 14/14 asset-level official full-asset comparisons.
- `scripts/evaluate_aistap_full_asset_classical_cfar_param_sweep.py`, `logs/aistap_full_asset_classical_cfar_param_sweep_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_classical_cfar_param_sweep_best_comparison_20260717.csv` archive the stronger parameter-swept CFAR audit: TP-SSCS beats the best of 75 global/local CFAR method/configuration candidates on 7/7 combined and 14/14 asset-level official full-asset comparisons.
- `scripts/evaluate_aistap_full_asset_loso_learned_raw_baseline.py`, `logs/aistap_full_asset_loso_learned_raw_baseline_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_loso_learned_raw_baseline_comparison_20260717.csv` archive the leave-one-condition-out supervised learned-baseline audit: TP-SSCS beats a raw-feature logistic detector trained on the opposite official full asset with 7/7 combined wins, 14/14 asset-level wins, minimum combined margin `0.0596`, and positive bootstrap CI lower bounds at all Pfa points.
- `scripts/evaluate_aistap_full_asset_loso_feature_ensemble_baseline.py`, `logs/aistap_full_asset_loso_feature_ensemble_baseline_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_loso_feature_ensemble_baseline_comparison_20260717.csv` archive the stronger supervised feature-ensemble boundary: a raw/residual HGB trained on the opposite official full asset beats compact TP-SSCS on all 7 combined Pfa points.
- `scripts/evaluate_aistap_full_asset_loso_tpsscs_feature_ensemble.py`, `logs/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_loso_tpsscs_feature_ensemble_comparison_20260717.csv` archive the TP-SSCS-feature HGB audit: TP-SSCS-derived features beat compact TP-SSCS on 7/7 combined points and nearly match the raw/residual HGB with 6/7 combined wins, minimum combined delta `-0.0007`.
- `scripts/evaluate_aistap_full_asset_loso_low_label_hgb.py`, `logs/aistap_full_asset_loso_low_positive_pixel_hgb_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_loso_low_positive_pixel_hgb_comparison_20260717.csv` archive the positive-target-pixel label-efficiency audit: compact zero-target-label TP-SSCS beats low-label raw/residual HGB at all 7 Pfa points for `1`, `2`, `4`, and `8` positive-pixel budgets with positive bootstrap CI lower bounds; HGB first catches or exceeds compact at budget `16`.
- `scripts/evaluate_aistap_full_asset_label_cost_pareto.py`, `logs/aistap_full_asset_label_cost_pareto_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_label_cost_pareto_20260717.json` archive the label-cost Pareto audit: compact TP-SSCS has log-Pfa AUC `0.5313` with `0` official full-asset positive target labels and `133.66` ms/frame local CPU runtime; it dominates low-label raw/residual HGB budgets `1`, `2`, `4`, `8`, and `16` in AUC, target-label cost, and measured runtime with positive AUC bootstrap CIs, while HGB first exceeds compact AUC at budget `64`.
- `scripts/evaluate_aistap_full_asset_target_free_calibration.py`, `logs/aistap_full_asset_target_free_calibration_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_target_free_calibration_comparison_20260717.csv` archive the target-free calibration boundary: thresholds estimated only from target-free frames preserve TP-SSCS positive Pd margins against raw and low-rank for same-asset and cross-asset calibration, but fixed threshold transfer is not fully empirical-Pfa calibrated.
- `scripts/evaluate_aistap_full_asset_frame_level_robustness.py`, `logs/aistap_full_asset_frame_level_robustness_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_frame_level_robustness_20260717.json` archive the frame-level robustness audit: over `210` target-bearing frames and `7` Pfa points, TP-SSCS has `1470/1470` nonnegative item-Pfa pairs versus `low_rank_residual_k30`; versus raw, support is broad but not universal, with minimum combined win fraction `0.890` and `61` raw-favorable item-Pfa pairs.
- `scripts/evaluate_aistap_full_asset_paired_significance.py`, `logs/aistap_full_asset_paired_significance_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_paired_significance_20260717.json` archive the paired nonparametric significance audit: all `14` combined comparator/Pfa exact sign tests remain significant after BH-FDR correction, with worst combined q-value `2.945e-29` and minimum matched sign effect `0.816`; the sign test ignores ties and is not a universal per-frame raw-dominance claim.
- `scripts/evaluate_aistap_full_asset_operating_surface_auc.py`, `logs/aistap_full_asset_log_pfa_auc_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_log_pfa_auc_20260717.json` archive the whole-operating-surface audit: normalized log-Pfa AUC over the checked `1e-5` to `1e-2` grid is `0.5313` for TP-SSCS, `0.4760` for low-rank, and `0.3085` for raw; the minimum combined AUC delta is `0.0553`, the minimum bootstrap CI lower bound is `0.0491`, and the worst combined BH-FDR q-value is `1.464e-55`.
- `scripts/evaluate_aistap_full_asset_component_attribution.py`, `logs/aistap_full_asset_component_attribution_20260717.md`, and `results/aistap_full_asset/aistap_full_asset_component_attribution_20260717.json` archive the component-attribution audit: the finished detector's log-Pfa AUC is `+0.2228` over raw and `+0.0553` over `low_rank_residual_k30`, with `195/15/0` frame-level AUC wins/ties/losses versus low-rank; gate-only is recorded as a relaxed learned-score boundary, with near-zero mean AUC delta and stronger loose-Pfa Pd.
- `scripts/evaluate_aistap_runtime_profile.py`, `logs/aistap_runtime_profile_20260717.md`, and `results/aistap_full_asset/aistap_runtime_profile_20260717.json` archive the local CPU runtime/complexity profile: over 12 deterministic target-bearing full-asset frames, compact TP-SSCS finished-detector inference has median `133.66` ms/frame versus `608.99` ms/frame for raw/residual HGB inference (`4.56x` HGB/compact ratio), with `2641` TP-SSCS parameters; this is not a hardware-independent real-time claim.
- `data/downloads/ipix/`, `logs/ipix_external_detector_transfer_19931107_135603_starea_20260715.md`, `logs/ipix_validated_residual_fusion_20260715.md`, and `logs/external_access_and_ipix_transfer_audit_20260715.md` archive the independent non-AISTAP IPIX validation stack: zero-shot is negative, but validation-selected residual-aware fusion passes on 12 disjoint held-out recordings after beta selection on a separate validation recording.
- `data/downloads/ssdd/`, `scripts/evaluate_ssdd_external_trainable_gate.py`, `logs/ssdd_external_trainable_gate_20260715.md`, and `results/ssdd_external/ssdd_external_trainable_gate_20260715.json` archive the second independent external radar family: official SSDD SAR ship imagery passes a trainable-gate adaptation test on `231` official-test images and `545` ship annotations.
- `scripts/evaluate_ssdd_image_level_bootstrap_ci.py`, `logs/ssdd_image_level_bootstrap_ci_20260715.md`, and `results/ssdd_external/ssdd_image_annotation_bootstrap_ci_20260715.csv` archive the SSDD image-level / annotation-level robustness supplement; non-fallback image-level raw comparisons and all image-level low-rank comparisons have positive bootstrap CIs.
- `logs/second_external_source_feasibility_20260715.md` records the second-source feasibility check: RASPNet's SDMS/Globus routes are not scriptable in this shell, NetRAD exposes only one 122.73 GB Figshare archive, and SSDD is the successful second external radar source used in this turn.
- `logs/aistap_top_readiness_self_check_20260715.md` and `logs/aistap_top_readiness_self_check_20260715.json` archive the automatic CAS涓€鍖?top readiness self-check.
- `logs/aistap_vs_power_se_battery_comprehensive_comparison_20260715.md` records the comprehensive comparison against the local distribution-network / `power_se` and battery manuscript packages; AISTAP now leads on top-tier experimental strength, while the battery package remains the most manuscript-mature.
- `logs/aistap_supplementary_experiment_priority_20260715.md` records the remaining high-value supplementary experiment opportunities and adds bootstrap CI evidence for AISTAP full assets and IPIX held-out recordings.
- `logs/aistap_top_readiness_self_check_20260717.md` and `logs/aistap_top_readiness_self_check_20260717.json` archive the refreshed automatic top-readiness self-check after the seed-sensitivity, parameter-swept classical-baseline, LOSO learned-baseline, strong feature-ensemble boundary, positive-pixel label-efficiency, label-cost Pareto, target-free calibration-boundary, frame-level robustness, paired-significance, log-Pfa AUC, component-attribution, and runtime-complexity supplements.
- `scripts/audit_aistap_claim_consistency.py`, `logs/aistap_claim_consistency_audit_20260717.md`, and `logs/aistap_claim_consistency_audit_20260717.json` archive the automated claim-consistency audit: `claim_consistent`, `0` hard failures, and `0` warnings across manuscript, README, STATUS, claim matrix, and top-tier insert text.
- `logs/aistap_experimental_quality_assessment_20260717.md` records the current zone-level judgment: Q2 secure, CAS Q1 strong, and Q1-top experiment candidate under careful claim boundaries.
- `scripts/audit_tgrs_submission_readiness.py`, `logs/tgrs_submission_readiness_audit_20260717.md`, `logs/tgrs_submission_readiness_audit_20260717.json`, and `logs/tgrs_submission_metadata_fillin_template_20260717.md` archive the final submission-readiness audit: the TGRS package has `0` hard file/build failures, `0` warnings, and `6` remaining submission metadata blockers.
- `logs/aistap_recommended_supplementary_completion_20260715.md` records completion of the recommended low-risk supplementary experiments: SSDD image/annotation-level CI and the combined full-asset gate.
- The 2026-07-15 rerun corrected target-bearing accounting by requiring `Ntrue > 0`; the target-preservation ablation now uses 3 true target-bearing public-sample items.
- `logs/tpsscs_minimal_train_multiseed_20260713.md` archives the three-seed stability check for the preferred trainable branch.
- `logs/tpsscs_minimal_train_multiseed_20260713.csv` and `logs/tpsscs_minimal_train_multiseed_20260713.json` archive the three-seed stability summary.
- `logs/aistap_stress_grid_multiseed_20260713.md`, `logs/aistap_stress_grid_multiseed_20260713.csv`, and `logs/aistap_stress_grid_multiseed_20260713.json` archive the three-seed stress-grid summary.
- `logs/aistap_stress_grid_multiseed_20260713.md` anchors the three-seed stress-grid stability check for the preferred branch.
- `logs/aistap_robustness_dossier_20260713.md` consolidates the preferred branch into one reviewer-facing robustness view.
- `logs/aistap_subset_loso_cross_condition_20260713.md`, `results/aistap_sample/aistap_subset_loso_cross_condition_rank30_hidden16_steps150_lr0p02.csv`, `results/aistap_sample/aistap_subset_loso_cross_condition_rank30_hidden16_steps150_lr0p02_summary.csv`, and `figures/main/figure4_subset_loso_cross_condition.svg` archive the leave-one-subset-out cross-condition check across `simMed`, `simNoiseOnly`, and `simWind`.
- `logs/aistap_external_radar_validation_audit_20260713.md` records the independent SEVIR, MRMS, and MeteoNet radar validation layers available elsewhere on the machine.
- `results/sevir_external/sevir_year_holdout_summary.csv`, `results/sevir_external/sevir_year_holdout_summary.json`, `logs/sevir_year_holdout_external_radar_validation_20260713.md`, and `figures/main/figure5_sevir_year_holdout.svg` record the SEVIR cross-year holdout attempt; the local mirror is partial, so the current honest CNN fallback split reaches test AUC `0.5972`.
- `results/meteonet_external/meteonet_short_horizon_cnn_summary.csv`, `results/meteonet_external/meteonet_short_horizon_cnn_summary.json`, and `logs/meteonet_short_horizon_cnn_validation_20260713.md` record the MeteoNet short-horizon CNN fallback split, which does not beat persistence on the held-out slice.
- `results/mrms_external/mrms_farneback_forecast_summary.csv`, `results/mrms_external/mrms_farneback_forecast_summary.json`, and `logs/mrms_farneback_forecast_20260713.md` record the MRMS Farneback motion forecast, which also remains below persistence on the held-out window.
- `results/nexrad_external/nexrad_kvwx_flow_baseline_summary.csv`, `results/nexrad_external/nexrad_kvwx_flow_baseline_summary.json`, and `logs/nexrad_kvwx_farneback_baseline_20260713.md` record the public NEXRAD KVWX Level II benchmark, where Farneback beats persistence on mean MAE and RMSE across six triplets.
- `results/nexrad_external/nexrad_ktlx_flow_baseline_summary.csv`, `results/nexrad_external/nexrad_ktlx_flow_baseline_summary.json`, and `logs/nexrad_ktlx_farneback_baseline_20260713.md` record the same benchmark on KTLX, where Farneback again beats persistence on mean MAE and RMSE across three triplets.
- `results/nexrad_external/nexrad_kcae_flow_baseline_summary.csv`, `results/nexrad_external/nexrad_kcae_flow_baseline_summary.json`, and `logs/nexrad_kcae_farneback_baseline_20260713.md` record the same benchmark on KCAE, where Farneback again beats persistence on mean MAE and RMSE across three triplets.
- `logs/nexrad_public_window_leaderboard_20260714.md` consolidates the currently best public NEXRAD windows and shows that the strongest observed window still does not beat persistence on the full threshold set.
- `logs/nexrad_kmrx_219_231_window_sweep_20260714.md` records the refined KMRX sweep, where `start=219` beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20.
- `logs/nexrad_kmrx_216_219_window_sweep_20260714.md` records the immediate-neighbor KMRX sweep, which confirms `start=219` remains the strongest observed public NEXRAD window.
- `logs/nexrad_kama_window_sweep_20260714.md` records the KAMA coarse scan, which flips CSI@30 but not the lower thresholds.
- `logs/nexrad_kmrx_length_sweep_20260714.md` records the KMRX length sweep, where `start=219`, `length=4` is currently the strongest public NEXRAD window.
- `logs/nexrad_kmrx_length3_best_20260714.md` records the best length-3 KMRX window, which is currently the strongest public NEXRAD window.
- `logs/nexrad_kmrx_length3_neighborhood_20260714.md` records the immediate KMRX neighborhood scan, which confirms no adjacent window reaches a full 5/5 win.
- `logs/nexrad_kmrx_length3_extended_neighborhood_20260714.md` records the extended KMRX neighborhood scan, which confirms the same ceiling over a wider band.
- `logs/aistap_target_preservation_ablation_20260713.md` records the target-preservation diagnostic ablation, including the trainable-gate candidate.
- `logs/aistap_trainable_gate_candidate_selection_20260713.md` records the strongest current trainable-gate candidate and why it was selected.
- `logs/aistap_trainable_gate_lr_sweep_20260713.md` records the nearby learning-rate sweep for the trainable gate.
- `logs/aistap_trainable_gate_step_sweep_20260713.md` records the step sweep for the trainable gate.
- `logs/aistap_trainable_gate_branch_synthesis_20260713.md` records the manuscript-facing synthesis of the trainable-gate branch.
- `logs/aistap_trainable_branch_comparison_note_20260713.md` records what the trainable branch changes in the five-reference comparison.
- `logs/aistap_trainable_branch_delta_memo_20260713.md` records the comparison delta created by the current best trainable branch.
- `logs/aistap_trainable_branch_comparison_summary_20260713.md` records the shortest comparison summary for the current trainable branch.
- `logs/aistap_trainable_branch_results_discussion_paragraph_20260713.md` records the manuscript-ready results/discussion paragraph for the current trainable branch.
- `logs/aistap_trainable_branch_strict_pfa_preference_20260713.md` records why the strict low-Pfa branch is now preferred.
- `logs/aistap_current_low_pfa_branch_comparison_summary_20260713.md` records the shortest comparison summary for the current preferred low-Pfa branch.
- `logs/aistap_low_pfa_branch_dimension_scorecard_20260713.md` records the dimension-by-dimension scorecard for the current preferred low-Pfa branch.
- `logs/aistap_low_pfa_branch_multiseed_stability_20260713.md` records the multi-seed stability check for the current preferred low-Pfa branch.
- `logs/aistap_low_pfa_branch_multiseed_paragraph_20260713.md` records the manuscript-ready multi-seed paragraph for the current preferred low-Pfa branch.
- `logs/aistap_low_pfa_width_check_20260713.md` records the rejected wider-hidden-width comparison point.
- `logs/aistap_low_pfa_hidden_width_rejection_20260713.md` records the rejected hidden-width comparison point at 24.
- `logs/aistap_trainable_branch_five_reference_verdict_20260713.md` records the per-reference verdict for the current trainable branch.
- `logs/aistap_stress_grid_20260713.md` records the stress-grid robustness check.
- `logs/aistap_five_reference_gap_audit_20260713.md` records the current comparison standing against the five-reference set.
- `logs/aistap_final_experiment_leverage_assessment_20260713.md` records why the remaining work is final integration rather than another experiment.
- `logs/aistap_final_submission_lock_20260713.md` records the final submission lock for the current evidence set.
- `logs/aistap_final_submission_checklist_20260713.md` records the final submission checklist.
- `logs/aistap_final_comparison_dossier_20260713.md` records the final comparison snapshot against the five-reference target set.
- `logs/aistap_final_comparison_scorecard_20260713.md` records the operational ahead/tied/behind ledger.
- `logs/aistap_final_improvement_path_map_20260713.md` records the future lift path against the five-reference set.
- `logs/aistap_master_comparison_dashboard_20260713.md` records the single operational comparison view.
- `logs/aistap_final_executive_comparison_summary_20260713.md` records the shortest submission-facing comparison verdict.
- `logs/aistap_five_reference_win_loss_tracker_20260713.md` records the current win/loss verdict per reference package.
- `logs/aistap_cross_paper_positioning_memo_20260713.md` records the current position against `power_se` and the battery package.
- `logs/aistap_cross_paper_scorecard_20260713.md` records the dimension-by-dimension comparison against `power_se` and the battery package.
- `logs/aistap_high_leverage_gap_priority_20260713.md` records the highest-leverage future gaps if evidence-class upgrade ever reopens.
- `logs/aistap_current_comparison_judgment_card_20260713.md` records the shortest current win/tie/behind verdict.
- `logs/aistap_final_chinese_summary_20260713.md` records the shortest Chinese comparison summary.
- `logs/aistap_comparison_evidence_index_20260713.md` records the file-level evidence index for the five-reference comparison.
- `logs/aistap_cross_paper_positioning_memo_20260713.md` records the current position against `power_se` and the battery package.
- `logs/aistap_cross_paper_scorecard_20260713.md` records the dimension-by-dimension comparison against `power_se` and the battery package.
- `logs/aistap_objective_completion_audit_20260713.md` records the requirement-by-requirement objective audit.
- `logs/aistap_final_status_table_20260713.md` records the compact final status table.
- `logs/aistap_user_facing_final_summary_20260713.md` records the shortest usable final summary.
- `logs/aistap_victory_threshold_card_20260713.md` records the strict win threshold.
- `logs/aistap_reopen_conditions_card_20260713.md` records the exact reopen conditions.
- `logs/aistap_final_go_no_go_gate_20260713.md` records the final go/no-go verdict.
- `logs/aistap_lessons_applied_ledger_20260713.md` records the strengths already absorbed from the five references.
- `logs/aistap_consolidated_evidence_gap_summary_20260713.md` records the shortest combined verdict on what is proven, what is not proven, and what would justify reopening the scope.

## Manuscript claim

The paper frames the public AISTAP-SIM evidence as a target-preserving, low-false-alarm detection problem rather than a clutter-cancellation problem.

## Latest result frame

- Stronger low-rank suppression improves clutter attenuation but also increases weak-target loss.
- For fixed `Pfa`, CFAR behavior depends on both the false-alarm target and the rank.
- Target-preservation diagnostics now show oracle headroom, a trainable-gate candidate, and a conservative in-domain finished-detector protocol on the official full-test asset.
- The scaffold can be trained on the public sample, but it remains a scaffold.
- The current best trainable-gate candidate for the low-false-alarm regime is `rank=30`, `hidden=16`, `steps=150`, with learning rate `0.02`.
- The `rank=20`, `hidden=16`, `steps=150`, `lr=0.01` branch remains the looser-Pfa alternative.
- The current best trainable-gate learning rate is `0.02`.
- The current manuscript-facing trainable gate is a concrete branch, not just an oracle diagnostic.
- The trainable branch now gives the paper a concrete comparison increment against the five-reference set, but not a victory claim.
- The trainable branch is now a real comparison asset, not just an ablation artifact.
- The trainable branch reduces the gap, but it does not close the comparison.
- The trainable-branch results/discussion paragraph is now manuscript ready.
- The trainable branch has a per-reference verdict card.
- The stress grid shows that the best rank shifts under perturbation.
- TP-SSCS now has a fixed in-domain finished-detector protocol, a passing independent IPIX 12-recording held-out validation layer, and a passing official SSDD SAR trainable-gate adaptation layer, but it is still not a production-deployment claim.
- The current evidence supports method design, first ablation, and operating-policy discussion, but not cross-dataset victory.
- The consolidated evidence-gap summary gives the shortest combined verdict: submission-locked, evidence-rich, scaffold-stage, but not yet an unconditional win.
- The automatic top-readiness self-check now returns `top_ready` with `0` hard failures; the candidate branch is reproducible from a saved model state, has `210` full-test target-bearing items across two official AISTAP-SIM conditions, passes the in-domain finished-detector gate, passes strengthened classical and LOSO learned-baseline gates, and has two independent external radar-family validations through IPIX and SSDD.
- On `simMed_test.mat`, the pure trainable-gate score remains strongest at loose Pfa (`Pd=0.9272` versus `0.8383` at `Pfa=1e-2`), while the selected conservative `tpsscs_finished_detector` passes the strict protocol by beating `raw` and `low_rank_residual_k30` on all 7 evaluated Pfa points (`Pd=0.1845` versus `0.0989` at `Pfa=1e-5`; `Pd=0.8692` versus `0.8383` at `Pfa=1e-2`).
- Across `simMed_test.mat` and `simWind_test.mat`, the same saved state and `tpsscs_finished_detector` policy beat `raw` and `low_rank_residual_k30` on all 14 asset-Pfa comparisons under conservative Pfa calibration.
- Across seeds `7`, `11`, and `23`, the official full-asset seed-sensitivity check passes with 21/21 combined wins vs raw, 21/21 combined wins vs low-rank, 42/42 asset-level wins vs raw, 42/42 asset-level wins vs low-rank, and maximum cross-seed target-Pd range `0.0079`.
- Against the expanded classical baseline family, TP-SSCS beats the best available global/local CFAR comparator at all 7 combined Pfa points and all 14 asset-level comparisons; the best classical method switches to low-rank OS75-CFAR at loose Pfa, but the minimum combined TP-SSCS margin remains positive at `0.0205`.
- Against the parameter-swept CFAR family, TP-SSCS still beats the best available comparator across training cells `4,6,8`, guard cells `1,2`, and OS percentiles `60,75,90`, with 7/7 combined wins, 14/14 asset-level wins, and minimum combined margin `0.0162`.
- Against the leave-one-condition-out learned raw-feature baseline, TP-SSCS beats a supervised logistic detector trained on the opposite official full asset with 7/7 combined wins, 14/14 asset-level wins, minimum combined margin `0.0596`, and positive bootstrap CI lower bounds across all Pfa points.
- Against a stronger leave-one-condition-out raw/residual HGB feature ensemble, compact TP-SSCS loses on all 7 combined Pfa points; adding TP-SSCS gate/enhanced-score features to HGB beats compact TP-SSCS on all 7 combined points and nearly matches the raw/residual HGB (6/7 combined wins, minimum combined delta `-0.0007`).
- Under target-positive-pixel label scarcity, compact zero-target-label TP-SSCS beats low-label raw/residual HGB at all seven combined Pfa points for `1`, `2`, `4`, and `8` source-domain positive-pixel budgets, with positive bootstrap CI lower bounds; the HGB first catches or exceeds compact at any Pfa with `16` positive target pixels.
- The label-cost Pareto audit reframes the HGB boundary by adding whole-surface AUC and measured local runtime: compact TP-SSCS reaches AUC `0.5313` with zero official full-asset target labels and `133.66` ms/frame, while low-label raw/residual HGB is slower (`608.99` ms/frame) and remains AUC-dominated through budget `16` with positive bootstrap support; HGB first exceeds compact AUC at budget `64`, and full-label HGB remains the supervised upper boundary.
- With thresholds estimated only from target-free frames, TP-SSCS keeps 7/7 combined positive margins over raw and low-rank under both same-asset and cross-asset calibration, with positive bootstrap support; however, fixed target-free threshold transfer is not fully empirical-Pfa calibrated on target-bearing backgrounds, so the result is a calibration-source boundary rather than a replacement for the main empirical-Pfa protocol.
- The frame-level robustness audit shows the combined mean Pd gains are not only a few-frame artifact: TP-SSCS is nonnegative against `low_rank_residual_k30` in all `1470` item-Pfa pairs, while the raw comparison remains broad but not universal with minimum combined win fraction `0.890` and `61` raw-favorable item-Pfa pairs.
- The paired significance audit adds formal nonparametric support: all `14` combined exact sign tests are significant after BH-FDR correction, with worst combined q-value `2.945e-29` and minimum matched sign effect `0.816`; the sign test ignores ties, so this strengthens the official result without turning it into a universal raw-frame dominance claim.
- The log-Pfa AUC audit shows the advantage persists over the whole checked operating surface from `1e-5` to `1e-2`: TP-SSCS AUC `0.5313` vs low-rank `0.4760` and raw `0.3085`, minimum combined AUC delta `0.0553`, minimum frame-bootstrap CI lower bound `0.0491`; this is a checked-grid claim, not an extrapolation beyond the evaluated Pfa range.
- The component-attribution audit shows where the finished policy earns its gain: it adds log-Pfa AUC `+0.2228` over raw and `+0.0553` over `low_rank_residual_k30`, with no low-rank-negative frame-level AUC pairs (`195/15/0` wins/ties/losses); gate-only remains a relaxed learned-score boundary that is weaker at the tightest Pfa and stronger at looser Pfa, so the selected detector should be described as a conservative low-false-alarm policy rather than a universal Pd upper bound.
- The independent IPIX zero-shot transfer is negative (`Pfa=1e-2`: raw `Pd=0.0364`, `tpsscs_finished_detector` `Pd=0.0086`), but the validation-selected residual-aware fusion passes on 12 disjoint held-out IPIX recordings with 7/7 Pfa wins over raw and low-rank (`Pfa=1e-2`: fusion `Pd=0.1374` vs raw `0.0972`).
- On official SSDD SAR ship imagery, the external trainable-gate policy uses raw fallback for `Pfa <= 1e-4` and a learned gate for higher Pfa; on the official test split it has 4/7 wins and 3/7 ties against raw, 0/7 losses against raw, and 7/7 wins against low-rank (`Pfa=1e-2`: gate `Pd=0.7469` vs raw `0.5284`).

## Main files

- `logs/aistap_manuscript_final_draft_20260715.md`
- `logs/aistap_pure_text_manuscript_20260715.md`
- `logs/aistap_figure_table_final_pack_20260715.md`
- `logs/aistap_manuscript_submission_package_20260715.md`
- `logs/aistap_results_methods_discussion_insert_20260715.md`
- `logs/aistap_submission_figures_20260715.md`
- `figures/main/figure4_official_full_asset_validation_20260715.svg`
- `figures/main/figure5_external_radar_validation_20260715.svg`
- `figures/main/extended_data_figure1_ssdd_robustness_20260715.svg`
- `logs/aistap_next_revision_order_20260715.md`
- `logs/aistap_manuscript_final_draft_20260713.md`
- `logs/aistap_manuscript_draft_20260713.md`
- `logs/aistap_next_revision_order_20260713.md`
- `logs/aistap_experiment_completion_plan_20260713.md`
- `logs/aistap_five_reference_comparison_matrix_20260713.md`
- `logs/aistap_operating_surface_note_20260713.md`
- `logs/aistap_target_preservation_ablation_20260713.md`
- `logs/tpsscs_minimal_train_note_20260713.md`
- `logs/tpsscs_detector_candidate_20260715.md`
- `logs/aistap_full_asset_detector_candidate_simMed_test_20260715.md`
- `logs/aistap_full_asset_detector_candidate_simWind_test_20260715.md`
- `logs/aistap_cross_condition_full_asset_validation_20260715.md`
- `logs/aistap_finished_detector_protocol_20260715.md`
- `logs/aistap_combined_full_asset_protocol_20260715.md`
- `logs/aistap_full_asset_seed_sensitivity_20260717.md`
- `logs/aistap_full_asset_classical_cfar_baselines_20260717.md`
- `logs/aistap_full_asset_classical_cfar_param_sweep_20260717.md`
- `logs/aistap_full_asset_loso_learned_raw_baseline_20260717.md`
- `logs/aistap_full_asset_loso_feature_ensemble_baseline_20260717.md`
- `logs/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.md`
- `logs/aistap_full_asset_loso_low_positive_pixel_hgb_20260717.md`
- `logs/aistap_full_asset_target_free_calibration_20260717.md`
- `logs/aistap_full_asset_frame_level_robustness_20260717.md`
- `logs/aistap_full_asset_paired_significance_20260717.md`
- `logs/aistap_full_asset_log_pfa_auc_20260717.md`
- `logs/aistap_runtime_profile_20260717.md`
- `logs/aistap_claim_consistency_audit_20260717.md`
- `logs/aistap_experimental_quality_assessment_20260717.md`
- `logs/tgrs_submission_readiness_audit_20260717.md`
- `logs/tgrs_submission_metadata_fillin_template_20260717.md`
- `logs/ipix_external_detector_transfer_19931107_135603_starea_20260715.md`
- `logs/ssdd_external_trainable_gate_20260715.md`
- `logs/ssdd_image_level_bootstrap_ci_20260715.md`
- `logs/external_access_and_ipix_transfer_audit_20260715.md`
- `logs/second_external_source_feasibility_20260715.md`
- `logs/aistap_top_readiness_self_check_20260715.md`
- `logs/aistap_top_readiness_self_check_20260717.md`
- `logs/aistap_vs_power_se_battery_comprehensive_comparison_20260715.md`
- `logs/aistap_supplementary_experiment_priority_20260715.md`
- `logs/aistap_recommended_supplementary_completion_20260715.md`
- `logs/aistap_stress_grid_20260713.md`
- `logs/aistap_five_reference_gap_audit_20260713.md`
- `logs/aistap_section_evidence_map_20260713.md`
- `logs/aistap_submission_results_note_20260713.md`
- `logs/aistap_figure_claim_crosswalk_20260713.md`
- `logs/aistap_figure_text_linkage_20260713.md`
- `logs/aistap_figure_results_paragraph_20260713.md`
- `logs/aistap_method_ablation_crosswalk_20260713.md`
- `logs/aistap_manuscript_submission_package_20260715.md`
- `logs/aistap_figure_table_final_pack_20260715.md`
- `logs/aistap_manuscript_submission_package_20260713.md`
- `logs/aistap_figure_table_final_pack_20260713.md`
- `figures/README.md`

## Latest manuscript entry

- `logs/aistap_manuscript_final_draft_20260715.md` is the newest manuscript-facing draft.
- `logs/aistap_pure_text_manuscript_20260715.md` is the current no-figure pure-text manuscript draft.
- `logs/aistap_manuscript_submission_package_20260715.md` is the newest submission-facing package.
- `logs/aistap_results_methods_discussion_insert_20260715.md` is the current ready-to-insert Results/Methods/Discussion block.
- `logs/aistap_next_revision_order_20260715.md` is the active revision order.
- `logs/aistap_experiment_completion_plan_20260713.md` is the active experiment completion plan.
- `logs/aistap_five_reference_comparison_matrix_20260713.md` is the active cross-paper comparison matrix.
- `logs/aistap_operating_surface_note_20260713.md` is the first dense operating-surface result note.
- `logs/aistap_operating_surface_20260713.csv` and `logs/aistap_operating_surface_20260713.json` are the dense operating-surface data artifacts.
- `logs/aistap_target_preservation_ablation_20260713.csv` and `logs/aistap_target_preservation_ablation_20260713.json` are the target-preservation data artifacts.
- `logs/tpsscs_minimal_train_20260713.json` and `logs/tpsscs_minimal_train_curves_20260713.csv` are the minimal trainability data artifacts.
- `logs/tpsscs_minimal_train_multiseed_20260713.md` is the three-seed stability artifact.
- `logs/tpsscs_minimal_train_multiseed_20260713.csv` and `logs/tpsscs_minimal_train_multiseed_20260713.json` are the three-seed stability data artifacts.
- `logs/aistap_stress_grid_multiseed_20260713.md` is the three-seed stress-grid artifact.
- `logs/aistap_stress_grid_multiseed_20260713.csv` and `logs/aistap_stress_grid_multiseed_20260713.json` are the three-seed stress-grid data artifacts.
- `logs/aistap_robustness_dossier_20260713.md` is the consolidated robustness artifact.
- `logs/aistap_subset_loso_cross_condition_20260713.md` is the cross-condition holdout artifact.
- `logs/aistap_external_radar_validation_audit_20260713.md` is the cross-radar-source audit.
- `logs/sevir_year_holdout_external_radar_validation_20260713.md` is the SEVIR year-holdout artifact.
- `logs/aistap_stress_grid_multiseed_20260713.md` is the three-seed stress-grid stability artifact.
- `logs/aistap_figure_table_final_pack_20260715.md` is the newest figure/table delivery pack.

## Figures

- `figures/README.md` is the current figure-package entry.
- `figures/main/` contains the current SVG figure drafts.
- `logs/aistap_sample_preview.png` is the current visual preview asset.

## Directory map

- `cards/` contains claims, evidence, CFAR evidence, and scaffold cards.
- `gates/` contains phase gates.
- `logs/` contains experiment notes, result paragraphs, and manuscript material.
- `data/` contains the public sample and intermediate artifacts.
- `scripts/` contains read, audit, evaluation, and smoke-test scripts.

## Execution principle

- Tighten the boundary before expanding claims.
- Make the public sample and scaffold robust before writing stronger conclusions.
- Every new claim must map back to `logs/`, `cards/`, or `gates/` evidence.

