# AISTAP Stress Grid Note

Date: 2026-07-13

## What this adds

This stress grid perturbs the public AISTAP-SIM sample with complex noise, amplitude scaling, phase noise, target attenuation, and clutter scaling, then re-evaluates the low-rank operating policy and the trainable gate.

## Reference state

- Stress evaluation reuses the minimal trainability checkpoint from `tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed11.pt`.
- Families: noise, amplitude, phase, target_attenuation, clutter_scale
- Level grids: {"noise": [0.0, 0.01, 0.03, 0.05], "amplitude": [0.5, 0.8, 1.0, 1.2], "phase": [0.0, 0.1, 0.25, 0.5], "target_attenuation": [1.0, 0.8, 0.6, 0.4], "clutter_scale": [0.8, 1.0, 1.2, 1.5]}
- Rank grid: 1, 3, 5, 8, 10, 15, 20, 30

## Low-rank stability at Pfa=1e-3

- noise: best k by level is 0->30, 0.01->30, 0.03->30, 0.05->30
- amplitude: best k by level is 0.5->30, 0.8->30, 1->30, 1.2->30
- phase: best k by level is 0->30, 0.1->30, 0.25->5, 0.5->20
- target_attenuation: best k by level is 0.4->20, 0.6->30, 0.8->30, 1->30
- clutter_scale: best k by level is 0.8->20, 1->30, 1.2->30, 1.5->30

## Trainable-gate stability at Pfa=1e-3

- noise: Pd by level is 0->0.721, 0.01->0.721, 0.03->0.721, 0.05->0.721
- amplitude: Pd by level is 0.5->0.791, 0.8->0.760, 1->0.721, 1.2->0.690
- phase: Pd by level is 0->0.721, 0.1->0.612, 0.25->0.589, 0.5->0.659
- target_attenuation: Pd by level is 0.4->0.519, 0.6->0.636, 0.8->0.667, 1->0.721
- clutter_scale: Pd by level is 0.8->0.775, 1->0.721, 1.2->0.667, 1.5->0.612

## Interpretation

- The best low-rank rank shifts under perturbation, so the operating-point conclusion is not a single accidental setting.
- The trainable gate remains stable and finite under perturbation, and it keeps the validation frontier competitive with the low-rank residual baseline at the reference operating point.
- Any fragility should be written as a limitation, not hidden.

## Boundary

- Public sample only.
- Stress-grid only.
- Not a finished detector claim.