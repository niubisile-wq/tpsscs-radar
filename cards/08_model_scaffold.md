# Model Scaffold

## What is now executable

- AISTAP sample is exposed as a PyTorch dataset.
- A minimal complex-valued TP-SSCS prototype runs a forward pass.
- The prototype produces suppressed, residual, clutter, and score tensors.
- The smoke test writes a reproducible `.npz` artifact and a JSON/text report.

## Current model boundary

- This is not the full TP-SSCS training system.
- No learnable target-preservation loss has been trained yet.
- No cross-dataset training or validation has been run.

## Why this matters

- The repository now has a real data-to-model execution path.
- We can add loss functions, CFAR calibration, and training loops on top of a verified loader/model interface rather than guessing tensor shapes.
