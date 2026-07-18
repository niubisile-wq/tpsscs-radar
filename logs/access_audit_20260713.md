# Access Audit 2026-07-13

## Source status

### AISTAP-SIM

- Status: downloaded and extracted sample archive locally.
- Evidence:
  - `data/downloads/aistap_sim/sampledata.zip`
  - `data/downloads/aistap_sim/sampledata/`
  - `logs/aistap_sample_download_report.txt`
  - `logs/aistap_sample_extract_report.txt`

### RASPNet

- Status: public page verified, but direct download endpoint currently lands on login gate in this environment.
- Evidence:
  - SDMS page states CVNN and EXAMPLES are available for immediate download.
  - Local browser call to the download link redirected to public-login.

### NetRAD

- Status: public dataset page verified.
- Evidence:
  - UCL Figshare page shows DOI `10.5522/04/32676582`.
  - Page shows `Download (122.73 GB)`.
  - Page shows licence `CC BY-NC 4.0`.

### IPIX

- Status: page-based access still needs local download verification.

## Local probe results

- `probe_raspnet_access.ps1`: DNS failure for `www.sdms.afrl.af.mil` in this shell environment.
- `probe_ipix_page.ps1`: HTTP probe failed in this shell environment.
- `probe_netrad_page.ps1`: HTTP 403 in this shell environment.

## Interpretation

- These probe failures do not negate public availability claims observed via browser/web inspection.
- They do mean the current shell environment cannot yet be used as a one-click downloader for these three sources.
