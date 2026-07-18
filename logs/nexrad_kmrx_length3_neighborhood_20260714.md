# NEXRAD KMRX Length-3 Neighborhood Scan

Date: 2026-07-14

## Purpose

Check the immediate neighborhood of the strongest KMRX length-3 window to see whether any adjacent start can flip CSI@30.

## Search range

- Station: `KMRX`
- Date: `2019-05-20`
- Window length: `3` scans
- Candidate starts: `216` to `221`

## Results

### `start=219`, `end=221`

- mean MAE: `5.1027` vs persistence `5.9165`
- mean RMSE: `6.9123` vs persistence `7.9982`
- mean CSI@10: `0.0954` vs persistence `0.0725`
- mean CSI@20: `0.0255` vs persistence `0.0215`
- mean CSI@30: `0.0000` vs persistence `0.0000`
- score: `4/5`

### `start=218`, `end=220`

- mean MAE: `6.2071` vs persistence `5.9740`
- mean RMSE: `8.2781` vs persistence `8.0853`
- mean CSI@10: `0.0365` vs persistence `0.0778`
- mean CSI@20: `0.0084` vs persistence `0.0217`
- mean CSI@30: `0.0000` vs persistence `0.0000`
- score: `0/5`

## Interpretation

- The immediate neighborhood does not reveal any public KMRX window that beats persistence on all five metrics.
- `start=219` remains the strongest observed public NEXRAD window in the current batch.
- CSI@30 still does not move off zero in the best short window, so the remaining gap is genuine rather than an artifact of a too-long averaging window.
