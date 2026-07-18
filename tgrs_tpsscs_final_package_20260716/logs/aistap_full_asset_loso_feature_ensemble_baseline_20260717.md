# AISTAP Full-Asset LOSO Feature-Ensemble Learned Baseline

Date: 20260717

## Verdict

- Passed: `false`
- Learned baseline: `loso_supervised_raw_residual_hgb`
- Proposed method: `tpsscs_finished_detector`
- Held-out target-bearing items: `210`
- Asset-level wins vs learned baseline: `0/14`
- Combined wins vs learned baseline: `0/7`
- Minimum combined delta vs learned baseline: `-0.2876`
- Minimum asset-level delta vs learned baseline: `-0.2950`
- Bootstrap CI lower bounds positive: `false`
- All Pfa calibrated: `true`

## Protocol

- Train a nonlinear histogram-gradient-boosting detector on one official full asset.
- Test it on the other official full asset, then swap train/test assets.
- Features include raw power, rank-30 low-rank residual power, local z-scores, local contrasts, gradient magnitudes, and raw/residual cross-features.
- Score calibration uses the same conservative per-frame background thresholding policy as the TP-SSCS full-asset protocol.
- The learned baseline does not use TP-SSCS gate scores or target coordinates at test time.

## Training Directions

| Train asset | Test asset | Frames | Positive frames | Positive pixels | Background pixels |
|---|---|---:|---:|---:|---:|
| `simMed_test.mat` | `simWind_test.mat` | 128 | 105 | 3943 | 524288 |
| `simWind_test.mat` | `simMed_test.mat` | 128 | 105 | 3943 | 524288 |

## Combined Comparisons

| Pfa | TP-SSCS Pd | Learned HGB Pd | Raw Pd | Low-rank Pd | Delta vs learned | Learned empirical Pfa |
|---:|---:|---:|---:|---:|---:|---:|
| 1e-05 | 0.1845 | 0.3052 | 0.0800 | 0.1015 | -0.1207 | 0 |
| 3e-05 | 0.2358 | 0.4109 | 0.1210 | 0.1571 | -0.1750 | 1.52675e-05 |
| 1e-04 | 0.3682 | 0.6558 | 0.2049 | 0.3026 | -0.2876 | 9.16052e-05 |
| 3e-04 | 0.5261 | 0.7833 | 0.2809 | 0.4722 | -0.2572 | 0.000290083 |
| 1e-03 | 0.7029 | 0.8707 | 0.3771 | 0.6592 | -0.1678 | 0.00099239 |
| 3e-03 | 0.8130 | 0.9243 | 0.4865 | 0.7778 | -0.1112 | 0.00299244 |
| 1e-02 | 0.8678 | 0.9622 | 0.6551 | 0.8388 | -0.0944 | 0.00999282 |

## Bootstrap CI

| Pfa | n | Mean TP-SSCS minus learned Pd | 95% CI | Positive fraction |
|---:|---:|---:|---:|---:|
| 1e-05 | 210 | -0.1207 | [-0.1451, -0.0952] | 0.290 |
| 3e-05 | 210 | -0.1750 | [-0.1996, -0.1500] | 0.157 |
| 1e-04 | 210 | -0.2876 | [-0.3104, -0.2661] | 0.014 |
| 3e-04 | 210 | -0.2572 | [-0.2786, -0.2377] | 0.019 |
| 1e-03 | 210 | -0.1678 | [-0.1826, -0.1541] | 0.014 |
| 3e-03 | 210 | -0.1112 | [-0.1254, -0.0980] | 0.043 |
| 1e-02 | 210 | -0.0944 | [-0.1067, -0.0833] | 0.024 |

## Boundary

- This is stronger than the raw-feature logistic LOSO baseline because it uses nonlinear boosted trees and both raw and low-rank residual local features.
- It is still an in-domain AISTAP-SIM learned baseline, not a large pretrained radar detector and not an independent non-AISTAP zero-shot test.
- The result addresses whether TP-SSCS only wins against hand-designed or linear learned comparators on the official full assets.
