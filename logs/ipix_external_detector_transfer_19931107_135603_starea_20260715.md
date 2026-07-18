# IPIX External Detector Transfer

Date: 20260715

## Setup

- CDF: `C:\Users\鍒樺瓙杞‐Desktop\绗笁鎵?\data\downloads\ipix\19931107_135603_starea.cdf`
- State: `C:\Users\鍒樺瓙杞‐Desktop\绗笁鎵?\results\aistap_sample\tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt`
- Windows: `128`
- Window/stride: `1024` / `1024` sweeps
- Primary target bin: `9` (1-indexed)
- Guard bins excluded from background: `8,9,10,11` (1-indexed)
- Transform: per-channel mean removal, Hann window, FFT-shift along sweep time, range-Doppler scoring.

## Detection Summary

| Method | Pfa | Pd mean | Pd std | Empirical Pfa mean | Windows |
|---|---:|---:|---:|---:|---:|
| low_rank_residual_k30 | 1e-05 | 0.0005 | 0.0027 | 0 | 128 |
| low_rank_residual_k30 | 3e-05 | 0.0005 | 0.0027 | 0 | 128 |
| low_rank_residual_k30 | 1e-04 | 0.0007 | 0.0042 | 9.76563e-05 | 128 |
| low_rank_residual_k30 | 3e-04 | 0.0009 | 0.0049 | 0.000292969 | 128 |
| low_rank_residual_k30 | 1e-03 | 0.0015 | 0.0069 | 0.000976562 | 128 |
| low_rank_residual_k30 | 3e-03 | 0.0029 | 0.0095 | 0.00292969 | 128 |
| low_rank_residual_k30 | 1e-02 | 0.0071 | 0.0161 | 0.00996094 | 128 |
| raw | 1e-05 | 0.0061 | 0.0097 | 0 | 128 |
| raw | 3e-05 | 0.0061 | 0.0097 | 0 | 128 |
| raw | 1e-04 | 0.0075 | 0.0111 | 9.76563e-05 | 128 |
| raw | 3e-04 | 0.0093 | 0.0137 | 0.000292969 | 128 |
| raw | 1e-03 | 0.0135 | 0.0185 | 0.000976562 | 128 |
| raw | 3e-03 | 0.0197 | 0.0254 | 0.00292969 | 128 |
| raw | 1e-02 | 0.0364 | 0.0422 | 0.00996094 | 128 |
| tpsscs_finished_detector | 1e-05 | 0.0021 | 0.0059 | 0 | 128 |
| tpsscs_finished_detector | 3e-05 | 0.0021 | 0.0059 | 0 | 128 |
| tpsscs_finished_detector | 1e-04 | 0.0023 | 0.0067 | 9.76563e-05 | 128 |
| tpsscs_finished_detector | 3e-04 | 0.0025 | 0.0071 | 0.000292969 | 128 |
| tpsscs_finished_detector | 1e-03 | 0.0031 | 0.0085 | 0.000976562 | 128 |
| tpsscs_finished_detector | 3e-03 | 0.0044 | 0.0105 | 0.00292969 | 128 |
| tpsscs_finished_detector | 1e-02 | 0.0086 | 0.0164 | 0.00996094 | 128 |
| tpsscs_trainable_gate | 1e-05 | 0.0016 | 0.0054 | 0 | 128 |
| tpsscs_trainable_gate | 3e-05 | 0.0016 | 0.0054 | 0 | 128 |
| tpsscs_trainable_gate | 1e-04 | 0.0022 | 0.0070 | 9.76563e-05 | 128 |
| tpsscs_trainable_gate | 3e-04 | 0.0029 | 0.0093 | 0.000292969 | 128 |
| tpsscs_trainable_gate | 1e-03 | 0.0045 | 0.0144 | 0.000976562 | 128 |
| tpsscs_trainable_gate | 3e-03 | 0.0094 | 0.0301 | 0.00292969 | 128 |
| tpsscs_trainable_gate | 1e-02 | 0.0241 | 0.0722 | 0.00996094 | 128 |

## Boundary

- This is independent non-AISTAP IPIX Dartmouth sea-clutter evidence using the published target-bin annotation for file #17.
- It is a zero-shot transfer smoke test from the AISTAP-SIM-trained saved state, not an IPIX-trained detector.
- It should not be used as a top-readiness pass unless the method beats raw and low-rank baselines under the same Pfa protocol.
