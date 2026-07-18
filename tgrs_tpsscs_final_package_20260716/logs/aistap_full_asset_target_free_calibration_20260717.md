# AISTAP Full-Asset Target-Free Calibration Audit

Date: 20260717

## Verdict

- Target-bearing items: `210`
- Calibration modes: `cross_asset_target_free, same_asset_target_free`
- Positive-delta modes: `cross_asset_target_free, same_asset_target_free`
- Fully Pfa-calibrated modes: `none`
- Passed modes: `none`

## Calibration Support

| Asset | Target-free frames | Target-bearing frames |
|---|---:|---:|
| `simMed_test.mat` | 23 | 105 |
| `simWind_test.mat` | 23 | 105 |

## Mode Summary

| Mode | Combined wins vs raw | Combined wins vs low-rank | Min delta vs raw | Min delta vs low-rank | CI positive vs raw | CI positive vs low-rank |
|---|---:|---:|---:|---:|---:|---:|
| `cross_asset_target_free` | 7/7 | 7/7 | 0.2415 | 0.0519 | true | true |
| `same_asset_target_free` | 7/7 | 7/7 | 0.2431 | 0.0512 | true | true |

## Combined Operating Points

| Mode | Pfa | TP-SSCS Pd | Raw Pd | Low-rank Pd | Delta vs raw | Delta vs low-rank | TP-SSCS empirical Pfa |
|---|---:|---:|---:|---:|---:|---:|---:|
| `cross_asset_target_free` | 1e-05 | 0.6283 | 0.1222 | 0.5133 | 0.5061 | 0.1149 | 0.000898522 |
| `cross_asset_target_free` | 3e-05 | 0.6663 | 0.1670 | 0.5614 | 0.4992 | 0.1049 | 0.00120472 |
| `cross_asset_target_free` | 1e-04 | 0.7216 | 0.2292 | 0.6303 | 0.4924 | 0.0913 | 0.00201255 |
| `cross_asset_target_free` | 3e-04 | 0.7699 | 0.2942 | 0.6889 | 0.4757 | 0.0810 | 0.00368733 |
| `cross_asset_target_free` | 1e-03 | 0.8253 | 0.3805 | 0.7553 | 0.4447 | 0.0699 | 0.0082424 |
| `cross_asset_target_free` | 3e-03 | 0.8591 | 0.4840 | 0.7984 | 0.3751 | 0.0607 | 0.0176103 |
| `cross_asset_target_free` | 1e-02 | 0.8998 | 0.6583 | 0.8479 | 0.2415 | 0.0519 | 0.0419499 |
| `same_asset_target_free` | 1e-05 | 0.6235 | 0.1216 | 0.5103 | 0.5019 | 0.1132 | 0.000889287 |
| `same_asset_target_free` | 3e-05 | 0.6642 | 0.1684 | 0.5611 | 0.4959 | 0.1032 | 0.00115505 |
| `same_asset_target_free` | 1e-04 | 0.7207 | 0.2295 | 0.6311 | 0.4912 | 0.0896 | 0.00185578 |
| `same_asset_target_free` | 3e-04 | 0.7673 | 0.2946 | 0.6885 | 0.4727 | 0.0789 | 0.0031915 |
| `same_asset_target_free` | 1e-03 | 0.8190 | 0.3797 | 0.7507 | 0.4392 | 0.0682 | 0.00662356 |
| `same_asset_target_free` | 3e-03 | 0.8643 | 0.4853 | 0.8047 | 0.3790 | 0.0596 | 0.0137507 |
| `same_asset_target_free` | 1e-02 | 0.9012 | 0.6581 | 0.8500 | 0.2431 | 0.0512 | 0.0332728 |

## Bootstrap CI

