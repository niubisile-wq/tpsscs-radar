# AISTAP Minimal TP-SSCS Trainability Check

Date: 2026-07-13

## Setup

- Train split: 4 items
- Validation split: 2 items
- Rank: 30
- Hidden width: 16
- Steps: 150
- Learning rate: 0.02

## Trainability result

- Train loss changed from 0.6719 to 0.0168.
- Train gate gap changed from -0.0483 to 0.8803.
- Train gate mean changed from 0.4076 to 0.0053.
- Validation gate gap changed from -0.0654 to 0.9211.

## Validation detection summary

- raw: at the loosest evaluated Pfa=1e-02, Pd=0.5349, empirical_Pfa=0.0100.
- low_rank_residual: at the loosest evaluated Pfa=1e-02, Pd=0.9070, empirical_Pfa=0.0100.
- trainable_gate: at the loosest evaluated Pfa=1e-02, Pd=0.9767, empirical_Pfa=0.0100.

- Relative to the low-rank residual baseline, the trainable gate changes the validation frontier from Pd=0.9070 to Pd=0.9767 at the loosest tested Pfa, while remaining finite.

## Interpretation

- The scaffold is trainable: the loss remains finite and the gate separates target and background more than at initialization.
- The check is intentionally minimal; it does not claim a finished detector or cross-dataset generalization.
- If the validation frontier does not improve uniformly, the manuscript should present this as a bounded trainability check rather than a win claim.

## Boundary

- Public sample only.
- Trainable scaffold only.
- Not a finished TP-SSCS detector.