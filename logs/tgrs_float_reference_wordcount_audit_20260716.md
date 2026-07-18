---
date: 2026-07-16
manuscript: manuscripts/tgrs_tpsscs_nofig_20260715.tex
pdf: manuscripts/tgrs_tpsscs_nofig_20260715.pdf
task: Same-page figure/table reference audit and conclusion expansion
---

# Float Reference and Word-Allocation Audit

## Main Changes

- Added explicit same-page explanatory references for all 9 figures and 7 tables.
- Converted Figures 6--9 from floating `figure*` blocks to non-floating full-width `strip` blocks so the figure, caption, and explanatory paragraph stay together.
- Added short table-level explanatory paragraphs under Tables I--VII to prevent wide-table floats from separating tables from their interpretive text.
- Expanded the conclusion from 323 words to 595 words.
- Synced the updated main source to `manuscripts/tgrs_tpsscs_withfig_20260716.tex`.

## Figure/Table Page Audit

The PDF was checked with `pdftotext -layout` after two `pdflatex` passes.

| Item | Page | Same-page reference status |
|---|---:|---|
| Fig. 1 | 3 | Pass |
| Fig. 2 | 6 | Pass |
| Fig. 3 | 8 | Pass |
| Fig. 4 | 9 | Pass |
| Fig. 5 | 10 | Pass |
| Fig. 6 | 15 | Pass |
| Fig. 7 | 18 | Pass |
| Fig. 8 | 19 | Pass |
| Fig. 9 | 20 | Pass |
| Table I | 11 | Pass |
| Table II | 13 | Pass |
| Table III | 14 | Pass |
| Table IV | 14 | Pass |
| Table V | 14 | Pass |
| Table VI | 17 | Pass |
| Table VII | 17 | Pass |

## Section Word Counts

| Section | Words |
|---|---:|
| Introduction | 948 |
| Related Work | 1687 |
| Problem Setting and Motivation | 1095 |
| Target-Preserving Structured-Clutter Suppression | 1712 |
| Experimental Protocol | 1399 |
| Results | 2830 |
| Discussion | 1664 |
| Conclusion | 595 |

## TGRS-Style Structure Reference

Three publicly accessible TGRS-format PDFs were downloaded for coarse structural comparison:

| Reference PDF | Pages | Figures | Tables | Approx. conclusion words |
|---|---:|---:|---:|---:|
| `captioning_tgrs2020.pdf` | 12 | 5 | 7 | 127 |
| `dntr_tgrs2024.pdf` | 15 | 10 | 11 | 185 |
| `time_warping_tgrs2012.pdf` | 15 | 6 | 2 | 671 |

Interpretation:

- The revised manuscript has 24 pages, 9 figures, and 7 tables.
- The figure/table count is within the observed TGRS-style range.
- The conclusion is no longer abnormally short relative to the manuscript evidence structure.

## Compile Status

Commands:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error tgrs_tpsscs_nofig_20260715.tex
pdflatex -interaction=nonstopmode -halt-on-error tgrs_tpsscs_nofig_20260715.tex
```

Final log scan:

- No fatal LaTeX errors.
- No undefined references.
- No undefined citations.
- No overfull hbox warnings.
- Remaining warnings are underfull hbox/vbox warnings from IEEE two-column line/page breaking.
