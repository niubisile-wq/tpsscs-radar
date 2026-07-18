# AISTAP Section-Evidence Map

Date: 2026-07-13

## Purpose

Map the current manuscript draft to the evidence that already exists in the repository, so each section can be expanded without inventing claims.

## Abstract

### Supported

- The paper is about target-preserving, low-false-alarm detection rather than pure clutter removal.
- The public AISTAP-SIM sample shows a real suppression-vs-target-loss trade-off.
- CFAR-style detection on low-rank residuals can improve detection probability over the raw map at fixed low false-alarm rates.
- The TP-SSCS design combines complex-valued self-supervision, sparse target gating, and CFAR calibration.

### Evidence

- `cards/04_claims.md`
- `cards/06_aistap_evidence.md`
- `cards/07_cfar_evidence.md`
- `logs/aistap_sample_lowrank_report.txt`
- `logs/aistap_sample_cfar_ks1_3_5_10_20_pfas1e-2_1e-3_1e-4.txt`

### Not yet claimable

- Cross-dataset superiority
- Finished training results for the full TP-SSCS model
- Benchmark-wide performance beyond the public sample

## Introduction

### Supported

- Low-rank suppression is a natural baseline for the public sample.
- Stronger low-rank suppression removes more clutter but also erases weak target energy.
- The right framing is low-false-alarm detection, not image-quality style clutter cancellation.

### Evidence

- `cards/04_claims.md`
- `cards/06_aistap_evidence.md`
- `logs/aistap_sample_lowrank_report.txt`
- `logs/aistap_manuscript_draft_20260713.md`

### Not yet claimable

- Claims that the method is already validated across the broader public dataset stack
- Claims that TP-SSCS is already trained as a full detector

## Results

### Public sample readout

#### Supported

- The public AISTAP-SIM sample is readable locally as v7.3 HDF5.
- The sample contains `rd_img` and `rd_targ_only` tensors with shape `(2, 6, 64, 1024)`.
- The smoke path is numerically finite and returns the expected tensor shapes.

#### Evidence

- `cards/08_model_scaffold.md`
- `logs/tpsscs_smoke_report.txt`
- `logs/tpsscs_smoke_report.json`

#### Not yet claimable

- Full model training stability
- Cross-dataset generalization

### Low-rank suppression trade-off

#### Supported

- On `simMed`, clutter attenuation rises from `2.197 dB` at `k=1` to `11.268 dB` at `k=20`.
- Over the same sweep, target loss rises from `0.925 dB` to `13.906 dB`.
- The same qualitative pattern appears on `simWind` and `simNoiseOnly`.

#### Evidence

- `logs/aistap_sample_lowrank_report.txt`
- `logs/aistap_lowrank_k1_3_5_10_20_baseline_report.txt`
- `cards/06_aistap_evidence.md`
- `cards/04_claims.md`

#### Not yet claimable

- A universal optimal rank `k`
- A claim that stronger suppression is always better

### CFAR operating behavior

#### Supported

- At `Pfa=1e-4`, raw `Pd=0.0659`, while low-rank residual reaches `Pd=0.1667` at `k=20`.
- At `Pfa=1e-3`, raw `Pd=0.2171`, while low-rank residual reaches `Pd=0.3837`.
- At `Pfa=1e-2`, raw `Pd=0.3140`, while low-rank residual reaches `Pd=0.4690` at `k=5`.
- The best operating point depends jointly on suppression rank and false-alarm target.

#### Evidence

- `logs/aistap_sample_cfar_ks1_3_5_10_20_pfas1e-2_1e-3_1e-4.txt`
- `cards/07_cfar_evidence.md`

#### Not yet claimable

- A full detector claim for TP-SSCS
- Any statement that one `k` dominates all `Pfa` values

### Scaffold check

#### Supported

- The loader returns `(6, 64, 1024)` tensors.
- The prototype emits suppressed, residual, clutter, and score outputs.
- The forward path is finite at the scaffold rank.

#### Evidence

