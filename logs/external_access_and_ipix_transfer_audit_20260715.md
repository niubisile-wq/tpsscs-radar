# External Access And IPIX Transfer Audit

Date: 2026-07-15

## Access probes

- RASPNet page probe: `logs/probe_raspnet_access.txt` now returns `HttpCode: 200`.
- NetRAD page probe: `logs/probe_netrad_page.txt` now returns `HttpCode: 202`.
- IPIX page probe: `logs/probe_ipix_page.txt` now returns `HttpCode: 200`.

## IPIX external source used

- Downloaded files: all 14 Dartmouth IPIX weak-target CDF recordings under `data/downloads/ipix/`.
- Reference smoke-test file: `data/downloads/ipix/19931107_135603_starea.cdf`.
- Reference file size: `15,732,284` bytes.
- Source page annotation: Dartmouth IPIX file `#17`, primary target range bin `9`, secondary bins `8:11`.
- Local structure: `14` range bins, `131072` sweeps, `2` transmit polarizations, `4` ADC channels.

## Transfer protocol

- Script: `scripts/evaluate_ipix_external_detector_transfer.py`.
- Output CSV: `results/ipix_external/ipix_external_detector_transfer_19931107_135603_starea_20260715.csv`.
- Output JSON: `results/ipix_external/ipix_external_detector_transfer_19931107_135603_starea_20260715.json`.
- Output note: `logs/ipix_external_detector_transfer_19931107_135603_starea_20260715.md`.
- The CDF is split into `128` windows of `1024` sweeps.
- Each window is converted to a range-Doppler map by per-channel mean removal, Hann windowing, and FFT-shift along sweep time.
- The target mask is primary bin `9`; bins `8,9,10,11` are excluded from the background false-alarm estimate.

## Result

- The independent IPIX zero-shot transfer is not a passing external-validation result.
- At `Pfa=1e-2`, raw reaches `Pd=0.0364`, while `tpsscs_finished_detector` reaches `Pd=0.0086`.
- At `Pfa=1e-2`, `tpsscs_trainable_gate` reaches `Pd=0.0241`, also below raw.
- The TP-SSCS detector remains calibrated by empirical Pfa, but it does not beat raw on this IPIX smoke test.

## Validated residual-aware fusion

- Script: `scripts/evaluate_ipix_validated_residual_fusion.py`.
- Output CSV: `results/ipix_external/ipix_validated_residual_fusion_test_20260715.csv`.
- Output JSON: `results/ipix_external/ipix_validated_residual_fusion_20260715.json`.
- Output note: `logs/ipix_validated_residual_fusion_20260715.md`.
- Development file: `19931107_135603_starea.cdf`.
- Validation file for beta selection: `19931107_141630_starea.cdf`.
- Held-out test files: the 12 recordings not used for development or beta selection.
- Selected score: `raw_z + 1.5 * (raw_z - TPSSCS_residual_z)`.
- No range-bin index feature is used.
- Held-out result: 7/7 Pfa wins over raw and low-rank.
- At `Pfa=1e-2`, fusion reaches `Pd=0.1374`, raw reaches `Pd=0.0972`, and low-rank reaches `Pd=0.0096`.
- The published IPIX table maps `19931107_145028_starea.cdf` to primary target bin `8`; this corrected mapping is used in the 12-recording held-out run.

## Interpretation

- The zero-shot pipeline is useful negative evidence: the current AISTAP-SIM-trained state alone does not transfer strongly enough.
- The validation-selected residual-aware fusion is positive independent IPIX evidence across 12 held-out recordings, but it is still one external dataset family and does not by itself match the battery package's multi-tier external-validation breadth.
- The official AISTAP-SIM `simMed_test`/`simWind_test` evidence supports method-level cross-condition robustness inside AISTAP-SIM.
- It closes the method-level independent external-validation gate, but it still does not close the broader local-reference-superiority gap against the battery package.
