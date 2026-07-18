# Runbook 03: TP-SSCS Smoke Test

Goal:

- Verify the public AISTAP sample can flow through a minimal complex-valued low-rank suppression model.

Expected outputs:

- `results/tpsscs_smoke/smoke_outputs.npz`
- `logs/tpsscs_smoke_report.json`
- `logs/tpsscs_smoke_report.txt`

Checkpoints:

1. The dataset loader returns complex tensors with shape `(C, D, R)`.
2. The prototype model returns suppressed, residual, clutter, and score tensors.
3. The score map shape is `(D, R)`.
4. The smoke output powers are finite.

