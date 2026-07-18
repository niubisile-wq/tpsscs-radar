param(
  [string]$Root = (Join-Path $env:USERPROFILE "Desktop\第三批3"),
  [ValidateSet("archive","all")]
  [string]$Mode = "archive",
  [switch]$Force
)

$ErrorActionPreference = "Stop"

$downloadDir = Join-Path $Root "data\downloads\aistap_sim"
New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null

$api = "https://api.github.com/repos/mit-ll/AISTAP-SIM/releases/tags/Data"
$release = Invoke-RestMethod -Headers @{ 'User-Agent' = 'Codex' } -Uri $api

$sampleAssets = $release.assets | Where-Object {
  if ($Mode -eq "archive") {
    $_.name -eq "sampledata.zip"
  } else {
    $_.name -match 'sample'
  }
} | Sort-Object name

if (-not $sampleAssets) {
  throw "No sample assets found in AISTAP-SIM release Data."
}

$manifest = Join-Path $downloadDir "assets_manifest.tsv"
$rows = @()

foreach ($asset in $sampleAssets) {
  $target = Join-Path $downloadDir $asset.name
  $rows += [pscustomobject]@{
    name = $asset.name
    size = $asset.size
    url = $asset.browser_download_url
    target = $target
  }

  if ((Test-Path $target) -and (-not $Force)) {
    continue
  }

  Invoke-WebRequest -Headers @{ 'User-Agent' = 'Codex' } -Uri $asset.browser_download_url -OutFile $target
}

$rows | Export-Csv -Path ($manifest -replace '\.tsv$', '.csv') -NoTypeInformation -Encoding UTF8
$rows | ForEach-Object { "$($_.name)`t$($_.size)`t$($_.url)`t$($_.target)" } | Set-Content -Path $manifest -Encoding utf8

$report = Join-Path $Root "logs\aistap_sample_download_report.txt"
$lines = @()
$lines += "AISTAP-SIM sample download"
$lines += "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$lines += "Mode: $Mode"
$lines += "Assets: $($sampleAssets.Count)"
$lines += "Directory: $downloadDir"
$lines += ""
$lines += "Files:"
foreach ($asset in $sampleAssets) {
  $target = Join-Path $downloadDir $asset.name
  if (Test-Path $target) {
    $info = Get-Item $target
    $lines += " - $($asset.name) | size=$($info.Length) | expected=$($asset.size)"
  } else {
    $lines += " - $($asset.name) | missing"
  }
}
$lines | Set-Content -Path $report -Encoding utf8
Write-Host "Wrote $report"
