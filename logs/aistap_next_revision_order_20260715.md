# AISTAP Next Revision Order

Date: 2026-07-15

## Purpose

Turn the completed evidence stack into a submission-ready manuscript without reopening high-risk experiments.

## Current Evidence State

- Official AISTAP-SIM full-asset gate: complete and passed.
- Combined full-asset bootstrap CI: complete and passed.
- IPIX held-out residual-aware fusion: complete and passed, with zero-shot transfer retained as a negative boundary.
- SSDD supervised SAR adaptation: complete and passed.
- SSDD image-level / annotation-level bootstrap CI: complete and passed.
- Automatic top-readiness self-check: `top_ready`, `0` hard failures.

## Revision Sequence

### 1. Lock the Results Structure

Use this order:

1. Low-rank suppression exposes target loss.
2. CFAR operating surfaces show rank/Pfa dependence.
3. Trainable target-preservation branch reduces target loss.
4. Official AISTAP-SIM full-asset detector protocol passes.
5. IPIX held-out fusion validates bounded external radar behavior.
6. SSDD supervised SAR adaptation validates a second external radar family.
7. Cross-paper readiness comparison states why AISTAP now leads on radar-specific experimental strength.

Do not lead with comparison to other local papers. Lead with the scientific/technical result.

### 2. Replace the Abstract

Use the 2026-07-15 abstract in `logs/aistap_manuscript_final_draft_20260715.md`.

Required content:

- Problem: clutter suppression can erase weak targets.
- Method framing: target-preserving low-false-alarm detection.
- In-domain evidence: 210 target-bearing frames across two official AISTAP-SIM full-test assets.
- External evidence: IPIX held-out fusion and SSDD SAR supervised adaptation.
- Boundary: not production deployment, not zero-shot cross-dataset superiority.

### 3. Update Methods for Reproducibility

Methods must include:

- Official full-asset protocol.
- Combined bootstrap CI over target-bearing frames.
- IPIX validation-selected fusion protocol and recording-level unit.
- SSDD supervised train/test protocol and raw fallback at `Pfa <= 1e-4`.
- SSDD image-level / annotation-level CI using fixed global thresholds.

### 4. Build Figures After Text Lock

Use `logs/aistap_figure_table_final_pack_20260715.md`.

Priority:

1. Figure 4: official full-asset detector protocol and CIs.
2. Figure 5: IPIX + SSDD external validation.
3. Extended Data Figure 1: SSDD image/annotation-level robustness.
4. Refresh captions for Figures 1-3 so they lead into the stronger 20260715 evidence.

### 5. Keep Boundary Language Visible

Every external result needs a boundary phrase:

- IPIX: validation-selected residual-aware fusion; direct zero-shot is negative.
- SSDD: supervised external adaptation; not zero-shot saved-state transfer.
- Top-readiness: internal readiness gate; not a journal acceptance guarantee.

### 6. Final QA Before Submission

Check:

- Abstract and Results use the same numbers.
- Methods and Results name the same protocols.
- Figure captions do not imply zero-shot transfer.
- Claim matrix agrees with the manuscript.
- README/STATUS point to the 2026-07-15 manuscript files.

## Do Not Reopen

- No broad new data-source hunt.
- No rushed classical-baseline expansion without identical Pfa calibration.
- No final-state seed/rank/hidden sweep unless the user explicitly accepts the risk of exposing weak seeds.

