# AISTAP Figure and Table Caption Draft

Date: 2026-07-13

## Figure captions

### Figure 1

Public AISTAP-SIM sample and TP-SSCS pipeline. The sample provides complex-valued range-Doppler input and target-only reference tensors, and the TP-SSCS path applies target-preserving suppression, sparse gating, and CFAR-calibrated scoring. The figure frames the task as low-false-alarm detection rather than clutter removal alone.

### Figure 2

Target-preservation frontier on the public sample. The figure compares raw RD, low-rank residual, oracle diagnostics, and the trainable gate, showing that target preservation changes the operating frontier rather than merely explaining the failure mode. The best trainable gate candidate sharply reduces target loss relative to the low-rank residual baseline while remaining finite.

### Figure 3

Dense low-`Pfa` CFAR operating surface for the public AISTAP sample. Detection probability is evaluated across `k = 1, 2, 3, 5, 8, 10, 15, 20, 30` and `Pfa = 1e-5` to `1e-2`, showing that the best operating point depends jointly on the false-alarm target and the suppression rank.

### Figure 4

Prototype smoke path for the complex-valued TP-SSCS scaffold. The figure shows the sample loader, the suppression module, and the suppressed/residual/clutter/score outputs, confirming that the implementation is numerically finite but still a scaffold rather than a trained detector.

## Table captions

### Table 1

Low-rank baseline summary on the public sample. Clutter attenuation, target loss, and target retention ratio are reported for each subset and each rank `k`, making the suppression trade-off visible without relying only on plots.

### Table 2

CFAR operating summary on the public sample. Raw and residual `Pd` are reported at fixed `Pfa` values together with the empirical false-alarm rate, so the manuscript can discuss the detector as an operating policy rather than as a visual filter.

### Table 3

Manuscript boundary table. Supported claims from the public AISTAP sample are separated from claims that remain unsupported, so the paper does not overstate cross-dataset superiority, finished training maturity, or a universal solution to clutter suppression.

## Caption rule

- Keep every caption tied to the current public-sample evidence.
- Do not introduce a claim that is not already supported by the draft.
- Do not phrase the current scaffold as if the full method has already been trained or validated across the broader benchmark stack.
