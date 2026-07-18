# AISTAP Cross-Paper Scorecard

Date: 2026-07-13

## Purpose

This scorecard compares the current AISTAP / TP-SSCS evidence stack against the local `power_se` and battery paper packages using the dimensions that are already material to the repository.

The aim is to make the comparison explicit and falsifiable, not to overclaim a win.

## Dimensions

| Dimension | AISTAP current evidence | `power_se` current evidence | battery current evidence | Current edge |
|---|---|---|---|---|
| Operating-policy depth | Dense low-rank / CFAR surface, target-preservation frontier, stress grid, strict full-asset detector protocol | Feeder runnable baseline, learned DNN baselines, shift check | External validation hierarchy, real-fleet comparators, holdout logic | AISTAP on detector operating-policy evidence |
| Trainability | Minimal trainability check succeeds and the saved state now drives a fixed conservative full-test detector | Learned DNN baselines across feeders, but in a different task family | Baselines and external validators, not a comparable trainability story | AISTAP on explicit trainable detector-path evidence |
| Boundary discipline | Public-sample boundary, scaffold-stage boundary, claim matrix, submission lock | Reproducibility-first and boundary-aware, but with a different task scope | Validation hierarchy and explicit non-claims about missing Beihang binding | AISTAP ties for discipline, not a decisive edge |
| External validation breadth | Two official AISTAP-SIM full-test conditions (`simMed_test`, `simWind_test`) with `210` target-bearing frames; independent IPIX validation-selected residual fusion passes on 12 disjoint held-out recordings; official SSDD SAR trainable-gate validation passes on `231` test images and `545` ship annotations | IEEE feeder family on the local machine | Multiple external source tiers and cross-source holdout | AISTAP now has the stronger radar-specific breadth |
| Cross-source / cross-domain reach | Not claimed | Feeder-to-feeder comparison within power systems | Real-fleet plus fallback transfer checks | battery on validation reach |
| Manuscript closure | Submission-locked package with figure/table pack and claim matrix | Mature manuscript pack with explicit baseline summaries | Mature submission package and validation artifacts | Tie or battery, depending on the reviewer lens |

## Readout

### Where AISTAP is ahead

- The AISTAP package now has the densest operating-policy story of the three.
- The AISTAP package now includes a measurable target-preservation frontier instead of only a residual baseline.
- The AISTAP package now has a saved-state detector path and a strict in-domain finished-detector protocol rather than only a static scaffold.
- The AISTAP package now has official cross-condition full-asset evidence across `simMed_test` and `simWind_test`.

### Where AISTAP is not yet ahead

- The AISTAP package now has one positive independent IPIX dataset-family validation layer, with 12 disjoint held-out recordings after separate validation-file beta selection.
- The AISTAP package now has a second positive independent radar-family validation layer on official SSDD SAR ship imagery, with 4/7 wins and 3/7 ties against raw, 0/7 raw losses, and 7/7 wins against low-rank.
- The independent IPIX zero-shot smoke test remains negative, so the positive result depends on validation-selected residual-aware adaptation rather than pure zero-shot transfer.
- The AISTAP package no longer has only one independent external radar family; it now combines IPIX and SSDD, which is stronger radar-specific external breadth than before.
- The AISTAP package is not a cross-feeder IEEE benchmark like `power_se`.

### Current honest conclusion

- AISTAP now beats the two reference packages on detector-operating-policy evidence density inside its own sample boundary.
- AISTAP now has stronger in-domain detector closure than before, including two official full-test AISTAP-SIM conditions.
- AISTAP now has enough radar-specific external breadth to test a superiority claim against the local battery package, while still avoiding a universal production-deployment claim.
- Therefore, the repository can justify a stronger internal-method and external-radar breadth story than before, subject to the automatic top-readiness gate.

## Next leverage point

The next useful addition, if the scope reopens, is a third independent non-AISTAP radar source such as authenticated RASPNet or a manageable NetRAD subset.
