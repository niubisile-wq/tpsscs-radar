# AISTAP Full-Asset LOSO Low-Label HGB Label-Efficiency Audit

Date: 20260717

## Verdict

- Compact zero-target-label method: `tpsscs_finished_detector`
- Low-label learned method: `loso_low_label_raw_residual_hgb`
- Held-out target-bearing items: `210`
- Seeds: `20260717, 20260718, 20260719`
- Label budgets: `1, 2, 4, 8, 16, 32, 64, all` positive source-domain target frames
- Compact all-Pfa win budgets: `none`
- Compact all-Pfa positive-CI budgets: `none`
- First budget where HGB catches or exceeds compact at any Pfa: `1`
- All methods Pfa calibrated: `true`

## Protocol

- Cache the same raw/residual feature cube used by the full LOSO HGB boundary audit for every target-bearing frame in each official full asset.
- For each train/test direction, randomly select a fixed number of source-domain target-bearing frames and train a raw/residual HGB only from those labeled frames.
- Test on every target-bearing frame in the opposite official full asset; repeat for each seed and label budget.
- Compare the low-label HGB to compact TP-SSCS, which uses no target labels from either official full asset at this stage.

## Budget Summary

| Label budget | Compact wins / Pfa | Min compact-HGB delta | Mean compact-HGB delta | All CI lows positive | Mean item win fraction |
|---:|---:|---:|---:|---:|---:|
| 1 | 5/7 | -0.0269 | 0.0369 | false | 0.522 |
| 2 | 1/7 | -0.0795 | -0.0445 | false | 0.313 |
| 4 | 0/7 | -0.1519 | -0.0893 | false | 0.213 |
| 8 | 0/7 | -0.2216 | -0.1330 | false | 0.140 |
| 16 | 0/7 | -0.2582 | -0.1504 | false | 0.101 |
| 32 | 0/7 | -0.2750 | -0.1674 | false | 0.086 |
| 64 | 0/7 | -0.2854 | -0.1752 | false | 0.073 |
| all | 0/7 | -0.2865 | -0.1773 | false | 0.068 |

## Combined Operating Points

