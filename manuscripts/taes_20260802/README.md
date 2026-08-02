# TAES Snapshot

This folder stores the current TAES manuscript snapshot for the TP-SSCS paper.

## Contents

- current submission source `.tex`
- compiled manuscript PDF

## Related folders

- `scripts/taes_20260802/`: figure-generation scripts
- `figures/taes_20260802/`: submission figures in PDF/SVG form
- `results/taes_20260802/`: derived CSV, JSON, and NPZ files used by the figures

## Rebuild

From the repository root, regenerate the main paper figures with:

```powershell
python .\scripts\taes_20260802\make_taes_single_column_figures.py
python .\scripts\taes_20260802\make_fig5_external_boundary.py
```

Then rebuild the manuscript PDF with a local LaTeX toolchain:

```powershell
$tex = Get-ChildItem .\manuscripts\taes_20260802 -Filter *.tex | Select-Object -First 1
latexmk -pdf -interaction=nonstopmode -halt-on-error $tex.FullName
```