- `logs/tpsscs_smoke_report.txt`
- `logs/tpsscs_smoke_report.json`
- `cards/08_model_scaffold.md`

#### Not yet claimable

- Training convergence
- Loss-function performance
- End-to-end detector quality

## Discussion

### Supported

- The manuscript should not be written as a generic clutter-cancellation paper.
- Target gating prevents over-suppression.
- CFAR calibration turns the pipeline into a detector rather than a denoiser.
- `k` should be treated as a controllable trade-off parameter.

### Evidence

- `logs/aistap_manuscript_draft_20260713.md`
- `cards/04_claims.md`
- `cards/07_cfar_evidence.md`

### Not yet claimable

- Any conclusion that the full benchmark problem is solved
- Any statement that the current scaffold is already a submission-ready detector

## Methods

### Supported

- The current method section can describe the public sample boundary.
- The low-rank baseline is executable at multiple ranks.
- The CFAR audit is a fixed false-alarm operating-policy test.
- The target-preservation diagnostics are measured as oracle upper bounds and now include a trainable-gate candidate.
- The minimal trainability check shows the scaffold can be optimized without numerical collapse.
- The TP-SSCS scaffold exists and can be extended with a target-preservation loss and a trainable gate.

### Evidence

- `logs/aistap_manuscript_draft_20260713.md`
- `logs/aistap_figure_table_outline_20260713.md`
- `cards/08_model_scaffold.md`

### Not yet claimable

- A finalized training recipe
- A completed deployable ablation suite for the full method

## Boundary

### Supported

- The draft is intentionally limited to the public sample and scaffold stage.
- The manuscript should not claim cross-dataset victory.
- The current evidence supports method design, first ablations, and low-false-alarm framing.
- The five-reference gap audit shows the current paper is closer on evidence layering, but still not at finished-detector closure.

### Evidence

- `logs/aistap_manuscript_draft_20260713.md`
- `logs/aistap_figure_caption_draft_20260713.md`
- `logs/aistap_five_reference_gap_audit_20260713.md`
- `cards/04_claims.md`

### Not yet claimable

- Final benchmark superiority
- Universal solution language
- Finished training maturity
- Finished-detector parity with the strongest references

## Figures and Tables

### Figure 1

- Problem framing and pipeline.
- Evidence: `logs/tpsscs_smoke_report.txt`, `cards/08_model_scaffold.md`

### Figure 2

- Target-preservation frontier on the public sample.
- Evidence: `logs/aistap_target_preservation_ablation_20260713.csv`, `logs/aistap_target_preservation_ablation_20260713.json`, `logs/aistap_target_preservation_ablation_note_20260713.md`, `figures/main/figure2_target_preservation_frontier.svg`

### Figure 3

Dense low-Pfa CFAR operating surface.
Evidence: `logs/aistap_operating_surface_20260713.csv`, `logs/aistap_operating_surface_20260713.json`, `logs/aistap_operating_surface_note_20260713.md`, `figures/main/figure3_operating_surface.svg`

### Figure 4

- Stress boundary and trainable-gate robustness.
- Evidence: `logs/aistap_stress_grid_20260713.md`, `logs/tpsscs_minimal_train_note_20260713.md`, `logs/tpsscs_minimal_train_curves_20260713.csv`

### Table 1

- Low-rank baseline summary.
- Evidence: `logs/aistap_sample_lowrank_report.txt`, `cards/06_aistap_evidence.md`

### Table 2

- CFAR operating summary.
- Evidence: `logs/aistap_sample_cfar_ks1_3_5_10_20_pfas1e-2_1e-3_1e-4.txt`, `cards/07_cfar_evidence.md`

### Table 3

- Manuscript boundary table.
- Evidence: `logs/aistap_manuscript_draft_20260713.md`, `cards/04_claims.md`

## Revision rule

- If a sentence is not backed by one of the evidence files above, keep it out of the main text.
- If a claim is supported only by the public sample, state that boundary explicitly.
- If a result depends on the current scaffold only, treat it as a method-development statement, not a final benchmark claim.
