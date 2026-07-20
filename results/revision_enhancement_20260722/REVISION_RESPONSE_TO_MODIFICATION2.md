# Modification-2 Experiment Execution Report

Date: 2026-07-21

This report records the concrete experiments and audits executed in response to the 16 comments in `修改意见2.txt`. Outputs are under `results/revision_enhancement_20260722`.

## Executive Findings

- Adaptive gate remains necessary under strict low-PFA operation. At `PFA=1e-5`, the adaptive detector reaches Pd `0.184532`, while the best validation-selected fixed fusion degenerates to pure residual (`w_residual=1.0`) with Pd `0.101461`. The paired frame bootstrap delta is `+0.083071`, 95% CI `[0.075228, 0.090999]`.
- IPIX background z-score and robust z-score calibration were attempted. Because the evaluation uses per-window rank-constrained thresholds, monotone within-window normalization does not change detections. The best IPIX `PFA=1e-5` result remains validated residual fusion Pd `0.074257` versus raw Pd `0.067560`. This is a measured-domain limitation, not a solved transfer result.
- CFAR low-PFA concern is addressed directly: at `PFA=1e-5`, the proposed detector Pd is `0.184532`; the best classical local CFAR in the sweep is `raw_goca_t4_g1_cfar_local` with Pd `0.102489`.
- SSDD low-PFA gate failure is quantified by tail moments. At `PFA=1e-5`, raw Pd is `0.018806`, gate Pd is `0.003469`, and low-rank Pd is `0.000032`. Gate background has a heavy extreme tail: kurtosis `38.286`, q99.99 `7.544`, max `61.443`, and threshold `17.245`.
- Temperature scaling of the SSDD gate score was run over `0.5, 0.75, 1, 1.5, 2, 4`. Since scaling is monotone and thresholds are recalibrated per PFA, Pd/Pfa are unchanged. This should be reported as a negative but informative calibration audit.
- A failure-oriented heatmap was generated from official AISTAP-SIM, not a success cherry-pick: `simMed_test.mat#124`, raw Pd `0.120`, adaptive Pd `0.000` at `PFA=1e-5`.

## Comment-by-Comment Resolution

