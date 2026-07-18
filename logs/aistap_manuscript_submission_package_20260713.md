# AISTAP Manuscript Submission Package

## Title

Target-preserving low-false-alarm radar detection under clutter suppression

## One-line takeaway

The manuscript argues that radar detection should be framed as a target-preserving, low-false-alarm problem rather than a clutter-cancellation problem.

## Highlights

- The public AISTAP-SIM sample shows a clear suppression-versus-target-loss trade-off.
- CFAR improves detection on low-rank residuals, but the best operating point depends on suppression rank.
- Target-preservation diagnostics show oracle headroom and a trainable-gate candidate, but still not a finished detector.
- The minimal trainability check shows the scaffold can be optimized without numerical collapse.
- The multi-seed stability note shows the preferred trainable branch stays stable across seeds `7`, `11`, and `23`.
- The stress grid shows that the operating conclusion is robust to perturbation, while best `k` still shifts.
- The multi-seed stress note shows the preferred branch stays finite and competitive across seeds `7`, `11`, and `23`.
- The robustness dossier consolidates the preferred branch into one reviewer-facing stability view.
- The new leave-one-subset-out cross-condition check across `simMed`, `simNoiseOnly`, and `simWind` broadens the protocol class, but it is still not independent external-dataset breadth.
- The external radar validation audit records independent SEVIR, MRMS, and MeteoNet sources already available elsewhere on the machine.
- The SEVIR year-holdout attempt records an external-radar smoke benchmark only; the local mirror is partial and the current honest CNN fallback split reaches test AUC `0.5972`.
- The five-reference gap audit shows that the paper is closer on evidence layering, but still not at finished-detector closure.
- The cross-paper scorecard shows that AISTAP is ahead on detector-operating-policy evidence density and explicit trainability, but still behind on external-validation breadth.
- The multi-seed stability note anchors the preferred branch at validation `Pd=0.9767` and empirical `Pfa=0.0100` across all three seeds.
- The multi-seed stress note anchors the preferred branch at a stable stress-grid response across all three seeds.
- The TP-SSCS scaffold is executable, but it remains a scaffold rather than a finished detector.
- The evidence is bounded to the public sample and does not claim cross-dataset superiority.

## Key points

1. Low-rank suppression is a diagnostic baseline, not a monotone operational win.
2. The right problem framing is target preservation under low false alarm.
3. Calibration belongs in the main method, not an appendix.
4. The target-preservation ablation is diagnostic, not a deployable detector, although it now includes a trainable-gate candidate.
5. The scaffold is trainable, but still not a finished detector.
6. The stress grid shows robustness without universal optimality.
7. The five-reference gap audit shows that the paper is closer on evidence layering, but still not at finished-detector closure.
8. The current evidence supports method design and first ablations, not a finished benchmark victory.
9. The manuscript should stay inside the public-sample boundary.
10. The strongest current trainable-gate candidate for the low-false-alarm regime is `rank=30`, `hidden=16`, `steps=150`, with learning rate `0.02`.
11. The `rank=20`, `hidden=16`, `steps=150`, `lr=0.01` branch remains the looser-Pfa alternative.
12. The strongest current learning rate for the preferred branch is `0.02`.
13. The trainable gate is now a concrete manuscript-facing branch rather than only an oracle diagnostic.
14. The trainable branch gives a concrete comparison increment against the five-reference set, but it is not yet a victory claim.
15. The trainable branch is now a real comparison asset, not just an ablation artifact.
16. The trainable branch reduces the gap, especially in the stricter low-Pfa regime, but it does not close the comparison.
17. The shortest comparison summary is that the branch reduces the gap, but it does not close the comparison.
18. The trainable-branch results/discussion paragraph is now written in manuscript-ready form.
19. The strict low-Pfa preference note now records why the `rank=30`, `hidden=16`, `steps=150`, `lr=0.02` branch is preferred.
20. The current low-Pfa branch comparison summary now records the shortest comparison summary for the preferred low-Pfa branch.
21. The low-Pfa branch dimension scorecard now records a dimension-by-dimension ledger for the preferred low-Pfa branch.
22. The low-Pfa branch multi-seed stability note now records repeat-seed evidence for the preferred low-Pfa branch.
23. The low-Pfa branch multi-seed paragraph now records a manuscript-ready multi-seed summary for the preferred low-Pfa branch.
24. The low-Pfa width check now records a rejected wider-hidden-width comparison point.
25. The low-Pfa hidden-width rejection now records a rejected hidden-width comparison point at 24.
26. The trainable branch now has a per-reference verdict card.

## Submission boundary

- Do not claim final detector closure.
- Do not expand beyond the public AISTAP-SIM sample.
- Do not convert the scaffold into a finished benchmark claim.
- Do not turn the five-reference gap audit or cross-paper scorecard into a victory claim.
- Do not turn the leave-one-subset-out cross-condition check into a claim of external-dataset breadth.
- Do not turn the external radar-source audit into an AISTAP retraining claim.
- Do not turn the SEVIR year-holdout result into an AISTAP transfer result without actually transferring the method.
- Do not keep expanding experiments for marginal leverage; the remaining work is final integration.
- The final submission lock is active for the current evidence set.
- The final comparison dossier records the final standing against the five-reference target set.
- The cross-paper scorecard records the dimension-by-dimension comparison against `power_se` and the battery package.
- The robustness dossier records the consolidated trainability and stress evidence for the preferred branch.
- The final improvement path map records the future lift path without reopening the experimental scope.
- The master comparison dashboard records the single operational comparison view.
- The final executive comparison summary records the shortest submission-facing comparison verdict.
- The five-reference win/loss tracker records the current win/loss verdict per reference package.
- The high-leverage gap priority list ranks the remaining gaps by future evidence-class leverage.
- The current comparison judgment card records the shortest current win/tie/behind verdict.
- The final Chinese summary records the shortest Chinese-language comparison summary.
- The comparison evidence index records the file-level evidence used for each reference package.
- The objective completion audit records which objective requirements are proven and which are still not.
- The final status table records the compact current state of the objective.
- The user-facing final summary records the shortest usable final summary.
- The consolidated evidence-gap summary records the shortest combined verdict on what is proven, what is not proven, and what would justify reopening the scope.
- The victory threshold card records the strict conditions required for an unconditional win claim.
- The reopen conditions card records exactly when the scope may be reopened for further evidence-class upgrades.
- The final go/no-go gate records whether the paper is presently allowed to claim a win over the five-reference set.
- The lessons-applied ledger records the strengths already absorbed from the five references.
- Keep the claim matrix and boundary reminder attached to the paper.
