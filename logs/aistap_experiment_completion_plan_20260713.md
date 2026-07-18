# AISTAP Experiment Strengthening Plan

Date: 2026-07-13

## Purpose

This plan focuses only on the TP-SSCS project AISTAP / TP-SSCS paper. The goal is to turn the current public-sample evidence into a stronger submission-grade experiment package without widening the claim beyond the evidence.

The current paper already has a readable manuscript draft, a figure/table pack, a claim crosswalk, and public-sample low-rank / CFAR evidence. The weak point is now submission integration: the public-sample experiments are measured, but the manuscript still needs to absorb them cleanly and keep the boundary tight.

Update: the dense CFAR operating surface, target-preservation diagnostics, minimal trainability check, and stress grid are now measured on the public sample; the remaining work is final manuscript integration.

## Current Experimental State

Supported now:

- Public AISTAP-SIM sample is readable locally.
- Tensor path and TP-SSCS smoke path are executable.
- Low-rank baseline exposes the clutter-attenuation versus target-loss trade-off.
- CFAR audit shows that residual maps can improve `Pd` over raw maps at fixed low `Pfa`.
- Dense low-rank / CFAR operating surface is measured.
- Target-preservation diagnostics are measured as oracle upper bounds.
- Minimal TP-SSCS trainability check is measured.
- Stress grid is measured.
- Figure/table map and manuscript draft are aligned to the current evidence.

Not closed yet:

- No trained TP-SSCS detector result.
- No deployable target-preservation branch.
- No deployable cross-dataset claim.
- No final benchmark victory claim.

## Phase A. Reproducibility Freeze

Purpose:

Re-run the existing public-sample scripts and freeze a clean numerical baseline before adding new experiments.

Commands:

- `py -3 scripts/build_aistap_sample_inventory.py`
- `py -3 scripts/analyze_aistap_sample_lowrank.py`
- `py -3 scripts/evaluate_aistap_lowrank_baseline.py`
- `py -3 scripts/evaluate_aistap_sample_cfar.py`
- `py -3 scripts/tpsscs_smoke_test.py`

Required outputs:

- `logs/aistap_sample_inventory_report.txt`
- `logs/aistap_sample_lowrank_report.txt`
- `logs/aistap_lowrank_k1_3_5_10_20_baseline_report.txt`
- `logs/aistap_sample_cfar_ks1_3_5_10_20_pfas1e-2_1e-3_1e-4.txt`
- `logs/tpsscs_smoke_report.json`
- `logs/tpsscs_smoke_report.txt`

Pass criteria:

- All scripts complete without shape, NaN, or missing-file errors.
- Existing headline values remain consistent with the manuscript.
- Any changed value is propagated to the manuscript draft, figure/table pack, and evidence cards.

## Phase B. Dense Low-Rank / CFAR Operating Surface

Purpose:

Replace the sparse rank/Pfa audit with a denser operating-policy result. This is the most direct way to strengthen the paper without claiming a finished detector.

Experiment:

- Rank grid: `k = 1, 2, 3, 5, 8, 10, 15, 20, 30`
- False-alarm grid: `Pfa = 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2`
- Subsets: `simMed`, `simWind`, `simNoiseOnly` if available in the current public sample bundle.

Metrics:

- clutter attenuation in dB
- weak-target loss in dB
- target retention ratio
- residual target-to-clutter ratio
- `Pd` at fixed requested `Pfa`
- empirical `Pfa`
- best `k` per `Pfa`
- operating-frontier table: highest `Pd` subject to target-loss ceiling

New script:

- `scripts/evaluate_aistap_operating_surface.py`

Required outputs:

- `logs/aistap_operating_surface_20260713.csv`
- `logs/aistap_operating_surface_20260713.json`
- `logs/aistap_operating_surface_note_20260713.md`
- `figures/main/figure3_operating_surface.svg`

Pass criteria:

- The result identifies whether any `k` is robust across `Pfa`.
- The result states the target-loss cost of each best-`Pd` operating point.
- The manuscript can say why `k` is an operating parameter, not a universal optimum.

Do not claim:

- A final TP-SSCS detector result.
- Universal best rank.
- Cross-dataset superiority.

Status:

- Measured on the public sample and archived as `logs/aistap_operating_surface_20260713.csv`, `logs/aistap_operating_surface_20260713.json`, `logs/aistap_operating_surface_note_20260713.md`, and `figures/main/figure3_operating_surface.svg`.
- The dense operating-surface result now exists as a reusable evidence artifact.

## Phase C. Target-Preservation Ablation

Purpose:

Turn the paper's central design argument into a measured ablation: low-rank suppression alone is not enough, and an explicit target-preservation mechanism changes the trade-off.

Experiment levels:

- raw RD map
- low-rank residual baseline
- oracle target-preserving residual using the target-only tensor as an upper-bound diagnostic
- soft target-gated residual with threshold / percentile sweep
- residual blend: `score = alpha * residual + (1 - alpha) * target_gate`, with `alpha` grid

Important boundary:

The oracle / target-only gate is an upper-bound diagnostic, not a deployable method. It is allowed only to prove the target-preservation mechanism is the right direction.

Metrics:

- `Pd` at fixed `Pfa`
- target loss
- clutter attenuation
- target retention
- empirical `Pfa`
- improvement over low-rank residual at matched target-loss ceiling

