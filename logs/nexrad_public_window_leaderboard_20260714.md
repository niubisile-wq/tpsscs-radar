# NEXRAD Public Window Leaderboard

Date: 2026-07-14

## Purpose

Keep the current public NEXRAD search focused on the windows that actually moved the comparison.

## Best supported windows so far

### KMRX `2019-05-20`

- `start=219`, `length=3`, `end=221`
- beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20 across the short event window
- CSI@30 still ties persistence at zero
- This is now the strongest public NEXRAD window observed so far in the current batch

### KMRX `2019-05-20`

- `start=219`, `length=4`, `end=222`
- beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20 across the refined four triplets
- CSI@30 still ties persistence at zero
- This remains strong, but it is now second to `start=219, length=3`

### KMRX `2019-05-20`

- `start=219`, `end=224`
- beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20 across the refined four triplets
- CSI@30 still ties persistence at zero
- This remains a strong nearby window, but it is now second to `start=219, length=4`

### KMRX `2019-05-20`

- `start=230`, `end=235`
- beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@30 across the selected four triplets
- CSI@20 still favors persistence
- This remains a near-top threshold-sensitive window, but it is now second to `start=219`

### KMRX `2019-05-20`

- `start=220`, `end=225`
- beats persistence on mean MAE, mean RMSE, and CSI@20 across the selected four triplets
- CSI@10 and CSI@30 still favor persistence
- This is the only currently observed window where CSI@20 clearly flips the comparison

## Recent negative / weaker checks

### KMAF `2019-06-26`

- `start=240`, `end=245`
- beats persistence on mean MAE, mean RMSE, and CSI@30
- CSI@10 and CSI@20 still favor persistence

### KSHV `2019-06-26`

- `start=240`, `end=245`
- beats persistence on mean MAE and mean RMSE
- CSI@10, CSI@20, and CSI@30 still favor persistence

### KCRP `2019-06-26`

- `start=260`, `end=265`
- beats persistence on mean MAE and mean RMSE
- CSI@10 and CSI@30 still favor persistence, CSI@20 also still favors persistence

### KCRP `2019-06-26`

- `start=300`, `end=305`
- beats persistence on mean MAE and mean RMSE
- CSI@20 still favors persistence

### KAMA `2019-06-26`

- `start=190`, `end=195`
- beats persistence on mean MAE and mean RMSE, and flips CSI@30
- CSI@10 and CSI@20 still favor persistence

## Working conclusion

The public NEXRAD line now has a reproducible continuous-error win across multiple sites, plus one threshold-sensitive window where CSI@20 flips and one where CSI@10/CSI@30 flip.

What it does not yet have is a single window or site that cleanly and reproducibly beats persistence on the full MAE/RMSE/CSI set.
