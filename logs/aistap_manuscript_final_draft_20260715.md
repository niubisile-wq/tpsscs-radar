# AISTAP Manuscript Final Draft

Date: 2026-07-15

## Title

Target-preserving low-false-alarm radar detection under clutter suppression

## Abstract

Clutter suppression is often evaluated as if removing residual energy were the only objective. That framing is incomplete for operational radar detection, because aggressive suppression can erase weak targets at the same false-alarm rates where detection systems are most constrained. We frame the problem as target-preserving, low-false-alarm detection and evaluate a TP-SSCS detector policy against raw and low-rank residual baselines. On two official AISTAP-SIM full-test assets, the fixed detector passed all 14 asset-by-operating-point comparisons against both baselines, with 210 target-bearing frames and calibrated false-alarm control. A combined full-asset gate also passed on all seven operating points, with positive bootstrap confidence intervals for mean detection-probability gains over raw and rank-matched low-rank residuals. Two independent radar-family checks broadened the evidence: a validation-selected residual-aware fusion passed on 12 held-out Dartmouth IPIX recordings, whereas direct zero-shot transfer remained negative; and a supervised trainable-gate adaptation passed on the official SSDD SAR ship test split with 231 images and 545 annotations, including image-level and annotation-level bootstrap support. These results support TP-SSCS as a target-preserving detector design for low-false-alarm operation, while bounding the claim away from production deployment and away from zero-shot cross-dataset superiority.

## Introduction

Radar clutter suppression is commonly presented as a separation task: remove structured clutter, keep the residual, and assess the method by how much unwanted energy disappears. That evaluation is useful but incomplete. In weak-target detection, especially at low false-alarm rates, a method can look strong by residual-energy metrics while suppressing the target energy needed by the final detector.

The AISTAP-SIM public and full-test assets make this failure mode visible. Low-rank truncation is a natural baseline because the range-Doppler maps contain strong structured components, but the same sweep that improves clutter attenuation also increases target loss. This creates a detector-design problem rather than a denoising problem: the algorithm must preserve weak targets, suppress enough clutter to operate at low false-alarm rates, and calibrate detection thresholds rather than optimize visual residual cleanliness.

We therefore frame TP-SSCS as a target-preserving low-false-alarm detector policy. The method combines low-rank residual structure, sparse target-aware gating, and CFAR-style false-alarm calibration. The evaluation follows the same logic. We first establish the suppression-versus-target-loss trade-off, then test a fixed detector on official AISTAP-SIM full-test assets, and finally ask whether the operating logic survives independent radar-family checks.

The evidence now has three layers. First, the same saved candidate state and finished detector policy pass a combined official full-asset gate over `simMed_test.mat` and `simWind_test.mat`. Second, the IPIX sea-clutter recordings test whether a validation-selected residual-aware fusion improves held-out weak-target detection; the direct zero-shot path is negative, so the positive claim is deliberately limited to the validated fusion policy. Third, the SSDD SAR ship imagery tests whether a supervised external trainable-gate adaptation can preserve target regions on a different radar image family; image-level and annotation-level bootstrap analyses check that the gain is not only a pooled-pixel artifact.

This paper therefore does not claim universal clutter removal or production-ready deployment. It claims that target preservation and false-alarm calibration should be treated as first-class detector objectives, and that this framing is supported by official AISTAP-SIM full-test evidence plus two bounded external radar-family validations.

## Results

### Low-rank suppression exposed the target-loss trade-off

The public AISTAP-SIM sample loaded locally with raw range-Doppler inputs and target-only reference tensors, allowing the suppression result to be evaluated against target preservation rather than residual energy alone. The low-rank audit made the central trade-off explicit. On `simMed`, clutter attenuation increased from `2.197 dB` at `k=1` to `11.268 dB` at `k=20`, while target loss increased from `0.925 dB` to `13.906 dB`. The same qualitative pattern appeared on `simWind` and `simNoiseOnly`. Thus, aggressive low-rank suppression was not a monotone detector win: it removed clutter but also removed weak target energy.

This observation fixed the evaluation target. The detector should not be judged only by how clean the residual map appears. It should be judged by detection probability under fixed false-alarm control and by whether target-preserving branches reduce the target-loss penalty introduced by suppression.

### CFAR-calibrated operating surfaces showed that the best rank depends on false-alarm regime

