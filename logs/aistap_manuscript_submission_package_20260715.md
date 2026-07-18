# AISTAP Manuscript Submission Package

Date: 2026-07-15

## Title

Target-preserving low-false-alarm radar detection under clutter suppression

## One-line Takeaway

TP-SSCS reframes radar clutter suppression as target-preserving low-false-alarm detection and is supported by official AISTAP-SIM full-asset validation plus bounded IPIX and SSDD external radar-family tests.

## Highlights

- Low-rank suppression improves clutter attenuation but can erase weak targets, so clutter removal alone is the wrong operational objective.
- Dense CFAR operating surfaces show that the best suppression rank depends on the target false-alarm regime.
- The trainable target-preservation branch cuts public-sample target loss from `6.191 dB` for the low-rank residual baseline to `0.197 dB` while keeping comparable detection behavior.
- The official combined full-asset gate passes on `210` target-bearing frames across `simMed_test.mat` and `simWind_test.mat`.
- The combined full-asset protocol gives `7/7` wins versus raw and `7/7` wins versus rank-matched low-rank residuals.
- IPIX direct zero-shot transfer is negative and should be reported as a boundary.
- IPIX validation-selected residual-aware fusion passes on `12` disjoint held-out recordings with `7/7` Pfa wins versus raw and low-rank.
- SSDD supervised trainable-gate adaptation passes on `231` official-test images and `545` ship annotations, with `4` wins, `3` ties, and `0` losses versus raw, plus `7/7` wins versus low-rank.
- SSDD image-level and annotation-level bootstrap CIs show that non-fallback raw gains and all low-rank gains are not only pooled-pixel artifacts.
- The current automatic top-readiness self-check returns `top_ready` with `0` hard failures.

## Core Claims

1. The correct framing is target-preserving, low-false-alarm detection, not clutter cancellation alone.
2. TP-SSCS improves the official AISTAP-SIM full-asset detector operating curve relative to raw and low-rank residual baselines.
3. IPIX supports validation-selected residual-aware fusion on held-out recordings, not unmodified zero-shot transfer.
4. SSDD supports supervised external trainable-gate adaptation on SAR ship imagery, not zero-shot transfer of the AISTAP-SIM saved state.
5. The paper is now experimentally ready for a high-impact submission route, pending final manuscript integration and figure production.

## Claim Boundaries

- Do not claim production-ready radar deployment.
- Do not claim universal sea-clutter suppression.
- Do not claim direct zero-shot transfer success on IPIX.
- Do not claim SSDD is zero-shot transfer.
- Do not treat SEVIR, MRMS, MeteoNet, or NEXRAD audit files as TP-SSCS transfer results unless a TP-SSCS protocol is actually run there.
- Do not present the automatic `top_ready` gate as a journal acceptance guarantee.

## Main Evidence Files

- `logs/aistap_manuscript_final_draft_20260715.md`
- `logs/aistap_figure_table_final_pack_20260715.md`
- `logs/aistap_combined_full_asset_protocol_20260715.md`
- `logs/ipix_validated_residual_fusion_20260715.md`
- `logs/ssdd_external_trainable_gate_20260715.md`
- `logs/ssdd_image_level_bootstrap_ci_20260715.md`
- `logs/aistap_top_readiness_self_check_20260715.md`
- `logs/aistap_recommended_supplementary_completion_20260715.md`
- `claim_matrix.md`

## Immediate Submission Tasks

1. Generate or update Figure 4 from `results/aistap_full_asset/aistap_combined_full_asset_protocol_20260715.csv` and `results/aistap_full_asset/aistap_combined_full_asset_bootstrap_ci_20260715.csv`.
2. Generate or update Figure 5 from IPIX and SSDD external-validation CSVs.
3. Convert the SSDD image/annotation-level CI table into an Extended Data figure or supplement table.
4. Replace the old public-sample-only abstract with the 2026-07-15 abstract.
5. Update Methods to include the official full-asset protocol, IPIX validation-selected fusion, and SSDD supervised adaptation.
6. Keep the limitations paragraph explicit: IPIX zero-shot negative; SSDD supervised adaptation only.

