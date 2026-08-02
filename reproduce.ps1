Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

python .\scripts\taes_20260802\make_taes_single_column_figures.py
python .\scripts\taes_20260802\make_fig5_external_boundary.py

$tex = Get-ChildItem .\manuscripts\taes_20260802 -Filter *.tex | Select-Object -First 1
latexmk -pdf -interaction=nonstopmode -halt-on-error $tex.FullName
