# AISTAP Label-Cost Pareto Audit

Date: 20260717

## Verdict

- Compact TP-SSCS AUC: `0.5313` with `0` official full-asset positive target labels.
- Compact TP-SSCS runtime: `133.66` ms/frame.
- Raw/residual HGB runtime: `608.99` ms/frame (`4.56x` compact).
- Low-label HGB budgets dominated by compact TP-SSCS in AUC, labels, and runtime with positive AUC bootstrap CI: `['1', '2', '4', '8', '16']`.
- First positive-pixel budget where low-label HGB exceeds compact AUC: `64`.
- Strong full-label raw/residual HGB boundary AUC: `0.7156`.

## Budget AUC

| HGB positive-pixel budget | Compact AUC | HGB AUC | Delta | CI95 low | CI95 high | Positive fraction |
|---:|---:|---:|---:|---:|---:|---:|
| `1` | 0.5313 | 0.1380 | 0.3933 | 0.3851 | 0.4015 | 1.000 |
| `2` | 0.5313 | 0.1959 | 0.3354 | 0.3274 | 0.3435 | 1.000 |
| `4` | 0.5313 | 0.3063 | 0.2250 | 0.2165 | 0.2335 | 0.983 |
| `8` | 0.5313 | 0.3469 | 0.1845 | 0.1748 | 0.1939 | 0.922 |
| `16` | 0.5313 | 0.4567 | 0.0746 | 0.0683 | 0.0808 | 0.832 |
| `32` | 0.5313 | 0.5301 | 0.0012 | -0.0056 | 0.0078 | 0.502 |
| `64` | 0.5313 | 0.5834 | -0.0521 | -0.0594 | -0.0449 | 0.273 |
| `128` | 0.5313 | 0.6518 | -0.1205 | -0.1282 | -0.1126 | 0.105 |
| `256` | 0.5313 | 0.6750 | -0.1437 | -0.1515 | -0.1359 | 0.059 |
| `512` | 0.5313 | 0.6924 | -0.1611 | -0.1696 | -0.1526 | 0.060 |
| `all` | 0.5313 | 0.7271 | -0.1958 | -0.2045 | -0.1873 | 0.010 |

## Pareto Points

| Method | Positive target pixels | Runtime ms/frame | AUC | Dominated | Dominated by |
|---|---:|---:|---:|---:|---|
| `compact_tpsscs` | 0 | 133.66 | 0.5313 | false | `` |
| `low_label_raw_residual_hgb_budget_64` | 64 | 608.99 | 0.5834 | false | `` |
| `low_label_raw_residual_hgb_budget_128` | 128 | 608.99 | 0.6518 | false | `` |
| `low_label_raw_residual_hgb_budget_256` | 256 | 608.99 | 0.6750 | false | `` |
| `low_label_raw_residual_hgb_budget_512` | 512 | 608.99 | 0.6924 | false | `` |
| `low_label_raw_residual_hgb_budget_all` | 3943 | 608.99 | 0.7271 | false | `` |
| `low_label_raw_residual_hgb_budget_1` | 1 | 608.99 | 0.1380 | true | `compact_tpsscs` |
| `low_label_raw_residual_hgb_budget_2` | 2 | 608.99 | 0.1959 | true | `compact_tpsscs` |
| `low_label_raw_residual_hgb_budget_4` | 4 | 608.99 | 0.3063 | true | `compact_tpsscs` |
| `low_label_raw_residual_hgb_budget_8` | 8 | 608.99 | 0.3469 | true | `compact_tpsscs` |
| `low_label_raw_residual_hgb_budget_16` | 16 | 608.99 | 0.4567 | true | `compact_tpsscs` |
| `low_label_raw_residual_hgb_budget_32` | 32 | 608.99 | 0.5301 | true | `compact_tpsscs` |
| `raw_residual_hgb_full_boundary` | 3943 | 608.99 | 0.7156 | true | `low_label_raw_residual_hgb_budget_all` |

## Boundary

- This audit combines already-frozen low-label HGB, full HGB-boundary, and runtime outputs; it does not retrain a new detector.
- Runtime is the local CPU profile already reported for compact TP-SSCS and the checked raw/residual HGB inference stack; it is not hardware-independent.
- The Pareto claim is scoped to official AISTAP-SIM full assets, the checked Pfa grid, positive-target-pixel supervision, and the measured local implementation.
- Full-label HGB remains the supervised in-domain upper boundary; this audit strengthens the low-target-label/low-cost positioning, not universal superiority.
