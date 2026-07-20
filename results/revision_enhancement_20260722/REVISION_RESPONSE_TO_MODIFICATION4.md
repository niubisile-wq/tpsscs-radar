# Modification-4 Follow-up Execution Report

Date: 2026-07-21

This report records the follow-up actions taken after the fourth external critique.

## Actions Completed

1. **IPIX wording tightened.**
   The manuscript no longer implies that IPIX transfer is generally unrepairable. It now states that simple feature-level monotone calibration is insufficient under rank-calibrated thresholds, while higher-order domain adaptation such as covariance alignment, subspace adaptation, or adversarial matching is a separate problem beyond the scope of this detector-policy paper.

2. **Temperature scaling removed from the main manuscript.**
   The critique was correct: temperature scaling is a monotone transform and cannot change rank ordering after per-score PFA recalibration. It is retained only as an internal negative audit in `p1_ssdd_temperature_scaling.csv`, not as a main-text result.

3. **Failure heatmap removed from the main manuscript.**
   The failure-oriented heatmap remains generated and archived:
   `p2_failure_case_heatmap_aistap_official_pfa1e5.png`.
   It is no longer a main-text figure, because the case is visually severe and could distract from the aggregate official result unless moved to supplementary material with fuller explanation.

4. **SSDD tail result reframed.**
   The manuscript keeps the tail-statistics evidence but does not claim the present method fixes the extreme SSDD tail. It now identifies tail-stabilized learned scoring, extreme-value tail modeling, and validation-stabilized thresholds as natural future extensions.

5. **CNN baseline boundary strengthened.**
   The manuscript now states explicitly that the tiny CNN baseline tests whether a very simple learned pixel scorer can replace the gate. It does not claim superiority over all larger or task-specific CNN/SAR detectors.

6. **Residual absorption mechanism empirically tested.**
   A new AISTAP public-sample mechanism audit was run:
   `scripts/revision_mod4_subspace_absorption.py`.
   It measures how much of each target cell's multichannel energy is represented by the rank-30 low-rank approximation and correlates that projection fraction with target absorption.

## New Mechanism Result

Output files:

- `p0_subspace_projection_absorption_detail.csv`
- `p0_subspace_projection_absorption_summary.csv`
- `p0_subspace_projection_absorption.json`

Key result:

- `n = 129` target cells.
- Pearson correlation between subspace projection fraction and relative residual absorption: `0.891`.
- Spearman correlation: `0.950`.
- Mean relative absorption by projection quartile:
  - Q1 low projection: `0.216`
  - Q2: `0.496`
  - Q3: `0.745`
  - Q4 high projection: `0.966`

Interpretation:

Targets that are more representable by the estimated rank-30 clutter subspace are much more likely to be absorbed by residualization. This converts the physical explanation from a qualitative claim into an empirical mechanism check.

## Manuscript Integration

Updated file:

- `投稿专用/02_latex_source/manuscripts/TGRS终稿.tex`

Main manuscript changes:

- IPIX result now states “simple monotone calibration is insufficient,” not “IPIX cannot be repaired.”
- SSDD temperature scaling no longer appears in the main text.
- Failure heatmap no longer appears as a main-text figure.
- SSDD tail section now points to tail-stabilized learned scoring as future work.
- CNN baseline caveat strengthened.
- Discussion now includes the subspace-projection/absorption correlation result.

