# Shutdown Checkpoint - 2026-07-18

Project root:

Use the parent directory of this checkpoint's `logs` folder as the project root. In PowerShell, start from this project folder before running the commands below. The absolute path contains Chinese characters, so it is intentionally not repeated here to avoid console-encoding copy issues.

## Active objective

Continue strengthening the TP-SSCS paper toward a credible CAS Q1 Top submission.

## Completed before shutdown

1. Existing final package before this turn was technically complete but still not a locked Q1 Top case:
   - `top_readiness`: `top_ready`, hard failures `0`.
   - Submission audit: `technically_complete_metadata_blocked`, hard failures `0`, warnings `0`, page count `12`.
   - Remaining non-hard partial gates were:
     - `cross_condition_holdout`
     - `feature_ensemble_boundary`
     - `target_free_calibration_boundary`

2. Rechecked current weakness and found that the old `cross_condition_holdout` gate was still using early public-sample subset LOSO evidence.

3. Generated a stronger official full-asset cross-condition validation for 20260718:

```powershell
py scripts\evaluate_aistap_cross_condition_full_asset_validation.py --root . --date 20260718 --inputs 'results\aistap_full_asset\aistap_full_asset_detector_candidate_simMed_test_20260715.csv,results\aistap_full_asset\aistap_full_asset_detector_candidate_simWind_test_20260715.csv'
```

Generated files:

- `logs/aistap_cross_condition_full_asset_validation_20260718.json`
- `logs/aistap_cross_condition_full_asset_validation_20260718.md`
- `results/aistap_full_asset/aistap_cross_condition_full_asset_summary_20260718.csv`

Key result:

- `passed=true`
- assets: `simMed_test.mat`, `simWind_test.mat`
- comparisons: `14`
- failures: `0`
- all 14 asset-Pfa rows beat `raw`
- all 14 asset-Pfa rows beat `low_rank_residual_k30`
- all empirical-Pfa rows are calibrated under the script tolerance
- this is official AISTAP-SIM cross-condition evidence, not independent non-AISTAP external validation

4. Patched `scripts/evaluate_aistap_top_readiness.py`:

- `gate_cross_condition(root)` now first reads the latest `logs/aistap_cross_condition_full_asset_validation_*.json` and `results/aistap_full_asset/aistap_cross_condition_full_asset_summary_*.csv`.
- It requires:
  - at least 2 official assets
  - at least 14 comparisons
  - at least 100 target-bearing items per asset
  - all rows beat raw
  - all rows beat low-rank
  - all rows are empirical-Pfa calibrated
- It falls back to the old public-sample subset LOSO summary only if the official full-asset evidence is absent.
- Syntax check passed:

```powershell
py -m py_compile scripts\evaluate_aistap_top_readiness.py
```

## Interrupted / not yet completed

The next patch to `scripts/audit_aistap_claim_consistency.py` was attempted but failed to apply because the expected context did not match. No partial change from that failed patch was applied.

The following integration steps are still pending:

1. Patch `scripts/audit_aistap_claim_consistency.py` to include:
   - JSON evidence path:
     - `logs/aistap_cross_condition_full_asset_validation_20260718.json`
   - hard evidence check:
     - `passed=true`
     - assets include `simMed_test.mat` and `simWind_test.mat`
     - `comparison_count >= 14`
     - minimum `n_items >= 100`
     - all `beats_raw=true`
     - all `beats_lowrank=true`
     - all `pfa_calibrated=true`
     - boundary says this is not independent non-AISTAP external validation
   - expected top-readiness gate status:
     - `"cross_condition_holdout": "pass"`
   - required phrase check over manuscript, README, and claim matrix:
     - mentions `simMed_test` and `simWind_test`
     - mentions `14/14` or all 14 asset-Pfa comparisons
     - mentions empirical/conservative Pfa calibration
     - mentions the non-AISTAP external-validation boundary

2. Patch `scripts/audit_tgrs_submission_readiness.py` expected package files to include:
   - source data:
     - `source_data/aistap_full_asset/aistap_cross_condition_full_asset_summary_20260718.csv`
   - script:
     - `scripts/evaluate_aistap_cross_condition_full_asset_validation.py`
   - logs:
     - `logs/aistap_cross_condition_full_asset_validation_20260718.md`
     - `logs/aistap_cross_condition_full_asset_validation_20260718.json`