| Budget | Pfa | Compact Pd | Low-label HGB Pd | Compact-HGB delta | Compact item win fraction |
|---:|---:|---:|---:|---:|---:|
| 1 | 1e-05 | 0.1845 | 0.0784 | 0.1061 | 0.790 |
| 1 | 3e-05 | 0.2358 | 0.1285 | 0.1074 | 0.724 |
| 1 | 1e-04 | 0.3682 | 0.3179 | 0.0503 | 0.560 |
| 1 | 3e-04 | 0.5261 | 0.5279 | -0.0018 | 0.417 |
| 1 | 1e-03 | 0.7029 | 0.6901 | 0.0128 | 0.429 |
| 1 | 3e-03 | 0.8130 | 0.8024 | 0.0107 | 0.425 |
| 1 | 1e-02 | 0.8678 | 0.8947 | -0.0269 | 0.311 |
| 2 | 1e-05 | 0.1845 | 0.1707 | 0.0139 | 0.552 |
| 2 | 3e-05 | 0.2358 | 0.2439 | -0.0081 | 0.492 |
| 2 | 1e-04 | 0.3682 | 0.4269 | -0.0587 | 0.327 |
| 2 | 3e-04 | 0.5261 | 0.6057 | -0.0795 | 0.227 |
| 2 | 1e-03 | 0.7029 | 0.7737 | -0.0709 | 0.181 |
| 2 | 3e-03 | 0.8130 | 0.8689 | -0.0559 | 0.238 |
| 2 | 1e-02 | 0.8678 | 0.9199 | -0.0521 | 0.176 |
| 4 | 1e-05 | 0.1845 | 0.2245 | -0.0400 | 0.422 |
| 4 | 3e-05 | 0.2358 | 0.3224 | -0.0866 | 0.310 |
| 4 | 1e-04 | 0.3682 | 0.5201 | -0.1519 | 0.163 |
| 4 | 3e-04 | 0.5261 | 0.6674 | -0.1412 | 0.157 |
| 4 | 1e-03 | 0.7029 | 0.7911 | -0.0883 | 0.154 |
| 4 | 3e-03 | 0.8130 | 0.8678 | -0.0547 | 0.176 |
| 4 | 1e-02 | 0.8678 | 0.9298 | -0.0621 | 0.108 |
| 8 | 1e-05 | 0.1845 | 0.2801 | -0.0956 | 0.313 |
| 8 | 3e-05 | 0.2358 | 0.3846 | -0.1488 | 0.187 |
| 8 | 1e-04 | 0.3682 | 0.5898 | -0.2216 | 0.071 |
| 8 | 3e-04 | 0.5261 | 0.7196 | -0.1935 | 0.078 |
| 8 | 1e-03 | 0.7029 | 0.8311 | -0.1282 | 0.083 |
| 8 | 3e-03 | 0.8130 | 0.8918 | -0.0788 | 0.137 |
| 8 | 1e-02 | 0.8678 | 0.9325 | -0.0647 | 0.114 |
| 16 | 1e-05 | 0.1845 | 0.2815 | -0.0969 | 0.290 |
| 16 | 3e-05 | 0.2358 | 0.3998 | -0.1640 | 0.140 |
| 16 | 1e-04 | 0.3682 | 0.6263 | -0.2582 | 0.025 |
| 16 | 3e-04 | 0.5261 | 0.7565 | -0.2303 | 0.040 |
| 16 | 1e-03 | 0.7029 | 0.8474 | -0.1445 | 0.035 |
| 16 | 3e-03 | 0.8130 | 0.9001 | -0.0871 | 0.092 |
| 16 | 1e-02 | 0.8678 | 0.9394 | -0.0716 | 0.084 |
| 32 | 1e-05 | 0.1845 | 0.3225 | -0.1379 | 0.237 |
| 32 | 3e-05 | 0.2358 | 0.4292 | -0.1934 | 0.127 |
| 32 | 1e-04 | 0.3682 | 0.6432 | -0.2750 | 0.030 |
| 32 | 3e-04 | 0.5261 | 0.7683 | -0.2421 | 0.029 |
| 32 | 1e-03 | 0.7029 | 0.8529 | -0.1500 | 0.041 |
| 32 | 3e-03 | 0.8130 | 0.9074 | -0.0943 | 0.079 |
| 32 | 1e-02 | 0.8678 | 0.9464 | -0.0787 | 0.059 |
| 64 | 1e-05 | 0.1845 | 0.3127 | -0.1282 | 0.260 |
| 64 | 3e-05 | 0.2358 | 0.4362 | -0.2004 | 0.098 |
| 64 | 1e-04 | 0.3682 | 0.6536 | -0.2854 | 0.024 |
| 64 | 3e-04 | 0.5261 | 0.7816 | -0.2555 | 0.013 |
| 64 | 1e-03 | 0.7029 | 0.8653 | -0.1625 | 0.025 |
| 64 | 3e-03 | 0.8130 | 0.9186 | -0.1056 | 0.048 |
| 64 | 1e-02 | 0.8678 | 0.9567 | -0.0889 | 0.040 |
| all | 1e-05 | 0.1845 | 0.3210 | -0.1365 | 0.246 |
| all | 3e-05 | 0.2358 | 0.4299 | -0.1940 | 0.113 |
| all | 1e-04 | 0.3682 | 0.6546 | -0.2865 | 0.016 |
| all | 3e-04 | 0.5261 | 0.7803 | -0.2542 | 0.016 |
| all | 1e-03 | 0.7029 | 0.8698 | -0.1670 | 0.017 |
| all | 3e-03 | 0.8130 | 0.9225 | -0.1095 | 0.044 |
| all | 1e-02 | 0.8678 | 0.9614 | -0.0936 | 0.024 |

## Bootstrap CI

