param(
  [string]$Root = (Join-Path $env:USERPROFILE "Desktop\第三批3")
)

$ErrorActionPreference = "Stop"

$url = "http://soma.ece.mcmaster.ca/ipix/dartmouth/datasets.html"
$report = Join-Path $Root "logs\probe_ipix_page.txt"
$lines = @()
$lines += "IPIX page probe"
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
