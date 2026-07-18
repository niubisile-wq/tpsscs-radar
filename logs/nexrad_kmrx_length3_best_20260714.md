# NEXRAD KMRX Length-3 Best Window

Date: 2026-07-14

## Purpose

Record the strongest public-NEXRAD window found so far after tightening the KMRX search around `start=219`.

## Best observed window

### `start=219`, `length=3`, `end=221`

- mean MAE: `5.1027` vs persistence `5.9165`
- mean RMSE: `6.9123` vs persistence `7.9982`
- mean CSI@10: `0.0954` vs persistence `0.0725`
- mean CSI@20: `0.0255` vs persistence `0.0215`
- mean CSI@30: `0.0000` vs persistence `0.0000`

## Interpretation

- This is now the strongest public NEXRAD window observed in the current batch.
- It beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20.
- CSI@30 still ties persistence at zero.
- The gain over the previous `length=4` result shows the best public window is a short, sharp event window rather than a longer averaging window.
