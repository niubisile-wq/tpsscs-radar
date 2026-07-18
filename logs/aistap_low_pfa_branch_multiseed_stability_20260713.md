# AISTAP Low-Pfa Branch Multi-Seed Stability

Date: 2026-07-13

## Branch under review

- `rank=30`
- `hidden=16`
- `steps=150`
- `lr=0.02`

## Seeds checked

- `seed=7`
- `seed=11`
- `seed=23`

## Stability table

| Seed | Train loss | Train gate gap | Val loss | Val gate gap | Mean Pd over Pfa <= 1e-3 | Mean Pd over all tested Pfa | Pd at Pfa=1e-2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 7 | 0.0168 | 0.8803 | 0.0093 | 0.9211 | 0.3442 | 0.5249 | 0.9767 |
| 11 | 0.0350 | 0.4806 | 0.0264 | 0.5006 | 0.2930 | 0.4817 | 0.9767 |
| 23 | 0.0169 | 0.8606 | 0.0099 | 0.9130 | 0.3349 | 0.5150 | 0.9767 |

## Interpretation

- The branch is not a one-off seed artifact.
- All checked seeds keep the low-Pfa branch finite and competitive.
- Seed 11 is weaker than seeds 7 and 23, but it still remains in the same bounded trainable-branch regime rather than collapsing.
- The preferred branch remains the same after the repeat check: `rank=30`, `hidden=16`, `steps=150`, `lr=0.02`.

## What this adds to the comparison

- It strengthens the trainable-branch evidence against the reproducibility-first reference.
- It strengthens the strict low-Pfa evidence against the protocol-sensitive references.
- It still does not prove deployable closure or unconditional victory over the five-reference set.

## Boundary

- Public sample only.
- Trainable scaffold only.
- Not a finished detector claim.
- Not a cross-dataset victory claim.

