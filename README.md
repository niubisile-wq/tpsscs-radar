# TP-SSCS TAES Snapshot

This branch snapshot packages the current TAES submission state for the TP-SSCS radar paper.

## Layout

- `manuscripts/taes_20260802/`: manuscript source and compiled PDF
- `scripts/taes_20260802/`: figure-generation scripts used for the paper
- `figures/taes_20260802/`: submission figures in PDF/SVG form
- `results/taes_20260802/`: derived CSV/JSON/NPZ files used by the figures
- `REPRODUCIBILITY.md`: step-by-step rebuild instructions for reviewers
- `reproduce.ps1`: PowerShell entry point for the local rebuild sequence
- `requirements.txt`: minimal Python dependencies for the figure scripts

## Notes

- This snapshot is intended for reproducibility and Zenodo mirroring.
- Raster previews are intentionally omitted to keep the repository lightweight.
- Public datasets used by the paper are not mirrored here; the repo stores the derived outputs and scripts needed to regenerate the paper figures.
