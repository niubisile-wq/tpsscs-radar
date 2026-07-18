# AISTAP Top-Readiness Self Check

Date: 20260715

## Verdict

- Overall: `top_ready`
- Hard failures: `0`

## Gate Table

| Gate | Status | Hard | Evidence | Detail |
|---|---:|---:|---|---|
| reproducibility_package | `pass` | `false` | claim_matrix.md, README.md, STATUS.md, logs\aistap_final_go_no_go_gate_20260713.md, logs\aistap_top_ready_completion_audit_20260715.md, logs\aistap_final_comparison_scorecard_20260713.md, logs\aistap_manuscript_final_draft_20260715.md, logs\aistap_figure_table_final_pack_20260715.md, logs\aistap_manuscript_submission_package_20260715.md, results\aistap_sample\aistap_operating_surface_20260713.csv | all core package artifacts exist |
| deployable_candidate_artifact | `pass` | `true` | results\aistap_sample\tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt | saved trainable-gate state exists; this supports reproducibility of the candidate branch |
| target_preservation_frontier | `pass` | `false` | results\aistap_sample\aistap_target_preservation_ablation_ranks5_20_30_alphas0_0.25_0.5_0.75_1_gates50_70_80_90_95_pfas1e-5_3e-5_1e-4_3e-4_1e-3_3e-3_1e-2.csv | trainable gate improves the low-rank frontier at pfa=0.01: Pd 1.0000 vs 0.9767, target loss 0.393 vs 3.715 dB |
| top_tier_sample_scale | `pass` | `true` | logs\aistap_cross_condition_full_asset_validation_20260715.json | 210 target-bearing full-asset items evaluated across 2 official assets; top-tier gate requires >=100 or an independent external dataset |
| cross_condition_holdout | `partial` | `false` | results\aistap_sample\aistap_subset_loso_cross_condition_rank30_hidden16_steps150_lr0p02_summary.csv | trainable gate finite on 3 holdouts; wins/ties low-rank on 1 holdouts at Pfa=1e-2 |
| aistap_external_method_validation | `pass` | `true` | logs\aistap_cross_condition_full_asset_validation_20260715.json, results\aistap_full_asset\aistap_combined_full_asset_protocol_20260715.json, results\ipix_external\ipix_validated_residual_fusion_20260715.json, results\ipix_external\ipix_external_detector_transfer_19931107_135603_starea_20260715.json, results\ssdd_external\ssdd_external_trainable_gate_20260715.json, results\ssdd_external\ssdd_image_level_bootstrap_ci_20260715.json, logs\ssdd_external_trainable_gate_20260715.md, logs\ssdd_image_level_bootstrap_ci_20260715.md, logs\external_access_and_ipix_transfer_audit_20260715.md, logs\aistap_external_radar_validation_audit_20260713.md, logs\sevir_year_holdout_external_radar_validation_20260713.md, logs\nexrad_public_window_leaderboard_20260714.md | AISTAP-SIM cross-condition full-asset validation passed on 2 official assets; combined official full-asset protocol passed on 210 target-bearing items (7/7 combined Pfa wins vs raw and low-rank); independent IPIX validated residual-aware fusion passed on 12 held-out recordings (7/7 Pfa wins vs raw); official SSDD SAR external trainable-gate validation passed on 231 test images/545 ship annotations (4 wins, 3 ties, 0 losses vs raw); SSDD image/annotation-level bootstrap CI supplement passed on 231 images/545 annotations; this gives one official in-domain full-asset layer and two independent external radar dataset families |
| local_reference_superiority | `pass` | `true` | logs\aistap_cross_paper_scorecard_20260713.md; power_se/STATUS.md; battery/BATTERY_EXTERNAL_VALIDATION_ONE_PAGER_20260713.md; results\ipix_external\ipix_validated_residual_fusion_20260715.json; results\ssdd_external\ssdd_external_trainable_gate_20260715.json; results\ssdd_external\ssdd_image_level_bootstrap_ci_20260715.json | AISTAP is ahead on detector operating-policy density and now has two positive independent external radar families: IPIX over 12 disjoint held-out recordings (7/7 Pfa wins vs raw, 7/7 vs low-rank) and official SSDD over 231 test images/545 ship annotations (4 wins, 3 ties, 0 losses vs raw; 7/7 wins vs low-rank). The SSDD image/annotation-level CI supplement also passes. This closes the local reference superiority gate against the selected power and battery packages |
| finished_detector_result | `pass` | `true` | logs\aistap_finished_detector_protocol_20260715.json | finished-detector protocol gate passed on 105 target-bearing full-asset items |

## CAS Q1 Top Interpretation

All hard gates passed. The package can be treated as top-readiness candidate evidence, pending manuscript-level review.