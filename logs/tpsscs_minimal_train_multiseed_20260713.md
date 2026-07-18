# TP-SSCS Minimal Trainability Multi-Seed Note

Date: 2026-07-13

## Purpose

This note checks whether the current best trainable gate branch stays stable across nearby random seeds.

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

| seed | val Pd @ Pfa=1e-2 | val empirical Pfa | train Pd @ Pfa=1e-2 | train empirical Pfa | final train loss | final gate gap |
|---|---:|---:|---:|---:|---:|---:|
| 7 | 0.9767 | 0.0100 | 1.0000 | 0.0100 | 0.0093 | 0.9211 |
| 11 | 0.9767 | 0.0100 | 1.0000 | 0.0100 | 0.0264 | 0.5006 |
| 23 | 0.9767 | 0.0100 | 1.0000 | 0.0100 | 0.0099 | 0.9130 |

## Aggregate readout

- Mean validation `Pd` at `Pfa=1e-2`: `0.9767`
- Mean validation empirical `Pfa`: `0.0100`
- Mean train `Pd` at `Pfa=1e-2`: `1.0000`
- Mean train empirical `Pfa`: `0.0100`
- Mean final train loss: `0.0152`
- Mean final gate gap: `0.7782`

## Interpretation

- The branch is stable across all three seeds at the loosest evaluated operating point.
- The validation operating point does not depend on a single lucky seed in this local check.
- The trainability claim is therefore stronger than a one-off run, but it is still a public-sample trainability claim, not a finished detector claim.

## Boundary

- Public sample only.
- Trainable scaffold only.
- Not a finished TP-SSCS detector.
