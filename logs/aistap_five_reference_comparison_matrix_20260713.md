# AISTAP Five-Reference Comparison Matrix

Date: 2026-07-13

## Purpose

This matrix compares the current Third Batch 3 AISTAP / TP-SSCS paper against five mature reference packages already present on the desktop. The goal is not to copy them. The goal is to extract the strongest standard from each one, then close the remaining experimental gaps in this paper so the manuscript can beat the reference set on evidence density, boundary discipline, and submission readiness.

## Reference set

1. `第二批1`
2. `第二批2`
3. `第三批1`
4. `power_se`
5. `battery`

## What each reference package does well

### 第二批1

- Strongest trait: closed manuscript packaging and submission hygiene.
- Useful lesson: a paper should have a clean, authoritative submission route with no draft drift.
- What this paper must match: a stable manuscript package, a readable proof chain, and no claim drift across draft / figures / boundary notes.

### 第二批2

- Strongest trait: claim discipline, boundary control, and validation layering.
- Useful lesson: the manuscript should separate supported claims, bounded claims, and unsupported claims with very little ambiguity.
- What this paper must beat: the current AISTAP draft should not just be bounded; it should also show a denser operating-policy result and a stronger evidence-to-claim mapping.

### 第三批1

- Strongest trait: reproducibility-first benchmarking and strong-baseline acquisition discipline.
- Useful lesson: the paper should keep a ledger of runnable, partial, proxy, and blocked baselines.
- What this paper must beat: TP-SSCS should move from scaffold-level proof toward a measured operating surface and a target-preservation ablation, not just a baseline acquisition matrix.

### power_se

- Strongest trait: multi-feeder scaling stability and explicit claim matrix separation.
- Useful lesson: the paper should show when a result is stable, feeder-dependent, or bounded, and say that early.
- What this paper must beat: the current AISTAP paper should convert the low-rank / CFAR trade-off into a real operating surface and then stress it, not stop at a single rank sweep.

### battery

- Strongest trait: protocol-sensitive ranking, split-level reversal, and ensemble sensitivity.
- Useful lesson: a manuscript becomes stronger when it distinguishes average performance, split wins, and ensemble behavior instead of collapsing them into one leaderboard.
- What this paper must beat: the AISTAP paper should not just show one best operating point. It should show the frontier across `k`, `Pfa`, and target-preservation settings, and use that frontier as the core result.

## Comparison matrix

| Reference | Main strength | Current AISTAP gap | What to add |
|---|---|---|---|
| 第二批1 | Submission closure | AISTAP is not yet at final submission closure | Keep the package authoritative and prevent draft drift |
| 第二批2 | Claim hygiene and validation layering | AISTAP boundary is good, but the evidence is still sparse | Add dense CFAR, target-preservation, and stress evidence |
| 第三批1 | Strong-baseline acquisition ledger | AISTAP has scaffold evidence, but not a trainability check | Add a minimal trainability check and keep the acquisition matrix explicit |
| power_se | Scaling stability and claim separation | AISTAP does not yet have a dense operating surface | Add rank/Pfa surfaces and stress the operating-policy logic |
| battery | Rank stability and ensemble sensitivity | AISTAP currently has trade-off evidence, not a full frontier | Add a target-preservation frontier and use it as the main result |

## What the current paper must prove to beat the set

1. The public sample supports a dense low-rank / CFAR operating surface, not just one sparse sweep.
2. A target-preservation ablation improves the frontier rather than only explaining the problem.
3. The TP-SSCS scaffold is trainable at minimum scale, or the paper clearly documents why it is not yet.
4. The manuscript can defend its boundary with the same rigor as the best reference packages.
5. The final manuscript reads as a controlled detection study, not as a toy smoke-test writeup.

## Experimental priorities derived from the comparison

1. Dense low-rank / CFAR operating surface.
2. Target-preservation diagnostic ablation.
3. Minimal TP-SSCS trainability check.
4. Stress grid on noise, phase, and target attenuation.
5. Manuscript integration and claim-boundary synchronization.

## Success condition

The current paper beats the five-reference set if it ends with:

- a denser operating frontier than the sparse rank/Pfa audit,
- a measured target-preservation story rather than only an argument,
- a trainability result or a clearly bounded non-result,
- a stress test that defines the fragility boundary,
- and a manuscript package whose claims stay tighter than the strongest reference notes.
