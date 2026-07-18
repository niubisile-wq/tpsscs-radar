# NEXRAD KMRX 216-219 Window Sweep

Date: 2026-07-14

## Purpose

Check whether any immediate neighbor of the current best KMRX window can also flip CSI@30 without losing the other wins.

## Results

### `start=216`, `end=221`

- mean MAE: `5.9118` vs persistence `6.0917`
- mean RMSE: `7.9036` vs persistence `8.2153`
- mean CSI@10: `0.0522` vs persistence `0.0664`
- mean CSI@20: `0.0175` vs persistence `0.0199`
- mean CSI@30: `0.0000` vs persistence `0.0016`

### `start=217`, `end=222`

- mean MAE: `5.7873` vs persistence `6.0994`
- mean RMSE: `7.7376` vs persistence `8.2064`
- mean CSI@10: `0.0554` vs persistence `0.0645`
- mean CSI@20: `0.0152` vs persistence `0.0178`
- mean CSI@30: `0.0000` vs persistence `0.0016`

### `start=218`, `end=223`

- mean MAE: `5.7102` vs persistence `6.1497`
- mean RMSE: `7.6420` vs persistence `8.2633`
- mean CSI@10: `0.0571` vs persistence `0.0634`
- mean CSI@20: `0.0162` vs persistence `0.0145`
- mean CSI@30: `0.0000` vs persistence `0.0000`

### `start=219`, `end=224`

- mean MAE: `5.6700` vs persistence `6.1782`
- mean RMSE: `7.5791` vs persistence `8.2810`
- mean CSI@10: `0.0594` vs persistence `0.0592`
- mean CSI@20: `0.0171` vs persistence `0.0127`
- mean CSI@30: `0.0000` vs persistence `0.0000`

## Interpretation

- `start=219` remains the strongest immediate-neighbor window.
- It is the best public NEXRAD threshold-sensitive result currently observed in this batch.
- The data still does not reveal a public window that cleanly beats persistence on CSI@30 while preserving the other wins.
