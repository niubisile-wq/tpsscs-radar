# AISTAP Conservative Target-Free Calibration Sweep

Date: 20260717_gatewide

## Verdict

- Target-bearing items: `210`.
- Target-free support per asset: `{'simMed_test.mat': 23, 'simWind_test.mat': 23}` frames.
- Residual safety factors: `[1000.0]`.
- Gate margin scales: `[256.0, 1024.0, 4096.0, 16384.0, 65536.0]`.
- Strict passing configurations: `0`.
- No strict configuration satisfied both empirical-Pfa calibration and all-Pfa TP-SSCS wins.

## Passing Configurations

| Mode | Residual safety | Gate margin | Min delta raw | Min delta low-rank | Max Pfa ratio |
|---|---:|---:|---:|---:|---:|
| none | | | | | |

## Boundary

- This is a target-free calibration sensitivity sweep, not a new model-training result.
- The sweep uses target-bearing backgrounds to audit empirical Pfa after applying target-free thresholds; selected conservative settings should therefore be described as diagnostic unless pre-registered on a future collection.
- The result addresses whether a conservative target-free safety margin can recover empirical-Pfa control on the current official assets; it does not prove deployment-ready fixed calibration under arbitrary background shift.
- The paired bootstrap unit is the target-bearing frame.
