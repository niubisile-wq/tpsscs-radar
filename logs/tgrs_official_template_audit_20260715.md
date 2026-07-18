# TGRS Official Template Audit

Date: 2026-07-15

## Purpose

Verify whether the current manuscript format matches the TGRS / IEEE official submission format, and clarify whether TGRS expects single-column or double-column submission.

## Official TGRS Requirement

Source: TGRS Information for Authors PDF, GRSS author resources.

Key formatting requirement:

- Manuscripts must use IEEE standard format.
- TGRS specifies double column, single-spaced PDF format for submission and revision PDFs.
- TGRS points authors to IEEE Template Selector for the correct template.

Official links:

- `https://www.grss-ieee.org/publications/author-resources/tgrs-information-for-authors/`
- `https://www.grss-ieee.org/wp-content/uploads/2023/12/Information-for-Authors_TGRS_pdf.pdf`
- `https://template-selector.ieee.org/`

## Downloaded Template Package

The IEEE Template Selector page blocked command-line download, so the IEEEtran package was downloaded from the CTAN official mirror:

- Downloaded archive: `manuscripts/official_ieee_template_audit/IEEEtran_ctan.zip`
- Extracted directory: `manuscripts/official_ieee_template_audit/IEEEtran/`
- CTAN URL: `https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip`

The downloaded package contains:

- `IEEEtran.cls`
- `bare_jrnl.tex`
- `IEEEtran_HOWTO.pdf`
- BibTeX styles and auxiliary IEEEtran tools.

## Template Class Check

Official `bare_jrnl.tex` uses:

```tex
\documentclass[journal]{IEEEtran}
```

Current manuscript uses:

```tex
\documentclass[journal]{IEEEtran}
```

Therefore the manuscript uses the same journal-mode class line as the official IEEEtran journal skeleton.

## Class File Hash Check

The local TeX Live class and the downloaded CTAN class are identical.

| Source | SHA256 |
|---|---|
| TeX Live `IEEEtran.cls` | `DA751920A317ED318B7B5CD7FA585A6CC7D28502D457856382E9BE24B10A3BD7` |
| Downloaded CTAN `IEEEtran.cls` | `DA751920A317ED318B7B5CD7FA585A6CC7D28502D457856382E9BE24B10A3BD7` |

## Current Manuscript Compile Format

Compiled PDF:

- File: `manuscripts/tgrs_tpsscs_nofig_20260715.pdf`
- Pages: 14
- Paper size: letter, 8.5 in x 11 in
- Font size: 10 pt
- Column layout: two-column IEEEtran journal mode
- Log evidence: `Lines per column: 58 (exact)`

## Verdict

The current manuscript is in the correct IEEEtran journal two-column format for TGRS-style submission. TGRS does not require switching this manuscript to single-column format under the current author instructions checked here.

Strictly stated:

- The manuscript was not originally created by unpacking a freshly downloaded IEEE Template Selector bundle.
- It was created with TeX Live's installed `IEEEtran.cls`.
- The installed `IEEEtran.cls` is byte-identical to the downloaded official CTAN `IEEEtran.cls`.
- The current class line matches the official `bare_jrnl.tex` journal skeleton.

## Remaining Formatting Tasks Before Submission

- Replace placeholder author names, affiliations, funding, and corresponding-author email.
- Add actual figures/tables only after the text is locked.
- Confirm whether TGRS submission portal requests any separate source-file packaging convention at upload time.
