# AISTAP Figure/Table Outline

Date: 2026-07-13

## Goal

Map the current public-sample evidence to a manuscript structure that supports a full submission without inventing new claims.

## Main Figures

### Figure 1. Problem framing and pipeline

- Show the public AISTAP-SIM sample, the target-only reference, and the TP-SSCS pipeline.
- Message: the paper is about detection under low false alarm, not pure clutter removal.
- Inputs from current evidence:
  - public sample loader
  - complex-valued TP-SSCS scaffold
  - smoke test tensor shapes

### Figure 2. Low-rank trade-off on the public sample

- Show clutter attenuation and target loss versus rank `k`.
- Use `simMed`, `simWind`, and `simNoiseOnly`.
- Message: stronger low-rank suppression is not monotone improvement.
- Evidence source:
  - `aistap_lowrank_k1_3_5_10_20_baseline.csv`
  - `aistap_sample_lowrank_report.txt`

### Figure 3. Low-Pfa CFAR audit

- Show `Pd` versus `k` at `Pfa=1e-2`, `1e-3`, and `1e-4`.
- Include raw versus low-rank residual comparison.
- Message: the best operating point depends on false-alarm target and suppression rank.
- Evidence source:
  - `aistap_sample_cfar_ks1_3_5_10_20_pfas1e-2_1e-3_1e-4.csv`
  - `aistap_sample_cfar_ks1_3_5_10_20_pfas1e-2_1e-3_1e-4.txt`

### Figure 4. Prototype smoke path

- Show the minimum end-to-end path from sample loader to suppressed / residual / score outputs.
- Message: the implementation is numerically finite and remains a scaffold rather than a trained detector.
- Evidence source:
  - `tpsscs_smoke_report.json`
  - `tpsscs_smoke_report.txt`

## Main Tables

### Table 1. Low-rank baseline summary

- Columns: dataset, `k`, clutter attenuation, target loss, target retention ratio.
- Purpose: make the rank trade-off readable without relying only on a plot.

### Table 2. CFAR operating summary

- Columns: `Pfa`, `k`, raw `Pd`, low-rank residual `Pd`, empirical `Pfa`.
- Purpose: show the operating-policy behavior directly.

### Table 3. Manuscript boundary table

- Columns: claim, supported by current sample, not yet supported, boundary statement.
- Purpose: prevent overclaiming in the main text.

## Supplementary Material

### Supplementary Note S1. Sample boundary and loader

- Describe the public sample, tensor shapes, and the scaffold smoke path.

### Supplementary Note S2. Low-rank rank sweep details

- Expand the rank-sweep results for all subsets.

### Supplementary Note S3. CFAR details

- Include the exact thresholding protocol and the full row-level results.

### Supplementary Note S4. Failure-case language

- State explicitly that stronger low-rank suppression can over-suppress weak targets.

## Writing rule

- Do not promote the sample outline into a cross-dataset victory claim.
- Do not turn the scaffold into a finished method claim.
- Keep the main message centered on target preservation and low-false-alarm detection.
