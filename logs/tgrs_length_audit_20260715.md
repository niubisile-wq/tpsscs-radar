# TGRS Manuscript Length Audit

Date: 2026-07-15

## Purpose

Estimate the normal manuscript length for TGRS-style remote-sensing target detection / clutter suppression papers and compare it with the current no-figure TP-SSCS draft.

## Current TP-SSCS Draft

| File | Format | Pages | Estimated words | Notes |
|---|---:|---:|---:|---|
| `manuscripts/tgrs_tpsscs_nofig_20260715.pdf` | IEEEtran two-column PDF | 7 | 6207 | no figures, placeholder references |
| `manuscripts/tgrs_tpsscs_nofig_20260715.tex` | TeX source | - | 5465 | source-word count excludes TeX command expansion |

## Downloadable TGRS / TGRS-Style Samples

Word counts were estimated by converting public author-version PDFs to text with `pdftotext` and counting alphanumeric tokens. Counts include title, abstract, body, references, and some visible table/figure text when present. They are therefore best used as writing-length references, not exact journal word counts.

| Sample | Topic fit | Pages | Estimated words | Source file |
|---|---:|---:|---:|---|
| Random Access Memories: A New Paradigm for Target Detection in High Resolution Aerial Remote Sensing Images | target detection | 12 | 9037 | `2017_zhengxia_zou_random.pdf` |
| A Degraded Reconstruction Enhancement-Based Method for Tiny Ship Detection in Remote Sensing Images With a New Large-Scale Dataset | ship detection | 14 | 11139 | `2022_jianqi_chen_a.pdf` |
| Contrastive Learning for Fine-Grained Ship Classification in Remote Sensing Images | ship recognition/classification | 16 | 12449 | `2022_jianqi_chen_contrastive.pdf` |
| Infrared Small Target Detection Based on Prior Guided Dense Nested Network | small target detection | 15 | 11973 | `2025_Chang_Liun_Infrared.pdf` |
| RSBEV: Multi-View Collaborative Segmentation of 3D Remote Sensing Scenes | remote-sensing segmentation | 15 | 10554 | `2024_Baihong_Lin_RSBEV.pdf` |
| Structure-Color Preserving Network for Hyperspectral Image Super-Resolution | remote-sensing reconstruction | 12 | 8021 | `2022_bin_pan_structure-color.pdf` |
| Geographical Supervision Correction for Remote Sensing Representation Learning | representation learning | 20 | 14428 | `2022_wenyuan_li_geographical_supervision.pdf` |

## Statistics

| Group | n | Page range | Mean pages | Word range | Mean words |
|---|---:|---:|---:|---:|---:|
| Closest target-detection / ship / small-target samples | 4 | 12-16 | 14.25 | 9037-12449 | 11149.5 |
| Broader TGRS-style remote-sensing samples | 7 | 12-20 | 14.86 | 8021-14428 | 11085.9 |

## Interpretation for TP-SSCS

- Current no-figure draft: 7 IEEEtran pages, about 6207 PDF-extracted words.
- Comparable target-detection TGRS samples: usually 12-16 pages and about 9000-12500 extracted words.
- Current draft is about 55.7% of the closest-sample mean word count and about 49.1% of the closest-sample mean page count.
- A figureless first draft can be shorter than final TGRS layout, but the current text is still underdeveloped for a full TGRS article.

## Recommended Target Length

- Text-only TeX source before figures: target 8500-9500 manuscript words.
- Final IEEEtran PDF with figures/tables: target 12-15 pages.
- Minimum credible TGRS full-paper draft: about 8000 words before references and captions.
- Stronger TGRS-ready target for this paper: about 9000 words plus verified references, then add figures/tables.

## Expansion Priorities

