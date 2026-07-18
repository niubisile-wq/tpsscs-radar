# AISTAP Figure/Table Final Pack

Date: 2026-07-15

This pack updates the figure and table plan after the official full-asset gate, IPIX held-out validation, SSDD SAR adaptation, and SSDD image/annotation-level bootstrap supplement.

## Figure 1. Problem framing and TP-SSCS pipeline

Purpose:
- Show the target-preserving low-false-alarm framing, the raw range-Doppler input, target-only reference, low-rank residual baseline, trainable gate, and CFAR-calibrated detector output.

Key claim:
- The paper is about target-preserving detection under false-alarm control, not clutter removal alone.

Source evidence:
- `logs/aistap_sample_preview.png`
- `logs/tpsscs_smoke_report.txt`
- `logs/aistap_method_ablation_crosswalk_20260713.md`
- `claim_matrix.md`

## Figure 2. Target-preservation frontier

Purpose:
- Show how raw, low-rank residual, oracle diagnostics, and the trainable gate move the target-loss / Pd frontier.

Key claim:
- Target preservation changes the frontier; the trainable gate is the first concrete manuscript-facing branch.

Source evidence:
- `logs/aistap_target_preservation_ablation_20260713.md`
- `logs/aistap_target_preservation_ablation_20260713.csv`
- `results/aistap_sample/aistap_target_preservation_ablation_ranks5_20_30_alphas0_0.25_0.5_0.75_1_gates50_70_80_90_95_pfas1e-5_3e-5_1e-4_3e-4_1e-3_3e-3_1e-2.csv`
- `figures/main/figure2_target_preservation_frontier.svg`

## Figure 3. Dense low-Pfa operating surface

Purpose:
- Show `Pd` versus suppression rank across a dense `Pfa` grid.

Key claim:
- The best operating point depends jointly on false-alarm target and suppression rank.

Source evidence:
- `logs/aistap_operating_surface_note_20260713.md`
- `logs/aistap_operating_surface_20260713.csv`
- `figures/main/figure3_operating_surface.svg`

## Figure 4. Official AISTAP-SIM full-asset detector validation

Purpose:
- Show the finished detector protocol on `simMed_test.mat` and `simWind_test.mat`, including combined bootstrap confidence intervals.

Key claim:
- The same saved state and `tpsscs_finished_detector` policy pass the official full-asset gate across 210 target-bearing frames.

Source evidence:
- `logs/aistap_finished_detector_protocol_20260715.md`
- `logs/aistap_cross_condition_full_asset_validation_20260715.md`
- `logs/aistap_combined_full_asset_protocol_20260715.md`
- `results/aistap_full_asset/aistap_combined_full_asset_protocol_20260715.csv`
- `results/aistap_full_asset/aistap_combined_full_asset_bootstrap_ci_20260715.csv`

Generated assets:
- `figures/main/figure4_official_full_asset_validation_20260715.svg`
- `figures/main/figure4_official_full_asset_validation_20260715.pdf`
- `figures/main/figure4_official_full_asset_validation_20260715.png`

Recommended panels:
- 4a: `Pd` versus `Pfa` for TP-SSCS, raw, and low-rank on the combined official full-test assets.
- 4b: paired mean delta Pd versus raw with 95% bootstrap CI.
- 4c: paired mean delta Pd versus low-rank with 95% bootstrap CI.
- 4d: calibration table or inset showing empirical Pfa remains within protocol tolerance.

## Figure 5. Independent radar-family external validation

Purpose:
- Present IPIX held-out residual-aware fusion and SSDD SAR supervised adaptation as two bounded external radar-family tests.

Key claim:
- External evidence supports bounded radar-family generalization/adaptation, but not unmodified zero-shot transfer.

Source evidence:
- `logs/ipix_validated_residual_fusion_20260715.md`
- `results/ipix_external/ipix_validated_residual_fusion_test_20260715.csv`
- `results/aistap_supplementary/ipix_heldout_bootstrap_delta_ci_20260715.csv`
- `logs/ssdd_external_trainable_gate_20260715.md`
- `logs/ssdd_image_level_bootstrap_ci_20260715.md`
- `results/ssdd_external/ssdd_image_annotation_bootstrap_ci_20260715.csv`

Generated assets:
- `figures/main/figure5_external_radar_validation_20260715.svg`
- `figures/main/figure5_external_radar_validation_20260715.pdf`
- `figures/main/figure5_external_radar_validation_20260715.png`

Recommended panels:
- 5a: IPIX held-out `Pd` versus `Pfa` for raw, low-rank, and residual-aware fusion.
- 5b: IPIX recording-level bootstrap delta Pd against raw and low-rank.
- 5c: SSDD aggregate `Pd` versus `Pfa` for candidate, raw, and low-rank.
- 5d: SSDD image-level bootstrap delta Pd at non-fallback Pfa points.

## Extended Data Figure 1. SSDD robustness localization

Purpose:
- Show the distribution of per-image and per-annotation gains.

Key claim:
- SSDD gains are not only pooled-pixel artifacts; non-fallback raw comparisons and all low-rank comparisons have positive bootstrap support.

Source evidence:
- `results/ssdd_external/ssdd_image_level_robustness_20260715.csv`
- `results/ssdd_external/ssdd_annotation_level_robustness_20260715.csv`
- `results/ssdd_external/ssdd_image_annotation_bootstrap_ci_20260715.csv`

Generated assets:
- `figures/main/extended_data_figure1_ssdd_robustness_20260715.svg`
- `figures/main/extended_data_figure1_ssdd_robustness_20260715.pdf`
- `figures/main/extended_data_figure1_ssdd_robustness_20260715.png`

## Table 1. Low-rank suppression trade-off

Purpose:
- Report clutter attenuation, target loss, and target retention ratio by subset and rank.

## Table 2. Official full-asset detector results

Purpose:
- Report combined TP-SSCS, raw, and low-rank `Pd`, empirical `Pfa`, and delta Pd across all seven Pfa points.

Source evidence:
- `results/aistap_full_asset/aistap_combined_full_asset_protocol_20260715.csv`

## Table 3. External validation summary

Purpose:
- Summarize IPIX and SSDD without overclaiming their protocol boundaries.

Rows:
- IPIX zero-shot: negative boundary result.
- IPIX validation-selected residual-aware fusion: positive held-out result.
- SSDD supervised trainable-gate adaptation: positive official-test result.
- SSDD image/annotation-level CI: robustness supplement.

## Table 4. Claim-boundary table

Purpose:
- Separate supported claims from unsupported claims.

Source evidence:
- `claim_matrix.md`
- `logs/aistap_top_readiness_self_check_20260715.md`
- `logs/aistap_recommended_supplementary_completion_20260715.md`

## Submission Usage

- Keep Figures 1-3 as the method-design and in-domain operating-policy story.
- Make Figure 4 the new main evidence figure for official full-asset validation.
- Make Figure 5 the external-validation figure.
- Put the SSDD per-image/per-annotation distributions in Extended Data unless space allows a compact main-panel inset.
- Do not present IPIX zero-shot as a success.
- Do not present SSDD as zero-shot transfer.
