# AISTAP Cross-Condition Full-Asset Validation

Date: 20260718

## Verdict

- Passed: `true`
- Assets: `2`
- Low-rank comparator: `low_rank_residual_k30`
- Minimum target-bearing items per asset: `100`

## Comparisons

| Asset | Pfa | TP-SSCS Pd | Raw Pd | Low-rank Pd | Empirical Pfa | Beats raw | Beats low-rank |
|---|---:|---:|---:|---:|---:|---:|---:|
| simMed_test.mat | 1e-05 | 0.1845 | 0.0783 | 0.0989 | 0 | `true` | `true` |
| simMed_test.mat | 3e-05 | 0.2329 | 0.1149 | 0.1504 | 1.52675e-05 | `true` | `true` |
| simMed_test.mat | 1e-04 | 0.3631 | 0.1956 | 0.2944 | 9.16052e-05 | `true` | `true` |
| simMed_test.mat | 3e-04 | 0.5155 | 0.2686 | 0.4575 | 0.000290083 | `true` | `true` |
| simMed_test.mat | 1e-03 | 0.6958 | 0.3569 | 0.6488 | 0.00099239 | `true` | `true` |
| simMed_test.mat | 3e-03 | 0.8139 | 0.4673 | 0.7764 | 0.00299244 | `true` | `true` |
| simMed_test.mat | 1e-02 | 0.8692 | 0.6340 | 0.8383 | 0.00999282 | `true` | `true` |
| simWind_test.mat | 1e-05 | 0.1845 | 0.0816 | 0.1041 | 0 | `true` | `true` |
| simWind_test.mat | 3e-05 | 0.2387 | 0.1271 | 0.1638 | 1.52675e-05 | `true` | `true` |
| simWind_test.mat | 1e-04 | 0.3732 | 0.2143 | 0.3108 | 9.16052e-05 | `true` | `true` |
| simWind_test.mat | 3e-04 | 0.5368 | 0.2932 | 0.4869 | 0.000290083 | `true` | `true` |
| simWind_test.mat | 1e-03 | 0.7100 | 0.3972 | 0.6697 | 0.00099239 | `true` | `true` |
| simWind_test.mat | 3e-03 | 0.8122 | 0.5056 | 0.7792 | 0.00299244 | `true` | `true` |
| simWind_test.mat | 1e-02 | 0.8663 | 0.6761 | 0.8393 | 0.00999282 | `true` | `true` |

## Failures

- None.

## Boundary

- This is AISTAP-SIM official cross-condition evidence.
- It validates the same saved state and detector policy across official `simMed_test` and `simWind_test` full-test conditions.
- It is not independent non-AISTAP external-dataset validation.