New script:

- `scripts/evaluate_aistap_target_preservation_ablation.py`

Required outputs:

- `logs/aistap_target_preservation_ablation_20260713.csv`
- `logs/aistap_target_preservation_ablation_20260713.json`
- `logs/aistap_target_preservation_ablation_note_20260713.md`
- `figures/main/figure2_target_preservation_frontier.svg`

Pass criteria:

- At least one target-preserving diagnostic setting reduces target loss at comparable `Pd`, or improves `Pd` under a target-loss ceiling.
- The note explicitly separates oracle upper-bound behavior from deployable TP-SSCS claims.

Do not claim:

- The oracle result is a real detector.
- The trainable gate is a finished branch.

Status:

- Measured on the public sample and archived as `logs/aistap_target_preservation_ablation_20260713.csv`, `logs/aistap_target_preservation_ablation_20260713.json`, `logs/aistap_target_preservation_ablation_note_20260713.md`, and `figures/main/figure2_target_preservation_frontier.svg`.
- The target-preservation frontier now exists as a reusable evidence artifact.

## Phase D. Minimal TP-SSCS Trainability Check

Purpose:

Move TP-SSCS from "executable scaffold" to "trainable scaffold" without pretending it is a finished detector.

Experiment:

- Add a minimal training loop on the public sample.
- Use a small split over CPI/sample index if enough slices are available.
- Loss components:
  - reconstruction / residual consistency
  - target-preservation proxy loss
  - sparsity regularization on score/gate
  - optional CFAR-aware calibration penalty if stable
- Run short experiments first: `10`, `50`, and `100` steps.

New script:

- `scripts/train_tpsscs_minimal.py`

Required outputs:

- `logs/tpsscs_minimal_train_20260713.json`
- `logs/tpsscs_minimal_train_20260713.md`
- `logs/tpsscs_minimal_train_curves_20260713.csv`

Pass criteria:

- Loss remains finite.
- Output tensors remain finite.
- Score map does not collapse to all-zero or all-one.
- If the trained scaffold improves over low-rank residual at a fixed `Pfa`, it can enter Results as a preliminary trained-scaffold result.
- If it does not improve, it enters Discussion as a bounded trainability check.

Do not claim:

- Finished detector.
- Generalization beyond the public sample.
- Full TP-SSCS superiority unless the measured result beats the defined baseline.

Status:

- Measured on the public sample as a trainability check.
- Not yet deployable as a finished branch.

## Phase E. Robustness / Stress Test

Purpose:

Show that the current operating-policy conclusion is not a single accidental setting.

Perturbations:

- additive complex noise
- amplitude scaling
- phase perturbation
- target-amplitude attenuation
- optional clutter-amplitude scaling

Metrics:

- stability of best `k`
- stability of `Pd` at fixed `Pfa`
- target-loss sensitivity
- whether target-preserving diagnostic still helps under stress

New script:

- `scripts/evaluate_aistap_stress_grid.py`

Required outputs:

- `logs/aistap_stress_grid_20260713.csv`
- `logs/aistap_stress_grid_20260713.md`
- `figures/main/figure4_stress_boundary.svg`

Pass criteria:

- The stress test either confirms the same trade-off or identifies where the current method is fragile.
- Any fragility is written as a limitation, not hidden.

## Phase F. Submission Integration

Purpose:

Convert the new experimental outputs into manuscript-ready artifacts.

Update targets:

- `logs/aistap_manuscript_final_draft_20260713.md`
- `logs/aistap_manuscript_submission_package_20260713.md`
- `logs/aistap_figure_table_final_pack_20260713.md`
- `logs/aistap_section_evidence_map_20260713.md`
- `logs/aistap_method_ablation_crosswalk_20260713.md`
- `claim_matrix.md`
- `README.md`
- `STATUS.md`

Required new manuscript notes:

- `logs/aistap_operating_surface_note_20260713.md`
- `logs/aistap_target_preservation_ablation_note_20260713.md`
- `logs/tpsscs_minimal_train_note_20260713.md`
- `logs/aistap_stress_grid_note_20260713.md`

Pass criteria:

- Every new number in the manuscript maps to a script output.
- Every figure maps to one result table.
- Every claim maps to either evidence, limitation, or planned-work status.
- The manuscript keeps the public-sample boundary unless broader data are actually measured.

## Priority Order

1. Phase F: manuscript integration.

The reason for this order is experimental leverage: Phase B, C, D, and E are already measured on the public sample; the remaining step is to integrate them cleanly into the manuscript and submission package.

Update: Phase B, Phase C, Phase D, and Phase E are now measured on the public sample. Remaining work is final submission integration.

## One-Page Claim After Completion

If the plan succeeds, the paper can safely claim:

The public AISTAP-SIM sample shows that low-rank clutter suppression creates a measurable clutter-attenuation / weak-target-loss trade-off. A dense CFAR operating surface shows that the best suppression rank depends on the false-alarm target, target-preservation diagnostics improve the operating frontier under bounded assumptions, the scaffold is trainable on the public sample, and the stress grid shows that the operating conclusion shifts but does not collapse under perturbation. TP-SSCS is therefore motivated as a target-preserving, low-false-alarm detection framework, with the current evidence limited to public-sample development and scaffold-level validation unless a trained TP-SSCS result beats the defined baselines.

