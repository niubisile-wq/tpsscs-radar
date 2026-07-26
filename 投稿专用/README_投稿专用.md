# 投稿专用文件夹说明

本文件夹只保留投稿和复核需要的最终材料，已排除历史草稿、LaTeX 中间文件、旧图、备份图和全量实验数据。

## 目录

- 01_manuscript_pdf/TAES终稿.pdf：最终投稿 PDF。
- 02_latex_source/：可编译 LaTeX 源文件，保留 tex 中的相对路径结构。
- 03_individual_figures/：单独上传图文件，包含最终入文图和可编辑 SVG/PNG 版本。
- 04_data_code_availability/：数据、代码、网盘上传说明。
- 05_metadata/：GitHub/Zenodo/CITATION/README 等仓库元数据。

## 投稿时优先使用

1. 上传 `01_manuscript_pdf/TAES终稿.pdf` 作为 manuscript PDF。
2. 如系统要求源文件，上传 `TAES_submission_source_CLEAN.zip` 或 `02_latex_source`。
3. 如系统要求单独图件，上传 `03_individual_figures` 中对应最终图。
4. 数据和代码不要从旧工程零散挑选，按 `04_data_code_availability` 中说明上传网盘或填写链接。

## 已排除内容

- `.aux`, `.log`, `.fls`, `.fdb_latexmk`, `.synctex.gz` 等编译中间文件。
- `backup`, `before`, `old`, 临时截图、微信缓存图。
- 未被 `TAES终稿.tex` 引用的旧版投稿图和早期 manuscript 草稿。
- 全量 `data`, `results`, `logs`，这些应单独上传网盘或归档仓库。
