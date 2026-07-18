# TP-SSCS Model Scaffold Note

Date: 2026-07-13

## Smoke test result

The AISTAP sample loader and the minimal TP-SSCS prototype are connected end-to-end.

Observed shapes:

- input: `(6, 64, 1024)`
- suppressed: `(6, 64, 1024)`
- score: `(64, 1024)`

Observed powers:

- input power: `9.4623`
- residual power: `1.7922`
- suppressed power: `0.9578`

## Interpretation

The forward path is numerically finite and compatible with the sample data. The next real step is to add a training loop with a target-preservation loss and CFAR-calibrated detection objective.

