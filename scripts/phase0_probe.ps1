param(
  [string]$Root = (Join-Path $env:USERPROFILE "Desktop\TP-SSCS项目")
)

$ErrorActionPreference = "Stop"

$paths = @(
  (Join-Path $Root "cards")
  (Join-Path $Root "gates")
  (Join-Path $Root "data")
  (Join-Path $Root "data\manifests")
  (Join-Path $Root "data\downloads")
  (Join-Path $Root "logs")
  (Join-Path $Root "runbooks")
)

foreach ($p in $paths) {
  if (-not (Test-Path $p)) {
    throw "Missing required path: $p"
  }
}

$report = Join-Path $Root "logs\phase0_probe_report.txt"
$lines = @()
$lines += "Phase 0 probe"
$lines += "Root: $Root"
$lines += "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$lines += ""
$lines += "Checked paths:"
foreach ($p in $paths) {
  $lines += " - $p"
}

$lines | Set-Content -Path $report -Encoding utf8
Write-Host "Wrote $report"

