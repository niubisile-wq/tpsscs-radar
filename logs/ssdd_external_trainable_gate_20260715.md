# SSDD External Trainable-Gate Validation

Date: 20260715

## Setup

- Source: Official SSDD SAR Ship Detection Dataset.
- Split: official train images are split deterministically into development/validation; official test images are held out.
- Candidate: TP-SSCS-style trainable pixel gate over raw SAR intensity and low-rank/local residual features.
- Policy selection: `Pfa <= 1e-04` uses raw fallback; validation split selects the conservative operating policy for higher Pfa points.
- Test calibration: empirical Pfa threshold is calibrated only on official-test background pixels outside dilated ship boxes.

## Verdict

- Passed: `true`
- Official-test images: `231`
- Official-test annotations: `545`
- Test wins vs raw: `4/7`
- Test ties vs raw: `3/7`
- Test losses vs raw: `0/7`
- Test wins vs low-rank: `7/7`
- Mean Pd delta vs raw: `0.090855`

## Test Comparisons

| Pfa | Policy | Candidate Pd | Raw Pd | Low-rank Pd | Candidate empirical Pfa | Beats/ties raw | Beats low-rank |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1e-05 | `raw` | 0.0188 | 0.0188 | 0.0000 | 9.69004e-06 | `true` | `true` |
| 3e-05 | `raw` | 0.0373 | 0.0373 | 0.0004 | 2.99597e-05 | `true` | `true` |
| 1e-04 | `raw` | 0.0428 | 0.0428 | 0.0010 | 8.1714e-05 | `true` | `true` |
| 3e-04 | `gate` | 0.2630 | 0.1625 | 0.0025 | 0.000299946 | `true` | `true` |
| 1e-03 | `gate` | 0.4512 | 0.3317 | 0.0044 | 0.000999948 | `true` | `true` |
| 3e-03 | `gate` | 0.6096 | 0.4122 | 0.0067 | 0.00299994 | `true` | `true` |
| 1e-02 | `gate` | 0.7469 | 0.5284 | 0.0195 | 0.00999996 | `true` | `true` |

## Boundary

- This is a second independent radar dataset family, but it is SAR ship imagery rather than AISTAP range-Doppler simulation or IPIX sea-clutter time series.
- The result validates external trainable-gate adaptation, not zero-shot transfer of the AISTAP-SIM saved state.
- The protocol is acceptable as breadth evidence only when interpreted together with the IPIX held-out validation and the official AISTAP-SIM full-asset tests.