# AISTAP Full-Asset LOSO TP-SSCS-Feature Ensemble

Date: 20260717

## Verdict

- Passed gain vs raw/residual HGB: `false`
- TP-SSCS-feature HGB: `loso_supervised_tpsscs_feature_hgb`
- Baseline HGB: `loso_supervised_raw_residual_hgb`
- Held-out target-bearing items: `210`
- Asset-level wins vs raw/residual HGB: `11/14`
- Combined wins vs raw/residual HGB: `6/7`
- Minimum combined delta vs raw/residual HGB: `-0.0007`
- Minimum combined delta vs compact TP-SSCS: `0.0971`
- CI lower bounds positive vs raw/residual HGB: `false`
- CI lower bounds positive vs compact TP-SSCS: `true`
- All Pfa calibrated: `true`

## Protocol

- Train a nonlinear histogram-gradient-boosting detector on one official full asset and test on the other.
- Features include raw power, rank-30 low-rank residual power, compact TP-SSCS enhanced score, TP-SSCS gate map, local z-scores, local contrasts, gradients, and cross-features.
- The baseline comparator is the raw/residual HGB trained and evaluated by the same LOSO protocol.
- The test asset is not used for fitting in its corresponding direction.

## Training Directions

| Train asset | Test asset | Frames | Positive frames | Positive pixels | Background pixels |
|---|---|---:|---:|---:|---:|
| `simMed_test.mat` | `simWind_test.mat` | 128 | 105 | 3943 | 524288 |
| `simWind_test.mat` | `simMed_test.mat` | 128 | 105 | 3943 | 524288 |

## Combined Comparisons

| Pfa | TP-SSCS-feature HGB Pd | Raw/residual HGB Pd | Compact TP-SSCS Pd | Delta vs HGB | Delta vs compact |
|---:|---:|---:|---:|---:|---:|
| 1e-05 | 0.3396 | 0.3052 | 0.1845 | 0.0343 | 0.1550 |
| 3e-05 | 0.4500 | 0.4109 | 0.2358 | 0.0392 | 0.2142 |
| 1e-04 | 0.6558 | 0.6558 | 0.3682 | 0.0000 | 0.2876 |
| 3e-04 | 0.7826 | 0.7833 | 0.5261 | -0.0007 | 0.2564 |
| 1e-03 | 0.8776 | 0.8707 | 0.7029 | 0.0069 | 0.1747 |
| 3e-03 | 0.9281 | 0.9243 | 0.8130 | 0.0039 | 0.1151 |
| 1e-02 | 0.9649 | 0.9622 | 0.8678 | 0.0027 | 0.0971 |

## Bootstrap CI

| Pfa | Comparator | n | Mean Delta Pd | 95% CI | Positive fraction |
|---:|---|---:|---:|---:|---:|
| 1e-05 | `loso_supervised_raw_residual_hgb` | 210 | 0.0343 | [0.0166, 0.0519] | 0.600 |
| 1e-05 | `tpsscs_finished_detector` | 210 | 0.1550 | [0.1299, 0.1787] | 0.771 |
| 3e-05 | `loso_supervised_raw_residual_hgb` | 210 | 0.0392 | [0.0242, 0.0544] | 0.624 |
| 3e-05 | `tpsscs_finished_detector` | 210 | 0.2142 | [0.1917, 0.2370] | 0.905 |
| 1e-04 | `loso_supervised_raw_residual_hgb` | 210 | 0.0000 | [-0.0087, 0.0087] | 0.400 |
| 1e-04 | `tpsscs_finished_detector` | 210 | 0.2876 | [0.2663, 0.3093] | 0.976 |
| 3e-04 | `loso_supervised_raw_residual_hgb` | 210 | -0.0007 | [-0.0067, 0.0057] | 0.371 |
| 3e-04 | `tpsscs_finished_detector` | 210 | 0.2564 | [0.2371, 0.2765] | 0.976 |
| 1e-03 | `loso_supervised_raw_residual_hgb` | 210 | 0.0069 | [0.0027, 0.0111] | 0.371 |
| 1e-03 | `tpsscs_finished_detector` | 210 | 0.1747 | [0.1612, 0.1894] | 0.967 |
| 3e-03 | `loso_supervised_raw_residual_hgb` | 210 | 0.0039 | [-0.0000, 0.0077] | 0.314 |
| 3e-03 | `tpsscs_finished_detector` | 210 | 0.1151 | [0.1016, 0.1296] | 0.910 |
| 1e-02 | `loso_supervised_raw_residual_hgb` | 210 | 0.0027 | [0.0001, 0.0053] | 0.214 |
| 1e-02 | `tpsscs_finished_detector` | 210 | 0.0971 | [0.0851, 0.1101] | 0.919 |

## Boundary

- This audit tests whether TP-SSCS-derived features add value to a strong in-domain supervised HGB detector.
- It does not establish zero-shot external transfer or replace the compact TP-SSCS fixed-detector result.
- If positive, it supports TP-SSCS as a target-preserving feature construction as well as a compact detector policy.
