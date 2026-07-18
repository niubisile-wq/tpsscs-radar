# AISTAP Figure/Text Linkage

Date: 2026-07-13

## Purpose

Map the existing figure and table draft directly to the prose that surrounds it in the manuscript.

## Linkage

### Figure 1

Text block: the task is framed as target-preserving detection under low false alarm, not pure clutter cancellation. The public sample is the evidence that makes that framing necessary.

### Figure 2

Text block: stronger low-rank suppression is not monotone improvement. The manuscript states that clutter attenuation rises with `k`, but weak-target loss also rises, so the baseline has an operational boundary.

### Figure 3

Text block: low-`Pfa` detection is discussed as an operating-policy problem. The manuscript states that the best residual baseline depends on both the false-alarm target and the suppression rank.

### Figure 4

Text block: the current TP-SSCS path is only a scaffold. The manuscript uses this figure to show numerical finiteness and implementation readiness, not final training maturity.

### Table 1

Text block: the rank sweep summary makes the trade-off readable in one place, with clutter attenuation and target loss reported together.

### Table 2

Text block: the CFAR summary reports raw and residual `Pd` at fixed `Pfa`, plus empirical false-alarm behavior.

### Table 3

Text block: the manuscript boundary table separates supported claims from unsupported ones and keeps the public-sample boundary explicit.

## Writing rule

- Put the narrative sentence before each figure or table.
- Never let the caption carry a claim the text has not already stated.
- Never let the text imply the scaffold is already a finished trained method.

## Boundary note

The linkage is complete enough to draft the first full results section, but the manuscript still remains bounded to the public sample and scaffold stage.
