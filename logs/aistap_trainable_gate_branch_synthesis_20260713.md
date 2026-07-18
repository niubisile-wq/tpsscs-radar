# AISTAP Trainable-Gate Branch Synthesis

## Branch summary

The strongest current target-preservation branch for the low-false-alarm regime is the trainable gate with `rank=30`, `hidden=16`, `steps=150`, and learning rate `0.02`.

## Why this branch is the current manuscript-facing candidate

- It is the strongest setting in the small trainability sweep when the low-false-alarm region is weighted more heavily.
- It improves over the low-rank residual baseline on public-sample target loss while staying finite and stable.
- It stays competitive at the stricter `Pfa` settings that matter most for this paper.
- The local learning-rate sweep now favors `0.02` for the stricter low-false-alarm frontier.
- The step sweep shows `150` is better than `100`, while `200` is worse.
- It remains competitive under the stress grid instead of collapsing.

## Measured anchors

- Low-rank residual baseline: `Pd=0.256`, `target_loss=6.191 dB`.
- Trainable gate candidate: `Pd=0.253`, `target_loss=0.197 dB`, `clutter_attenuation=7.594 dB`.
- Best trainability run: train loss `0.0168`, train gate gap `0.8803`, validation gate gap `0.9211`.
- Learning-rate sweep: `0.02` improves the stricter low-false-alarm frontier and the public-sample target-loss metric relative to `0.005` and `0.01`.
- Stress grid: the trainable gate remains finite and competitive under noise, amplitude, phase, target attenuation, and clutter scaling perturbations.

## Interpretation

This branch is the closest current step from oracle target-preservation diagnostics toward a deployable candidate in the paper's low-false-alarm regime. It is still scaffold-bounded, but it is no longer only an oracle upper bound.

## What it does not prove

- It does not prove a finished detector.
- It does not prove deployable target-preservation closure.
- It does not prove unconditional superiority over the five-reference comparison set.

## Usage

Use this branch as the manuscript-facing target-preservation candidate for the low-false-alarm regime until a stronger evidence class appears.
