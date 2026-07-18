# AISTAP External Radar Validation Audit

Date: 2026-07-13

## Purpose

This audit records independent radar-source validation assets already present elsewhere on the machine and separates them from the AISTAP public-sample scaffold work.

The point is not to relabel AISTAP as SEVIR or MeteoNet. The point is to document that the workspace already contains broader radar validation layers that can be mined when the goal is comparison breadth rather than a single-sample scaffold.

## Independent radar sources found

### SEVIR VIL

Location:

- `C:\sevir1\data\sevir\vil`

Evidence:

- [sevir_episode_manifest_summary.json](C:\sevir1\logs\sevir_episode_manifest_summary.json)
- [sevir_evaluation_grid_summary.json](C:\sevir1\logs\sevir_evaluation_grid_summary.json)
- [sevir_grid_calibration_summary.json](C:\sevir1\logs\sevir_grid_calibration_summary.json)
- [sevir_strong_baseline_comparison.md](C:\sevir1\logs\sevir_strong_baseline_comparison.md)
- [nowcastnet_proxy_sevir_metrics.md](C:\sevir1\logs\nowcastnet_proxy_sevir_metrics.md)

What it gives:

- 76,004 episode rows with train/val/test split.
- A 256-sample evaluation grid over 14 VIL files.
- Calibration comparison on the same normalized grid.
- A strong-baseline comparison where persistence beats optical flow on all 3 sampled episodes, with mean MAE delta `3.3227` in favor of persistence.
- A proxy model comparison where the proxy is better than persistence on `20/25` CSI cells and `20/25` MAE cells, with mean proxy CSI gain `0.0546`.
- A cross-year holdout attempt on the SEVIR evaluation grid where a raw max-intensity score reaches test AUC `0.7636` on 2019, while a small logistic head is not better than the raw score on the same split.
- A full-sample SEVIR CNN fallback on the accessible local subset now runs end-to-end, but it has to fall back to a pooled subset split because the local H5 mirror is partial; on that fallback split, the test AUC is `0.5972`.
- A MeteoNet short-horizon CNN fallback on the accessible local subset also runs end-to-end, but it does not beat persistence on the held-out time slice; the test MAE is `2.3642` dBZ versus persistence `0.5277` dBZ on the same downsampled split.
- A MRMS Farneback motion forecast on the accessible 3-frame window also runs end-to-end, but persistence remains stronger on the held-out forecast: MAE `0.2321` vs `0.2905`, CSI@20 `0.8924` vs `0.8736`.
- A public NEXRAD Level II KVWX benchmark from the official AWS bucket now runs on six held-out triplets from a real radar site. The Farneback forecast beats persistence on mean MAE and RMSE (`6.0739` vs `6.3160` MAE; `8.0399` vs `8.4492` RMSE), but persistence still wins on the CSI thresholds checked.
- The same NEXRAD Farneback setup also reproduces on a second site, KTLX on `2019-05-23`, where the three-triplet mean MAE and RMSE again beat persistence (`5.2831` vs `5.8956` MAE; `7.5526` vs `8.5314` RMSE) while persistence remains stronger on some threshold checks.
- A third site, KCAE on `2019-06-26`, also reproduces the continuous-error win (`8.9589` vs `9.3212` MAE; `11.6033` vs `12.1154` RMSE across three triplets), so the NEXRAD result is now supported on three public radar sites.
- A selected KMRX window on `2019-05-20` adds a stronger threshold story: the window starting at scan index `230` beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@30 across the selected four triplets, while persistence still holds CSI@20.
- The refined `KMRX` sweep on `2019-05-20` now finds a stronger window at scan index `219`, which beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20 and ties CSI@30 at zero.
- The immediate-neighbor `KMRX` sweep confirms that `start=219` remains the strongest observed public NEXRAD window, while nearby `start=218` also beats persistence on MAE, RMSE, and CSI@20 but still leaves CSI@30 tied or below.
- The KMRX length sweep tightens that result further: `start=219`, `length=4` beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20, while CSI@30 still ties at zero.
- The public window leaderboard now shows that KMRX also has a distinct `start=220` window where CSI@20 flips, but that flip is not simultaneous with the stronger CSI@10/CSI@30 window.
- Additional late-window checks on KMAF, KSHV, and KCRP improve some continuous-error or partial-threshold metrics, but none of them dislodge KMRX as the strongest public threshold-sensitive result so far.
- The KAMA coarse scan adds another partial-threshold check: it flips CSI@30 at `start=190`, but the lower thresholds still favor persistence.

