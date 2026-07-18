# AISTAP Full-Asset Classical CFAR Baseline Audit

Date: 20260717

## Verdict

- Strict wins vs best classical baseline: `True`
- Non-inferior vs best classical baseline: `True`
- Assets: `simMed_test.mat, simWind_test.mat`
- Combined target-bearing items: `210`
- Candidate methods: `11`
- Asset-level wins/ties vs best classical: `14/0/14`
- Combined wins/ties vs best classical: `7/0/7`
- Combined minimum delta vs best classical: `0.0205`
- Proposed Pfa calibrated: `True`

## Combined Best-Classical Comparison

| Pfa | TP-SSCS Pd | Best classical method | Best classical Pd | Delta |
|---:|---:|---|---:|---:|
| 1e-05 | 0.1845 | `low_rank_residual_k30_global_topk` | 0.1015 | 0.0831 |
| 3e-05 | 0.2358 | `low_rank_residual_k30_global_topk` | 0.1571 | 0.0788 |
| 1e-04 | 0.3682 | `low_rank_residual_k30_global_topk` | 0.3026 | 0.0656 |
| 3e-04 | 0.5261 | `low_rank_residual_k30_global_topk` | 0.4722 | 0.0539 |
| 1e-03 | 0.7029 | `low_rank_residual_k30_os75_cfar_local` | 0.6716 | 0.0313 |
| 3e-03 | 0.8130 | `low_rank_residual_k30_os75_cfar_local` | 0.7880 | 0.0250 |
| 1e-02 | 0.8678 | `low_rank_residual_k30_os75_cfar_local` | 0.8473 | 0.0205 |

## Baseline Family

- Global top-k empirical-Pfa baselines: raw power and rank-matched low-rank residual power.
- Local CFAR score-map baselines: CA, GOCA, SOCA, and OS-CFAR scores on both raw power and low-rank residual power.
- All methods are evaluated with the same conservative `score > threshold` empirical-Pfa cap on non-target pixels.

## Boundary

- This is a stronger classical-baseline audit, not a new dataset.
- The local CFAR scores are locally normalized score maps followed by the same empirical-Pfa calibration used by the main protocol.
- If strict wins are false, the result should be reported as a baseline-strength boundary rather than hidden.