3. Patch `tgrs_tpsscs_final_package_20260716/README_PRE_SUBMISSION.md` to list the 20260718 cross-condition files and add a final technical-check bullet.

4. Copy updated/new files into the final package:

```powershell
$pkg='tgrs_tpsscs_final_package_20260716'
Copy-Item -LiteralPath 'results\aistap_full_asset\aistap_cross_condition_full_asset_summary_20260718.csv' -Destination (Join-Path $pkg 'source_data\aistap_full_asset') -Force
Copy-Item -LiteralPath 'logs\aistap_cross_condition_full_asset_validation_20260718.md' -Destination (Join-Path $pkg 'logs') -Force
Copy-Item -LiteralPath 'logs\aistap_cross_condition_full_asset_validation_20260718.json' -Destination (Join-Path $pkg 'logs') -Force
Copy-Item -LiteralPath 'scripts\evaluate_aistap_cross_condition_full_asset_validation.py' -Destination (Join-Path $pkg 'scripts') -Force
Copy-Item -LiteralPath 'scripts\evaluate_aistap_top_readiness.py' -Destination (Join-Path $pkg 'scripts') -Force
```

5. Run checks:

```powershell
py -m py_compile scripts\evaluate_aistap_top_readiness.py scripts\audit_aistap_claim_consistency.py scripts\audit_tgrs_submission_readiness.py
py scripts\evaluate_aistap_top_readiness.py --root . --date 20260718
py scripts\audit_aistap_claim_consistency.py --root . --date 20260718
py scripts\evaluate_aistap_top_readiness.py --root . --date 20260718
py scripts\audit_aistap_claim_consistency.py --root . --date 20260718
```

6. Recompile manuscript if any manuscript text is changed. If only scripts/package README are changed, manuscript recompilation is not strictly required, but final submission audit still expects the existing clean PDF/log.

If recompiling:

```powershell
Set-Location tgrs_tpsscs_final_package_20260716\manuscript
pdflatex -interaction=nonstopmode -halt-on-error tgrs_tpsscs_nofig_20260715.tex
pdflatex -interaction=nonstopmode -halt-on-error tgrs_tpsscs_nofig_20260715.tex
Select-String -Path 'tgrs_tpsscs_nofig_20260715.log' -Pattern 'undefined|Overfull|Float too large|Underfull \\vbox|Output written'
Remove-Item -LiteralPath 'tgrs_tpsscs_nofig_20260715.aux' -Force -ErrorAction SilentlyContinue
Set-Location ..\..
```

7. Run final package audit:

```powershell
py scripts\audit_tgrs_submission_readiness.py
```

8. Sync final logs/scripts to package:

```powershell
$pkg='tgrs_tpsscs_final_package_20260716'
Copy-Item -LiteralPath 'scripts\evaluate_aistap_top_readiness.py' -Destination (Join-Path $pkg 'scripts') -Force
Copy-Item -LiteralPath 'scripts\audit_aistap_claim_consistency.py' -Destination (Join-Path $pkg 'scripts') -Force
Copy-Item -LiteralPath 'scripts\audit_tgrs_submission_readiness.py' -Destination (Join-Path $pkg 'scripts') -Force
Copy-Item -LiteralPath 'logs\aistap_top_readiness_self_check_20260718.md' -Destination (Join-Path $pkg 'logs') -Force
Copy-Item -LiteralPath 'logs\aistap_top_readiness_self_check_20260718.json' -Destination (Join-Path $pkg 'logs') -Force
Copy-Item -LiteralPath 'logs\aistap_claim_consistency_audit_20260718.md' -Destination (Join-Path $pkg 'logs') -Force
Copy-Item -LiteralPath 'logs\aistap_claim_consistency_audit_20260718.json' -Destination (Join-Path $pkg 'logs') -Force
Copy-Item -LiteralPath 'logs\tgrs_submission_readiness_audit_20260717.md' -Destination (Join-Path $pkg 'logs') -Force
Copy-Item -LiteralPath 'logs\tgrs_submission_readiness_audit_20260717.json' -Destination (Join-Path $pkg 'logs') -Force
```

## Expected next outcome

After the pending integration:

- `cross_condition_holdout` should become `pass`.
- Remaining non-hard partial gates should likely be only:
  - `feature_ensemble_boundary`
  - `target_free_calibration_boundary`
- This strengthens the Q1 Top case by replacing weak public-sample subset holdout evidence with official full-asset cross-condition evidence.
