# AISTAP Trainable-Branch Comparison Note

## Purpose

Map the current trainable-gate branch to the five-reference comparison set without turning it into a win claim.

## Branch state

- Current manuscript-facing branch for the low-false-alarm regime: `rank=30`, `hidden=16`, `steps=150`, `lr=0.02`.
- It improves target loss relative to the low-rank residual baseline while remaining finite and stable.
- It survives the current stress grid without collapsing.

## Comparison impact

### Against the reproducibility-first reference

The branch strengthens the paper because it moves the scaffold beyond a smoke test and into a measured trainable branch with better strict-Pfa behavior.

### Against the scaling / protocol-sensitive references

The branch strengthens the paper because it adds a trainable target-preservation candidate on top of dense rank/Pfa evidence and stress behavior.

### Against the frontier-maturity reference

The branch helps the paper because it turns target preservation from an oracle diagnostic into a concrete manuscript-facing branch, but it still does not close the frontier completely.

## What changes in the comparison ledger

- The paper is no longer only oracle-backed on target preservation.
- The paper now has a concrete trainable candidate with a stable nearby learning-rate setting, and the strict low-false-alarm branch is the preferred manuscript-facing one.
- The paper still lacks a deployable target-preservation branch and a finished detector.

## What does not change

- The paper does not yet win the five-reference comparison unconditionally.
- The paper does not yet have cross-dataset victory.
- The paper remains public-sample bounded and scaffold bounded.
