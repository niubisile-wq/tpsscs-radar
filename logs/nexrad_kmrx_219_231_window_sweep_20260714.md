# NEXRAD KMRX 219-231 Window Sweep

Date: 2026-07-14

## Purpose

Refine the strongest public NEXRAD threshold-sensitive window around the previously best KMRX region.

## Search range

- Station: `KMRX`
- Date: `2019-05-20`
- Candidate starts: `219` to `231`
- Window length: 6 scans

## Best observed window

### `start=219`, `end=224`

- mean MAE: `5.6700` vs persistence `6.1782`
- mean RMSE: `7.5791` vs persistence `8.2810`
- mean CSI@10: `0.0594` vs persistence `0.0592`
- mean CSI@20: `0.0171` vs persistence `0.0127`
- mean CSI@30: `0.0000` vs persistence `0.0000`

## Interpretation

- This is the strongest public NEXRAD window seen so far in the current batch.
- It beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20.
- It does not strictly beat persistence on CSI@30, but it ties it at zero.
- Compared with the earlier `start=230` window, this window is closer to a full-threshold win because it adds CSI@20.

## Secondary observations

- `start=230` remains strong on MAE, RMSE, CSI@10, and CSI@30, but it still loses CSI@20.
- Neighboring windows `220`, `228`, and `231` are still competitive but weaker than `219` on the current score rule.