Dense CFAR operating surfaces confirmed that the best suppression rank was operating-point dependent. The residual baseline beat the raw map across the tested `Pfa` grid, but the optimal rank shifted: very low `Pfa` preferred more aggressive suppression, whereas looser operating points shifted toward mid-range ranks. At `Pfa=1e-5`, the best residual point used `k=30` with `Pd=0.1628`; at `Pfa=3e-3` and `Pfa=1e-2`, the best point shifted to `k=8`, with `Pd=0.9767` and `1.0000`, respectively.

This result justified treating `k` as an operating-policy parameter rather than as a universal hyperparameter. It also motivated the TP-SSCS target-preservation branch: low-rank residuals can improve detection under CFAR, but the same residual path can over-suppress weak targets unless the detector explicitly protects them.

### A trainable target-preservation branch reduced target loss on the public sample

The target-preservation ablation separated raw, low-rank residual, oracle, and trainable-gate behavior. On the public target-bearing items, the raw map reached mean `Pd=0.145` at zero target loss, while the low-rank residual baseline raised mean `Pd` to `0.256` but paid `6.191 dB` mean target loss. The strongest trainable branch, `rank=30`, `hidden=16`, `steps=150`, and learning rate `0.02`, reached mean `Pd=0.253`, cut mean target loss to `0.197 dB`, and kept clutter attenuation at `7.594 dB`.

The oracle diagnostics showed remaining headroom, but the trainable branch was the first concrete manuscript-facing target-preservation branch. A three-seed stability check kept validation `Pd=0.9767` at `Pfa=1e-2` across seeds `7`, `11`, and `23`. Stress-grid experiments then showed that the branch remained finite and competitive under perturbations, although no single rank dominated every perturbation family.

### The finished detector passed official AISTAP-SIM full-asset validation

The fixed detector policy was next evaluated on official AISTAP-SIM full-test assets. `simMed_test.mat` and `simWind_test.mat` each contributed 105 target-bearing frames, giving 210 target-bearing full-test items. Across both assets, the same saved state and `tpsscs_finished_detector` policy beat raw and `low_rank_residual_k30` on all 14 asset-by-Pfa comparisons under conservative false-alarm calibration.

The combined official full-asset gate consolidated both assets into one protocol. It passed with 7/7 combined wins against raw and 7/7 combined wins against the rank-matched low-rank residual baseline. At `Pfa=1e-5`, TP-SSCS reached `Pd=0.1845`, compared with raw `Pd=0.0800` and low-rank `Pd=0.1015`. At `Pfa=1e-2`, TP-SSCS reached `Pd=0.8678`, compared with raw `Pd=0.6551` and low-rank `Pd=0.8388`. Bootstrap confidence intervals over the 210 target-bearing frames were positive for the mean detection-probability delta at every operating point against both comparators.

This full-asset result changed the evidence class from public-sample scaffold evidence to an in-domain finished-detector protocol. It did not, by itself, prove independent external generalization, so the next analyses tested bounded external radar-family behavior.

### IPIX held-out recordings supported validation-selected residual-aware fusion, while zero-shot transfer remained negative

Dartmouth IPIX sea-clutter recordings were used as an independent weak-target radar-family test. Direct zero-shot transfer of the AISTAP-SIM finished detector was negative: at `Pfa=1e-2`, raw reached `Pd=0.0364`, whereas the transferred finished detector reached `Pd=0.0086`. This negative result is retained as a boundary condition rather than hidden.

The positive IPIX result came from a validation-selected residual-aware fusion policy. After beta selection on a separate validation recording, the policy was evaluated on 12 disjoint held-out recordings. It passed all seven Pfa operating points against raw and low-rank residual comparators. At `Pfa=1e-2`, the fusion reached `Pd=0.1374`, compared with raw `Pd=0.0972` and low-rank `Pd=0.0096`. Recording-level bootstrap estimates supported positive mean detection-probability gains over raw and low-rank across the evaluated operating points.

The supported claim is therefore specific: IPIX validates a residual-aware fusion strategy selected without using the held-out recordings. It does not validate unmodified zero-shot transfer of the saved AISTAP-SIM detector state.

### SSDD SAR imagery supported supervised external trainable-gate adaptation

SSDD provided a second independent radar-family test using SAR ship imagery. The protocol trained a TP-SSCS-style trainable pixel gate on the official train split with a deterministic validation split, and evaluated only on the official test split. The official test set contained 231 images and 545 ship annotations. The selected policy used raw fallback for `Pfa <= 1e-4` to avoid perturbing the extreme background tail, and used a learned gate at higher Pfa points.

