# TGRS Submission Metadata Fill-In Template

Date: 20260717

This file lists the remaining non-technical submission fields that must be filled before formal TGRS submission. Do not submit while bracketed placeholders remain.

## Blocking Fields

- Real author names.
- IEEE membership status for each author, if applicable.
- Full author affiliations.
- Corresponding author name and email.
- ORCID identifiers required by the IEEE submission workflow.
- Funding and grant numbers.
- Final acknowledgment text.
- Public repository URL, DOI, or controlled-access statement for the code and processed source data.

## Author Block Template

Replace the current placeholder author block with a completed block in this form:

```tex
\author{
Author~One,~\IEEEmembership{Member,~IEEE,}
Author~Two,
and~Author~Three,~\IEEEmembership{Senior~Member,~IEEE}%
\thanks{Author One is with [Department], [Institution], [City, Postal Code], [Country] (e-mail: [author1@email]).}%
\thanks{Author Two is with [Department], [Institution], [City, Postal Code], [Country] (e-mail: [author2@email]).}%
\thanks{Author Three is with [Department], [Institution], [City, Postal Code], [Country] (e-mail: [author3@email]).}%
\thanks{Corresponding author: [Corresponding Author Name] (e-mail: [corresponding@email]).}%
\thanks{This work was supported by [Funding Agency] under Grant [Grant Number].}
}
```

If there is no funding support, replace the funding line with:

```tex
\thanks{This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.}
```

## ORCID Checklist

Fill this table before submission:

| Author | ORCID |
|---|---|
| [Author One] | [0000-0000-0000-0000] |
| [Author Two] | [0000-0000-0000-0000] |
| [Author Three] | [0000-0000-0000-0000] |

## Acknowledgment Template

```tex
\section*{Acknowledgment}

The authors thank [individuals/lab/group, if any] for [specific help]. The authors acknowledge the public AISTAP-SIM, Dartmouth IPIX sea-clutter, and SSDD SAR ship-detection datasets used in the experimental validation. [Add institutional computing resources or remove this sentence if not applicable.]
```

If no personal acknowledgment is needed:

```tex
\section*{Acknowledgment}

The authors acknowledge the public AISTAP-SIM, Dartmouth IPIX sea-clutter, and SSDD SAR ship-detection datasets used in the experimental validation.
```

## Data Availability Template

```tex
\section*{Data Availability}

The AISTAP-SIM, Dartmouth IPIX sea-clutter, and SSDD SAR ship-detection datasets used in this study are publicly available from their original data providers. The processed source-data tables, bootstrap summaries, seed-sensitivity outputs, and CFAR parameter-sweep outputs supporting the reported figures and tables are archived at [repository URL/DOI]. Access restrictions, if any, are described in the repository record.
```

## Code Availability Template

```tex
\section*{Code Availability}

The scripts used to reproduce the AISTAP-SIM validation, target-preservation ablation, IPIX residual-aware fusion, SSDD adaptation, bootstrap confidence intervals, seed-sensitivity analysis, strengthened CFAR baselines, and CFAR parameter sweep are archived at [repository URL/DOI].
```

## Current Manuscript Placeholder Hits

The 20260717 readiness audit detects these unresolved placeholders in `tgrs_tpsscs_final_package_20260716/manuscript/tgrs_tpsscs_nofig_20260715.tex`:

- `metadata_placeholder:author_name_placeholder`
- `metadata_placeholder:email_placeholder`
- `metadata_placeholder:journal_issue_placeholder`
- `metadata_placeholder:insert_before_submission`
- `metadata_placeholder:generic_data_availability`
- `metadata_placeholder:generic_code_availability`

The journal issue placeholder in `\markboth{IEEE Transactions on Geoscience and Remote Sensing,~Vol.~XX, No.~XX, 2026}` is usually acceptable for a preprint-style draft but should be aligned with the final IEEE template instructions before submission.
