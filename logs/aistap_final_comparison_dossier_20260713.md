# AISTAP Final Comparison Dossier

Date: 2026-07-13

## Purpose

This dossier summarizes the current TP-SSCS project AISTAP / TP-SSCS paper against the five-reference target set and against the internal standards established in the comparison matrix, gap audit, and final submission lock.

## Bottom line

The paper is now competitive on evidence layering, boundary discipline, and operating-policy detail, but it is still not a finished detector paper and it still does not justify a cross-dataset victory claim.

## Comparison dimensions

### 1. Evidence layering

- The paper now has a dense operating surface, target-preservation diagnostics, a minimal trainability check, and a stress grid.
- This is stronger than a sparse smoke-test package and closer to the strongest reproducibility-first reference style.
- Remaining gap: no deployed target-preservation branch and no finished detector result.

### 2. Boundary discipline

- The manuscript boundary is explicit in the draft, submission package, README, STATUS, claim matrix, and submission lock.
- This is at least as disciplined as the strongest package-style references.
- Remaining gap: the paper still should not be written as if the public-sample evidence already proves final superiority.

### 3. Operating-policy detail

- The dense low-rank / CFAR surface and the stress grid give a genuine operating-policy story.
- The multi-seed stress note shows that the preferred trainable branch remains finite and competitive across seeds `7`, `11`, and `23`.
- The new leave-one-subset-out cross-condition check across `simMed`, `simNoiseOnly`, and `simWind` broadens the protocol class and shows that the preferred branch remains finite under holdout.
- This is stronger than a single-rank or single-threshold audit.
- Remaining gap: the frontier is measured, but it is not yet a deployable detector frontier.

### 4. Trainability

- The minimal trainability check shows the scaffold can be optimized without numerical collapse, and the three-seed stability note shows the preferred branch is repeatable across seeds `7`, `11`, and `23`.
- The robustness dossier consolidates the preferred branch into one reviewer-facing stability view.
- This is stronger than a smoke test alone.
- Remaining gap: the trained scaffold is still not a finished detector.

### 5. Comparison standing

- The five-reference gap audit now places the paper closer to the reference set on evidence density and claim hygiene.
- The cross-paper positioning memo and scorecard now show that AISTAP is ahead on operating-policy depth and explicit trainability, but behind on external-validation breadth.
- The workspace now contains a separate radar-source audit on SEVIR, MRMS, and MeteoNet, which broadens the evidence class even though it is not yet an AISTAP retraining result.
- The SEVIR year-holdout radar validation attempt adds a direct independent-source test, but the local mirror is partial; the current honest CNN fallback split reaches test AUC `0.5972`, so this is smoke evidence rather than a real external-validation win.
- The new MeteoNet and MRMS smoke benchmarks broaden the external-validation stack, but both still sit below persistence on the held-out slice, so they are boundary evidence rather than new wins.
- The new public NEXRAD KVWX Level II benchmark is the first external radar result in this round that beats persistence on continuous-error metrics across multiple triplets, which strengthens the external-validation stack even though CSI thresholds still favor persistence.
- The KTLX repeat confirms the NEXRAD continuous-error win is reproducible across a second public radar site, which is materially stronger than a one-site smoke result.
- The KCAE repeat extends the same NEXRAD win to a third public radar site, making the continuous-error advantage look like a reproducible property of the chosen motion baseline rather than a site-specific fluke.
- The selected KMRX window sweep adds the best threshold-sensitive NEXRAD result in the current batch: the selected window beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@30, while CSI@20 still favors persistence.
- The refined KMRX `start=219` sweep improves the batch result further: it beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20, while CSI@30 ties at zero.
- The immediate-neighbor KMRX sweep confirms that no adjacent public window currently improves on the `start=219` result.
- The public leaderboard now makes the boundary sharper: KMRX also has a separate window where CSI@20 flips, but that window does not simultaneously beat persistence on the same full threshold set.
- Additional late-window checks on KMAF, KSHV, and KCRP do not dislodge KMRX as the strongest public threshold-sensitive result so far.
- The KAMA coarse scan adds another partial-threshold check: CSI@30 can flip in isolation, but the lower thresholds still favor persistence.
- The KMRX length sweep tightens the top result further: `start=219`, `length=4` beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20, while CSI@30 remains tied at zero.
- The length-3 KMRX refinement tightens the top result even further: `start=219`, `length=3` beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20, while CSI@30 remains tied at zero.
- The immediate KMRX neighborhood scan confirms that no adjacent window reaches a full 5/5 win, so the current boundary is real rather than a missed neighbor.
- The extended KMRX neighborhood scan confirms the same ceiling over `start=214` to `225`, so the remaining gap is structural rather than a local-neighbor miss.
- The paper still lacks the kind of final closure that would justify an unconditional win statement.
- The current best position is: stronger internal evidence stack, cleaner boundary, but still public-sample and scaffold bounded.

## What is now better than before

- The paper is no longer a smoke-test-only package.
- The paper now has a measured frontier rather than one sparse rank sweep.
- The paper now has a trainability result rather than a static scaffold only.
- The paper now has a genuine leave-one-subset-out cross-condition check rather than only a pooled split.
- The paper now has an explicit final lock and no longer treats further experiment expansion as high leverage.

## What still blocks a true win claim

- No deployable target-preservation branch.
- No finished detector result.
- No cross-dataset superiority.
- No universal best rank.
- No universal robustness guarantee.
- No external-validation layer comparable to the battery package.
- No independent external-validation layer comparable to the battery package.
- No AISTAP retraining result yet on the independent radar-source audit datasets.
- No AISTAP method result yet that exploits the SEVIR year-holdout layer directly.
- No completed AISTAP cross-source transfer result yet on the SEVIR holdout.

## Use in the final package

This dossier should be treated as the final comparison snapshot for the current public-sample evidence set. It is the document to cite when explaining why the manuscript is locked, what it already beats on evidence structure, and which claims remain out of scope.

