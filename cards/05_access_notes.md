# Access Notes

## 已完成

- AISTAP-SIM sample archive downloaded locally.
- AISTAP-SIM sample archive extracted locally.
- Dataset manifest generated.
- Phase 0 probe report generated.

## 当前可确认的公开数据状态

- AISTAP-SIM: GitHub release public, sample archive accessible without login.
- NetRAD: UCL Figshare page public; page shows DOI, 122.73 GB download size, and CC BY-NC 4.0 licence.
- RASPNet: public CVNN / EXAMPLES are marked as immediate download on the SDMS page, but the download endpoint redirects to a public-login gate in this environment.
- IPIX: public dataset page exists and remains the next manual verification target.
- Shell probe results:
  - `RASPNet`: DNS failure in current shell.
  - `IPIX`: HTTP probe failed in current shell.
  - `NetRAD`: HTTP 403 in current shell.

## Execution rule

- Do not treat a data source as usable for the main experiment until a local download or a verified session-based retrieval path exists.
- Do not write model code ahead of a reproducible data read path.
