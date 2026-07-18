# AISTAP Full-Asset Frame-Level Robustness Audit

Date: 20260717

## Verdict

- Broad frame-level support: `true`
- Target-bearing items: `210`
- Pfa points: `7`
- Low-rank nonnegative item-Pfa pairs: `1470/1470`
- Low-rank loss item-Pfa pairs: `0`
- Raw nonnegative item-Pfa pairs: `1409/1470`
- Raw loss item-Pfa pairs: `61`
- Minimum combined win fraction vs raw: `0.890`
- Minimum combined nonnegative fraction vs `low_rank_residual_k30`: `1.000`

## Combined Distribution

| Comparator | Pfa | n | Win | Tie | Loss | Win fraction | Nonnegative | Median delta | q05 delta | Min delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `low_rank_residual_k30` | 1e-05 | 210 | 195 | 15 | 0 | 0.929 | 1.000 | 0.0715 | 0.0000 | 0.0000 |
| `low_rank_residual_k30` | 3e-05 | 210 | 191 | 19 | 0 | 0.910 | 1.000 | 0.0667 | 0.0000 | 0.0000 |
| `low_rank_residual_k30` | 1e-04 | 210 | 182 | 28 | 0 | 0.867 | 1.000 | 0.0513 | 0.0000 | 0.0000 |
| `low_rank_residual_k30` | 3e-04 | 210 | 154 | 56 | 0 | 0.733 | 1.000 | 0.0400 | 0.0000 | 0.0000 |
| `low_rank_residual_k30` | 1e-03 | 210 | 127 | 83 | 0 | 0.605 | 1.000 | 0.0310 | 0.0000 | 0.0000 |
| `low_rank_residual_k30` | 3e-03 | 210 | 109 | 101 | 0 | 0.519 | 1.000 | 0.0169 | 0.0000 | 0.0000 |
| `low_rank_residual_k30` | 1e-02 | 210 | 96 | 114 | 0 | 0.457 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `raw` | 1e-05 | 210 | 188 | 18 | 4 | 0.895 | 0.981 | 0.0885 | 0.0000 | -0.1200 |
| `raw` | 3e-05 | 210 | 187 | 9 | 14 | 0.890 | 0.933 | 0.1071 | -0.0427 | -0.1613 |
| `raw` | 1e-04 | 210 | 188 | 9 | 13 | 0.895 | 0.938 | 0.1606 | -0.0342 | -0.1000 |
| `raw` | 3e-04 | 210 | 200 | 5 | 5 | 0.952 | 0.976 | 0.2290 | 0.0455 | -0.1500 |
| `raw` | 1e-03 | 210 | 205 | 2 | 3 | 0.976 | 0.986 | 0.3248 | 0.0555 | -0.2000 |
| `raw` | 3e-03 | 210 | 198 | 9 | 3 | 0.943 | 0.986 | 0.3305 | 0.0000 | -0.1034 |
| `raw` | 1e-02 | 210 | 188 | 3 | 19 | 0.895 | 0.910 | 0.2045 | -0.0608 | -0.2143 |

## Boundary

- This audit asks whether the official full-asset mean Pd gains are broadly distributed over frames.
- The low-rank comparison has no negative item-Pfa pairs, but loose-Pfa gains include many ties where both detectors already detect the same target cells.
- The raw comparison has a high frame-level win fraction but not universal per-frame improvement; raw-favorable frames remain part of the boundary.
- This is a distributional support audit over the existing official full-asset result, not a new dataset.