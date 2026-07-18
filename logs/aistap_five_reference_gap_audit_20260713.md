# AISTAP Five-Reference Gap Audit

Date: 2026-07-13

## Purpose

This note records the current position of the Third Batch 3 AISTAP / TP-SSCS paper against the five-reference comparison set.

It is not a victory claim. It is a boundary audit for what is now measured, what is still missing, and what the final manuscript can safely say.

## Where the paper is now strong

- The public-sample evidence is denser than a sparse smoke-test package: it now includes the low-rank trade-off, dense CFAR surface, oracle target-preservation diagnostics, a minimal trainability check with a trainable-gate candidate, and a stress grid.
- The manuscript boundary is explicit and consistent across the draft, submission package, README, STATUS, and claim matrix.
- The paper now separates diagnostic upper bounds, trainable-scaffold evidence, and robustness limits instead of mixing them into one claim, and the trainable-gate candidate now has a stable nearby learning-rate setting.
- The paper now separates diagnostic upper bounds, trainable-branch evidence, and robustness limits instead of mixing them into one claim, and the trainable-gate branch now adds a concrete comparison increment.
- The paper now separates diagnostic upper bounds, trainable-branch evidence, and robustness limits instead of mixing them into one claim, and the trainable-gate branch now adds a concrete comparison increment.

## Where the paper is still behind the strongest references

- It still does not have a finished detector result.
- It still does not have a cross-dataset victory claim.
- It still does not have a deployed target-preservation branch.
- It still does not have the final submission closure that the most mature reference packages already have.

## Practical comparison summary

### Versus the closed submission/package references

The current paper now has comparable boundary discipline and clearer experiment layering, but it still needs final package closure and the last round of manuscript integration.

### Versus the reproducibility-first reference

The current paper now matches the style of explicit evidence layering and moves beyond a single smoke path, but it still stops short of a finished detector claim.

### Versus the scaling / protocol-sensitive references

The current paper now has dense rank/Pfa evidence and trainability/stress diagnostics, which makes its internal evidence stack richer, but it still needs the final manuscript-to-claim tightening to make the comparison fully persuasive.

## What the manuscript can safely claim now

- The public AISTAP-SIM sample supports a target-preserving, low-false-alarm framing.
- The low-rank suppression baseline exposes a real clutter-versus-target-loss trade-off.
- The dense CFAR surface shows the operating point depends on both rank and false-alarm target.
- The target-preservation diagnostics and minimal trainability check show the scaffold can move in the expected direction without numerical collapse, and the trainable-gate branch now closes part of the target-preservation gap with a stable nearby learning-rate setting.
- The stress grid shows the operating conclusion is robust in direction but perturbation-sensitive in detail.

## What the manuscript should still not claim

- Final TP-SSCS superiority.
- A finished detector.
- Cross-dataset victory.
- Universal best rank.
- Universal robustness.

## Conclusion

The paper is now much closer to the five-reference target set on evidence density, boundary discipline, and robustness language. The remaining work is final integration and claim tightening, not new scope expansion.
