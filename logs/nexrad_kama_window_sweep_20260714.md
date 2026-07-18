# NEXRAD KAMA Window Sweep

Date: 2026-07-14

## Purpose

Check whether the KAMA public radar site can improve on the current best public-NEXRAD threshold result.

## Coarse scan

- Station: `KAMA`
- Date: `2019-06-26`
- Window length: 6 scans
- Candidate starts: `150`, `160`, `170`, `180`, `190`

## Best observed window

### `start=190`, `end=195`

- mean MAE: `4.0110` vs persistence `4.1740`
- mean RMSE: `5.5094` vs persistence `5.7843`
- mean CSI@10: `0.1840` vs persistence `0.2051`
- mean CSI@20: `0.0098` vs persistence `0.0112`
- mean CSI@30: `0.0033` vs persistence `0.0025`

## Interpretation

- KAMA did not dislodge the current KMRX/KCRP-derived threshold leader.
- The best KAMA window only flips CSI@30, while the other threshold metrics still favor persistence.
- KAMA remains useful as a negative/partial-threshold check, not a stronger external win.
