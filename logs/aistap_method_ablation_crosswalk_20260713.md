# AISTAP Method/Ablation Crosswalk

Date: 2026-07-13

## Purpose

Lock the current TP-SSCS method story to the evidence already available in the public sample, so the manuscript can move from scaffold to ablation language without inventing new claims.

## Crosswalk

| method component | current evidence | manuscript role |
|---|---|---|
| low-rank suppression baseline | rank sweep on `simMed`, `simWind`, `simNoiseOnly` | establishes the trade-off between clutter attenuation and weak-target loss |
| target-preservation branch | scaffold and manuscript argument only | proposed fix for over-suppression; not yet a finished ablation result |
| CFAR calibration | low-`Pfa` audit at `1e-2`, `1e-3`, `1e-4` | turns the method into a detector with explicit operating-point control |
| sparse gating | scaffold and manuscript argument only | proposed mechanism to retain weak targets under suppression |
| end-to-end TP-SSCS scaffold | smoke path with finite shapes and powers | proves numerical compatibility, not training maturity |

## What the manuscript can already say

1. Low-rank suppression alone is a diagnostic baseline, not the final solution.
2. Target preservation is required because the sample shows strong suppression can erase weak targets.
3. CFAR calibration is required because detection quality depends on the false-alarm regime.
4. The scaffold is executable, so loss design and ablation, not infrastructure debugging, remain the method work.

## What the manuscript does not claim

- The target-preservation branch is not yet fully validated.
- Sparse gating superiority is not established before an actual ablation.
- The scaffold is not described as a trained detector.

## Boundary note

This crosswalk is the bridge from sample evidence to the method section. It is intentionally conservative and keeps the current work bounded to the public sample and scaffold stage.
