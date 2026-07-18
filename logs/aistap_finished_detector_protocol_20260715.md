# AISTAP Finished Detector Protocol Gate

Date: 20260715

## Verdict

- Passed: `true`
- Input: `C:\Users\鍒樺瓙杞‐Desktop\绗笁鎵?\results\aistap_full_asset\aistap_full_asset_detector_candidate_simMed_test_20260715.csv`
- Target-bearing items: `105`
- TP-SSCS method: `tpsscs_finished_detector`
- Low-rank comparator: `low_rank_residual_k30`

## Criteria

- Minimum target-bearing items: `100`
- Pfa calibration tolerance: `1.05`
- Wins vs raw: `7`
- Wins vs rank-matched low-rank: `7`

## Pfa Comparisons

| Pfa | TP-SSCS Pd | Raw Pd | Low-rank Pd | Beats raw | Beats low-rank |
|---:|---:|---:|---:|---:|---:|
| 1e-05 | 0.1845 | 0.0783 | 0.0989 | `true` | `true` |
| 3e-05 | 0.2329 | 0.1149 | 0.1504 | `true` | `true` |
| 1e-04 | 0.3631 | 0.1956 | 0.2944 | `true` | `true` |
| 3e-04 | 0.5155 | 0.2686 | 0.4575 | `true` | `true` |
| 1e-03 | 0.6958 | 0.3569 | 0.6488 | `true` | `true` |
| 3e-03 | 0.8139 | 0.4673 | 0.7764 | `true` | `true` |
| 1e-02 | 0.8692 | 0.6340 | 0.8383 | `true` | `true` |

## Failures

- None.

## Boundary

- Passing this gate means the saved model state has a fixed, reproducible in-domain full-test detector protocol.
- It does not by itself prove independent external validation or superiority over the local battery external-validation stack.
