# AISTAP Consolidated Evidence-Gap Summary

## One-line verdict

The paper is submission-locked, evidence-rich, and clearly stronger than the early scaffold state, but it has not yet earned an unconditional win over the five-reference comparison set.

## What is proven

- The public AISTAP-SIM sample is sufficient for the current TP-SSCS scaffold, the first ablations, and the operating-policy discussion.
- The low-rank suppression baseline shows the expected suppression-versus-target-loss trade-off.
- The dense operating-surface note captures a measured rank / `Pfa` frontier.
- The target-preservation diagnostics show oracle headroom, but only as upper-bound evidence.
- The target-preservation diagnostics now also include a trainable-gate candidate for the low-false-alarm regime (`rank=30`, `hidden=16`, `steps=150`, `lr=0.02`) that improves over the low-rank residual baseline on target loss while remaining scaffold-bounded.
- The minimal trainability check shows the scaffold can be optimized without numerical collapse.
- The stress grid shows that the best rank shifts under perturbation.
- The five-reference comparison is fully documented at the boundary, the scorecard, the dashboard, and the win/loss level.
- The manuscript draft, the submission package, the claim matrix, and the root status files are aligned.

## What is not proven

- A deployable target-preservation branch.
- A finished detector result.
- Cross-dataset victory.
- Universal robustness.
- Unconditional superiority over the five-reference set.

## What has been absorbed from the five references

- Second Batch 1: submission closure discipline.
- Second Batch 2: claim hygiene and validation layering.
- reference package 1: reproducibility-first benchmarking and strong-baseline acquisition.
- `power_se`: scaling stability and claim separation.
- `battery`: frontier maturity and layered result framing.

## What would justify reopening the scope

1. A new data source beyond the current public AISTAP-SIM boundary.
2. A deployable target-preservation branch that changes the evidence class.
3. A finished detector result that is no longer scaffold-bound.

## Current interpretation

The right current framing is:

- locked manuscript
- evidence-rich public-sample study
- scaffold-stage TP-SSCS paper
- comparison complete
- target-preservation now has a trainable candidate, but not a finished detector
- unconditional win not yet proven

