# AISTAP Combined Full-Asset Protocol Gate

Date: 20260715

## Verdict

- Passed: `true`
- Assets: `simMed_test.mat, simWind_test.mat`
- Combined target-bearing items: `210`
- Asset-level wins vs raw: `14/14`
- Asset-level wins vs low-rank: `14/14`
- Combined wins vs raw: `7/7`
- Combined wins vs low-rank: `7/7`
- All Pfa calibrated: `true`

## Combined Comparisons

| Pfa | TP-SSCS Pd | Raw Pd | Low-rank Pd | Delta vs raw | Delta vs low-rank | Empirical Pfa |
|---:|---:|---:|---:|---:|---:|---:|
| 1e-05 | 0.1845 | 0.0800 | 0.1015 | 0.1046 | 0.0831 | 0 |
| 3e-05 | 0.2358 | 0.1210 | 0.1571 | 0.1148 | 0.0788 | 1.52675e-05 |
| 1e-04 | 0.3682 | 0.2049 | 0.3026 | 0.1633 | 0.0656 | 9.16052e-05 |
| 3e-04 | 0.5261 | 0.2809 | 0.4722 | 0.2452 | 0.0539 | 0.000290083 |
| 1e-03 | 0.7029 | 0.3771 | 0.6592 | 0.3258 | 0.0436 | 0.00099239 |
| 3e-03 | 0.8130 | 0.4865 | 0.7778 | 0.3266 | 0.0353 | 0.00299244 |
| 1e-02 | 0.8678 | 0.6551 | 0.8388 | 0.2127 | 0.0290 | 0.00999282 |

## Combined Bootstrap CI

| Pfa | Comparator | n | Mean Delta Pd | 95% CI | Positive fraction |
|---:|---|---:|---:|---:|---:|
| 1e-05 | `raw` | 210 | 0.1046 | [0.0942, 0.1152] | 0.895 |
| 1e-05 | `low_rank_residual_k30` | 210 | 0.0831 | [0.0751, 0.0909] | 0.929 |
| 3e-05 | `raw` | 210 | 0.1148 | [0.1019, 0.1278] | 0.890 |
| 3e-05 | `low_rank_residual_k30` | 210 | 0.0788 | [0.0711, 0.0871] | 0.910 |
| 1e-04 | `raw` | 210 | 0.1633 | [0.1471, 0.1783] | 0.895 |
| 1e-04 | `low_rank_residual_k30` | 210 | 0.0656 | [0.0586, 0.0732] | 0.867 |
| 3e-04 | `raw` | 210 | 0.2452 | [0.2260, 0.2659] | 0.952 |
| 3e-04 | `low_rank_residual_k30` | 210 | 0.0539 | [0.0471, 0.0619] | 0.733 |
| 1e-03 | `raw` | 210 | 0.3258 | [0.3034, 0.3486] | 0.976 |
| 1e-03 | `low_rank_residual_k30` | 210 | 0.0436 | [0.0371, 0.0505] | 0.605 |
| 3e-03 | `raw` | 210 | 0.3266 | [0.3035, 0.3494] | 0.943 |
| 3e-03 | `low_rank_residual_k30` | 210 | 0.0353 | [0.0292, 0.0417] | 0.519 |
| 1e-02 | `raw` | 210 | 0.2127 | [0.1917, 0.2349] | 0.895 |
| 1e-02 | `low_rank_residual_k30` | 210 | 0.0290 | [0.0228, 0.0353] | 0.457 |

## Boundary

- This gate consolidates `simMed_test.mat` and `simWind_test.mat` into one in-domain official full-asset protocol artifact.
- It is an in-domain official AISTAP-SIM gate, not an independent external-dataset result.
- Independent external support remains IPIX held-out validation and SSDD SAR adaptation.