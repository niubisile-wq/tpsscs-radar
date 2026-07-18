# AISTAP High-Leverage Gap Priority

Date: 2026-07-13

## Purpose

This list ranks the remaining gaps by how likely they are, in principle, to improve the paper's position against the five-reference target set.

It does not reopen the current scope. It tells future work where the biggest leverage would be if the paper ever moves beyond the final lock.

## Priority 1: deployable target-preservation branch

Why this is first:

- It is the clearest path from scaffold evidence to detector evidence.
- It would improve the strong-baseline acquisition reference and the result-layering reference at the same time.
- It would also make the target-preservation story more concrete than the current oracle diagnostics.

What it would need to show:

- stable train/infer behavior,
- improved frontier over the low-rank baseline,
- and a clear boundary between diagnostic and deployable behavior.

## Priority 2: finished detector result

Why this is second:

- A finished detector result would directly attack the biggest remaining gap against the strongest references.
- It would change the evidence class more than another descriptive frontier summary.

What it would need to show:

- end-to-end numerical stability,
- consistent operating improvement over the baseline,
- and enough maturity to stop calling the method a scaffold.

## Priority 3: new data source or broader protocol family

Why this is third:

- It would test whether the current operating frontier generalizes beyond the public AISTAP-SIM boundary.
- It would strengthen the scaling / protocol-sensitive reference comparison.

What it would need to show:

- the same trade-off structure,
- a comparable or stronger frontier,
- and a stable claim boundary across datasets or protocols.

## Priority 4: tighter claim-to-figure mapping

Why this still matters:

- It would improve claim hygiene even if no new detector result exists.
- It helps close the gap against the validation-layering / package references.

What it would need to show:

- fewer boundary phrases in the prose,
- stronger one-to-one mapping between evidence, figure captions, and claims,
- and less need to remind the reader about unsupported territory.

## Priority 5: package closure polish

Why this is last:

- The package is already locked for the current evidence set.
- Further polishing is useful, but it is not the main lever for changing the comparison position.

What it would need to show:

- no drift between draft, package, README, STATUS, claim matrix, and final comparison files.

## Bottom line

If the paper ever gets another evidence-class upgrade, the order should be:

1. deployable target-preservation branch,
2. finished detector result,
3. new data source / broader protocol family,
4. tighter claim-to-figure mapping,
5. package polish.

That is the shortest honest answer to "where should the next lift happen if we want to beat the five-reference set?"
