# AISTAP Low-Pfa Hidden-Width Rejection

Date: 2026-07-13

## Candidate under test

- `rank=30`
- `hidden=24`
- `steps=150`
- `lr=0.02`

## Comparison against the preferred branch

The wider hidden branch does not replace the current preferred low-Pfa branch (`rank=30`, `hidden=16`, `steps=150`, `lr=0.02`).

### Seed-7 snapshot

- Preferred branch (`hidden=16`): validation gate gap `0.9211`, mean Pd over `Pfa <= 1e-3` `0.3442`.
- Wider branch (`hidden=24`): validation gate gap `0.9135`, mean Pd over `Pfa <= 1e-3` `0.2930`.

### Interpretation

- The wider branch remains finite and competitive, but it is worse on the strict low-Pfa frontier that the paper cares about.
- The wider branch therefore does not replace the current preferred branch.

## Boundary

- Public sample only.
- Trainable scaffold only.
- Not a finished detector claim.