| Budget | Pfa | n pairs | Mean compact-HGB delta | 95% CI | Positive fraction |
|---:|---:|---:|---:|---:|---:|
| 1 | 1e-05 | 630 | 0.1061 | [0.0953, 0.1160] | 0.790 |
| 1 | 3e-05 | 630 | 0.1074 | [0.0952, 0.1196] | 0.724 |
| 1 | 1e-04 | 630 | 0.0503 | [0.0350, 0.0654] | 0.560 |
| 1 | 3e-04 | 630 | -0.0018 | [-0.0185, 0.0149] | 0.417 |
| 1 | 1e-03 | 630 | 0.0128 | [-0.0027, 0.0291] | 0.429 |
| 1 | 3e-03 | 630 | 0.0107 | [-0.0025, 0.0236] | 0.425 |
| 1 | 1e-02 | 630 | -0.0269 | [-0.0352, -0.0188] | 0.311 |
| 2 | 1e-05 | 630 | 0.0139 | [0.0029, 0.0246] | 0.552 |
| 2 | 3e-05 | 630 | -0.0081 | [-0.0196, 0.0038] | 0.492 |
| 2 | 1e-04 | 630 | -0.0587 | [-0.0696, -0.0475] | 0.327 |
| 2 | 3e-04 | 630 | -0.0795 | [-0.0897, -0.0698] | 0.227 |
| 2 | 1e-03 | 630 | -0.0709 | [-0.0800, -0.0625] | 0.181 |
| 2 | 3e-03 | 630 | -0.0559 | [-0.0640, -0.0477] | 0.238 |
| 2 | 1e-02 | 630 | -0.0521 | [-0.0592, -0.0451] | 0.176 |
| 4 | 1e-05 | 630 | -0.0400 | [-0.0543, -0.0260] | 0.422 |
| 4 | 3e-05 | 630 | -0.0866 | [-0.1012, -0.0732] | 0.310 |
| 4 | 1e-04 | 630 | -0.1519 | [-0.1665, -0.1367] | 0.163 |
| 4 | 3e-04 | 630 | -0.1412 | [-0.1556, -0.1265] | 0.157 |
| 4 | 1e-03 | 630 | -0.0883 | [-0.1013, -0.0755] | 0.154 |
| 4 | 3e-03 | 630 | -0.0547 | [-0.0655, -0.0438] | 0.176 |
| 4 | 1e-02 | 630 | -0.0621 | [-0.0688, -0.0555] | 0.108 |
| 8 | 1e-05 | 630 | -0.0956 | [-0.1095, -0.0818] | 0.313 |
| 8 | 3e-05 | 630 | -0.1488 | [-0.1622, -0.1345] | 0.187 |
| 8 | 1e-04 | 630 | -0.2216 | [-0.2342, -0.2085] | 0.071 |
| 8 | 3e-04 | 630 | -0.1935 | [-0.2061, -0.1809] | 0.078 |
| 8 | 1e-03 | 630 | -0.1282 | [-0.1376, -0.1187] | 0.083 |
| 8 | 3e-03 | 630 | -0.0788 | [-0.0868, -0.0709] | 0.137 |
| 8 | 1e-02 | 630 | -0.0647 | [-0.0721, -0.0578] | 0.114 |
| 16 | 1e-05 | 630 | -0.0969 | [-0.1104, -0.0837] | 0.290 |
| 16 | 3e-05 | 630 | -0.1640 | [-0.1776, -0.1504] | 0.140 |
| 16 | 1e-04 | 630 | -0.2582 | [-0.2713, -0.2455] | 0.025 |
| 16 | 3e-04 | 630 | -0.2303 | [-0.2426, -0.2184] | 0.040 |
| 16 | 1e-03 | 630 | -0.1445 | [-0.1536, -0.1361] | 0.035 |
| 16 | 3e-03 | 630 | -0.0871 | [-0.0953, -0.0800] | 0.092 |
| 16 | 1e-02 | 630 | -0.0716 | [-0.0788, -0.0647] | 0.084 |
| 32 | 1e-05 | 630 | -0.1379 | [-0.1527, -0.1227] | 0.237 |
| 32 | 3e-05 | 630 | -0.1934 | [-0.2083, -0.1792] | 0.127 |
| 32 | 1e-04 | 630 | -0.2750 | [-0.2885, -0.2612] | 0.030 |
| 32 | 3e-04 | 630 | -0.2421 | [-0.2539, -0.2307] | 0.029 |
| 32 | 1e-03 | 630 | -0.1500 | [-0.1590, -0.1412] | 0.041 |
| 32 | 3e-03 | 630 | -0.0943 | [-0.1026, -0.0872] | 0.079 |
| 32 | 1e-02 | 630 | -0.0787 | [-0.0861, -0.0717] | 0.059 |
| 64 | 1e-05 | 630 | -0.1282 | [-0.1423, -0.1132] | 0.260 |
| 64 | 3e-05 | 630 | -0.2004 | [-0.2144, -0.1873] | 0.098 |
| 64 | 1e-04 | 630 | -0.2854 | [-0.2981, -0.2724] | 0.024 |
| 64 | 3e-04 | 630 | -0.2555 | [-0.2678, -0.2438] | 0.013 |
| 64 | 1e-03 | 630 | -0.1625 | [-0.1712, -0.1535] | 0.025 |
| 64 | 3e-03 | 630 | -0.1056 | [-0.1137, -0.0979] | 0.048 |
| 64 | 1e-02 | 630 | -0.0889 | [-0.0963, -0.0821] | 0.040 |
| all | 1e-05 | 630 | -0.1365 | [-0.1506, -0.1211] | 0.246 |
| all | 3e-05 | 630 | -0.1940 | [-0.2084, -0.1796] | 0.113 |
| all | 1e-04 | 630 | -0.2865 | [-0.2990, -0.2743] | 0.016 |
| all | 3e-04 | 630 | -0.2542 | [-0.2661, -0.2429] | 0.016 |
| all | 1e-03 | 630 | -0.1670 | [-0.1760, -0.1580] | 0.017 |
| all | 3e-03 | 630 | -0.1095 | [-0.1178, -0.1018] | 0.044 |
| all | 1e-02 | 630 | -0.0936 | [-0.1008, -0.0866] | 0.024 |

