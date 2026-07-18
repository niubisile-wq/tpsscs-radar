# AISTAP Supplementary Experiment Strengthening Audit

Date: 20260715

## Verdict

- The current evidence remains `top_ready`; no hard experiment blocker is visible.
- Further work should not be another broad data hunt. The highest-value additions are uncertainty reporting and robustness localization.
- The single best next experiment was SSDD image-level / annotation-level robustness with bootstrap confidence intervals; it is now completed in `logs/ssdd_image_level_bootstrap_ci_20260715.md`.
- The best low-cost supplement is a formal bootstrap CI table for AISTAP full assets and IPIX held-out recordings; this audit generates that table for the available per-unit artifacts.
- The final-state full-asset seed-sensitivity check is now completed in `logs/aistap_full_asset_seed_sensitivity_20260717.md`; seeds `7`, `11`, and `23` all preserve the official full-asset win pattern.
- The stronger classical-baseline audit is now completed in `logs/aistap_full_asset_classical_cfar_baselines_20260717.md`; TP-SSCS beats the best of raw/residual global top-k plus CA/GOCA/SOCA/OS-CFAR local baselines on the official full assets.
- The parameter-swept classical-baseline audit is now completed in `logs/aistap_full_asset_classical_cfar_param_sweep_20260717.md`; TP-SSCS still beats the best of 75 global/local CFAR methods/configurations on the official full assets.
- The leave-one-condition-out learned-baseline audit is now completed in `logs/aistap_full_asset_loso_learned_raw_baseline_20260717.md`; TP-SSCS beats a supervised raw-feature logistic detector trained on the opposite official full asset with positive bootstrap CI lower bounds.
- The stronger feature-ensemble learned-boundary audit is now completed in `logs/aistap_full_asset_loso_feature_ensemble_baseline_20260717.md` and `logs/aistap_full_asset_loso_tpsscs_feature_ensemble_20260717.md`; compact TP-SSCS loses to raw/residual HGB, while TP-SSCS-feature HGB beats compact TP-SSCS and nearly matches raw/residual HGB.

## Priority Experiments

| Rank | Experiment | Status | Impact | Cost | Risk | Why it matters |
|---:|---|---|---|---|---|---|
| 1 | SSDD image-level / annotation-level robustness and bootstrap CI | `completed_20260715` | `high` | `medium` | `low` | SSDD is the newest external positive source; per-image and per-annotation deltas now answer whether gains are broad or driven by a small subset. |
| 2 | AISTAP + IPIX paired bootstrap / confidence interval reporting | `partially_completed_by_this_audit` | `high` | `low` | `low` | The main wins are already present; confidence intervals convert win-count evidence into reviewer-facing uncertainty evidence. |
| 3 | Formal combined full-asset protocol gate over simMed + simWind | `completed_20260715` | `medium` | `low` | `low` | The cross-condition summary already passed on both assets; the new combined gate now makes the in-domain claim easier to defend. |
| 4 | Final-state sensitivity across seed / rank / hidden width on full assets | `completed_seed_check_20260717` | `medium_high` | `medium` | `low_after_pass` | The full-asset seed check now shows seeds `7`, `11`, and `23` preserve the official win pattern; rank/hidden-width sweeps remain optional and higher-risk. |
| 5 | Additional classical detector baselines beyond raw CFAR and low-rank residual | `completed_20260717_plus_param_sweep` | `medium_high` | `high` | `low_after_pass` | The CA/GOCA/SOCA/OS-CFAR audit and parameter sweep now pass cleanly under the same empirical-Pfa calibration; TP-SSCS wins 7/7 combined and 14/14 asset-level comparisons vs the best of 75 swept classical candidates. |
| 6 | Leave-one-condition-out supervised learned raw-feature baseline | `completed_20260717` | `medium_high` | `medium` | `low_after_pass` | This closes the narrow learned-comparator criticism inside official AISTAP-SIM: TP-SSCS wins 7/7 combined and 14/14 asset-level comparisons, with minimum combined delta `0.0596` and positive bootstrap CI lower bounds. |
| 7 | Strong supervised raw/residual and TP-SSCS-feature HGB boundary | `completed_20260717_boundary` | `high` | `medium_high` | `informative_negative` | Raw/residual HGB beats compact TP-SSCS, but TP-SSCS-feature HGB beats compact TP-SSCS and nearly matches raw/residual HGB; this defines the current supervised upper bound and prevents overclaiming. |

## Bootstrap CI Snapshot

### AISTAP Full Assets

