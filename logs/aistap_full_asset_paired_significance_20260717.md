# AISTAP Full-Asset Paired Significance Audit

Date: 20260717

## Verdict

- Target-bearing items: `210`
- Pfa points: `7`
- Combined tests significant after BH-FDR: `true`
- Low-rank combined significant after BH-FDR: `true`
- Raw combined significant after BH-FDR: `true`
- Worst combined BH-FDR q-value: `2.945e-29`
- Minimum combined matched sign effect: `0.816`

## Combined Paired Tests

| Comparator | Pfa | n | Win | Tie | Loss | Sign effect | one-sided sign p | BH q | Significant |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `low_rank_residual_k30` | 1e-05 | 210 | 195 | 15 | 0 | 1.000 | 1.991e-59 | 8.364e-58 | `true` |
| `low_rank_residual_k30` | 3e-05 | 210 | 191 | 19 | 0 | 1.000 | 3.186e-58 | 6.691e-57 | `true` |
| `low_rank_residual_k30` | 0.0001 | 210 | 182 | 28 | 0 | 1.000 | 1.631e-55 | 1.713e-54 | `true` |
| `low_rank_residual_k30` | 0.0003 | 210 | 154 | 56 | 0 | 1.000 | 4.379e-47 | 2.299e-46 | `true` |
| `low_rank_residual_k30` | 0.001 | 210 | 127 | 83 | 0 | 1.000 | 5.877e-39 | 2.244e-38 | `true` |
| `low_rank_residual_k30` | 0.003 | 210 | 109 | 101 | 0 | 1.000 | 1.541e-33 | 4.978e-33 | `true` |
| `low_rank_residual_k30` | 0.01 | 210 | 96 | 114 | 0 | 1.000 | 1.262e-29 | 2.945e-29 | `true` |
| `raw` | 1e-05 | 210 | 188 | 18 | 4 | 0.958 | 8.929e-51 | 5.358e-50 | `true` |
| `raw` | 3e-05 | 210 | 187 | 9 | 14 | 0.861 | 4.261e-40 | 1.790e-39 | `true` |
| `raw` | 0.0001 | 210 | 188 | 9 | 13 | 0.871 | 3.154e-41 | 1.472e-40 | `true` |
| `raw` | 0.0003 | 210 | 200 | 5 | 5 | 0.951 | 5.728e-53 | 4.009e-52 | `true` |
| `raw` | 0.001 | 210 | 205 | 2 | 3 | 0.971 | 3.646e-57 | 5.105e-56 | `true` |
| `raw` | 0.003 | 210 | 198 | 9 | 3 | 0.970 | 4.212e-55 | 3.538e-54 | `true` |
| `raw` | 0.01 | 210 | 188 | 3 | 19 | 0.816 | 1.909e-36 | 6.683e-36 | `true` |

## Boundary

- This is a paired nonparametric audit over the frozen official full-asset frame-level rows.
- The one-sided exact sign test ignores ties and tests whether positive TP-SSCS-minus-comparator deltas outnumber negative deltas.
- BH-FDR is applied across all asset-level and combined comparator/Pfa tests in this audit.
- This strengthens statistical reporting for the official AISTAP-SIM result; it is not a new dataset or a universal per-frame dominance claim.
