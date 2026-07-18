# AISTAP Full-Asset Log-Pfa AUC Audit

Date: 20260717

## Verdict

- Target-bearing items: `210`
- Pfa points: `7`
- Combined AUC wins vs raw and low-rank: `true`
- Combined bootstrap CI lower bounds positive: `true`
- Combined BH-FDR significant sign tests: `true`
- Minimum combined AUC delta: `0.0553`
- Worst combined BH-FDR q-value: `1.464e-55`

## Combined Log-Pfa AUC

| Comparator | n | TP-SSCS AUC | Comparator AUC | Delta | CI95 low | CI95 high | Win/Tie/Loss | BH q |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `low_rank_residual_k30` | 210 | 0.5313 | 0.4760 | 0.0553 | 0.0491 | 0.0618 | 195/15/0 | 1.195e-58 |
| `raw` | 210 | 0.5313 | 0.3085 | 0.2228 | 0.2080 | 0.2378 | 206/0/4 | 1.464e-55 |

## Boundary

- AUC is the normalized trapezoidal integral of Pd over log10(Pfa) from 1e-5 to 1e-2.
- This audit summarizes the existing seven operating points; it does not add a new dataset.
- The paired bootstrap unit is the target-bearing frame, not pixels.
- The result supports whole-operating-surface robustness under the official Pfa grid, not performance outside the checked Pfa range.
