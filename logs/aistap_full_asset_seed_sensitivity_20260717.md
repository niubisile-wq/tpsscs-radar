# AISTAP Full-Asset Seed Sensitivity

Date: 20260717

## Verdict

- Passed: `true`
- Seeds: `7, 11, 23`
- Assets: `simMed_test.mat, simWind_test.mat`
- Combined target-bearing items per seed: `210`
- Combined wins vs raw: `21/21`
- Combined wins vs low-rank: `21/21`
- Asset-level wins vs raw: `42/42`
- Asset-level wins vs low-rank: `42/42`
- Worst combined delta vs raw: `0.1033`
- Worst combined delta vs low-rank: `0.0252`
- Maximum cross-seed target-Pd range over Pfa points: `0.0079`

## Per-Seed Summary

| Seed | Combined wins vs raw | Combined wins vs low-rank | Asset-level wins vs raw | Asset-level wins vs low-rank | Min delta vs raw | Min delta vs low-rank | Pfa calibrated |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 7/7 | 7/7 | 14/14 | 14/14 | 0.1046 | 0.0290 | `true` |
| 11 | 7/7 | 7/7 | 14/14 | 14/14 | 0.1033 | 0.0329 | `true` |
| 23 | 7/7 | 7/7 | 14/14 | 14/14 | 0.1079 | 0.0252 | `true` |

## Cross-Seed Stability By Pfa

| Pfa | Target Pd min | Target Pd max | Range | Min delta vs raw | Min delta vs low-rank |
|---:|---:|---:|---:|---:|---:|
| 1e-05 | 0.1832 | 0.1879 | 0.0047 | 0.1033 | 0.0817 |
| 3e-05 | 0.2358 | 0.2387 | 0.0029 | 0.1148 | 0.0788 |
| 1e-04 | 0.3682 | 0.3724 | 0.0042 | 0.1633 | 0.0656 |
| 3e-04 | 0.5259 | 0.5312 | 0.0053 | 0.2450 | 0.0537 |
| 1e-03 | 0.7010 | 0.7083 | 0.0073 | 0.3239 | 0.0418 |
| 3e-03 | 0.8104 | 0.8183 | 0.0079 | 0.3240 | 0.0327 |
| 1e-02 | 0.8640 | 0.8717 | 0.0077 | 0.2090 | 0.0252 |

## Interpretation

- The final `rank=30`, `hidden=16`, `steps=150`, `lr=0.02` full-asset result is not a single-seed artifact under this three-seed check.
- All checked seeds preserve the full official AISTAP-SIM combined gate against both raw and rank-matched low-rank residual comparators.
- The evidence remains an in-domain official AISTAP-SIM full-asset sensitivity check; it should be paired with IPIX and SSDD for external-support claims.

## Boundary

- This does not prove universal seed invariance over all possible initializations.
- This does not change the IPIX zero-shot boundary or the SSDD supervised-adaptation boundary.
- It does strengthen the finished-detector protocol by showing that nearby training seeds keep the same official full-asset win pattern.