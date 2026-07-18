# TGRS reference cleanup and word/page-limit audit

Date: 2026-07-16

## Files updated

- `manuscripts/tgrs_tpsscs_nofig_20260715.tex`
- `manuscripts/tgrs_tpsscs_withfig_20260716.tex`

## Reference cleanup

- Kept the total reference count at 32 to avoid expanding the bibliography pages.
- Replaced five generic computer-vision references with five recent TGRS references on SAR ship / remote-sensing target detection.
- Removed:
  - `liu2020objectsurvey`
  - `ren2017fasterrcnn`
  - `redmon2016yolo`
  - `shelhamer2017fcn`
  - `ronneberger2015unet`
- Added:
  - `liu2024evidence`: TGRS 2024, SAR ship detection with explainable evidence learning.
  - `zhou2024fewshot`: TGRS 2024, domain-adaptive few-shot SAR ship detection.
  - `shen2024ellknet`: TGRS 2024, lightweight large-kernel SAR ship detection.
  - `ma2024ssdnet`: TGRS 2024, SAR small ship detection network.
  - `qin2025rdbdino`: TGRS 2025, transformer-based small-scale SAR ship detection.

## Reference distribution after cleanup

- Total references: 32
- References since 2020: 14
- References since 2022: 10
- TGRS references: 11
- TGRS references since 2020: 10
- Pre-2015 references: 11, retained mainly for STAP, CFAR, adaptive detection, sea clutter, RPCA/bootstrap foundations.

## Word and page audit

- Current PDF length: 24 pages, letter paper, IEEEtran journal two-column format.
- `texcount` sum count: 12,402
- Words in text: 11,889
- Main section counts from `texcount`:
  - Introduction: 940 text words
  - Related Work: 1,685 text words
  - Results: 2,666 text words
  - Discussion: 1,675 text words
  - Conclusion: 486 text words

## TGRS rule check

- The official TGRS author page requires IEEE standard double-column, single-spaced format for submission PDFs.
- The same page states that, for original submissions after 1 January 2026, the mandatory overlength page charge starts with page 11 for accepted TGRS papers.
- No separate official word-count ceiling was found on the TGRS author-information page during this audit.

## Compile audit

- `pdflatex` completed successfully for both updated TeX files.
- Log scan found no fatal errors, undefined references, undefined citations, overfull hboxes, or float-too-large warnings.
- Remaining warnings are underfull hbox/vbox messages from dense IEEE two-column tables and floats.

## Practical risk assessment

- The manuscript is not over a stated TGRS word-count limit because no explicit official word-count limit was found.
- It is over the 10 printed-page threshold used for mandatory overlength page charges after acceptance.
- The current 24-page draft should be treated as a strong full draft, not a cost-optimized final submission. A later compression pass can target 18-20 pages first, then decide whether further compression is worth the loss in evidential clarity.
