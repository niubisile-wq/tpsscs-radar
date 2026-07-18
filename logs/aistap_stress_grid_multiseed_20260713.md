# AISTAP Stress Grid Multi-Seed Note

Date: 2026-07-13

## Purpose

This note checks whether the stress-grid conclusion for the preferred trainable branch persists across nearby random seeds.

The branch tested here is the current preferred branch:

- `rank=30`
- `hidden=16`
- `steps=150`
- `lr=0.02`

Seeds:

- `7`
- `11`
- `23`

## Summary table

| seed | mean trainable Pd at Pfa=1e-3 | mean trainable empirical Pfa at Pfa=1e-3 | best-rank set for low-rank baseline |
|---|---:|---:|---|
| 7 | 0.7860 | 0.0010 | 1,20,30 |
| 11 | 0.7651 | 0.0010 | 1,20,30 |
| 23 | 0.7860 | 0.0010 | 1,15,20,30 |

## Interpretation

- The trainable gate remains finite under the stress grid across all three seeds.
- The mean stress behavior is stable enough to treat the preferred branch as repeatable in this local check.
- The stress conclusion is therefore stronger than a one-off run, but it is still bounded to the public sample and the current perturbation families.

## Boundary

- Public sample only.
- Stress-grid only.
- Not a finished detector claim.
