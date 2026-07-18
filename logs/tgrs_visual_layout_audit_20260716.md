# TGRS TP-SSCS visual layout audit, 2026-07-16

## Files checked

- `manuscripts/tgrs_tpsscs_nofig_20260715.tex`
- `manuscripts/tgrs_tpsscs_nofig_20260715.pdf`
- `manuscripts/tgrs_tpsscs_withfig_20260716.tex`
- `manuscripts/tgrs_tpsscs_withfig_20260716.pdf`

## Final compiled state

- Page count: 18 pages for both PDFs.
- Text count by `texcount`: 11715 words in text; 12188 sum count.
- Visual contact sheet: `layout_audit_20260716_final2/contact_sheet_18pages_final2.png`.
- Main layout inventory: 5 displayed figures and 4 displayed tables.

## Layout fixes applied

- Converted wide result tables to controlled full-width blocks so they no longer force large blank gaps around pages 12--14.
- Removed the previous Fig. 5 split across pages 14--15 by converting the external radar validation graphic to a `figure*` top float.
- Reduced Fig. 5 display width to keep the graphic, caption, and interpretation block together on page 15.
- Let the SSDD/external-validation prose fill page 14 after Table IV, eliminating the mid-page blank region.

## Visual audit result

- Pages 1--18 were rendered to images and inspected as a contact sheet.
- Pages 12--15 were inspected individually after the final change.
- No large mid-document blank page or large mid-page gap remains.
- Remaining white space is normal page margin/end-of-document slack, not a float-placement gap.

## Follow-up split-float fix

- User visual inspection showed Fig. 4 being cut across the page break after Table III.
- Cause: a `cuted`/`strip` wide block was inserted into insufficient remaining page space, so the graphic body and caption were split across pages.
- Fix: Fig. 4 was converted to an unbroken `figure*` top float at `0.78\textwidth`.
- A follow-up split of Table IV was then removed by converting Table IV to an unbroken `table*` top float.
- Final checked state after this fix: 19 pages, with no half-cut figure/table in the middle of the manuscript.
- Visual contact sheet: `layout_audit_20260716_nosplit_final/contact_sheet_19pages_nosplit_final.png`.

## Figure/table reference proximity pass

- Requirement: every figure/table should have its own explanatory reference paragraph as close as possible, preferably on the same rendered page, and should not rely on a numbered citation one page before the display.
- Action: removed or rewrote advance numbered references in body prose, replacing them with non-numbered forward cues such as "the following protocol table" or "the subsequent full-asset figure".
- Action: added short same-page explanatory paragraphs to Fig. 1, Fig. 2, and Fig. 3, matching the existing same-page explanations for Fig. 4, Fig. 5, and all tables.
- PDF text audit after compilation shows all explicit numbered occurrences on the display pages only:
  - Fig. 1: page 3
  - Fig. 2: page 7
  - Fig. 3: page 9
  - Table I: page 10
  - Table II and Table III: page 12
  - Fig. 4: page 13
  - Table IV and Fig. 5: page 15
- Visual contact sheet: `layout_audit_20260716_refs_close/contact_sheet_19pages_refs_close.png`.

## Log audit

No matches were found for:

- fatal LaTeX errors
- undefined references or citations
- `Float too large`
- `Overfull \hbox`
- `Overfull \vbox`
