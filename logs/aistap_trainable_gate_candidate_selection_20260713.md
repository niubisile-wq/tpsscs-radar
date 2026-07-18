# AISTAP Trainable-Gate Candidate Selection

## Goal

Select the strongest currently available trainable target-preservation candidate without leaving the public AISTAP-SIM scaffold boundary.

## Compared candidates

| Rank | Hidden | Steps | Train loss | Train gate gap | Val gate gap | Val Pd @ Pfa=1e-2 |
|---|---:|---:|---:|---:|---:|---:|
| 20 | 8 | 100 | 0.0469 | 0.3624 | 0.3933 | 1.0000 |
| 20 | 16 | 50 | 0.0310 | 0.7973 | 0.9207 | 1.0000 |
| 20 | 16 | 100 | 0.0189 | 0.8499 | 0.9210 | 1.0000 |
| 20 | 16 | 150 | 0.0149 | 0.8711 | 0.9216 | 1.0000 |
| 30 | 8 | 50 | 0.0645 | 0.3211 | 0.3688 | 0.9767 |

## Selection

The strongest current trainable candidate for the low-false-alarm regime is `rank=30`, `hidden=16`, `steps=150`, with learning rate `0.02`.

## Why this candidate

- The follow-up learning-rate sweep on the same rank/hidden/step setting shows `0.02` improves the stricter low-false-alarm frontier and the public-sample target-loss metric relative to `0.005` and `0.01`.
- The branch remains finite and stable.
- The step sweep still supports `150` over `100`, while `200` degrades the frontier.

## Follow-up preferred branch

- `rank=30`, `hidden=16`, `steps=150`, `lr=0.02` is now the preferred manuscript-facing branch for the low-false-alarm regime.

## What it does not prove

- It does not prove a finished detector.
- It does not prove deployable target-preservation closure.
- It does not prove unconditional superiority over the five-reference comparison set.

## Usage

Use this candidate as the manuscript-facing trainable-gate branch until a stronger evidence class appears.
