# AISTAP Full-Asset Component Attribution Audit

Date: 20260717

## Verdict

- Target-bearing frames: `210` across `['simMed_test.mat', 'simWind_test.mat']`.
- Pfa grid: `['1e-05', '3e-05', '1e-04', '3e-04', '0.001', '0.003', '0.01']`.
- Finished detector vs raw AUC delta: `0.2228` (wins/ties/losses `206/0/4`).
- Finished detector vs low-rank residual AUC delta: `0.0553` (wins/ties/losses `195/15/0`).
- Finished detector vs gate-only AUC delta: `0.0000` (wins/ties/losses `124/0/86`).

## Combined Mean Pd by Component

| Pfa | Finished detector | Raw | Low-rank residual | Gate-only |
|---:|---:|---:|---:|---:|
| `1e-05` | 0.1845 | 0.0800 | 0.1015 | 0.0961 |
| `3e-05` | 0.2358 | 0.1210 | 0.1571 | 0.1562 |
| `1e-04` | 0.3682 | 0.2049 | 0.3026 | 0.3117 |
| `3e-04` | 0.5261 | 0.2809 | 0.4722 | 0.5345 |
| `0.001` | 0.7029 | 0.3771 | 0.6592 | 0.7744 |
| `0.003` | 0.8130 | 0.4865 | 0.7778 | 0.8834 |
| `0.01` | 0.8678 | 0.6551 | 0.8388 | 0.9210 |

## Paired Delta by Pfa

| Comparator | Pfa | Mean delta Pd | CI95 low | CI95 high | Wins/Ties/Losses | BH q |
|---|---:|---:|---:|---:|---:|---:|
| `raw` | `1e-05` | 0.1046 | 0.0938 | 0.1151 | 188/18/4 | 7.032e-50 |
| `raw` | `3e-05` | 0.1148 | 0.1019 | 0.1278 | 187/9/14 | 2.440e-39 |
| `raw` | `1e-04` | 0.1633 | 0.1474 | 0.1796 | 188/9/13 | 1.987e-40 |
| `raw` | `3e-04` | 0.2452 | 0.2255 | 0.2654 | 200/5/5 | 5.155e-52 |
| `raw` | `0.001` | 0.3258 | 0.3026 | 0.3487 | 205/2/3 | 5.743e-56 |
| `raw` | `0.003` | 0.3266 | 0.3032 | 0.3498 | 198/9/3 | 4.422e-54 |
| `raw` | `0.01` | 0.2127 | 0.1906 | 0.2346 | 188/3/19 | 9.253e-36 |
| `low_rank_residual_k30` | `1e-05` | 0.0831 | 0.0753 | 0.0911 | 195/15/0 | 1.255e-57 |
| `low_rank_residual_k30` | `3e-05` | 0.0788 | 0.0709 | 0.0866 | 191/19/0 | 6.691e-57 |
| `low_rank_residual_k30` | `1e-04` | 0.0656 | 0.0584 | 0.0729 | 182/28/0 | 2.055e-54 |
| `low_rank_residual_k30` | `3e-04` | 0.0539 | 0.0466 | 0.0615 | 154/56/0 | 3.065e-46 |
| `low_rank_residual_k30` | `0.001` | 0.0436 | 0.0369 | 0.0508 | 127/83/0 | 3.086e-38 |
| `low_rank_residual_k30` | `0.003` | 0.0353 | 0.0290 | 0.0419 | 109/101/0 | 6.933e-33 |
| `low_rank_residual_k30` | `0.01` | 0.0290 | 0.0231 | 0.0352 | 96/114/0 | 3.787e-29 |
| `tpsscs_trainable_gate` | `1e-05` | 0.0884 | 0.0802 | 0.0971 | 193/17/0 | 2.509e-57 |
| `tpsscs_trainable_gate` | `3e-05` | 0.0797 | 0.0674 | 0.0920 | 169/18/23 | 1.492e-28 |
| `tpsscs_trainable_gate` | `1e-04` | 0.0565 | 0.0433 | 0.0703 | 138/17/55 | 1.309e-09 |
| `tpsscs_trainable_gate` | `3e-04` | -0.0083 | -0.0233 | 0.0068 | 96/17/97 | 1.000e+00 |
| `tpsscs_trainable_gate` | `0.001` | -0.0715 | -0.0861 | -0.0574 | 41/25/144 | 1.000e+00 |
| `tpsscs_trainable_gate` | `0.003` | -0.0704 | -0.0823 | -0.0595 | 8/42/160 | 1.000e+00 |
| `tpsscs_trainable_gate` | `0.01` | -0.0532 | -0.0638 | -0.0433 | 4/61/145 | 1.000e+00 |

## Log-Pfa AUC Attribution

| Comparator | Target AUC | Comparator AUC | Mean delta | CI95 low | CI95 high | Wins/Ties/Losses | BH q |
|---|---:|---:|---:|---:|---:|---:|---:|
| `low_rank_residual_k30` | 0.5313 | 0.4760 | 0.0553 | 0.0489 | 0.0620 | 195/15/0 | 1.792e-58 |
| `raw` | 0.5313 | 0.3085 | 0.2228 | 0.2078 | 0.2377 | 206/0/4 | 2.195e-55 |
| `tpsscs_trainable_gate` | 0.5313 | 0.5313 | 0.0000 | -0.0082 | 0.0079 | 124/0/86 | 6.750e-03 |

## Interpretation

- The finished detector inherits broad Pd gains from residual clutter suppression and adds the zero-false gate branch where the learned score exceeds every background pixel.
- Against low-rank residual alone, the finished detector is nonnegative on every frame-level AUC pair; the gain is largest at the tightest Pfa points.
- Gate-only is a relaxed learned-score endpoint, not the selected conservative detector. It is weaker at the tightest Pfa point and stronger at looser Pfa points, so the finished detector should be presented as a low-false-alarm operating policy rather than a universal Pd upper bound.

## Boundary

- This audit reuses the frozen full-asset detector-candidate CSVs; it does not add a new dataset or retrain the model.
- The paired unit is the target-bearing frame, not pixels.
- AUC integrates the checked seven-point Pfa grid from 1e-5 to 1e-2 only.
- The component-attribution claim is mechanistic and empirical on AISTAP full assets; it does not remove the existing external-transfer and metadata limitations.
