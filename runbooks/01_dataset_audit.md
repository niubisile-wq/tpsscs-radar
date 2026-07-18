# Runbook 01: Dataset Audit

目标：

- 把所有公开数据源变成可追踪的审计记录。

产物：

- `data/manifests/datasets.tsv`
- `data/manifests/licenses.tsv`
- `data/manifests/filesystem_map.tsv`
- `logs/phase0_dataset_audit.md`

检查项：

- 下载链接是否可达。
- 文件是否完整。
- 许可是否明确。
- 是否存在目标真值。
- 是否需要 target injection。

