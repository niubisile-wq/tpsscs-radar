# AISTAP Experimental Quality Assessment

Date: 20260717

## Verdict

- Experimental tier: `Q1_candidate / Q1_top_experiment_candidate`.
- Submission interpretation: the experiment stack is now strong enough to support a bounded CAS Q1 and a credible Q1-top submission attempt if the manuscript is framed as compact target-preserving detector policy plus bounded supervised feature evidence, not as universal learned-detector superiority.
- Main reason: the paper now has an official in-domain full-asset gate, uncertainty reporting, two independent external radar-family validation layers, finished-detector full-asset seed-sensitivity, stronger classical-baseline audits, a leave-one-condition-out logistic learned-baseline audit, an explicit strong supervised HGB boundary, low-label and label-cost Pareto evidence, frame-level and paired-significance audits, whole-operating-surface log-Pfa AUC and component-attribution audits, and a bounded runtime/complexity profile.
- Main boundary: the IPIX zero-shot result is negative and SSDD is a supervised adaptation result rather than a zero-shot transfer result, so the paper should still avoid unconditional cross-dataset superiority claims.

## Evidence Supporting The Q1 Candidate Label

- Official AISTAP-SIM full assets: `simMed_test.mat` and `simWind_test.mat`, `210` combined target-bearing items, `14/14` asset-level wins and `7/7` combined Pfa wins against both raw and rank-matched low-rank residual comparators.
- Full-asset uncertainty reporting: positive bootstrap confidence intervals for the combined AISTAP full-asset mean Pd deltas.
- Finished-detector seed sensitivity: seeds `7`, `11`, and `23` all pass on the official full assets; the combined check gives `21/21` wins vs raw, `21/21` wins vs low-rank, `42/42` asset-level wins vs raw, and `42/42` asset-level wins vs low-rank.
- Seed-sensitivity margins: worst combined delta is `0.1033` vs raw and `0.0252` vs low-rank; the maximum cross-seed target-Pd range over evaluated Pfa points is `0.0079`.
- Strengthened classical baselines: TP-SSCS beats the best of 11 global/local CFAR baselines on the official full assets, with `7/7` combined wins, `14/14` asset-level wins, and minimum combined delta `0.0205`.
- Parameter-swept classical baselines: TP-SSCS beats the best of 75 global/local CFAR methods/configurations over training cells `4,6,8`, guard cells `1,2`, and OS percentiles `60,75,90`, with `7/7` combined wins, `14/14` asset-level wins, and minimum combined delta `0.0162`.
- Leave-one-condition-out learned baseline: a supervised raw-feature logistic detector trained on one official full asset and tested on the other is beaten by TP-SSCS with `7/7` combined wins, `14/14` asset-level wins, minimum combined delta `0.0596`, and positive bootstrap CI lower bounds at every Pfa point.
- Strong supervised HGB boundary: raw/residual HGB trained on one official full asset and tested on the other beats compact TP-SSCS at all seven combined Pfa points, so compact TP-SSCS should not be described as superior to all supervised learned detectors.
- TP-SSCS-feature HGB: adding TP-SSCS gate/enhanced-score features to the HGB beats compact TP-SSCS at all seven combined Pfa points and nearly matches the raw/residual HGB boundary with `6/7` combined wins and minimum combined delta `-0.0007`; bootstrap CIs are positive versus compact TP-SSCS but not strictly positive versus raw/residual HGB.
- Positive-target-pixel label-efficiency audit: compact zero-target-label TP-SSCS beats low-label raw/residual HGB at all seven combined Pfa points for `1`, `2`, `4`, and `8` source-domain positive-pixel budgets, with positive bootstrap CI lower bounds; the same audit honestly records that HGB first catches or exceeds compact at budget `16`.
- Label-cost Pareto audit: compact TP-SSCS has AUC `0.5313`, zero official full-asset positive target labels, and local CPU runtime `133.66` ms/frame; it dominates low-label HGB budgets `1`, `2`, `4`, `8`, and `16` in AUC, target-label cost, and measured runtime with positive AUC bootstrap CIs, while HGB first exceeds compact AUC at budget `64`.
- Target-free calibration audit: using only target-free frames to estimate thresholds preserves TP-SSCS positive Pd margins over raw and low-rank for both same-asset and cross-asset threshold sources (`7/7` combined wins in each mode, positive bootstrap support); fixed target-free threshold transfer is not fully empirical-Pfa calibrated on target-bearing backgrounds, so this is a rank-order robustness result and a calibration boundary.
- Frame-level robustness audit: over `210` target-bearing official full-asset frames and `7` Pfa points, TP-SSCS has `1470/1470` nonnegative item-Pfa pairs versus `low_rank_residual_k30`; versus raw, support remains broad but not universal, with minimum combined win fraction `0.890` and `61` raw-favorable item-Pfa pairs.
- Paired significance audit: all `14` combined comparator/Pfa exact sign tests remain significant after BH-FDR correction, with worst combined q-value `2.945e-29` and minimum matched sign effect `0.816`; the sign test ignores ties, so this is formal paired support over frozen full-asset frame rows rather than a pixel-independent trial claim.
- Whole-operating-surface AUC audit: normalized log-Pfa AUC over the checked `1e-5` to `1e-2` grid is `0.5313` for TP-SSCS, `0.4760` for low-rank, and `0.3085` for raw, with minimum combined delta `0.0553`, minimum frame-bootstrap CI lower bound `0.0491`, and worst combined BH-FDR q-value `1.464e-55`.
- Component-attribution audit: the finished detector adds log-Pfa AUC `+0.2228` over raw and `+0.0553` over `low_rank_residual_k30`, with `195/15/0` frame-level AUC wins/ties/losses versus low-rank; gate-only is weaker at the tightest Pfa and stronger at looser Pfa, so it is retained as a relaxed learned-score boundary rather than a uniformly dominated endpoint.
- Runtime/complexity audit: a local CPU profile over `12` deterministic target-bearing official full-asset frames reports compact TP-SSCS finished-detector median inference time `133.66` ms/frame versus `608.99` ms/frame for raw/residual HGB inference (`4.56x` HGB/compact ratio), with `2641` trainable TP-SSCS parameters; this supports a bounded deployment-cost claim, not a hardware-independent real-time claim.
- IPIX validation-selected external layer: residual-aware fusion passes on `12` disjoint held-out recordings with `7/7` Pfa wins vs raw and low-rank.
- SSDD external SAR layer: official test split has `231` images and `545` ship annotations, with `4` wins plus `3` ties vs raw, `0` losses vs raw, and `7/7` wins vs low-rank.
- SSDD localization supplement: image-level and annotation-level bootstrap CIs support that the SSDD gain is not only an aggregate artifact.
- Automatic self-check: `logs/aistap_top_readiness_self_check_20260717.md` reports `top_ready` with `0` hard failures.

