# AISTAP Submission Figure Generation

Date: 20260715

## Figure Contract

- Figure 4 conclusion: the official AISTAP-SIM full-asset detector gate passes with calibrated Pfa and positive paired bootstrap support.
- Figure 5 conclusion: IPIX and SSDD provide bounded external radar-family support, with explicit zero-shot and supervised-adaptation boundaries.
- Extended Data Figure 1 conclusion: SSDD gains are visible at image and annotation levels, not only in pooled-pixel aggregates.

## Outputs

### Figure 4
- `figures\main\figure4_official_full_asset_validation_20260715.svg`
- `figures\main\figure4_official_full_asset_validation_20260715.pdf`
- `figures\main\figure4_official_full_asset_validation_20260715.png`

### Figure 5
- `figures\main\figure5_external_radar_validation_20260715.svg`
- `figures\main\figure5_external_radar_validation_20260715.pdf`
- `figures\main\figure5_external_radar_validation_20260715.png`

### Extended Data Figure 1
- `figures\main\extended_data_figure1_ssdd_robustness_20260715.svg`
- `figures\main\extended_data_figure1_ssdd_robustness_20260715.pdf`
- `figures\main\extended_data_figure1_ssdd_robustness_20260715.png`

## Draft Figure Legends

### Figure 4 | Official AISTAP-SIM full-asset detector validation

a, Combined detector operating curves over `simMed_test.mat` and `simWind_test.mat` show TP-SSCS, raw maps, and rank-matched low-rank residuals across seven target Pfa values. b, Paired bootstrap confidence intervals over 210 target-bearing frames show positive mean delta Pd for TP-SSCS versus both comparators. c, Asset-level heatmap shows positive delta Pd on both official full-test assets and against both comparator families. d, Empirical Pfa remains within the protocol ceiling across the combined full-asset operating points.

### Figure 5 | Bounded external radar-family validation

a, IPIX held-out recordings show validation-selected residual-aware fusion against raw and low-rank residual baselines; direct zero-shot transfer is retained as a negative boundary. b, Recording-level bootstrap confidence intervals show positive mean delta Pd for the IPIX fusion policy. c, SSDD official-test SAR ship imagery shows supervised trainable-gate adaptation against raw and low-rank baselines. d, SSDD image-level bootstrap confidence intervals show no-regression raw fallback at extreme low Pfa and positive non-fallback gains.

### Extended Data Figure 1 | SSDD image- and annotation-level robustness

Image-level and annotation-level boxplots show the distribution of SSDD detection-probability gains against raw at non-fallback Pfa points and against low-rank residuals across all Pfa points. Box centres show medians, boxes show interquartile ranges, whiskers exclude plotted outliers, and filled circles mark means.

## Source Data

- `results/aistap_full_asset/aistap_combined_full_asset_protocol_20260715.csv`
- `results/aistap_full_asset/aistap_combined_full_asset_bootstrap_ci_20260715.csv`
- `results/ipix_external/ipix_validated_residual_fusion_test_20260715.csv`
- `results/aistap_supplementary/ipix_heldout_bootstrap_delta_ci_20260715.csv`
- `results/ssdd_external/ssdd_external_trainable_gate_20260715.csv`
- `results/ssdd_external/ssdd_image_annotation_bootstrap_ci_20260715.csv`
- `results/ssdd_external/ssdd_image_level_robustness_20260715.csv`
- `results/ssdd_external/ssdd_annotation_level_robustness_20260715.csv`

## Boundary

- IPIX zero-shot transfer remains negative and is annotated as a boundary.
- SSDD is supervised external adaptation, not zero-shot saved-state transfer.
- The figures visualize existing result artifacts only; no synthetic data are generated.