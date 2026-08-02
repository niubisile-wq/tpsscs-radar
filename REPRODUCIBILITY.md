# Reproducibility Guide

This repository snapshot corresponds to the TAES submission state of the TP-SSCS radar paper as of 2026-08-02.

## Included artifacts

- the manuscript source `.tex` file in `manuscripts/taes_20260802/`
- the compiled manuscript PDF in `manuscripts/taes_20260802/`
- `scripts/taes_20260802/`: figure-generation scripts
- `figures/taes_20260802/`: submission-ready figure PDFs and SVGs
- `results/taes_20260802/`: derived CSV, JSON, and NPZ files used by the figures

## External data

The paper uses public datasets that are not mirrored in this repository:

- AISTAP-SIM
- Dartmouth IPIX sea-clutter recordings
- SSDD

The repository stores the derived outputs and plotting scripts needed to reproduce the paper figures from those public sources.

## Python environment

Install the minimal plotting environment:

```powershell
python -m pip install -r requirements.txt
```

The figure scripts use:

- Python 3.10+
- `numpy`
- `matplotlib`

## Regenerate figures

From the repository root:

```powershell
python .\scripts\taes_20260802\make_taes_single_column_figures.py
python .\scripts\taes_20260802\make_fig5_external_boundary.py
```

These scripts write the final PDF and SVG figure files into `figures/taes_20260802/`.

## Rebuild the manuscript

After the figures are in place, rebuild the paper with a local LaTeX toolchain:

```powershell
$tex = Get-ChildItem .\manuscripts\taes_20260802 -Filter *.tex | Select-Object -First 1
latexmk -pdf -interaction=nonstopmode -halt-on-error $tex.FullName
```

If `latexmk` is not available, use the local TeX distribution's standard LaTeX/BibTeX sequence.

## File mapping

- `results/taes_20260802/fig2_mechanism.csv` -> Fig. 2 mechanism audit
- `results/taes_20260802/fig3_ablation.csv` -> Fig. 3 rescue ablation
- `results/taes_20260802/fig4_main_validation.csv` -> Fig. 4 main validation
- `results/taes_20260802/fig5_ipix.csv` -> Fig. 5 IPIX boundary audit
- `results/taes_20260802/fig5_ssdd.csv` -> Fig. 5 SSDD boundary audit
- `results/taes_20260802/fig6_statistical_robustness.csv` -> Fig. 6 statistical robustness
- `results/taes_20260802/fig7_aistap_case_audit.npz` and `fig7_aistap_case_audit.json` -> Fig. 7 case audit
- `results/taes_20260802/fig8_alarm_budget_bootstrap.csv` and `fig8_alarm_budget_summary.csv` -> Fig. 8 alarm budget