## Why It Is Not Yet Q1-Top Locked

- The strongest independent non-AISTAP claim is not zero-shot: IPIX zero-shot transfer is negative, and the passing IPIX result uses validation-selected residual-aware fusion.
- SSDD is a supervised trainable-gate adaptation on a different radar-imaging modality, not a direct deployment of the saved AISTAP-SIM detector state.
- The wider CA/GOCA/SOCA/OS-CFAR classical-baseline criticism, fixed-window-parameter criticism, and narrow supervised raw-feature logistic-baseline criticism are addressed for the official AISTAP-SIM full assets; however, the stronger raw/residual HGB boundary beats compact TP-SSCS, so the compact detector should be positioned below a supervised feature-ensemble upper bound.
- The low-label result strengthens the target-instance-scarcity argument, but it does not overturn the supervised-data boundary: with enough source-domain target pixels, HGB can match or exceed compact TP-SSCS at some operating points.
- The label-cost Pareto result strengthens the resource-aware story but keeps the boundary explicit: compact is the zero/low-label, lower-runtime Pareto point, while HGB becomes higher-AUC once at least `64` positive target pixels are available.
- The target-free calibration audit strengthens claim control around threshold-source dependence, but it also shows that a fully deployment-like fixed-threshold calibration story still needs either online background support or a better transfer-calibration design.
- The frame-level robustness audit rules out a few-frame explanation versus low-rank residuals, but it also confirms that raw-favorable frames exist; the raw-map comparison should remain a broad distributional result rather than a universal per-frame claim.
- The paired significance audit strengthens statistical reporting but does not replace the existing paired-bootstrap uncertainty or create independent pixel-level samples; it should be reported as a frame-level sign-test supplement.
- The log-Pfa AUC audit strengthens the whole-surface story but is limited to the checked `1e-5` to `1e-2` operating grid; it should not be used to claim behavior at unmeasured false-alarm rates.
- The component-attribution audit strengthens the mechanism story, but it also confirms a gate-only tradeoff: the selected detector is the conservative low-false-alarm policy, not the maximum-Pd endpoint at every loose operating point.
- The runtime/complexity audit is machine-specific and sampled; it strengthens the compact-policy story but does not prove real-time performance or hardware-independent speed superiority.
- Large pretrained radar detectors, end-to-end deep object detectors, and independent non-AISTAP zero-shot learned baselines remain outside the current scope.
- Cross-condition holdout is useful but still partial relative to an unconditional cross-dataset superiority claim.
- The final manuscript package now passes a technical submission-readiness audit with `0` hard file/build failures and `0` warnings, but formal submission is still blocked by real author metadata, affiliations, corresponding email, ORCID, funding, acknowledgments, and public repository or access statements for data/code availability.

## Practical Zone Judgment

- Ordinary CAS Q2: `secure`.
- CAS Q1 lower to middle: `strong`.
- CAS Q1 top: `stronger credible candidate, still not locked`; the positive-pixel label-efficiency and label-cost Pareto audits give a defensible zero/low-target-label, lower-runtime advantage at severe target-instance scarcity, the target-free calibration audit preempts a threshold-source criticism, the frame-level, paired-significance, log-Pfa AUC, and component-attribution audits show the aggregate full-asset gain is broadly distributed, statistically supported, not a single-operating-point artifact, and mechanistically tied to residual-plus-gate policy design, and the runtime/complexity audit supports a compact deployment-cost story, while the full-label HGB upper-bound, raw-favorable item-level cases, gate-only loose-Pfa boundary, fixed-threshold Pfa-transfer result, and hardware-specific runtime boundary still require careful framing.
