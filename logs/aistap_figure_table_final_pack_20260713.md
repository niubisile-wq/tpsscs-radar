# AISTAP Figure/Table Final Pack

Date: 2026-07-13

This pack turns the current figure outline and caption draft into a submission-facing delivery list.
It stays inside the public AISTAP-SIM sample and the current scaffold boundary.

## Figure 1. Problem framing and pipeline

Purpose:
- Show the public sample, the target-only reference, and the TP-SSCS pipeline.

Key claim:
- The paper is about target-preserving detection at low false-alarm rates, not clutter removal alone.

Source evidence:
- `aistap_sample_preview.png`
- `aistap_sample_inventory_report.txt`
- `tpsscs_model_scaffold_note_20260713.md`
- `tpsscs_smoke_report.txt`

## Figure 2. Target-preservation frontier

Purpose:
- Show how raw, low-rank residual, oracle diagnostics, and the trainable gate move the target-loss / Pd frontier.

Key claim:
- Target-preservation changes the frontier in the right direction, and the trainable gate is the closest deployable candidate.

Source evidence:
- `aistap_target_preservation_ablation_20260713.csv`
- `aistap_target_preservation_ablation_20260713.json`
- `aistap_target_preservation_ablation_note_20260713.md`
- `figure2_target_preservation_frontier.svg`

## Figure 3. Dense low-Pfa CFAR operating surface

Purpose:
- Show `Pd` versus `k` across a denser `Pfa` grid.

Key claim:
- The best operating point depends jointly on the false-alarm target and the suppression rank, and the optimal `k` shifts across the grid.

Source evidence:
- `aistap_operating_surface_20260713.md`
- `aistap_operating_surface_20260713.csv`
- `aistap_operating_surface_20260713.json`
- `figure3_operating_surface.svg`

## Figure 4. Stress boundary and robustness

Purpose:
- Show the robustness boundary under perturbation and the stability of the best operating point.

Key claim:
- The best low-rank rank shifts under perturbation, while the trainable gate stays finite and competitive.

Source evidence:
- `aistap_stress_grid_20260713.md`
- `aistap_stress_grid_stress_tpsscs_minimal_train_state_rank20_hidden8_steps100_lr0p01_seed7.csv`
- `tpsscs_minimal_train_note_20260713.md`
- `tpsscs_minimal_train_note_20260713.md`

## Table 1. Low-rank baseline summary

Purpose:
- Report clutter attenuation, target loss, and target retention ratio by subset and rank.

## Table 2. CFAR operating summary

Purpose:
- Report raw and residual `Pd` together with empirical `Pfa`.

## Target-preservation diagnostic note

Purpose:
- Record oracle blend and oracle gate upper bounds on the target-preservation branch.

Key claim:
- Target-preservation changes the frontier in the right direction, but remains diagnostic rather than deployable.

Source evidence:
- `aistap_target_preservation_ablation_20260713.md`
- `aistap_manuscript_final_draft_20260713.md`

## Minimal trainability note

Purpose:
- Show that the scaffold can be optimized on the public sample without numerical collapse.

Key claim:
- The scaffold is trainable, but still not a finished detector.

Source evidence:
- `tpsscs_minimal_train_note_20260713.md`
- `aistap_minimal_trainability_check_20260713.md`
- `aistap_manuscript_final_draft_20260713.md`

## Table 3. Manuscript boundary table

Purpose:
- Separate supported claims from unsupported claims so the paper does not overstate the sample.

## Submission usage

- Figure 1 should anchor the paper framing.
- Figure 2 should anchor the suppression trade-off.
- Figure 3 should anchor the dense low-Pfa operating policy.
- Figure 4 should anchor the stress / robustness boundary.
- The target-preservation diagnostic note should support the oracle upper-bound argument in the Results and Discussion sections.
- The minimal trainability note should support the trainable-scaffold argument in the Results and Discussion sections.
- Tables 1-3 should keep the claim boundary explicit.
