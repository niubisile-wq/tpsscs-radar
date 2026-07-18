# AISTAP Robustness Dossier

Date: 2026-07-13

## Purpose

This dossier consolidates the strongest current AISTAP / TP-SSCS branch into one reviewer-facing robustness view.

The branch under review is:

- `rank=30`
- `hidden=16`
- `steps=150`
- `lr=0.02`

This is the current preferred trainable target-preservation branch.

## Consolidated evidence

### Target-preservation frontier

- Raw: mean `Pd=0.145`, mean target loss `0.000 dB`
- Low-rank residual: mean `Pd=0.256`, mean target loss `6.191 dB`
- Trainable gate: mean `Pd=0.253`, mean target loss `0.197 dB`
- Oracle gate: mean `Pd=0.236`, mean target loss `~0 dB`
- Oracle blend: mean `Pd=0.359`, mean target loss `2.726 dB`

### Minimal trainability

- Train loss: `0.6719 -> 0.0168`
- Train gate gap: `-0.0483 -> 0.8803`
- Validation gate gap: `-0.0654 -> 0.9211`
- Validation `Pd` at `Pfa=1e-2`: `0.9767`
- Validation empirical `Pfa` at `Pfa=1e-2`: `0.0100`

### Three-seed trainability stability

Seeds tested:

- `7`
- `11`
- `23`

Across all three seeds:

- Validation `Pd` at `Pfa=1e-2` stays at `0.9767`
- Validation empirical `Pfa` stays at `0.0100`
- Training `Pd` at `Pfa=1e-2` stays at `1.0000`
- Training empirical `Pfa` stays at `0.0100`
- Final train loss ranges from `0.0093` to `0.0264`
- Final gate gap ranges from `0.5006` to `0.9211`

### Three-seed stress stability

Seeds tested:

- `7`
- `11`
- `23`

At the `noise=0.05` / `Pfa=1e-3` check:

- Trainable gate mean `Pd` is `0.7442` for all three seeds
- Trainable gate empirical `Pfa` is `0.0010` for all three seeds

The low-rank baseline best-rank set varies only modestly across seeds:

- `7`: `1,20,30`
- `11`: `1,20,30`
- `23`: `1,15,20,30`

### Three-subset cross-condition holdout

Subsets tested in leave-one-subset-out mode:

- `simMed`
- `simNoiseOnly`
- `simWind`

Across seeds `7`, `11`, and `23`, the held-out test-time `Pd` at `Pfa=1e-2` is:

- `simMed`: `0.8178 ± 0.2169`
- `simNoiseOnly`: `0.8682 ± 0.0120`
- `simWind`: `0.8295 ± 0.1719`

The low-rank residual baseline still remains stronger on `simMed` and `simWind` at several operating points, and the raw map remains competitive on `simNoiseOnly` at the loosest tested point. The important addition is protocol breadth: the preferred branch now survives a genuine leave-one-subset-out check rather than only a single pooled split.

## What this proves

- The preferred trainable branch is not a one-off optimization artifact.
- The target-preservation frontier stays well separated from the low-rank residual baseline.
- The trainable gate remains finite under perturbation and across nearby random seeds.
- The current operating-policy conclusion is robust in direction.
- The current branch also survives a three-subset cross-condition holdout check on `simMed`, `simNoiseOnly`, and `simWind`.

## What it does not prove

- It does not prove a finished detector.
- It does not prove cross-dataset superiority.
- It does not prove the external-validation breadth of the battery package.
- It does not prove independent external-dataset breadth comparable to the battery package.
- It does not prove the cross-feeder benchmark framing of `power_se`.

## Bottom line

The current AISTAP branch is stable enough to support a serious manuscript-facing claim about target-preserving, low-false-alarm operating behavior.

It is still not enough to honestly claim that the paper has fully beaten both the local power-system and battery manuscript packages in every comparison dimension.
