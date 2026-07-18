# AISTAP Trainable-Gate Learning-Rate Sweep

## Goal

Check whether the strongest trainable-gate candidate (`rank=20`, `hidden=16`, `steps=150`) can be improved by a small learning-rate sweep without leaving the public-sample scaffold boundary.

## Compared settings

| LR | Train loss | Train gate gap | Val gate gap | Val Pd @ Pfa=1e-2 |
|---|---:|---:|---:|---:|
| 0.005 | 0.0257 | 0.8081 | 0.9194 | 1.0000 |
| 0.010 | 0.0189 | 0.8499 | 0.9210 | 1.0000 |
| 0.020 | 0.0297 | 0.7832 | 0.9024 | 1.0000 |

## Selection

The best learning rate remains `0.01`.

## Interpretation

- The candidate is stable to nearby learning-rate changes.
- `lr=0.01` remains the best current setting on loss and gate separation.
- The validation operating point is unchanged at the loosest tested `Pfa`.

## Boundary

- Public sample only.
- Candidate selection only.
- Not a finished detector result.
