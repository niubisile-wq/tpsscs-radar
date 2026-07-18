# AISTAP Full-Asset Classical CFAR Parameter-Sweep Audit

Date: 20260717

## Verdict

- Strict wins vs best swept classical baseline: `True`
- Non-inferior vs best swept classical baseline: `True`
- Assets: `simMed_test.mat, simWind_test.mat`
- Combined target-bearing items: `210`
- Candidate methods/configurations: `75`
- Training grid: `4, 6, 8`
- Guard grid: `1, 2`
- OS percentiles: `60, 75, 90`
- Asset-level wins/ties vs best swept classical: `14/0/14`
- Combined wins/ties vs best swept classical: `7/0/7`
- Combined minimum delta vs best swept classical: `0.0162`

## Combined Best-Swept-Classical Comparison

| Pfa | TP-SSCS Pd | Best swept classical method | Best Pd | Delta |
|---:|---:|---|---:|---:|
| 1e-05 | 0.1845 | `raw_goca_t4_g1_cfar_local` | 0.1025 | 0.0820 |
| 3e-05 | 0.2358 | `low_rank_residual_k30_global_topk` | 0.1571 | 0.0788 |
| 1e-04 | 0.3682 | `low_rank_residual_k30_goca_t4_g1_cfar_local` | 0.3180 | 0.0502 |
| 3e-04 | 0.5261 | `low_rank_residual_k30_goca_t4_g1_cfar_local` | 0.4925 | 0.0336 |
| 1e-03 | 0.7029 | `low_rank_residual_k30_ca_t4_g1_cfar_local` | 0.6866 | 0.0162 |
| 3e-03 | 0.8130 | `low_rank_residual_k30_os75_t8_g1_cfar_local` | 0.7906 | 0.0225 |
| 1e-02 | 0.8678 | `low_rank_residual_k30_os60_t8_g2_cfar_local` | 0.8500 | 0.0178 |

## Boundary

- This audit gives the classical CFAR baselines multiple local-window settings rather than a single fixed setting.
- The result is still an official AISTAP-SIM full-asset baseline-strength audit, not a new external dataset.
- All score families remain calibrated with the same conservative empirical-Pfa thresholding rule.