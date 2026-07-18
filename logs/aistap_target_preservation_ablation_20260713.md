# AISTAP Target-Preservation Ablation Note

Date: 2026-07-13

## What this adds

This ablation compares raw RD, low-rank residuals, oracle blend diagnostics, oracle target-gated diagnostics, and the minimal trainable gate on the public AISTAP-SIM sample.

The point is not deployability. The point is to test whether preserving target information can improve the operating frontier relative to the low-rank residual baseline.

## Measured rows

- Target-bearing public samples contributed 3 evaluated items.
- The target-preservation metric is computed from metadata-derived target masks, so every measured item is scored on the same target-pixel protocol.

## Key aggregated result

- raw: Pd=0.290, target_loss=0.000 dB, clutter_attenuation=0.000 dB
- low_rank_residual: Pd=0.512, target_loss=12.382 dB, clutter_attenuation=6.723 dB
- trainable_gate: Pd=0.506, target_loss=0.393 dB, clutter_attenuation=6.655 dB
- oracle_gate: Pd=0.472, target_loss=-0.001 dB, clutter_attenuation=6.412 dB
- oracle_blend: Pd=0.518, target_loss=5.452 dB, clutter_attenuation=10.048 dB

## Operating frontier

- pfa=1e-05: best low-rank residual is k=30 with Pd=0.1628, target_loss=19.525 dB, clutter_attenuation=1.506 dB
- pfa=3e-05: best low-rank residual is k=20 with Pd=0.2791, target_loss=13.906 dB, clutter_attenuation=1.022 dB
- pfa=0.0001: best low-rank residual is k=30 with Pd=0.4419, target_loss=19.525 dB, clutter_attenuation=1.506 dB
- pfa=0.0003: best low-rank residual is k=30 with Pd=0.6279, target_loss=19.525 dB, clutter_attenuation=1.506 dB
- pfa=0.001: best low-rank residual is k=30 with Pd=0.8140, target_loss=19.525 dB, clutter_attenuation=10.813 dB
- pfa=0.003: best low-rank residual is k=20 with Pd=0.9535, target_loss=13.906 dB, clutter_attenuation=11.268 dB
- pfa=0.01: best low-rank residual is k=5 with Pd=0.9767, target_loss=3.715 dB, clutter_attenuation=7.226 dB
- pfa=1e-05: trainable gate is Pd=0.0465, target_loss=0.393 dB, clutter_attenuation=10.074 dB
- pfa=3e-05: trainable gate is Pd=0.1163, target_loss=0.393 dB, clutter_attenuation=10.074 dB
- pfa=0.0001: trainable gate is Pd=0.3023, target_loss=0.393 dB, clutter_attenuation=10.074 dB
- pfa=0.0003: trainable gate is Pd=0.4651, target_loss=0.393 dB, clutter_attenuation=10.074 dB
- pfa=0.001: trainable gate is Pd=0.7907, target_loss=0.393 dB, clutter_attenuation=1.331 dB
- pfa=0.003: trainable gate is Pd=1.0000, target_loss=0.393 dB, clutter_attenuation=10.074 dB
- pfa=0.01: trainable gate is Pd=1.0000, target_loss=0.393 dB, clutter_attenuation=10.074 dB

- Oracle blend diagnostics provide the strongest Pd upper bound, but alpha=0 is target-dominant and not deployable.
- Oracle gate diagnostics keep target loss near zero and reach Pd=1.0 at looser operating points, which shows headroom but still not a trained detector.
- The trainable gate is the closest deployable candidate in this ablation, but it still remains scaffold-bounded evidence rather than finished-detector evidence.

## Interpretation

- The low-rank residual baseline still pays a material target-loss tax.
- The oracle blend and oracle gate diagnostics show headroom for target-preservation, but they remain bounded upper bounds rather than deployable detectors.
- The trainable gate provides the strongest current bridge from oracle diagnostics to a deployable candidate, but it still remains scaffold-bounded evidence rather than finished-detector evidence.
- The measured result is therefore diagnostic: the manuscript should claim that target-preservation is the right direction and that a trainable gate is a promising candidate, not that TP-SSCS is already closed.

## Boundary

- This is public-sample evidence only.
- This does not prove final TP-SSCS superiority.
- This does not replace a trained detector or a cross-dataset result.