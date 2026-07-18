# AISTAP Final Comparison Scorecard

Date: 2026-07-13

## Purpose

This scorecard turns the five-reference comparison matrix into a concrete progress table for the current AISTAP / TP-SSCS paper. It is not a victory claim. It is a working comparison ledger showing where the paper is already competitive and where it still trails the strongest reference packages.

## Scoring key

- `Ahead`: the current paper is stronger on this dimension.
- `Tied`: the current paper is roughly comparable on this dimension.
- `Behind`: the current paper still needs work on this dimension.
- `Not applicable`: the dimension does not cleanly compare to the reference package.

## Scorecard

| Comparison dimension | Reference packages strongest on this dimension | Current AISTAP standing | Why |
|---|---|---|---|
| Submission closure / package hygiene | The closed submission/package references | Behind | The package is now locked, but the manuscript is not being claimed as a finished closed detector paper. |
| Claim hygiene / boundary discipline | The validation-layering reference and the package references | Tied | Boundary language is now explicit across draft, submission package, README, STATUS, claim matrix, and lock artifacts. |
| Strong-baseline acquisition discipline | The reproducibility-first reference | Ahead on specificity, behind on closure | AISTAP has a full acquisition matrix and trainability check, but still no deployable target-preservation branch or finished detector. |
| Dense operating-policy detail | The scaling / protocol-sensitive references | Ahead on operating-policy density | AISTAP now has dense rank/Pfa surfaces, target-preservation diagnostics, and stress-grid behavior. |
| Rank / frontier stability | The scaling / protocol-sensitive and battery references | Tied to slightly behind | AISTAP has a measurable frontier, but it is still public-sample bounded and does not yet show universal stability. |
| Trainability evidence | The reproducibility-first reference | Ahead on measured trainability | AISTAP now has a concrete trainable branch, a learning-rate sweep, and a step sweep with finite loss reduction and improved gate separation. |
| Result layering / split-level nuance | The battery reference | Ahead on layer count | AISTAP now separates low-rank trade-off, CFAR operating surface, target-preservation diagnostics, trainability, and stress robustness. |
| Cross-dataset victory | None of the mature reference packages justify this for AISTAP yet | Behind | The current paper is intentionally bounded to the public AISTAP-SIM sample and scaffold stage. |

## Current competitive position

The paper is strongest where the references were strongest at layering and boundary discipline, and it is now materially better than a smoke-test package because it has dense operating surfaces, oracle diagnostics, a concrete trainable branch, and stress checks.

The paper is still behind the best closed-package references on true submission closure and behind any deployable-detector standard because it remains scaffold bounded and public-sample bounded.

## What would move the scorecard further

- A deployable target-preservation branch would improve strong-baseline closure.
- A new data source would improve cross-dataset comparison standing.
- A finished detector result would be required before any unconditional victory claim.

## Use

Use this scorecard as the operational summary of where AISTAP is ahead, tied, or behind the reference set.
