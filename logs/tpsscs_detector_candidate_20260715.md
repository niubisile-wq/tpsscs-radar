# TP-SSCS Detector Candidate Evaluation

Date: 20260715

## Setup

- State: `C:\Users\刘子轩\Desktop\第三批3\results\aistap_sample\tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt`
- Low-rank comparator: `k=30`
- Evaluated target-bearing items: `3`
- CFAR threshold policy: `conservative_topk_strict_gt` (`score > threshold`; per-item false alarms are capped at `floor(Pfa * background_count)`).
- Finished detector policy: `residual_cfar_plus_zero_false_gate_union` (rank-matched residual CFAR plus a trainable-gate head that is admitted only above its background maximum).

## Detection Summary

| Method | Pfa | Pd mean | Empirical Pfa mean | Items |
|---|---:|---:|---:|---:|
| low_rank_residual_k30 | 1e-05 | 0.1240 | 0.0000 | 3 |
| low_rank_residual_k30 | 3e-05 | 0.1705 | 0.0000 | 3 |
| low_rank_residual_k30 | 1e-04 | 0.2713 | 0.0001 | 3 |
| low_rank_residual_k30 | 3e-04 | 0.5194 | 0.0003 | 3 |
| low_rank_residual_k30 | 1e-03 | 0.7752 | 0.0010 | 3 |
| low_rank_residual_k30 | 3e-03 | 0.8760 | 0.0030 | 3 |
| low_rank_residual_k30 | 1e-02 | 0.9070 | 0.0100 | 3 |
| raw | 1e-05 | 0.0233 | 0.0000 | 3 |
| raw | 3e-05 | 0.0775 | 0.0000 | 3 |
| raw | 1e-04 | 0.1240 | 0.0001 | 3 |
| raw | 3e-04 | 0.2171 | 0.0003 | 3 |
| raw | 1e-03 | 0.4341 | 0.0010 | 3 |
| raw | 3e-03 | 0.4961 | 0.0030 | 3 |
| raw | 1e-02 | 0.6279 | 0.0100 | 3 |
| tpsscs_finished_detector | 1e-05 | 0.1473 | 0.0000 | 3 |
| tpsscs_finished_detector | 3e-05 | 0.1938 | 0.0000 | 3 |
| tpsscs_finished_detector | 1e-04 | 0.2946 | 0.0001 | 3 |
| tpsscs_finished_detector | 3e-04 | 0.5349 | 0.0003 | 3 |
| tpsscs_finished_detector | 1e-03 | 0.7907 | 0.0010 | 3 |
| tpsscs_finished_detector | 3e-03 | 0.8915 | 0.0030 | 3 |
| tpsscs_finished_detector | 1e-02 | 0.9225 | 0.0100 | 3 |
| tpsscs_trainable_gate | 1e-05 | 0.0233 | 0.0000 | 3 |
| tpsscs_trainable_gate | 3e-05 | 0.1008 | 0.0000 | 3 |
| tpsscs_trainable_gate | 1e-04 | 0.2713 | 0.0001 | 3 |
| tpsscs_trainable_gate | 3e-04 | 0.4031 | 0.0003 | 3 |
| tpsscs_trainable_gate | 1e-03 | 0.7752 | 0.0010 | 3 |
| tpsscs_trainable_gate | 3e-03 | 0.9380 | 0.0030 | 3 |
| tpsscs_trainable_gate | 1e-02 | 0.9457 | 0.0100 | 3 |

## Boundary

- This is a public-sample detector-candidate evaluation.
- It proves a reusable model-state-to-CFAR evaluation path.
- It does not by itself prove finished-detector status, cross-dataset superiority, or CAS一区 top readiness.