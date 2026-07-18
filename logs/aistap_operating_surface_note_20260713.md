# AISTAP Operating Surface Note

Date: 2026-07-13

## What this adds

This experiment measures a dense low-rank / CFAR operating surface on the public AISTAP-SIM sample, rather than a sparse rank sweep.

## Dense low-rank trend

| k | mean clutter attenuation dB | mean target loss dB |
|---|---:|---:|
| 1 | 1.424 | 0.925 |
| 2 | 2.590 | 1.911 |
| 3 | 3.479 | 2.480 |
| 5 | 4.535 | 3.715 |
| 8 | 5.303 | 5.939 |
| 10 | 5.691 | 7.471 |
| 15 | 6.470 | 10.236 |
| 20 | 7.210 | 13.906 |
| 30 | 8.423 | 19.525 |

## Dense CFAR frontier

The frontier uses a target-loss ceiling of 5 dB.

| subset | Pfa | best k | best Pd | target loss dB | clutter attenuation dB | raw Pd | delta Pd |
|---|---:|---:|---:|---:|---:|---:|---:|
| overall | 1e-05 | 2 | 0.070 | 1.911 | 2.590 | 0.039 | 0.031 |
| overall | 3e-05 | 1 | 0.124 | 0.925 | 1.424 | 0.085 | 0.039 |
| overall | 0.0001 | 5 | 0.217 | 3.715 | 4.535 | 0.132 | 0.085 |
| overall | 0.0003 | 2 | 0.372 | 1.911 | 2.590 | 0.217 | 0.155 |
| overall | 0.001 | 5 | 0.752 | 3.715 | 4.535 | 0.434 | 0.318 |
| overall | 0.003 | 5 | 0.868 | 3.715 | 4.535 | 0.496 | 0.372 |
| overall | 0.01 | 5 | 0.938 | 3.715 | 4.535 | 0.628 | 0.310 |
| simMed | 1e-05 | 1 | 0.047 | 0.925 | 2.197 | 0.039 | 0.008 |
| simMed | 3e-05 | 1 | 0.116 | 0.925 | 2.197 | 0.085 | 0.031 |
| simMed | 0.0001 | 1 | 0.186 | 0.925 | 2.197 | 0.132 | 0.054 |
| simMed | 0.0003 | 1 | 0.326 | 0.925 | 2.197 | 0.217 | 0.109 |
| simMed | 0.001 | 5 | 0.744 | 3.715 | 7.226 | 0.434 | 0.310 |
| simMed | 0.003 | 5 | 0.860 | 3.715 | 7.226 | 0.496 | 0.364 |
| simMed | 0.01 | 5 | 0.977 | 3.715 | 7.226 | 0.628 | 0.349 |
| simNoiseOnly | 1e-05 | 2 | 0.116 | 1.911 | 0.122 | 0.039 | 0.078 |
| simNoiseOnly | 3e-05 | 1 | 0.140 | 0.925 | 0.062 | 0.085 | 0.054 |
| simNoiseOnly | 0.0001 | 5 | 0.279 | 3.715 | 0.280 | 0.132 | 0.147 |
| simNoiseOnly | 0.0003 | 2 | 0.465 | 1.911 | 0.122 | 0.217 | 0.248 |
| simNoiseOnly | 0.001 | 1 | 0.767 | 0.925 | 0.062 | 0.434 | 0.333 |
| simNoiseOnly | 0.003 | 1 | 0.837 | 0.925 | 0.062 | 0.496 | 0.341 |
| simNoiseOnly | 0.01 | 1 | 0.884 | 0.925 | 0.062 | 0.628 | 0.256 |
| simWind | 1e-05 | 1 | 0.047 | 0.925 | 2.012 | 0.039 | 0.008 |
| simWind | 3e-05 | 1 | 0.116 | 0.925 | 2.012 | 0.085 | 0.031 |
| simWind | 0.0001 | 1 | 0.209 | 0.925 | 2.012 | 0.132 | 0.078 |
| simWind | 0.0003 | 1 | 0.326 | 0.925 | 2.012 | 0.217 | 0.109 |
| simWind | 0.001 | 5 | 0.744 | 3.715 | 6.098 | 0.434 | 0.310 |
| simWind | 0.003 | 5 | 0.907 | 3.715 | 6.098 | 0.496 | 0.411 |
| simWind | 0.01 | 5 | 0.977 | 3.715 | 6.098 | 0.628 | 0.349 |

## Interpretation

The dense surface keeps the same qualitative result as the sparse CFAR audit: stronger suppression increases clutter attenuation, but the best operating rank depends on the requested false-alarm rate.
The frontier table also makes the target-loss cost explicit, so the paper can treat k as an operating parameter rather than a universal optimum.

## Boundary

This is public-sample evidence only.
It strengthens the operating-policy argument, but it does not prove a finished detector or cross-dataset win.