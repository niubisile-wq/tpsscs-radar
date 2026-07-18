# NEXRAD KMRX Length Sweep

Date: 2026-07-14

## Purpose

Check whether changing the scan-window length around the best KMRX region can improve the public threshold-sensitive result.

## Search range

- Station: `KMRX`
- Date: `2019-05-20`
- Candidate starts: `216` to `220`
- Candidate lengths: `4` to `9` scans

## Best observed window

### `start=219`, `length=4`, `end=222`

- mean MAE: `5.3417` vs persistence `6.0224`
- mean RMSE: `7.1759` vs persistence `8.0972`
- mean CSI@10: `0.0744` vs persistence `0.0634`
- mean CSI@20: `0.0220` vs persistence `0.0131`
- mean CSI@30: `0.0000` vs persistence `0.0000`

## Interpretation

- This is the strongest public NEXRAD window observed so far in the current round.
- It beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20.
- CSI@30 still ties persistence at zero.
- Compared with the previous best `start=219`, `length=6` window, shortening the window to 4 scans gives a cleaner threshold win.

## Secondary observations

- The same start with lengths 5, 6, 7, 8, and 9 remains competitive but weaker on the combined score rule.
- In this sweep, no public KMRX window reached a full `5/5` win against persistence.
