# AISTAP Recommended Supplementary Completion Audit

Date: 2026-07-15

## Verdict

- Recommended supplement status: `completed_for_low-risk_high-value_items`.
- Completed item 1: SSDD image-level / annotation-level robustness and bootstrap CI.
- Completed item 2: combined official AISTAP-SIM full-asset protocol gate over `simMed_test.mat` and `simWind_test.mat`.
- Current interpretation: these additions strengthen reviewer-facing robustness and uncertainty reporting; they do not change the core claim boundary.

## Completed Experiments

| Experiment | Output | Result |
|---|---|---:|
| SSDD image-level / annotation-level bootstrap CI | `logs/ssdd_image_level_bootstrap_ci_20260715.md` | `pass` |
| SSDD image-level rows | `results/ssdd_external/ssdd_image_level_robustness_20260715.csv` | `231` images |
| SSDD annotation-level rows | `results/ssdd_external/ssdd_annotation_level_robustness_20260715.csv` | `545` annotations |
| SSDD image/annotation bootstrap CI | `results/ssdd_external/ssdd_image_annotation_bootstrap_ci_20260715.csv` | `pass` |
| Combined AISTAP full-asset gate | `logs/aistap_combined_full_asset_protocol_20260715.md` | `pass` |
| Combined AISTAP full-asset CI | `results/aistap_full_asset/aistap_combined_full_asset_bootstrap_ci_20260715.csv` | `pass` |

## Key Numbers

### SSDD

- Official-test images: `231`.
- Official-test annotations: `545`.
- Image-level raw fallback points at `Pfa <= 1e-4`: exact no-regression ties vs raw by design.
- Image-level non-fallback raw comparisons:
  - `Pfa=3e-4`: mean delta Pd `0.1222`, 95% CI `[0.0986, 0.1449]`.
  - `Pfa=1e-3`: mean delta Pd `0.1596`, 95% CI `[0.1345, 0.1852]`.
  - `Pfa=3e-3`: mean delta Pd `0.2448`, 95% CI `[0.2178, 0.2720]`.
  - `Pfa=1e-2`: mean delta Pd `0.2182`, 95% CI `[0.1962, 0.2386]`.
- Image-level comparisons vs low-rank have positive 95% CI at every Pfa.
- Annotation-level comparisons show the same qualitative pattern across `545` ship annotations.

### Combined AISTAP Full Assets

- Assets: `simMed_test.mat`, `simWind_test.mat`.
- Combined target-bearing items: `210`.
- Asset-level wins vs raw: `14/14`.
- Asset-level wins vs low-rank: `14/14`.
- Combined wins vs raw: `7/7`.
- Combined wins vs low-rank: `7/7`.
- All Pfa points are calibrated under the protocol tolerance.

## Claim Boundary

- SSDD remains supervised external trainable-gate adaptation, not zero-shot transfer of the saved AISTAP-SIM state.
- The combined full-asset gate is official in-domain AISTAP-SIM evidence, not an independent external dataset.
- These additions are suitable for supplementary robustness/uncertainty reporting and for tightening the Results/Methods claims.

## Remaining Optional Work

- Final-state seed/rank/hidden sensitivity on full assets remains optional and medium risk.
- Additional classical detector baselines remain optional and higher risk unless implemented with identical Pfa calibration.
- No further broad data-source search is recommended unless a clean, scriptable radar dataset is already available.

