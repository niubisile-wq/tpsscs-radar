# AISTAP Full-Asset Detector Candidate Evaluation

Date: seed23_fullasset_sensitivity_20260717

## Setup

- Asset: `data\downloads\aistap_sim\full\simMed_test.mat`
- State: `results\aistap_sample\tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed23.pt`
- Total frames: `128`
- Target-bearing frames in asset: `105`
- Evaluated target-bearing frames: `105`
- CFAR threshold policy: `conservative_topk_strict_gt` (`score > threshold`; per-frame false alarms are capped at `floor(Pfa * background_count)`).
- Finished detector policy: `residual_cfar_plus_zero_false_gate_union` (rank-matched residual CFAR plus a trainable-gate head that is admitted only above its background maximum).

## Detection Summary

| Method | Pfa | Pd mean | Pd std | Empirical Pfa mean | Items |
|---|---:|---:|---:|---:|---:|
| low_rank_residual_k30 | 1e-05 | 0.0989 | 0.0635 | 0.0000 | 105 |
| low_rank_residual_k30 | 3e-05 | 0.1504 | 0.0702 | 0.0000 | 105 |
| low_rank_residual_k30 | 1e-04 | 0.2944 | 0.0940 | 0.0001 | 105 |
| low_rank_residual_k30 | 3e-04 | 0.4575 | 0.1062 | 0.0003 | 105 |
| low_rank_residual_k30 | 1e-03 | 0.6488 | 0.1216 | 0.0010 | 105 |
| low_rank_residual_k30 | 3e-03 | 0.7764 | 0.1334 | 0.0030 | 105 |
| low_rank_residual_k30 | 1e-02 | 0.8383 | 0.1341 | 0.0100 | 105 |
| raw | 1e-05 | 0.0783 | 0.0510 | 0.0000 | 105 |
| raw | 3e-05 | 0.1149 | 0.0633 | 0.0000 | 105 |
| raw | 1e-04 | 0.1956 | 0.0823 | 0.0001 | 105 |
| raw | 3e-04 | 0.2686 | 0.1003 | 0.0003 | 105 |
| raw | 1e-03 | 0.3569 | 0.1144 | 0.0010 | 105 |
| raw | 3e-03 | 0.4673 | 0.1234 | 0.0030 | 105 |
| raw | 1e-02 | 0.6340 | 0.1186 | 0.0100 | 105 |
| tpsscs_finished_detector | 1e-05 | 0.1874 | 0.0864 | 0.0000 | 105 |
| tpsscs_finished_detector | 3e-05 | 0.2346 | 0.0933 | 0.0000 | 105 |
| tpsscs_finished_detector | 1e-04 | 0.3634 | 0.1162 | 0.0001 | 105 |
| tpsscs_finished_detector | 3e-04 | 0.5134 | 0.1113 | 0.0003 | 105 |
| tpsscs_finished_detector | 1e-03 | 0.6922 | 0.1189 | 0.0010 | 105 |
| tpsscs_finished_detector | 3e-03 | 0.8104 | 0.1179 | 0.0030 | 105 |
| tpsscs_finished_detector | 1e-02 | 0.8652 | 0.1132 | 0.0100 | 105 |
| tpsscs_trainable_gate | 1e-05 | 0.0985 | 0.0723 | 0.0000 | 105 |
| tpsscs_trainable_gate | 3e-05 | 0.1681 | 0.0882 | 0.0000 | 105 |
| tpsscs_trainable_gate | 1e-04 | 0.3388 | 0.1163 | 0.0001 | 105 |
| tpsscs_trainable_gate | 3e-04 | 0.5511 | 0.1311 | 0.0003 | 105 |
| tpsscs_trainable_gate | 1e-03 | 0.7777 | 0.1135 | 0.0010 | 105 |
| tpsscs_trainable_gate | 3e-03 | 0.8881 | 0.0972 | 0.0030 | 105 |
| tpsscs_trainable_gate | 1e-02 | 0.9255 | 0.0798 | 0.0100 | 105 |

## Boundary

- This is an official AISTAP-SIM full test asset, not only the small sample bundle.
- It improves the sample-scale evidence for the saved detector candidate.
- It remains in-domain AISTAP-SIM evidence, not independent external-dataset validation.