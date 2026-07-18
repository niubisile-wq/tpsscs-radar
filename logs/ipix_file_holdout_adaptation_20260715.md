# IPIX File-Holdout Adaptation

Date: 20260715

## Setup

- Train files: `19931107_135603_starea.cdf, 19931107_141630_starea.cdf`
- Test files: `19931107_145028_starea.cdf`
- State: `C:\Users\鍒樺瓙杞‐Desktop\绗笁鎵?\results\aistap_sample\tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt`
- Train rows: `196608` (`65536` positive, `131072` negative)
- Features: robust per-window score features from raw, low-rank residual, saved TP-SSCS residual/gate, and range-contrast; no range-bin index feature is used.

## Verdict

- Passed: `false`

## Test Comparisons

| Pfa | Adapted Pd | Raw Pd | Low-rank Pd | Adapted empirical Pfa | Beats raw | Beats low-rank |
|---:|---:|---:|---:|---:|---:|---:|
| 1e-05 | 0.0163 | 0.0227 | 0.0000 | 0 | `false` | `true` |
| 3e-05 | 0.0163 | 0.0227 | 0.0000 | 0 | `false` | `true` |
| 1e-04 | 0.0188 | 0.0247 | 0.0001 | 9.76563e-05 | `false` | `true` |
| 3e-04 | 0.0219 | 0.0266 | 0.0003 | 0.000292969 | `false` | `true` |
| 1e-03 | 0.0257 | 0.0296 | 0.0009 | 0.000976562 | `false` | `true` |
| 3e-03 | 0.0294 | 0.0332 | 0.0028 | 0.00292969 | `false` | `true` |
| 1e-02 | 0.0386 | 0.0423 | 0.0097 | 0.00996094 | `false` | `true` |

## Failures

- adapted TP-SSCS does not beat raw at Pfa 1e-05
- adapted TP-SSCS does not beat raw at Pfa 3e-05
- adapted TP-SSCS does not beat raw at Pfa 0.0001
- adapted TP-SSCS does not beat raw at Pfa 0.0003
- adapted TP-SSCS does not beat raw at Pfa 0.001
- adapted TP-SSCS does not beat raw at Pfa 0.003
- adapted TP-SSCS does not beat raw at Pfa 0.01

## Boundary

- This is an independent non-AISTAP IPIX file-level holdout test.
- It uses target-bin annotations from the public IPIX page for training and evaluation.
- It is stronger than zero-shot smoke testing only if the adapted detector beats raw and low-rank baselines on the held-out file.
