param(
  [string]$Root = (Join-Path $env:USERPROFILE "Desktop\TP-SSCS项目")
)

$ErrorActionPreference = "Stop"

$url = "https://rdr.ucl.ac.uk/articles/dataset/NetRAD_-_Monostatic_Bistatic_Sea_Clutter_Dataset/32676582"
$report = Join-Path $Root "logs\probe_netrad_page.txt"
$lines = @()
$lines += "NetRAD page probe"
$lines += "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$lines += "URL: $url"

$curlOutput = & curl.exe --silent --show-error -L -I --max-time 30 --user-agent "Codex" --write-out "HttpCode: %{http_code}`nFinalUrl: %{url_effective}`n" --output NUL $url 2>&1
$exitCode = $LASTEXITCODE
$lines += "CurlExitCode: $exitCode"
$lines += $curlOutput
if ($exitCode -eq 0) {
  $lines += "Status: PROBED"
} else {
  $lines += "Status: FAILED"
}

$lines | Set-Content -Path $report -Encoding utf8
Write-Host "Wrote $report"

