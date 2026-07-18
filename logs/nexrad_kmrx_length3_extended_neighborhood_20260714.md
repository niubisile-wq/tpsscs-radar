# NEXRAD KMRX Length-3 Extended Neighborhood Scan

Date: 2026-07-14

## Purpose

Extend the immediate KMRX neighborhood scan to a wider band around the current best short window.

## Search range

- Station: `KMRX`
- Date: `2019-05-20`
- Window length: `3` scans
- Candidate starts: `214` to `225`

## Results summary

- `start=219` remains the best window in the band.
- `start=219` beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20.
- `CSI@30` still ties persistence at zero.
- No window in the scanned range reaches a full `5/5` win.

## Notable windows

### `start=219`, `end=221`

- mean MAE: `5.1027` vs persistence `5.9165`
- mean RMSE: `6.9123` vs persistence `7.9982`
- mean CSI@10: `0.0954` vs persistence `0.0725`
- mean CSI@20: `0.0255` vs persistence `0.0215`
- mean CSI@30: `0.0000` vs persistence `0.0000`
- score: `4/5`

### `start=216`, `end=218`

- mean MAE: `6.0788` vs persistence `6.0977`
- mean RMSE: `8.1037` vs persistence `8.2319`
- mean CSI@10: `0.0407` vs persistence `0.0617`
- mean CSI@20: `0.0277` vs persistence `0.0132`
- mean CSI@30: `0.0000` vs persistence `0.0000`
- score: `3/5`

## Interpretation

- The extended neighborhood confirms the same ceiling seen in the narrower search.
- The best public window remains short and sharp, but CSI@30 does not move off zero.
- This makes the remaining gap look structural rather than caused by a missed neighboring window.
