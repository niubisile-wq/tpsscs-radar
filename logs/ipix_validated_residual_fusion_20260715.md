# IPIX Validated Residual-Aware Fusion

Date: 20260715

## Setup

- Development files: `19931107_135603_starea.cdf`
- Validation files for beta selection: `19931107_141630_starea.cdf`
- Held-out test files: `19931107_145028_starea.cdf, 19931108_213827_starea.cdf, 19931108_220902_starea.cdf, 19931109_191449_starea.cdf, 19931109_202217_starea.cdf, 19931110_001635_starea.cdf, 19931111_163625_starea.cdf, 19931118_023604_stareC0000.cdf, 19931118_035737_stareC0000.cdf, 19931118_162155_stareC0000.cdf, 19931118_162658_stareC0000.cdf, 19931118_174259_stareC0000.cdf`
- Selected beta: `1.5`
- Score: `raw_z + beta * (raw_z - TPSSCS_residual_z)`.
- The score uses raw evidence plus the saved TP-SSCS residual as a validation-selected external adaptation head; no range-bin index feature is used.

## Verdict

- Passed: `true`
- Test wins vs raw: `7/7`
- Test wins vs low-rank: `7/7`
- Mean Pd delta vs raw: `0.022313`

## Held-Out Test Comparisons

| Pfa | Fusion Pd | Raw Pd | Low-rank Pd | Fusion empirical Pfa | Beats raw | Beats low-rank |
|---:|---:|---:|---:|---:|---:|---:|
| 1e-05 | 0.0644 | 0.0513 | 0.0003 | 0 | `true` | `true` |
| 3e-05 | 0.0644 | 0.0513 | 0.0003 | 0 | `true` | `true` |
| 1e-04 | 0.0695 | 0.0532 | 0.0005 | 8.65589e-05 | `true` | `true` |
| 3e-04 | 0.0770 | 0.0582 | 0.0007 | 0.000277761 | `true` | `true` |
| 1e-03 | 0.0897 | 0.0657 | 0.0016 | 0.000976562 | `true` | `true` |
| 3e-03 | 0.1062 | 0.0755 | 0.0035 | 0.00292969 | `true` | `true` |
| 1e-02 | 0.1374 | 0.0972 | 0.0096 | 0.00995683 | `true` | `true` |

## Validation Grid

- beta=0: wins_vs_raw=7, wins_vs_lowrank=7, mean_delta_vs_raw=0.000000
- beta=0.25: wins_vs_raw=7, wins_vs_lowrank=7, mean_delta_vs_raw=0.002956
- beta=0.5: wins_vs_raw=7, wins_vs_lowrank=7, mean_delta_vs_raw=0.003915
- beta=0.75: wins_vs_raw=7, wins_vs_lowrank=7, mean_delta_vs_raw=0.004375
- beta=1: wins_vs_raw=7, wins_vs_lowrank=7, mean_delta_vs_raw=0.004505
- beta=1.5: wins_vs_raw=7, wins_vs_lowrank=7, mean_delta_vs_raw=0.004570
- beta=2: wins_vs_raw=7, wins_vs_lowrank=7, mean_delta_vs_raw=0.004545

## Failures

- None.

## Boundary

- This is independent non-AISTAP IPIX file-level validation.
- Beta is selected on a validation file and reported on a disjoint held-out test file.
- This is stronger than the zero-shot smoke test, but it is still one external dataset family and does not by itself match the battery package's multi-tier external-validation breadth.