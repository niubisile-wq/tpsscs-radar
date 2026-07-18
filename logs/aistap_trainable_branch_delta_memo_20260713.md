# AISTAP Trainable-Branch Delta Memo

## Purpose

State the comparison delta created by the current best trainable branch for the low-false-alarm regime (`rank=30`, `hidden=16`, `steps=150`, `lr=0.02`) against the five-reference set.

## Delta summary

### Reference 1: closed submission / package hygiene

- Delta: small but real.
- Why: the paper now has a concrete trainable branch, so the package is more than a locked scaffold.
- Limit: it is still not a truly closed detector package.

### Reference 2: claim hygiene / validation layering

- Delta: mostly neutral to slightly positive.
- Why: the branch is now named, measured, and bounded consistently across draft, package, README, STATUS, and claim matrix.
- Limit: the strongest reference still has cleaner supported / bounded / unsupported closure.

### Reference 3: reproducibility-first benchmarking / strong-baseline acquisition

- Delta: positive.
- Why: the paper now adds a concrete trainable branch on top of dense operating surfaces, target-preservation diagnostics, and stress behavior.
- Limit: it still lacks a deployable branch or finished detector result.

### Reference 4: scaling stability / claim separation

- Delta: modestly positive.
- Why: the branch remains finite under stress and preserves the validation operating point.
- Limit: it is still public-sample bounded and not universally stable.

### Reference 5: protocol-sensitive ranking / ensemble sensitivity

- Delta: positive.
- Why: the paper now has a concrete trainable branch rather than only oracle target-preservation diagnostics.
- Limit: the reference still has a more mature frontier story at the level of average metrics, split-level behavior, and result hierarchy.

## What this delta does to the overall ledger

- It moves the paper farther away from a smoke-test package.
- It strengthens the claim that the manuscript is evidence-rich and scaffold-stage.
- It does not convert the paper into a finished detector or an unconditional winner.

## Practical takeaway

The trainable branch is now a real comparison asset, not just an ablation artifact. It reduces the gap on evidence layering and target-preservation specificity, especially in the stricter low-Pfa regime, but it does not by itself win the five-reference comparison.
