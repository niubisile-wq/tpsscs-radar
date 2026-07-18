# AISTAP Cross-Paper Positioning Memo

Date: 2026-07-13

## Purpose

This memo records where the current Third Batch 3 AISTAP / TP-SSCS evidence stack sits relative to the local `power_se` and battery paper packages.

It is a positioning note, not a victory claim.

## Relative position against `power_se`

What AISTAP now has:

- a dense low-rank / CFAR operating surface across `k` and `Pfa`
- a measured target-preservation frontier with oracle and trainable-gate behavior
- a minimal trainability check that improves the validation frontier without numerical collapse
- a stress-grid robustness check that shows the operating-point conclusion is not accidental
- an explicit manuscript boundary tied to the public sample and scaffold stage

What `power_se` is still stronger at:

- cross-feeder reproducibility across a family of IEEE-style networks
- learned baseline reporting over several feeder sizes and operating regimes
- a mature engineering framing around reproducibility and shift checks

What this means:

- AISTAP is now stronger on operating-policy depth and target-preservation evidence.
- `power_se` remains stronger on its own domain-specific reproducibility and feeder-generalization narrative.
- The current AISTAP evidence does not support a direct apples-to-apples superiority claim over `power_se`, but it now has a denser experimental story than a sparse rank sweep or smoke-test package.

## Relative position against the battery package

What AISTAP now has:

- a measured operating frontier rather than a single-point result
- an explicit trainable-gate candidate with finite optimization behavior
- stress testing across noise, amplitude, phase, target attenuation, and clutter scaling
- a manuscript boundary that stays inside the public sample and does not drift into a finished-detector claim

What the battery package is still stronger at:

- external validation hierarchy across multiple data sources
- real-fleet comparator construction
- cross-source holdout and provenance framing

What this means:

- AISTAP is now stronger on radar operating-policy evidence and target-preservation diagnostics.
- The battery package remains stronger on external-validation breadth and provenance layering.
- The current AISTAP evidence does not support a direct replacement of the battery package's external-validation story, but it does support a more explicit detector-operating-frontier story.

## Bottom line

The current AISTAP stack is submission-locked and evidence-rich.

It is now materially stronger than a sparse experiment notebook, but it is still not a finished detector and not a universal cross-domain winner.

If the objective ever reopens, the next leverage point is a deployable target-preservation branch plus a broader external validation layer.
