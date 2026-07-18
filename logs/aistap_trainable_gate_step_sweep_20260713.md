# AISTAP Trainable-Gate Step Sweep

## Goal

Check whether extending training beyond the current best `rank=20`, `hidden=16`, `steps=150`, `lr=0.01` candidate improves the branch without leaving the public-sample scaffold boundary.

## Compared settings

| Steps | Train loss | Train gate gap | Val gate gap | Val Pd @ Pfa=1e-2 |
|---|---:|---:|---:|---:|
| 50 | 0.0310 | 0.7973 | 0.9207 | 1.0000 |
| 100 | 0.0189 | 0.8499 | 0.9210 | 1.0000 |
| 150 | 0.0149 | 0.8711 | 0.9216 | 1.0000 |
| 200 | 0.1000 | 0.7658 | 0.8860 | 0.8837 |

## Selection

The best step count is `150`.

## Interpretation

- `150` improves train loss and gate separation over `100`.
- `200` degrades the validation frontier, so longer training is not monotonically better.
- The branch has a short stable window rather than an open-ended improvement path.

## Boundary

- Public sample only.
- Candidate selection only.
- Not a finished detector result.