The aggregate SSDD test passed the external adaptation gate: the candidate had 4/7 wins, 3/7 ties, and 0 losses against raw, and 7/7 wins against the low-rank residual comparator. At `Pfa=1e-2`, the candidate reached `Pd=0.7469`, compared with raw `Pd=0.5284` and low-rank `Pd=0.0195`.

To test whether the SSDD gain was broad rather than driven by pooled pixels, we added image-level and annotation-level bootstrap analyses with fixed global test thresholds. The image-level raw fallback points tied raw by design at `Pfa <= 1e-4`. At non-fallback operating points, the image-level mean detection-probability deltas versus raw were positive with 95% bootstrap confidence intervals: `0.1222` `[0.0986, 0.1449]` at `Pfa=3e-4`, `0.1596` `[0.1345, 0.1852]` at `Pfa=1e-3`, `0.2448` `[0.2178, 0.2720]` at `Pfa=3e-3`, and `0.2182` `[0.1962, 0.2386]` at `Pfa=1e-2`. Image-level comparisons against low-rank were positive at every Pfa, and annotation-level results over 545 ship instances showed the same qualitative pattern.

The SSDD result supports supervised external trainable-gate adaptation on a different radar image family. It should not be described as zero-shot transfer of the saved AISTAP-SIM state.

### Cross-paper readiness comparison

The completed evidence stack now exceeds the selected local `power_se` and battery reference packages on the specific dimension most relevant to this manuscript: detector operating-policy density with task-relevant external radar validation. The battery package remains more mature as a finished manuscript package and has broader raw data-source scale, while `power_se` remains a cleaner state-estimation baseline audit. AISTAP is now stronger on low-false-alarm radar detection evidence, with official AISTAP-SIM full-test validation, IPIX held-out validation, SSDD SAR adaptation, and explicit no-overclaim boundaries.

## Methods

### Data sources and scope

The in-domain data consisted of public AISTAP-SIM samples plus the official AISTAP-SIM full-test assets `simMed_test.mat` and `simWind_test.mat`. The independent radar-family tests used Dartmouth IPIX sea-clutter recordings and the official SSDD SAR ship detection dataset. The paper does not treat SEVIR, MRMS, MeteoNet, or NEXRAD audit artifacts as direct TP-SSCS transfer results; those sources remain adjacent radar-source audits unless a TP-SSCS protocol is explicitly run on them.

### Low-rank residual and CFAR baselines

Low-rank residual baselines were evaluated by sweeping truncation rank and computing clutter attenuation, target loss, and CFAR-calibrated detection probability. The low-rank baseline is diagnostic: it exposes the trade-off between clutter suppression and target preservation, and it provides a rank-matched comparator for TP-SSCS. CFAR thresholds were evaluated under fixed target false-alarm rates, so comparisons ask whether a score improves detection at the same operating constraint rather than whether it produces a visually cleaner map.

### TP-SSCS candidate and finished detector policy

The manuscript-facing TP-SSCS branch uses a saved trainable-gate candidate state with `rank=30`, `hidden=16`, `steps=150`, and learning rate `0.02`. The finished detector policy combines the target-preserving trainable branch with conservative CFAR calibration and raw fallback behavior where the operating tail is too sparse to perturb safely. The saved state is retained as a reproducibility artifact, and the detector outputs are evaluated against raw and rank-matched low-rank residual comparators.

### Official full-asset protocol

The official full-asset protocol evaluates all target-bearing frames in `simMed_test.mat` and `simWind_test.mat`. For each asset and Pfa point, TP-SSCS, raw, and rank-matched low-rank residual scores are compared under conservative empirical false-alarm calibration. The combined gate pools the two official assets at the protocol level and requires calibrated Pfa, wins against raw, and wins against the low-rank comparator across all seven operating points. Bootstrap confidence intervals are computed over target-bearing frames for paired detection-probability deltas.

### IPIX external validation protocol

IPIX is treated as a separate external radar-family validation. Direct zero-shot transfer is reported and bounded as negative. The positive IPIX analysis uses a residual-aware fusion policy selected on a validation recording and evaluated on 12 disjoint held-out recordings. The held-out recordings are the unit for recording-level bootstrap summaries, preventing window-level duplication from being overinterpreted as independent files.

### SSDD external adaptation protocol

