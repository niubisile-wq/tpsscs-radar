# AISTAP Current Low-Pfa Branch Comparison Summary

Date: 2026-07-13

## Current preferred branch

- `rank=30`
- `hidden=16`
- `steps=150`
- `lr=0.02`

## Why this branch is preferred

- It improves the stricter low-false-alarm frontier relative to the nearby learning-rate alternatives.
- It is finite and competitive under the stress grid.
- It remains finite and competitive across three checked seeds.
- It keeps the public-sample target-preservation evidence in a concrete trainable branch rather than only an oracle diagnostic.
- It is the branch now used by the manuscript-facing comparison notes.

## Current comparison position against the five-reference set

- Ahead on trainable-branch evidence.
- Ahead on strict low-Pfa target-preservation specificity.
- Ahead on operating-policy detail.
- Ahead on repeat-seed stability for the preferred branch.
- Tied on claim hygiene.
- Behind on submission closure.
- Behind on deployable target-preservation closure.
- Behind on finished-detector status.
- Behind on cross-dataset victory.

## What this means

- The paper is stronger than the early scaffold state.
- The current trainable branch is a real comparison asset, not just an ablation artifact.
- The current evidence still does not justify an unconditional victory claim over the five-reference set.

## Boundary

- Public sample only.
- Trainable scaffold only.
- Not a finished detector claim.
- Not a cross-dataset victory claim.
