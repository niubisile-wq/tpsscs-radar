# AISTAP Trainable-Branch Strict-Pfa Preference

Date: 2026-07-13

## Branches compared

- `rank=20`, `hidden=16`, `steps=150`, `lr=0.01`
- `rank=30`, `hidden=16`, `steps=150`, `lr=0.02`

## Why the stricter branch is preferred

The paper's operating regime is low false alarm, so the stricter Pfa region matters more than the loosest evaluated point.

In that region:

- `rank=30, hidden=16, steps=150, lr=0.02` has the better Pd profile at `Pfa <= 1e-3`.
- It also has lower target loss on the public target-bearing items than the `rank=20, hidden=16, steps=150, lr=0.01` branch.
- It remains finite and competitive under the stress grid.

## Comparison snapshot

- `rank=20, hidden=16, steps=150, lr=0.01`
  - Validation gate gap: `0.9216`
  - Validation Pd at `Pfa=1e-2`: `1.0`
  - Mean Pd over `Pfa <= 1e-3`: `0.3070`
  - Mean target loss: `0.5561 dB`

- `rank=30, hidden=16, steps=150, lr=0.02`
  - Validation gate gap: `0.9211`
  - Validation Pd at `Pfa=1e-2`: `0.9767`
  - Mean Pd over `Pfa <= 1e-3`: `0.3442`
  - Mean target loss: `0.1970 dB`

## Interpretation

- If the manuscript is optimized for the loosest tested operating point, the `rank=20` branch still looks attractive.
- If the manuscript is optimized for the low-false-alarm regime that the paper actually studies, the `rank=30, hidden=16, lr=0.02` branch is the better comparison asset.
- The `rank=30, hidden=16, lr=0.02` branch is therefore the preferred manuscript-facing branch for the current lock.

## Boundary

- This is still public-sample evidence only.
- This does not claim a finished detector.
- This does not claim unconditional victory over the five-reference set.