| ID | Reviewer concern | Status | Concrete action/result | Output |
|---|---|---|---|---|
| 1 | Theory formula is tautological, not predictive. | Completed in manuscript | Reframed as mechanism formalization, not a generalization bound. The formula now supports interpretation of target absorption and gate fallback only. | `投稿专用/02_latex_source/manuscripts/TGRS终稿.tex` |
| 2 | Gate training may leak or rely on same simulation distribution. | Audit completed; wording revised | Protocol table separates AISTAP public training, AISTAP official test, IPIX, and SSDD. No official AISTAP test labels are used for training; the real limitation is in-domain coupling and cross-domain transfer. | `p0_protocol_audit_train_test_split.csv` |
| 3 | AISTAP-SIM parameters not described. | Completed from official README | Official AISTAP-SIM README confirms scenario roles and key parameters: two-meter Ku-band antenna, 50 ms GMTI CPI, 100 m range resolution, six antenna channels, 50 km standoff, nominal array size 2048 x 6 x 64 x 1024, ideal point-scatterer targets, 30 dB average target SNR and 15 dB peak clutter-to-noise ratio in the ground-clutter dataset, and 35 dB Taylor tapering. | `p0_aistap_sim_parameter_table.csv`; official `mit-ll/AISTAP-SIM` README; manuscript protocol section |
| 4 | IPIX failure only diagnosed, not repaired. | Experiment completed; repair weak | Background z-score and robust z-score were tested for raw, residual, gate score, and validated residual fusion over 336 windows. Rank-based Pd did not change after monotone calibration. Best `PFA=1e-5`: validated residual fusion Pd `0.074257`, raw Pd `0.067560`. | `p0_ipix_normalization_repair_summary.csv`, `p0_ipix_normalization_repair_detail.csv` |
| 5 | Abstract overclaims measured-data validation. | Completed in manuscript | Abstract now states AISTAP-SIM-bounded detector policy, limited background-normalized IPIX calibration, and SSDD adaptation only outside the sparsest false-alarm tail. | `投稿专用/02_latex_source/manuscripts/TGRS终稿.tex` |
| 6 | 32/500 average is slightly better than 16/150. | Resolved using existing ablation | Keep 16/150 because `PFA=1e-5` is slightly higher for 16/150 (`0.184532`) than 32/500 (`0.184219`) while being lighter; acknowledge 32/500 has slightly higher average Pd. | Existing `p1_width_steps_ablation_summary.csv` from 20260721 |
| 7 | CFAR 75-win evidence incomplete. | Completed in manuscript | Low-PFA sweep summary extracted and added. At `PFA=1e-5`, proposed Pd `0.184532`; best local CFAR Pd `0.102489`. | `p1_cfar_low_pfa_parameter_sweep.csv`; manuscript Table `tab:low-pfa-robustness` |
| 8 | SSDD low-PFA gate failure not analyzed enough. | Experiment completed | Added mean/std/skew/kurtosis/q99.9/q99.99/max/threshold gap. Gate tail at `1e-5` shows heavy extreme outliers and much lower Pd than raw. | `p1_ssdd_tail_moments.csv` |
| 8b | Try temperature scaling. | Experiment completed; negative result | Gate temperature scaling over 6 temperatures leaves Pd/Pfa unchanged under rank-calibrated thresholds. Report as a calibration audit rather than improvement. | `p1_ssdd_temperature_scaling.csv` |
| 9 | Missing fixed-weight fusion baseline. | Completed in manuscript | Swept `w_residual=0,0.05,...,1`. Best fixed fusion at `PFA=1e-5` selects `w=1.0` and Pd `0.101461`; adaptive gate Pd `0.184532`. | `p1_fixed_weight_fusion_summary.csv`, `p1_fixed_vs_adaptive_gate_summary.csv`; manuscript Table `tab:low-pfa-robustness` |
| 10 | Missing `PFA=1e-5` bootstrap CI. | Completed in manuscript | Frame bootstrap: adaptive Pd `0.184532`, CI `[0.173539,0.196361]`; adaptive minus fixed fusion delta `0.083071`, CI `[0.075228,0.090999]`. Block bootstrap also reported but has only two asset blocks, so it is caveated. | `p1_bootstrap_ci_pfa1e5.csv`, `p1_block_bootstrap_ci_pfa1e5.csv`; Discussion |
| 11 | CNN baseline may be a strawman. | Completed in manuscript | Architecture and parameter count added: 2-channel tiny CNN, 737 parameters, 150 steps, Adam lr 0.01, public-sample training. It is described as a lightweight sanity baseline only. | `p2_cnn_architecture_protocol.csv`; manuscript Official AISTAP section |
| 12 | Code reproducibility insufficient. | Initial reproducibility pack completed | One-command script and README added for modification-2 experiments. | `scripts/revision_mod2_experiments.py`, `scripts/revision_mod2_p2_outputs.py`, `README_revision_experiments.md` |
| 13 | Heatmap only shows success. | Completed in manuscript | Added official AISTAP failure case: `simMed_test.mat#124`, raw Pd `0.120`, adaptive Pd `0.000` at `PFA=1e-5`. | `p2_failure_case_heatmap_aistap_official_pfa1e5.png`, `p2_failure_case_heatmap_meta.json`; manuscript Fig. `fig:failure-heatmap` |
| 14 | Runtime lacks hardware context. | Completed in manuscript | Hardware/runtime context recorded: Windows 11, Python 3.12.5, PyTorch 2.5.1+cu121, CUDA available, NVIDIA GeForce RTX 4060 Laptop GPU. | `p2_runtime_hardware_context.csv`; Discussion |
| 15 | Bootstrap independence assumption not discussed. | Completed with caveat | Frame bootstrap and asset-block bootstrap both generated. Since there are only two AISTAP assets, block bootstrap is conservative but statistically underpowered; manuscript should state this limitation. | `p1_bootstrap_ci_pfa1e5.csv`, `p1_block_bootstrap_ci_pfa1e5.csv` |
| 16 | Physical mechanism of residual absorption not discussed. | Completed in manuscript | Existing gate absorption diagnostic plus new failure heatmap support the mechanism: low-rank residualization can absorb target energy when target-like returns align with the clutter subspace; the adaptive branch helps but can fail at extreme low-PFA thresholds. | Prior `p0_aistap_gate_absorption_bin_summary.csv`; new failure heatmap; Discussion |

## Files Generated

- `p0_protocol_audit_train_test_split.csv`
- `p0_aistap_sim_parameter_table.csv`
- `p0_ipix_normalization_repair_detail.csv`
- `p0_ipix_normalization_repair_summary.csv`
- `p1_fixed_weight_fusion_official_detail.csv`
- `p1_fixed_weight_fusion_summary.csv`
- `p1_fixed_vs_adaptive_gate_summary.csv`
- `p1_bootstrap_ci_pfa1e5.csv`
- `p1_block_bootstrap_ci_pfa1e5.csv`
- `p1_cfar_low_pfa_parameter_sweep.csv`
- `p1_ssdd_tail_moments.csv`
- `p1_ssdd_temperature_scaling.csv`
- `p2_runtime_hardware_context.csv`
- `p2_cnn_architecture_protocol.csv`
- `p2_failure_case_heatmap_aistap_official_pfa1e5.png`
- `p2_failure_case_heatmap_meta.json`
- `revision_mod2_experiment_summary.json`
- `README_revision_experiments.md`

## Manuscript Integration Status

Completed in `投稿专用/02_latex_source/manuscripts/TGRS终稿.tex` and compiled successfully with:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error "TGRS终稿.tex"
```

The compiled PDF is 12 pages. The log contains underfull warnings only; no fatal errors and no overfull boxes remain after shortening the CNN architecture description.

Remaining boundary: none for the 16 modification-2 items at the current evidence level. Additional waveform details beyond the official README should still be checked against the paper or author-provided documentation before adding more specific claims.
