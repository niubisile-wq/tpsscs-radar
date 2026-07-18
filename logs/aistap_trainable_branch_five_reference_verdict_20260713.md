# AISTAP Trainable-Branch Five-Reference Verdict

## Branch under review

- `rank=30`
- `hidden=16`
- `steps=150`
- `lr=0.02`

## Per-reference verdict

| Reference package | Current verdict | Why |
|---|---|---|
| Second Batch 1 | Slightly behind overall | The trainable branch improves evidence layering, but the package still does not have the stronger submission closure model of the closed reference. |
| Second Batch 2 | Tied to slightly behind | The branch improves target-preservation specificity, but claim hygiene and validation layering are still cleaner in the strongest reference. |
| reference package 1 | Ahead on specificity | The branch turns the manuscript from a smoke-test scaffold into a measured trainable branch, which is a clear step up in evidence class. |
| `power_se` | Behind on closure | The branch narrows the gap on trainability, but `power_se` still has the stronger closed comparison story. |
| `battery` | Behind on frontier maturity | The branch improves the manuscript's target-preservation evidence, but `battery` still has the more mature layered frontier story. |

## What this means

- The trainable branch improves the paper's position against all five references.
- It is a real comparison asset, not just an ablation artifact.
- It now has repeat-seed support in addition to single-seed support.
- It does not by itself close the comparison against the strongest packages.

## What it does not mean

- It does not mean the paper has beaten all five packages.
- It does not mean the paper has a finished detector.
- It does not mean deployable target-preservation closure.