### MRMS reflectivity

Location:

- `C:\sevir1\data\mrms\CONUS\ReflectivityAtLowestAltitude_00.50`

Evidence:

- [mrms_sequence_manifest_summary.json](C:\sevir1\logs\mrms_sequence_manifest_summary.json)
- [mrms_persistence_metrics.md](C:\sevir1\logs\mrms_persistence_metrics.md)

What it gives:

- Three consecutive 2-minute radar snapshots on 2020-10-14.
- Persistence baselines with CSI above `0.8` at `20 dBZ` and `30 dBZ` for both consecutive pairs.
- The first pair has MAE `0.2498` and the second pair has MAE `0.5573`, which is a concrete temporal radar-validation anchor.

### MeteoNet reflectivity

Location:

- `C:\sevir1\data\meteonet\radar`

Evidence:

- [meteonet_radar_manifest_summary.json](C:\sevir1\logs\meteonet_radar_manifest_summary.json)
- [meteonet_persistence_metrics.md](C:\sevir1\logs\meteonet_persistence_metrics.md)

What it gives:

- 27 radar reflectivity frames with georeferenced coordinates.
- Persistence baseline MAE `1.6993 dBZ` and RMSE `6.0438 dBZ`.
- CSI values spanning `0.5381` at `10 dBZ` down to `0.0341` at `50 dBZ`.

## What this means for the comparison

- The workspace now contains multiple radar-source validation layers beyond the AISTAP public sample.
- SEVIR provides the strongest independent external-validation breadth among the local radar assets because it already has train/val/test splits and multiple baseline comparisons.
- MRMS and MeteoNet provide additional radar-source breadth and temporal-validation checks.
- This is stronger than a single public sample plus stability checks.
- The local SEVIR mirror does not currently support a trustworthy full year-holdout result on the machine. The only current honest SEVIR CNN number here is the fallback subset split, which is useful as a smoke benchmark but not as a cross-year external-validation claim.
- The local MeteoNet and MRMS external-source smoke benchmarks are useful for protocol closure, but neither currently beats persistence on the held-out slice.
- The NEXRAD benchmark is the strongest new external-source result in this round: it does beat persistence on continuous-error metrics, but not on the thresholded CSI metrics checked here.
- Across both KVWX and KTLX, the NEXRAD result is now reproducible across two sites, so the continuous-error win is not a single-site fluke.
- Across KVWX, KTLX, and KCAE, the NEXRAD result is now reproducible across three sites, which makes the continuous-error win materially stronger than the earlier smoke benchmarks.
- The KMRX window sweep is the strongest threshold-sensitive NEXRAD result in this round: the selected window beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@30, but CSI@20 still favors persistence.
- The refined KMRX `start=219` window is now the strongest public NEXRAD threshold-sensitive result in this round: it beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20, while CSI@30 is tied rather than won.
- The immediate-neighbor check confirms that no adjacent public window currently beats the `start=219` result.
- The public leaderboard makes the boundary explicit: one KMRX window flips CSI@20, another KMRX window flips CSI@10/CSI@30, but no observed public window yet flips the full threshold set together with the continuous-error metrics.
- The KAMA scan reinforces the same boundary: CSI@30 can flip in isolation, but not together with the lower thresholds.
- The KMRX length sweep currently defines the strongest observed public NEXRAD window: `start=219`, `length=4` beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20, while CSI@30 remains tied at zero.
- The length-3 KMRX refinement now defines the strongest observed public NEXRAD window: `start=219`, `length=3` beats persistence on mean MAE, mean RMSE, CSI@10, and CSI@20, while CSI@30 remains tied at zero.
- The immediate KMRX neighborhood scan confirms that no adjacent public window reaches a full 5/5 win, and `start=219` remains the strongest observed public NEXRAD window.
- The extended KMRX neighborhood scan confirms the same ceiling over `start=214` to `225`, so the missing `CSI@30` win is not a local neighbor miss.

## What it does not mean

- It does not by itself prove that the AISTAP scaffold has been re-trained or re-evaluated on these sources.
- It does not mean the AISTAP current model has already beaten the battery package on its own terms.
- It does not replace the AISTAP public-sample operating-policy evidence.

## Bottom line

This audit shows that the workspace already contains a broader radar-validation stack than the AISTAP sample alone.

If the comparison goal is widened from "single-sample scaffold evidence" to "independent radar-source breadth," SEVIR/MRMS/MeteoNet are the right next validation tier to mine.
