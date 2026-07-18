# AISTAP Full-Asset LOSO Learned Raw-Feature Baseline

Date: 20260717

## Verdict

- Passed: `true`
- Learned baseline: `loso_supervised_raw_feature_logreg`
- Proposed method: `tpsscs_finished_detector`
- Held-out target-bearing items: `210`
- Asset-level wins vs learned baseline: `14/14`
- Combined wins vs learned baseline: `7/7`
- Minimum combined delta vs learned baseline: `0.0596`
- Minimum asset-level delta vs learned baseline: `0.0448`
- All Pfa calibrated: `true`

## Protocol

- Train a supervised logistic detector on raw-score local features from one official full asset.
- Test it on the other official full asset, then swap train/test assets.
- Score calibration uses the same conservative per-frame background thresholding policy as the TP-SSCS full-asset protocol.
- The learned baseline uses only raw-score derived local features; it does not use TP-SSCS residuals or target coordinates.

## Training Directions

| Train asset | Test asset | Frames | Positive frames | Positive pixels | Background pixels |
|---|---|---:|---:|---:|---:|
| `simMed_test.mat` | `simWind_test.mat` | 128 | 105 | 3943 | 262144 |
| `simWind_test.mat` | `simMed_test.mat` | 128 | 105 | 3943 | 262144 |

## Combined Comparisons

| Pfa | TP-SSCS Pd | Learned Pd | Raw Pd | Low-rank Pd | Delta vs learned | Learned empirical Pfa |
|---:|---:|---:|---:|---:|---:|---:|
| 1e-05 | 0.1845 | 0.0741 | 0.0800 | 0.1015 | 0.1104 | 0 |
| 3e-05 | 0.2358 | 0.1156 | 0.1210 | 0.1571 | 0.1202 | 1.43224e-05 |
| 1e-04 | 0.3682 | 0.2427 | 0.2049 | 0.3026 | 0.1255 | 9.08054e-05 |
| 3e-04 | 0.5261 | 0.3918 | 0.2809 | 0.4722 | 0.1343 | 0.000289792 |
| 1e-03 | 0.7029 | 0.5876 | 0.3771 | 0.6592 | 0.1152 | 0.00099239 |
| 3e-03 | 0.8130 | 0.6985 | 0.4865 | 0.7778 | 0.1145 | 0.00299244 |
| 1e-02 | 0.8678 | 0.8082 | 0.6551 | 0.8388 | 0.0596 | 0.00999282 |

## Bootstrap CI

| Pfa | n | Mean TP-SSCS minus learned Pd | 95% CI | Positive fraction |
|---:|---:|---:|---:|---:|
| 1e-05 | 210 | 0.1104 | [0.0990, 0.1217] | 0.890 |
| 3e-05 | 210 | 0.1202 | [0.1084, 0.1326] | 0.900 |
| 1e-04 | 210 | 0.1255 | [0.1119, 0.1394] | 0.871 |
| 3e-04 | 210 | 0.1343 | [0.1160, 0.1520] | 0.862 |
| 1e-03 | 210 | 0.1152 | [0.0913, 0.1376] | 0.738 |
| 3e-03 | 210 | 0.1145 | [0.0917, 0.1371] | 0.767 |
| 1e-02 | 210 | 0.0596 | [0.0402, 0.0771] | 0.671 |

## Boundary

- This is not a benchmark against large pretrained radar detectors; it is a supervised, leave-one-condition-out learned detector baseline using the official AISTAP-SIM full assets.
- The test asset is never used to fit the learned baseline in its corresponding direction.
- The result addresses the narrow criticism that the paper only beats hand-designed CFAR variants on the official full assets.
