---
date: 2026-07-16
manuscript: manuscripts/tgrs_tpsscs_nofig_20260715.tex
task: Expand manuscript to seven main-text tables
---

# Seven-Table Insertion Log

The main manuscript was updated to contain seven tables. The added tables were selected to emphasize experimental evidence rather than generic reporting.

## Table Set

1. Table I: dataset/protocol and evidence mapping.
2. Table II: low-rank suppression-preservation audit on AISTAP-SIM public samples.
3. Table III: target-preservation branch evidence and claim boundaries.
4. Table IV: combined AISTAP-SIM official full-asset detection results.
5. Table V: paired bootstrap support for the combined AISTAP-SIM full-asset protocol.
6. Table VI: SSDD image- and annotation-level bootstrap support at non-fallback operating points.
7. Table VII: external validation and adaptation summary.

## Experimental Highlights Captured

- Suppression-preservation conflict: increasing low-rank clutter attenuation also increased target loss, motivating TP-SSCS rather than residual-only evaluation.
- Trainable gate evidence: the selected trainable gate reduced target loss from 6.191 dB to 0.197 dB while retaining residual-level public-sample detection behavior.
- Main in-domain evidence: TP-SSCS improved over both raw and rank-matched low-rank residual comparators at all seven AISTAP-SIM full-asset operating points.
- Statistical support: paired bootstrap intervals on 210 AISTAP-SIM target-bearing frames remained positive against both comparators.
- External supervised adaptation: SSDD gains were positive at non-fallback operating points under both image-level and annotation-level resampling.
- Claim boundaries: IPIX zero-shot transfer remains negative, while validation-selected IPIX fusion and supervised SSDD adaptation provide bounded external support.

## Compile Check

Command run twice:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error tgrs_tpsscs_nofig_20260715.tex
```

Result:

- PDF generated: `manuscripts/tgrs_tpsscs_nofig_20260715.pdf`
- Page count: 21
- Table count: 7
- Table labels resolved as Table I--VII
- No LaTeX fatal errors
- No undefined reference/citation warnings in the final log scan
- No overfull hbox warnings in the final log scan

Remaining warning class:

- Underfull hbox/vbox warnings remain in several narrow IEEE two-column areas. These are layout-quality warnings rather than compilation or data-consistency failures.