SSDD is treated as supervised external adaptation. A TP-SSCS-style pixel gate is trained on the official train split with a deterministic validation split and evaluated on the official test split only. Raw fallback is used for `Pfa <= 1e-4`; a learned gate is used at higher Pfa points selected by validation behavior. Aggregate test curves are computed using fixed global thresholds on official-test background pixels outside dilated ship boxes. Image-level and annotation-level robustness analyses reuse the same thresholds and therefore test the distribution of gains rather than retuning a detector per image.

### Readiness and comparison audit

An automatic top-readiness self-check verifies reproducibility artifacts, deployable candidate state, sample scale, full-asset detector behavior, external radar validation, and local reference comparison. This gate is a manuscript-readiness audit, not a journal acceptance guarantee. It is used to keep claims aligned with available evidence and to prevent positive external results from being promoted beyond their protocol boundaries.

## Discussion

The central result is that target preservation and false-alarm calibration change how clutter-suppression methods should be evaluated. Low-rank residuals can improve CFAR detection, but the same suppression path can remove weak target energy. TP-SSCS improves the operating surface because it treats target retention as part of the detector objective rather than as an incidental property of a cleaner residual map.

The official AISTAP-SIM full-asset results provide the strongest in-domain evidence. The same saved state and detector policy passed on both full-test assets, and the combined full-asset protocol produced positive paired bootstrap confidence intervals against raw and low-rank residual comparators. This makes the result stronger than a public-sample scaffold demonstration.

The external results add breadth but require careful wording. IPIX does not support direct zero-shot transfer; it supports a validation-selected residual-aware fusion policy on disjoint held-out recordings. SSDD does not support zero-shot transfer of the AISTAP-SIM saved state; it supports supervised external trainable-gate adaptation on official SAR ship imagery. These boundaries are not weaknesses to hide. They make the paper more credible by separating unsupported universal transfer from supported external detector behavior.

The comparison to local reference papers is also bounded. AISTAP is now the strongest of the local projects on task-specific low-false-alarm radar evidence and external radar-family validation. The battery project remains stronger as a polished manuscript package and broader raw data-source archive; `power_se` remains stronger as a clean reproducibility-first state-estimation audit. The correct positioning is therefore not that AISTAP is universally superior, but that it is now the best candidate for a radar-detection-focused high-impact submission route.

Several limitations remain. First, SSDD is a supervised adaptation experiment, so it should not be used to claim saved-state cross-domain generalization. Second, the IPIX positive result depends on validation-selected residual-aware fusion, while the direct zero-shot branch remains negative. Third, additional classical detector baselines may be valuable, but only if they are implemented with identical Pfa calibration; rushed baseline expansion would create avoidable reviewer risk. Finally, the current evidence supports manuscript-level readiness, not production deployment.

## Boundary

Supported claims:

- TP-SSCS improves target-preserving low-false-alarm detection relative to raw and low-rank residual baselines on official AISTAP-SIM full-test assets.
- The combined full-asset gate passes on 210 target-bearing frames across `simMed_test.mat` and `simWind_test.mat`.
- IPIX supports validation-selected residual-aware fusion on 12 held-out recordings, but not direct zero-shot transfer.
- SSDD supports supervised external trainable-gate adaptation on 231 official-test images and 545 annotations, with image-level and annotation-level bootstrap support.

Unsupported claims:

- Production-ready radar deployment.
- Universal clutter suppression.
- Zero-shot transfer success across all external radar datasets.
- Direct TP-SSCS retraining or transfer success on SEVIR, MRMS, MeteoNet, or NEXRAD.
- Guaranteed acceptance by a CAS Q1 Top journal.

## Figures and Tables

- Figure 1: target-preserving low-false-alarm detector framing and TP-SSCS pipeline.
- Figure 2: public-sample target-preservation frontier.
- Figure 3: dense low-Pfa operating surface and rank-dependent CFAR behavior.
- Figure 4: official AISTAP-SIM full-asset detector protocol and combined bootstrap CIs.
- Figure 5: external radar-family validation: IPIX held-out fusion and SSDD SAR adaptation.
- Extended Data Figure 1: SSDD image-level and annotation-level bootstrap distributions.
- Table 1: low-rank suppression trade-off across rank and subset.
- Table 2: official full-asset TP-SSCS vs raw and low-rank detector results.
- Table 3: IPIX and SSDD external validation summary with claim boundaries.
- Table 4: supported and unsupported claims.

