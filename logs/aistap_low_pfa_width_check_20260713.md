# AISTAP Low-Pfa Width Check

Date: 2026-07-13

## Candidate under test

- `rank=30`
- `hidden=32`
- `steps=150`
- `lr=0.02`

## Comparison against the preferred branch

The wider hidden branch does not replace the current preferred low-Pfa branch (`rank=30`, `hidden=16`, `steps=150`, `lr=0.02`).

### Seed-7 snapshot

- Preferred branch (`hidden=16`): validation gate gap `0.9211`, mean Pd over `Pfa <= 1e-3` `0.3442`.
- Wider branch (`hidden=32`): validation gate gap `0.9226`, mean Pd over `Pfa <= 1e-3` `0.2884`.

### Interpretation

- The wider branch keeps the detector finite and competitive, but it is worse on the strict low-Pfa frontier that the paper cares about.
- The wider branch therefore does not replace the current preferred branch.

## Boundary

- Public sample only.
- Trainable scaffold only.
- Not a finished detector claim.

