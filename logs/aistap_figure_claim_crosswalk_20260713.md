# AISTAP Figure/Claim Crosswalk

Date: 2026-07-13

## Purpose

Tie the current public-sample evidence to the exact manuscript claims so the figures, tables, and boundary statements stay synchronized.

## Crosswalk

| artifact | evidence source | manuscript claim |
|---|---|---|
| Figure 1 | public sample loader, smoke path, TP-SSCS scaffold | the task is target-preserving detection under low false alarm, not clutter removal alone |
| Figure 2 | low-rank sweep over `simMed`, `simWind`, `simNoiseOnly` | stronger low-rank suppression improves clutter attenuation but increases weak-target loss |
| Figure 3 | CFAR audit at `Pfa=1e-2`, `1e-3`, `1e-4` | low-false-alarm performance depends on both rank and operating point |
| Figure 4 | end-to-end scaffold smoke report | the implementation is numerically finite, but the model is still a scaffold |
| Table 1 | low-rank baseline summary | make the suppression trade-off readable without relying only on plots |
| Table 2 | CFAR operating summary | show the operating-policy behavior directly |
| Table 3 | manuscript boundary table | prevent overclaiming and keep the public-sample boundary explicit |

## What the crosswalk enforces

- Each main figure must support one primary claim.
- Each table must have one purpose and one boundary.
- No caption may imply cross-dataset superiority.
- No caption may describe the scaffold as a finished trained system.

## Publication-facing boundary

The current package supports a bounded paper about target preservation and low-false-alarm detection on the public sample. It does not support a claim of final benchmark victory across the broader data stack.
