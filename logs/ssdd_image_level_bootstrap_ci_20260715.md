# SSDD Image-Level Bootstrap CI

Date: 20260715

## Verdict

- Passed: `true`
- Official-test images: `231`
- Official-test annotations: `545`
- Unit-level robustness is now measured at both image and annotation levels.
- This supplements the aggregate SSDD result; it does not change the boundary that SSDD is supervised external trainable-gate adaptation rather than zero-shot transfer.

## CI Summary

| Level | Pfa | Comparator | n | Mean Delta Pd | 95% CI | Positive fraction | Negative fraction |
|---|---:|---|---:|---:|---:|---:|---:|
| `image` | 1e-05 | `raw` | 231 | 0.0000 | [0.0000, 0.0000] | 0.000 | 0.000 |
| `image` | 1e-05 | `lowrank` | 231 | 0.0436 | [0.0249, 0.0627] | 0.095 | 0.013 |
| `image` | 3e-05 | `raw` | 231 | 0.0000 | [0.0000, 0.0000] | 0.000 | 0.000 |
| `image` | 3e-05 | `lowrank` | 231 | 0.0739 | [0.0471, 0.1015] | 0.121 | 0.087 |
| `image` | 1e-04 | `raw` | 231 | 0.0000 | [0.0000, 0.0000] | 0.000 | 0.000 |
| `image` | 1e-04 | `lowrank` | 231 | 0.0840 | [0.0564, 0.1153] | 0.143 | 0.260 |
| `image` | 3e-04 | `raw` | 231 | 0.1222 | [0.0986, 0.1449] | 0.628 | 0.130 |
| `image` | 3e-04 | `lowrank` | 231 | 0.3577 | [0.3159, 0.4005] | 0.714 | 0.100 |
| `image` | 1e-03 | `raw` | 231 | 0.1596 | [0.1345, 0.1852] | 0.788 | 0.139 |
| `image` | 1e-03 | `lowrank` | 231 | 0.5597 | [0.5131, 0.6057] | 0.879 | 0.078 |
| `image` | 3e-03 | `raw` | 231 | 0.2448 | [0.2178, 0.2720] | 0.896 | 0.082 |
| `image` | 3e-03 | `lowrank` | 231 | 0.7361 | [0.6930, 0.7770] | 0.944 | 0.048 |
| `image` | 1e-02 | `raw` | 231 | 0.2182 | [0.1962, 0.2386] | 0.905 | 0.087 |
| `image` | 1e-02 | `lowrank` | 231 | 0.8246 | [0.7875, 0.8587] | 0.970 | 0.030 |
| `annotation` | 1e-05 | `raw` | 545 | 0.0000 | [0.0000, 0.0000] | 0.000 | 0.000 |
| `annotation` | 1e-05 | `lowrank` | 545 | 0.0271 | [0.0186, 0.0367] | 0.070 | 0.009 |
| `annotation` | 3e-05 | `raw` | 545 | 0.0000 | [0.0000, 0.0000] | 0.000 | 0.000 |
| `annotation` | 3e-05 | `lowrank` | 545 | 0.0489 | [0.0353, 0.0629] | 0.092 | 0.072 |
| `annotation` | 1e-04 | `raw` | 545 | 0.0000 | [0.0000, 0.0000] | 0.000 | 0.000 |
| `annotation` | 1e-04 | `lowrank` | 545 | 0.0572 | [0.0436, 0.0726] | 0.108 | 0.163 |
| `annotation` | 3e-04 | `raw` | 545 | 0.0797 | [0.0664, 0.0937] | 0.466 | 0.094 |
| `annotation` | 3e-04 | `lowrank` | 545 | 0.2459 | [0.2208, 0.2710] | 0.536 | 0.108 |
| `annotation` | 1e-03 | `raw` | 545 | 0.0820 | [0.0663, 0.0979] | 0.585 | 0.182 |
| `annotation` | 1e-03 | `lowrank` | 545 | 0.4104 | [0.3794, 0.4408] | 0.712 | 0.110 |
| `annotation` | 3e-03 | `raw` | 545 | 0.1680 | [0.1485, 0.1882] | 0.793 | 0.128 |
| `annotation` | 3e-03 | `lowrank` | 545 | 0.5911 | [0.5586, 0.6245] | 0.848 | 0.068 |
| `annotation` | 1e-02 | `raw` | 545 | 0.1885 | [0.1720, 0.2045] | 0.877 | 0.108 |
| `annotation` | 1e-02 | `lowrank` | 545 | 0.6987 | [0.6671, 0.7290] | 0.945 | 0.037 |

## Interpretation

- A positive image-level CI against raw at higher Pfa points supports broad SSDD gains rather than only aggregate pixel-pool gains.
- Low-Pfa raw fallback points are expected to tie raw by design; they should be described as no-regression operating points.
- Annotation-level rows measure target-region robustness across ship instances; they are supplementary because overlapping or polygon-level mask details can affect exact per-annotation counts.

## Boundary

- Thresholds are calibrated globally on official-test background pixels, matching the aggregate SSDD protocol.
- Image-level and annotation-level statistics reuse those fixed thresholds and therefore test distribution of gains, not a separately tuned per-image detector.