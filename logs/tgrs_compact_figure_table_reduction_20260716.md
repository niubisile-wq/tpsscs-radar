# TGRS compact figure/table reduction

Date: 2026-07-16

## Output

- Compact source: `manuscripts/tgrs_tpsscs_compact_20260716.tex`
- Compact PDF: `manuscripts/tgrs_tpsscs_compact_20260716.pdf`

## Rationale

The full draft had 24 pages, 9 figures, and 7 tables. The word count was not unusually high for a TGRS-style full article, but the figure/table layout inflated page count. The compact version therefore removes redundant explanatory figures and summary tables while retaining the core numerical evidence.

## Removed items

- Fig. 2, target-preserving principle figure.
  - Reason: largely overlaps with Fig. 1 and the local gate explanation in Fig. 4.
  - Replacement: prose statement of the suppression-preservation compromise.
- Fig. 5, experimental protocol figure.
  - Reason: overlaps with Table I, which already gives dataset roles, units, splits, and claim boundaries.
  - Replacement: shortened protocol paragraph before Table I.
- Fig. 8, SSDD unit robustness boxplot.
  - Reason: the exact image-level and annotation-level intervals are retained in Table VI.
  - Replacement: Table VI plus explanatory prose.
- Fig. 9, evidence hierarchy figure.
  - Reason: summary/claim-boundary content is already covered by Table I, the external-result text, and the Discussion.
  - Replacement: one evidence-hierarchy paragraph before Discussion.
- Table III, target-preservation branch evidence and claim boundaries.
  - Reason: branch-level values are already stated in prose.
  - Replacement: condensed branch-evidence paragraph.
- Table V, paired bootstrap support for AISTAP-SIM.
  - Reason: the full-asset main figure includes bootstrap intervals, and the text gives range summaries.
  - Replacement: Fig. 6 compact explanation plus prose summaries.
- Table VII, external validation and adaptation summary.
  - Reason: external-result numbers are stated in prose and visualized in the external validation figure; SSDD unit robustness is retained in Table VI.
  - Replacement: result text and Fig. external-radar-results.

## Retained core evidence

- Figures retained: 5 total.
  - Fig. 1 paradigm shift.
  - Fig. 3 architecture.
  - Fig. 4 local gating mechanism.
  - Official AISTAP-SIM full-asset validation figure.
  - External radar-family validation figure.
- Tables retained: 4 total.
  - Table I dataset roles and claim boundaries.
  - Table II low-rank suppression-preservation audit.
  - Table IV AISTAP-SIM full-asset operating values.
  - Table VI SSDD image- and annotation-level bootstrap support.

## Result

- Full draft: 24 pages, 9 figures, 7 tables.
- Compact draft: 21 pages, 5 figures, 4 tables.
- `texcount` compact text words: 11,767.
- `texcount` compact sum count: 12,196.

## Compile status

- `pdflatex` completed successfully after two passes.
- Log scan found no fatal errors, undefined references, undefined citations, overfull hboxes, or float-too-large warnings.
- Remaining warnings are underfull hbox/vbox warnings from IEEE two-column line/page breaking.

## Recommendation

This is the safest compact version. Further page reduction should first target prose tightening and figure scaling. Deleting additional core result figures/tables would save space but would weaken the TGRS evidence chain.