| Mode | Pfa | Comparator | n | Mean delta | 95% CI | Positive fraction |
|---|---:|---|---:|---:|---:|---:|
| `cross_asset_target_free` | 1e-05 | `raw` | 210 | 0.5061 | [0.4723, 0.5417] | 0.967 |
| `cross_asset_target_free` | 1e-05 | `low_rank_residual_k30` | 210 | 0.1149 | [0.1019, 0.1274] | 0.867 |
| `cross_asset_target_free` | 3e-05 | `raw` | 210 | 0.4992 | [0.4671, 0.5333] | 0.967 |
| `cross_asset_target_free` | 3e-05 | `low_rank_residual_k30` | 210 | 0.1049 | [0.0928, 0.1180] | 0.795 |
| `cross_asset_target_free` | 1e-04 | `raw` | 210 | 0.4924 | [0.4610, 0.5216] | 0.967 |
| `cross_asset_target_free` | 1e-04 | `low_rank_residual_k30` | 210 | 0.0913 | [0.0792, 0.1051] | 0.748 |
| `cross_asset_target_free` | 3e-04 | `raw` | 210 | 0.4757 | [0.4484, 0.5023] | 0.976 |
| `cross_asset_target_free` | 3e-04 | `low_rank_residual_k30` | 210 | 0.0810 | [0.0688, 0.0938] | 0.681 |
| `cross_asset_target_free` | 1e-03 | `raw` | 210 | 0.4447 | [0.4218, 0.4674] | 0.981 |
| `cross_asset_target_free` | 1e-03 | `low_rank_residual_k30` | 210 | 0.0699 | [0.0584, 0.0820] | 0.643 |
| `cross_asset_target_free` | 3e-03 | `raw` | 210 | 0.3751 | [0.3523, 0.3963] | 0.981 |
| `cross_asset_target_free` | 3e-03 | `low_rank_residual_k30` | 210 | 0.0607 | [0.0492, 0.0723] | 0.576 |
| `cross_asset_target_free` | 1e-02 | `raw` | 210 | 0.2415 | [0.2211, 0.2590] | 0.952 |
| `cross_asset_target_free` | 1e-02 | `low_rank_residual_k30` | 210 | 0.0519 | [0.0414, 0.0624] | 0.505 |
| `same_asset_target_free` | 1e-05 | `raw` | 210 | 0.5019 | [0.4679, 0.5359] | 0.976 |
| `same_asset_target_free` | 1e-05 | `low_rank_residual_k30` | 210 | 0.1132 | [0.1009, 0.1263] | 0.857 |
| `same_asset_target_free` | 3e-05 | `raw` | 210 | 0.4959 | [0.4625, 0.5288] | 0.967 |
| `same_asset_target_free` | 3e-05 | `low_rank_residual_k30` | 210 | 0.1032 | [0.0911, 0.1165] | 0.810 |
| `same_asset_target_free` | 1e-04 | `raw` | 210 | 0.4912 | [0.4618, 0.5209] | 0.981 |
| `same_asset_target_free` | 1e-04 | `low_rank_residual_k30` | 210 | 0.0896 | [0.0766, 0.1023] | 0.743 |
| `same_asset_target_free` | 3e-04 | `raw` | 210 | 0.4727 | [0.4451, 0.4999] | 0.976 |
| `same_asset_target_free` | 3e-04 | `low_rank_residual_k30` | 210 | 0.0789 | [0.0674, 0.0921] | 0.690 |
| `same_asset_target_free` | 1e-03 | `raw` | 210 | 0.4392 | [0.4144, 0.4628] | 0.986 |
| `same_asset_target_free` | 1e-03 | `low_rank_residual_k30` | 210 | 0.0682 | [0.0569, 0.0804] | 0.633 |
| `same_asset_target_free` | 3e-03 | `raw` | 210 | 0.3790 | [0.3594, 0.3985] | 0.990 |
| `same_asset_target_free` | 3e-03 | `low_rank_residual_k30` | 210 | 0.0596 | [0.0488, 0.0714] | 0.557 |
| `same_asset_target_free` | 1e-02 | `raw` | 210 | 0.2431 | [0.2259, 0.2596] | 0.962 |
| `same_asset_target_free` | 1e-02 | `low_rank_residual_k30` | 210 | 0.0512 | [0.0412, 0.0623] | 0.510 |

## Boundary

- This audit replaces per-target-frame background thresholding with thresholds estimated only from target-free frames.
- `same_asset_target_free` calibrates each asset from its own target-free frames.
- `cross_asset_target_free` calibrates each asset from the other official full asset's target-free frames.
- This is a calibration-robustness audit, not a new dataset or a fully blind deployment test.
