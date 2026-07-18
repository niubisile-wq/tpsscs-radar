# AISTAP Next Revision Order

Date: 2026-07-13

## Purpose

Turn the current section-evidence map into a concrete revision sequence for the manuscript draft. The goal is to expand the paper in the right order without widening claims beyond the public sample and scaffold stage.

## Revision sequence

### 1. Tighten the Results section first

#### Priority order

1. Public sample readout
2. Low-rank suppression trade-off
3. Low-false-alarm detection behavior
4. Scaffold check

#### What to add

- Make the public-sample paragraph explicitly state the tensor boundary, the smoke-path result, and the minimum correctness status.
- Keep the low-rank paragraph focused on the rank sweep and the trade-off between clutter attenuation and target loss.
- Keep the CFAR paragraph focused on fixed `Pfa` operating behavior and the rank dependence of `Pd`.
- Leave the scaffold paragraph as a bridge to future loss design, not as a claim of a finished detector.

#### Evidence to use

- `logs/tpsscs_smoke_report.txt`
- `logs/tpsscs_smoke_report.json`
- `logs/aistap_sample_lowrank_report.txt`
- `logs/aistap_lowrank_k1_3_5_10_20_baseline_report.txt`
- `logs/aistap_sample_cfar_ks1_3_5_10_20_pfas1e-2_1e-3_1e-4.txt`
- `cards/08_model_scaffold.md`

#### Do not add yet

- Any cross-dataset comparison
- Any full-model training claim
- Any universal statement about the best `k`

### 2. Rewrite the Methods section to match the evidence boundary

#### Priority order

1. Data and sample boundary
2. Low-rank baseline
3. CFAR audit
4. TP-SSCS scaffold

#### What to add

- State that the draft uses the public AISTAP-SIM sample only.
- State that the low-rank baseline is a diagnostic baseline, not the proposed detector.
- State that the CFAR audit is an operating-policy test under fixed false-alarm targets.
- State that the TP-SSCS scaffold is executable but not yet trained.

#### Evidence to use

- `logs/aistap_manuscript_draft_20260713.md`
- `logs/aistap_section_evidence_map_20260713.md`
- `cards/06_aistap_evidence.md`
- `cards/07_cfar_evidence.md`
- `cards/08_model_scaffold.md`

#### Do not add yet

- A full training recipe
- Any unverified ablation result for the target-preservation loss

### 3. Compress the Discussion into one controlled trade-off story

#### Priority order

1. Why clutter cancellation is not the right framing
2. Why target gating is required
3. Why CFAR calibration belongs in the main method
4. Why `k` is a controllable trade-off parameter

#### What to add

- Make the discussion read as a detector-design argument, not a performance recap.
- Explicitly connect strong suppression to weak-target loss.
- State the boundary that the public sample supports the framing, but not final benchmark superiority.

#### Evidence to use

- `logs/aistap_manuscript_draft_20260713.md`
- `logs/aistap_section_evidence_map_20260713.md`
- `cards/04_claims.md`
- `cards/07_cfar_evidence.md`

#### Do not add yet

- Language implying the detector is already finished
- Language implying the broader benchmark is already closed

### 4. Align the abstract with the same evidence contract

#### Priority order

1. Problem statement
2. Sample-level trade-off
3. CFAR operating behavior
4. Planned TP-SSCS ingredients

#### What to add

- Keep the abstract short and direct.
- Mention the public-sample boundary explicitly.
- Make the planned method sound like the next step, not a completed result.

#### Evidence to use

- `logs/aistap_section_evidence_map_20260713.md`
- `logs/aistap_figure_caption_draft_20260713.md`

#### Do not add yet

- Cross-dataset superiority claims
- Finished training claims

### 5. Lock figures and captions after the text is stable

#### Priority order

1. Figure 1 and Figure 2 captions
2. Figure 3 caption
3. Figure 4 caption
4. Table captions

#### What to add

- Keep every caption bounded to the public sample.
- Make the rank trade-off and CFAR operating point visible in the captions, not just the main text.
- Keep the boundary table explicit so no claim drifts into unsupported territory.

#### Evidence to use

- `logs/aistap_figure_table_outline_20260713.md`
- `logs/aistap_figure_caption_draft_20260713.md`
- `logs/aistap_section_evidence_map_20260713.md`

#### Do not add yet

- Any figure that implies a finished system
- Any table that compares against unsupported baselines

## Practical writing rule

- If a sentence can be tied to a specific evidence file, it can enter the main text.
- If a sentence is only supported by the public sample, it must carry a boundary phrase.
- If a sentence depends on future training, keep it in the planned-work layer, not the current result layer.
