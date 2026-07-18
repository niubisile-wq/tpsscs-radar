# AISTAP Runtime And Complexity Profile

Date: 20260717

## Verdict

- Timed target-bearing frames: `12` across `2` official full assets.
- Compact TP-SSCS finished-detector median inference time: `133.66` ms/frame.
- Raw/residual HGB median inference time: `608.99` ms/frame.
- HGB/compact median runtime ratio: `4.56x`.
- Trainable TP-SSCS parameter count: `2641`.
- Raw/residual HGB feature dimension: `15`.
- Main interpretation: `compact_inference_no_slower_than_raw_residual_hgb_on_this_cpu_profile`

## End-to-End Inference Profiles

| Profile | n | Median ms | Mean ms | P25-P75 ms | P95 ms |
|---|---:|---:|---:|---:|---:|
| `compact_tpsscs_finished_detector` | 12 | 133.66 | 136.90 | 127.12-146.26 | 152.42 |
| `raw_residual_hgb_inference` | 12 | 608.99 | 644.85 | 605.14-668.62 | 751.74 |
| `shared_low_rank_numpy_plus_hgb_features` | 12 | 525.76 | 557.53 | 521.16-582.57 | 659.75 |
| `tpsscs_gate_head_after_low_rank` | 12 | 10.85 | 15.38 | 10.29-11.81 | 35.57 |

## Component Timings

| Component | n | Median ms | Mean ms | P95 ms |
|---|---:|---:|---:|---:|
| `numpy_rank30_residual_score` | 12 | 505.58 | 534.32 | 636.01 |
| `tpsscs_total_forward_materialized` | 12 | 129.84 | 133.25 | 148.31 |
| `tpsscs_low_rank_torch` | 12 | 116.28 | 120.87 | 155.38 |
| `raw_residual_hgb_predict_proba` | 12 | 83.57 | 84.54 | 91.73 |
| `raw_residual_hgb_feature_cube` | 12 | 23.79 | 23.21 | 25.29 |
| `tpsscs_gate_and_enhanced_score_after_residual` | 12 | 10.85 | 15.38 | 35.57 |
| `finished_detector_thresholds_7pfa` | 12 | 3.97 | 3.65 | 4.46 |
| `raw_score_numpy` | 12 | 2.39 | 2.78 | 4.52 |

## HGB Training Cost Boundary

| Scope | Component | Median ms | Mean ms |
|---|---|---:|---:|
| `train_on_simMed_test.mat_for_test_simWind_test.mat` | `hgb_fit` | 1407.10 | 1407.10 |
| `train_on_simMed_test.mat_for_test_simWind_test.mat` | `hgb_training_sample_collection` | 13890.55 | 13890.55 |
| `train_on_simWind_test.mat_for_test_simMed_test.mat` | `hgb_fit` | 3686.29 | 3686.29 |
| `train_on_simWind_test.mat_for_test_simMed_test.mat` | `hgb_training_sample_collection` | 13498.59 | 13498.59 |

## Boundary

- This is a CPU runtime profile on the local machine, not a hardware-independent speed benchmark.
- The timing audit supports a bounded deployment-cost claim: the compact detector uses a small gate and no supervised HGB inference stack, while the dominant cost remains low-rank residual formation.
- The result should not be used to claim universal real-time performance or speed superiority on other hardware.