## Training Sample Audit

| Seed | Budget | Train asset | Test asset | Selected positive frames | Positive pixels | Background pixels | Training samples |
|---:|---:|---|---|---:|---:|---:|---:|
| 20260717 | 1 | `simMed_test.mat` | `simWind_test.mat` | 1 | 26 | 4096 | 4122 |
| 20260717 | 1 | `simWind_test.mat` | `simMed_test.mat` | 1 | 61 | 4096 | 4157 |
| 20260717 | 2 | `simMed_test.mat` | `simWind_test.mat` | 2 | 110 | 8192 | 8302 |
| 20260717 | 2 | `simWind_test.mat` | `simMed_test.mat` | 2 | 67 | 8192 | 8259 |
| 20260717 | 4 | `simMed_test.mat` | `simWind_test.mat` | 4 | 162 | 16384 | 16546 |
| 20260717 | 4 | `simWind_test.mat` | `simMed_test.mat` | 4 | 183 | 16384 | 16567 |
| 20260717 | 8 | `simMed_test.mat` | `simWind_test.mat` | 8 | 316 | 32768 | 33084 |
| 20260717 | 8 | `simWind_test.mat` | `simMed_test.mat` | 8 | 311 | 32768 | 33079 |
| 20260717 | 16 | `simMed_test.mat` | `simWind_test.mat` | 16 | 523 | 65536 | 66059 |
| 20260717 | 16 | `simWind_test.mat` | `simMed_test.mat` | 16 | 603 | 65536 | 66139 |
| 20260717 | 32 | `simMed_test.mat` | `simWind_test.mat` | 32 | 1181 | 131072 | 132253 |
| 20260717 | 32 | `simWind_test.mat` | `simMed_test.mat` | 32 | 1142 | 131072 | 132214 |
| 20260717 | 64 | `simMed_test.mat` | `simWind_test.mat` | 64 | 2442 | 262144 | 264586 |
| 20260717 | 64 | `simWind_test.mat` | `simMed_test.mat` | 64 | 2310 | 262144 | 264454 |
| 20260717 | all | `simMed_test.mat` | `simWind_test.mat` | 105 | 3943 | 430080 | 434023 |
| 20260717 | all | `simWind_test.mat` | `simMed_test.mat` | 105 | 3943 | 430080 | 434023 |
| 20260718 | 1 | `simMed_test.mat` | `simWind_test.mat` | 1 | 44 | 4096 | 4140 |
| 20260718 | 1 | `simWind_test.mat` | `simMed_test.mat` | 1 | 25 | 4096 | 4121 |
| 20260718 | 2 | `simMed_test.mat` | `simWind_test.mat` | 2 | 88 | 8192 | 8280 |
| 20260718 | 2 | `simWind_test.mat` | `simMed_test.mat` | 2 | 89 | 8192 | 8281 |
| 20260718 | 4 | `simMed_test.mat` | `simWind_test.mat` | 4 | 159 | 16384 | 16543 |
| 20260718 | 4 | `simWind_test.mat` | `simMed_test.mat` | 4 | 132 | 16384 | 16516 |
| 20260718 | 8 | `simMed_test.mat` | `simWind_test.mat` | 8 | 234 | 32768 | 33002 |
| 20260718 | 8 | `simWind_test.mat` | `simMed_test.mat` | 8 | 322 | 32768 | 33090 |
| 20260718 | 16 | `simMed_test.mat` | `simWind_test.mat` | 16 | 536 | 65536 | 66072 |
| 20260718 | 16 | `simWind_test.mat` | `simMed_test.mat` | 16 | 682 | 65536 | 66218 |
| 20260718 | 32 | `simMed_test.mat` | `simWind_test.mat` | 32 | 1128 | 131072 | 132200 |
| 20260718 | 32 | `simWind_test.mat` | `simMed_test.mat` | 32 | 1258 | 131072 | 132330 |
| 20260718 | 64 | `simMed_test.mat` | `simWind_test.mat` | 64 | 2385 | 262144 | 264529 |
| 20260718 | 64 | `simWind_test.mat` | `simMed_test.mat` | 64 | 2376 | 262144 | 264520 |
| 20260718 | all | `simMed_test.mat` | `simWind_test.mat` | 105 | 3943 | 430080 | 434023 |
| 20260718 | all | `simWind_test.mat` | `simMed_test.mat` | 105 | 3943 | 430080 | 434023 |
| 20260719 | 1 | `simMed_test.mat` | `simWind_test.mat` | 1 | 47 | 4096 | 4143 |
| 20260719 | 1 | `simWind_test.mat` | `simMed_test.mat` | 1 | 26 | 4096 | 4122 |
| 20260719 | 2 | `simMed_test.mat` | `simWind_test.mat` | 2 | 70 | 8192 | 8262 |
| 20260719 | 2 | `simWind_test.mat` | `simMed_test.mat` | 2 | 42 | 8192 | 8234 |
| 20260719 | 4 | `simMed_test.mat` | `simWind_test.mat` | 4 | 184 | 16384 | 16568 |
| 20260719 | 4 | `simWind_test.mat` | `simMed_test.mat` | 4 | 159 | 16384 | 16543 |
| 20260719 | 8 | `simMed_test.mat` | `simWind_test.mat` | 8 | 253 | 32768 | 33021 |
| 20260719 | 8 | `simWind_test.mat` | `simMed_test.mat` | 8 | 280 | 32768 | 33048 |
| 20260719 | 16 | `simMed_test.mat` | `simWind_test.mat` | 16 | 588 | 65536 | 66124 |
| 20260719 | 16 | `simWind_test.mat` | `simMed_test.mat` | 16 | 619 | 65536 | 66155 |
| 20260719 | 32 | `simMed_test.mat` | `simWind_test.mat` | 32 | 1129 | 131072 | 132201 |
| 20260719 | 32 | `simWind_test.mat` | `simMed_test.mat` | 32 | 1243 | 131072 | 132315 |
| 20260719 | 64 | `simMed_test.mat` | `simWind_test.mat` | 64 | 2306 | 262144 | 264450 |
| 20260719 | 64 | `simWind_test.mat` | `simMed_test.mat` | 64 | 2313 | 262144 | 264457 |
| 20260719 | all | `simMed_test.mat` | `simWind_test.mat` | 105 | 3943 | 430080 | 434023 |
| 20260719 | all | `simWind_test.mat` | `simMed_test.mat` | 105 | 3943 | 430080 | 434023 |

## Interpretation Boundary

- A compact win at small budgets supports a label-efficiency claim, not a universal superiority claim over fully supervised learned detectors.
- If the HGB catches up at larger budgets, that should be reported as a supervised-data boundary rather than hidden.
- This audit directly complements the full-label HGB boundary audit by separating zero-label structural robustness from supervised feature-ensemble capacity.
