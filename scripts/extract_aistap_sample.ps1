param(
  [string]$Root = (Join-Path $env:USERPROFILE "Desktop\第三批3")
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression.FileSystem

$zip = Join-Path $Root "data\downloads\aistap_sim\sampledata.zip"
if (-not (Test-Path $zip)) {
  throw "Missing archive: $zip"
}

$extractDir = Join-Path $Root "data\downloads\aistap_sim\sampledata"
if (Test-Path $extractDir) {
  Remove-Item -LiteralPath $extractDir -Recurse -Force
}
New-Item -ItemType Directory -Path $extractDir -Force | Out-Null

[System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $extractDir)

$entries = [System.IO.Compression.ZipFile]::OpenRead($zip).Entries | Sort-Object FullName
$manifest = Join-Path $extractDir "extracted_files.tsv"
$entries |
  Select-Object FullName, Length |
  ForEach-Object { "$($_.FullName)`t$($_.Length)" } |
  Set-Content -Path $manifest -Encoding utf8

$report = Join-Path $Root "logs\aistap_sample_extract_report.txt"
$lines = @()
$lines += "AISTAP-SIM sample extraction"
$lines += "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$lines += "Archive: $zip"
$lines += "ExtractDir: $extractDir"
$lines += "EntryCount: $($entries.Count)"
$lines += ""
$lines += "Entries:"
foreach ($entry in $entries) {
  $lines += " - $($entry.FullName) | size=$($entry.Length)"
}
$lines | Set-Content -Path $report -Encoding utf8
Write-Host "Wrote $report"