| Pfa | Comparator | n | Mean Delta Pd | 95% CI | Positive-unit fraction |
|---:|---|---:|---:|---:|---:|
| 1e-05 | `raw` | 210 | 0.1046 | [0.0942, 0.1152] | 0.895 |
| 1e-05 | `low_rank_residual_k30` | 210 | 0.0831 | [0.0751, 0.0909] | 0.929 |
| 3e-05 | `raw` | 210 | 0.1148 | [0.1019, 0.1278] | 0.890 |
| 3e-05 | `low_rank_residual_k30` | 210 | 0.0788 | [0.0711, 0.0871] | 0.910 |
| 1e-04 | `raw` | 210 | 0.1633 | [0.1471, 0.1783] | 0.895 |
| 1e-04 | `low_rank_residual_k30` | 210 | 0.0656 | [0.0586, 0.0732] | 0.867 |
| 3e-04 | `raw` | 210 | 0.2452 | [0.2260, 0.2659] | 0.952 |
| 3e-04 | `low_rank_residual_k30` | 210 | 0.0539 | [0.0471, 0.0619] | 0.733 |
| 1e-03 | `raw` | 210 | 0.3258 | [0.3034, 0.3486] | 0.976 |
| 1e-03 | `low_rank_residual_k30` | 210 | 0.0436 | [0.0371, 0.0505] | 0.605 |
| 3e-03 | `raw` | 210 | 0.3266 | [0.3035, 0.3494] | 0.943 |
| 3e-03 | `low_rank_residual_k30` | 210 | 0.0353 | [0.0292, 0.0417] | 0.519 |
| 1e-02 | `raw` | 210 | 0.2127 | [0.1917, 0.2349] | 0.895 |
| 1e-02 | `low_rank_residual_k30` | 210 | 0.0290 | [0.0228, 0.0353] | 0.457 |

### IPIX Held-out Recordings

| Pfa | Comparator | n recordings | Mean Delta Pd | 95% CI | Positive-recording fraction |
|---:|---|---:|---:|---:|---:|
| 1e-05 | `raw` | 12 | 0.0131 | [0.0024, 0.0250] | 0.500 |
| 1e-05 | `low_rank_residual_k30` | 12 | 0.0641 | [0.0179, 0.1242] | 1.000 |
| 3e-05 | `raw` | 12 | 0.0131 | [0.0017, 0.0252] | 0.500 |
| 3e-05 | `low_rank_residual_k30` | 12 | 0.0641 | [0.0180, 0.1241] | 1.000 |
| 1e-04 | `raw` | 12 | 0.0163 | [0.0036, 0.0296] | 0.583 |
| 1e-04 | `low_rank_residual_k30` | 12 | 0.0691 | [0.0232, 0.1294] | 1.000 |
| 3e-04 | `raw` | 12 | 0.0188 | [0.0053, 0.0332] | 0.667 |
| 3e-04 | `low_rank_residual_k30` | 12 | 0.0763 | [0.0269, 0.1359] | 1.000 |
| 1e-03 | `raw` | 12 | 0.0240 | [0.0072, 0.0404] | 0.750 |
| 1e-03 | `low_rank_residual_k30` | 12 | 0.0881 | [0.0344, 0.1576] | 1.000 |
| 3e-03 | `raw` | 12 | 0.0307 | [0.0120, 0.0526] | 0.750 |
| 3e-03 | `low_rank_residual_k30` | 12 | 0.1028 | [0.0458, 0.1703] | 1.000 |
| 1e-02 | `raw` | 12 | 0.0402 | [0.0151, 0.0700] | 0.833 |
| 1e-02 | `low_rank_residual_k30` | 12 | 0.1278 | [0.0657, 0.2043] | 1.000 |

## SSDD Gap Closure

- Current SSDD aggregate evidence: `231` test images, `545` annotations.
- Aggregate test result: `4` wins, `3` ties, `0` losses vs raw; mean Pd delta vs raw `0.09085510654600235`.
- Completed supplement: `logs/ssdd_image_level_bootstrap_ci_20260715.md` now reports image-level and annotation-level bootstrap CIs.
- Image-level raw comparisons at non-fallback Pfa points have positive 95% CIs.
- Image-level low-rank comparisons have positive 95% CIs at all Pfa points.

## Recommended Stopping Rule

- Treat SSDD image-level CI as completed.
- Treat the combined full-asset gate as completed.
- Treat the full-asset seed-sensitivity check as completed for seeds `7`, `11`, and `23`.
- Treat the stronger classical-baseline audit as completed for raw/residual global top-k plus CA/GOCA/SOCA/OS-CFAR local score maps.
- Treat the local-CFAR parameter-sensitivity audit as completed for training cells `4,6,8`, guard cells `1,2`, and OS percentiles `60,75,90`.
- Treat the LOSO supervised learned raw-feature baseline as completed for the official AISTAP-SIM full assets.
- Treat the strong HGB feature-ensemble boundary as completed and keep it visible as a claim-control result.
- Do not open a new data-source hunt unless a clean, scriptable radar dataset is already available.
- Do not add high-risk classical baselines unless they can be implemented with the same Pfa calibration and documented fairly.
