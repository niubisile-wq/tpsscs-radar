# AISTAP Full-Asset Detector Candidate Evaluation

Date: seed23_fullasset_sensitivity_20260717

## Setup

- Asset: `data\downloads\aistap_sim\full\simWind_test.mat`
- State: `results\aistap_sample\tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed23.pt`
- Total frames: `128`
- Target-bearing frames in asset: `105`
- Evaluated target-bearing frames: `105`
- CFAR threshold policy: `conservative_topk_strict_gt` (`score > threshold`; per-frame false alarms are capped at `floor(Pfa * background_count)`).
- Finished detector policy: `residual_cfar_plus_zero_false_gate_union` (rank-matched residual CFAR plus a trainable-gate head that is admitted only above its background maximum).

## Detection Summary

| Method | Pfa | Pd mean | Pd std | Empirical Pfa mean | Items |
|---|---:|---:|---:|---:|---:|
| low_rank_residual_k30 | 1e-05 | 0.1041 | 0.0724 | 0.0000 | 105 |
| low_rank_residual_k30 | 3e-05 | 0.1638 | 0.0810 | 0.0000 | 105 |
| low_rank_residual_k30 | 1e-04 | 0.3108 | 0.0898 | 0.0001 | 105 |
| low_rank_residual_k30 | 3e-04 | 0.4869 | 0.1067 | 0.0003 | 105 |
| low_rank_residual_k30 | 1e-03 | 0.6697 | 0.1220 | 0.0010 | 105 |
| low_rank_residual_k30 | 3e-03 | 0.7792 | 0.1341 | 0.0030 | 105 |
| low_rank_residual_k30 | 1e-02 | 0.8393 | 0.1263 | 0.0100 | 105 |
| raw | 1e-05 | 0.0816 | 0.0524 | 0.0000 | 105 |
| raw | 3e-05 | 0.1271 | 0.0620 | 0.0000 | 105 |
| raw | 1e-04 | 0.2143 | 0.0833 | 0.0001 | 105 |
| raw | 3e-04 | 0.2932 | 0.0952 | 0.0003 | 105 |
| raw | 1e-03 | 0.3972 | 0.1177 | 0.0010 | 105 |
| raw | 3e-03 | 0.5056 | 0.1235 | 0.0030 | 105 |
| raw | 1e-02 | 0.6761 | 0.1148 | 0.0100 | 105 |
| tpsscs_finished_detector | 1e-05 | 0.1883 | 0.0888 | 0.0000 | 105 |
| tpsscs_finished_detector | 3e-05 | 0.2428 | 0.0964 | 0.0000 | 105 |
| tpsscs_finished_detector | 1e-04 | 0.3749 | 0.1052 | 0.0001 | 105 |
| tpsscs_finished_detector | 3e-04 | 0.5384 | 0.1143 | 0.0003 | 105 |
| tpsscs_finished_detector | 1e-03 | 0.7098 | 0.1177 | 0.0010 | 105 |
| tpsscs_finished_detector | 3e-03 | 0.8105 | 0.1239 | 0.0030 | 105 |
| tpsscs_finished_detector | 1e-02 | 0.8629 | 0.1083 | 0.0100 | 105 |
| tpsscs_trainable_gate | 1e-05 | 0.1024 | 0.0722 | 0.0000 | 105 |
| tpsscs_trainable_gate | 3e-05 | 0.1780 | 0.0883 | 0.0000 | 105 |
| tpsscs_trainable_gate | 1e-04 | 0.3480 | 0.1000 | 0.0001 | 105 |
| tpsscs_trainable_gate | 3e-04 | 0.5663 | 0.1307 | 0.0003 | 105 |
| tpsscs_trainable_gate | 1e-03 | 0.7891 | 0.1123 | 0.0010 | 105 |
| tpsscs_trainable_gate | 3e-03 | 0.8769 | 0.1038 | 0.0030 | 105 |
| tpsscs_trainable_gate | 1e-02 | 0.9131 | 0.0836 | 0.0100 | 105 |

## Boundary

- This is an official AISTAP-SIM full test asset, not only the small sample bundle.
- It improves the sample-scale evidence for the saved detector candidate.
- It remains in-domain AISTAP-SIM evidence, not independent external-dataset validation.