# AISTAP Sample Evidence

## What the current sample proves

- The public AISTAP-SIM sample is readable locally as v7.3 HDF5.
- The sample contains `rd_img` and `rd_targ_only` tensors with shape `(2, 6, 64, 1024)`.
- The first CPI already exhibits strong low-rank structure in the raw RD matrix.
- A truncated low-rank residual baseline creates a clear clutter-vs-target trade-off.

## Observed trend from the current rank sweep

- `k=1` gives mild clutter attenuation and low target loss.
- `k=5` gives materially stronger clutter attenuation, but the target loss becomes noticeable.
- `k=20` further increases clutter attenuation, but target loss becomes severe.

## Interpretation for the paper

- Plain low-rank suppression is not enough.
- The method needs an explicit target-preservation mechanism.
- This supports the TP-SSCS design logic: low-rank clutter removal must be paired with sparse target gating and CFAR calibration.

## Current evidence boundary

- This evidence is from the public sample only.
- It supports method design and ablation logic.
- It does not replace the full benchmark experiments on broader public datasets.