1. Expand related work from four short subsections into a full radar/STAP/CFAR, low-rank suppression, weak-target learning, and SAR ship detection review with verified references.
2. Add a clearer algorithmic Method section with pseudo-code style steps, not only prose and formulas.
3. Add a fuller experimental-protocol section with dataset splits, calibration details, bootstrap units, and exact pass/fail gates.
4. Expand Results with table-ready numeric summaries for AISTAP-SIM, IPIX, and SSDD even before figures are inserted.
5. Add a limitations and ablation discussion that anticipates TGRS reviewer concerns about zero-shot transfer, supervised SSDD adaptation, and extra classical detector baselines.

## Verdict

The current draft has the correct TGRS skeleton but is too short for a full TGRS article. It should be expanded from roughly 6200 PDF-extracted words to about 8500-9500 source/body words before adding figures and tables.

## Post-Expansion Update

Date: 2026-07-15

The TGRS TeX draft was expanded after the initial audit.

| File | Format | Pages | Estimated words | Notes |
|---|---:|---:|---:|---|
| `manuscripts/tgrs_tpsscs_nofig_20260715.tex` | TeX source | - | 11416 | PowerShell `Measure-Object -Word`; includes TeX commands/placeholders |
| `manuscripts/tgrs_tpsscs_nofig_20260715.pdf` | IEEEtran two-column PDF | 13 | 12677 | `pdftotext` token count; includes headings, references, and PDF text artifacts |

Post-expansion status:

- The manuscript is now within the observed TGRS-style page range for target-detection papers.
- The TeX source is approximately at the requested 11000-word level.
- The draft still contains no figure environment or image inclusion command.
- The bibliography remains placeholder-based and must be replaced with verified IEEE references before submission.

## Citation-Replacement Update

Date: 2026-07-15

The placeholder bibliography was replaced with verified references for STAP, CFAR, adaptive detection, robust low-rank/subspace learning, weak-target detection, remote-sensing deep learning, AISTAP-SIM, IPIX sea clutter, SSDD, SAR ship detection, domain adaptation, and bootstrap uncertainty.

Post-citation status:

| File | Format | Pages | Estimated words | Notes |
|---|---:|---:|---:|---|
| `manuscripts/tgrs_tpsscs_nofig_20260715.tex` | TeX source | - | 11718 | no `REPLACE_` placeholders remain |
| `manuscripts/tgrs_tpsscs_nofig_20260715.pdf` | IEEEtran two-column PDF | 14 | 13126 | no undefined references in final compile log |

Final checks after citation replacement:

- No `REPLACE_` placeholders.
- No `Reference to be verified` strings.
- No undefined citation warnings after second `pdflatex` pass.
- No figure environment or image inclusion command.
- Current PDF length is 14 pages, within the audited TGRS target-detection range of 12-16 pages.

## Expanded Bibliography Update

Date: 2026-07-15

The reference list was expanded to satisfy the TGRS-style bibliography target requested by the user.

Final bibliography status:

| Metric | Value |
|---|---:|
| Total references | 32 |
| TGRS target-journal references | 6 |
| PDF pages | 14 |
| TeX source words | 12333 |
| PDF-extracted words | 13906 |

Target-journal references included:

- Panagopoulos and Soraghan, "Small-target detection in sea clutter," TGRS 2004.
- Liu et al., "Robust CFAR detector based on truncated statistics for polarimetric synthetic aperture radar," TGRS 2020.
- Chen et al., "A degraded reconstruction enhancement-based method for tiny ship detection in remote sensing images with a new large-scale dataset," TGRS 2022.
- Liu et al., "Infrared small target detection based on prior guided dense nested network," TGRS 2025.
- Leng et al., "Ship detection from raw SAR echo data," TGRS 2023.
- Chen et al., "Contrastive learning for fine-grained ship classification in remote sensing images," TGRS 2022.

Final checks after expansion:

- No undefined citation warnings after the second compile pass.
- No `REPLACE_` placeholders.
- No `Reference to be verified` placeholders.
- No figure environment or image inclusion command.
