# Pure Text Manuscript Draft

Date: 2026-07-15

## Title

Target-preserving low-false-alarm radar detection under clutter suppression

## Running Title

Target-preserving low-false-alarm radar detection

## Abstract

Clutter suppression is often evaluated as a separation problem in which the goal is to remove as much residual background energy as possible. That framing is incomplete for operational radar detection, because aggressive suppression can remove weak targets at the same low false-alarm rates where the detector must remain reliable. We formulate radar clutter suppression as a target-preserving, low-false-alarm detection problem and evaluate a TP-SSCS detector policy against raw and low-rank residual baselines. Low-rank audits on AISTAP-SIM showed that stronger suppression increased clutter attenuation but also increased target loss, motivating an explicit target-preservation branch and CFAR-calibrated operating analysis. A trainable target-preservation branch reduced mean target loss from 6.191 dB for the low-rank residual baseline to 0.197 dB while retaining comparable detection behavior on the public target-bearing sample. On two official AISTAP-SIM full-test assets, a fixed detector policy evaluated 210 target-bearing frames and passed all 14 asset-by-operating-point comparisons against raw and rank-matched low-rank residual baselines. In the combined full-asset protocol, TP-SSCS passed all seven operating points, with positive paired bootstrap confidence intervals for mean detection-probability gains over both comparators. Independent radar-family checks further tested the boundary of the approach. On Dartmouth IPIX sea-clutter recordings, direct zero-shot transfer remained negative, whereas a validation-selected residual-aware fusion policy passed on 12 disjoint held-out recordings. On the official SSDD SAR ship test split, supervised trainable-gate adaptation passed on 231 images and 545 annotations, with image-level and annotation-level bootstrap analyses supporting broad non-fallback gains. These results support TP-SSCS as a target-preserving detector design for low-false-alarm radar operation, while bounding the claim away from production deployment and away from unqualified zero-shot cross-dataset superiority.

## Keywords

Radar detection; clutter suppression; low false alarm; target preservation; CFAR; weak targets; AISTAP-SIM; IPIX; SAR ship detection.

## Introduction

Radar clutter suppression is commonly treated as a separation task: structured clutter is removed, the remaining residual is inspected, and the method is judged by how much unwanted energy disappears. This view is natural when the immediate objective is visual or signal separation, but it is not sufficient for weak-target detection. A detector operating at low false-alarm rates is not rewarded for suppressing energy in the abstract. It is rewarded for preserving target evidence while controlling false alarms. A suppression method can therefore look successful by residual-energy criteria and still fail the operational detection objective if weak targets are removed together with clutter.

This distinction is especially important in range-Doppler radar settings where low-rank or structured clutter models are strong baselines. Low-rank suppression can expose residual signals and improve detector contrast, but the same operation can also subtract target-bearing energy when weak targets are embedded in structured background. The relevant question is therefore not whether stronger suppression produces a cleaner residual map. The relevant question is whether the resulting score improves detection probability under a specified false-alarm constraint, and whether the detector can preserve weak targets across the operating regime.

We use the AISTAP-SIM public and official full-test assets to examine this trade-off. The public sample provides raw range-Doppler inputs and target-only reference tensors, making it possible to quantify both clutter attenuation and target loss. A rank sweep showed that stronger low-rank suppression increased clutter attenuation while sharply increasing target loss. This converted the problem from a denoising task into a detector-design task: a useful method must suppress enough clutter to operate at low false-alarm rates, preserve target evidence, and calibrate the final score under a CFAR-like operating constraint.

We therefore formulate TP-SSCS as a target-preserving, low-false-alarm detector policy. The method uses low-rank residual structure as a baseline representation, but augments it with a sparse target-aware gate and false-alarm-calibrated detector evaluation. The evaluation follows the same hierarchy. We first establish the suppression-versus-target-loss trade-off, then test whether a trainable target-preservation branch can reduce the target-loss penalty, then evaluate a fixed detector policy on official AISTAP-SIM full-test assets, and finally test bounded external behavior on independent radar-family data.

The final evidence stack has three layers. The in-domain layer uses `simMed_test.mat` and `simWind_test.mat`, two official AISTAP-SIM full-test assets, and evaluates 210 target-bearing frames across seven false-alarm operating points. The first external layer uses Dartmouth IPIX sea-clutter recordings. This layer deliberately separates a negative direct zero-shot result from a positive validation-selected residual-aware fusion result on held-out recordings. The second external layer uses the official SSDD SAR ship detection dataset, where a supervised external trainable-gate adaptation is tested on 231 official-test images and 545 ship annotations. The SSDD result is further checked with image-level and annotation-level bootstrap analyses so that the gain is not supported only by pooled-pixel aggregates.

The contribution is therefore a bounded detector-design result. We do not claim universal clutter suppression, production-ready deployment, or unqualified zero-shot cross-dataset transfer. We show that target preservation and false-alarm calibration are necessary evaluation objectives for radar clutter suppression, and that TP-SSCS improves target-preserving low-false-alarm detection under official AISTAP-SIM full-asset validation, with bounded support from two independent radar-family protocols.

## Results

### Low-rank suppression exposed a target-loss failure mode

The public AISTAP-SIM sample was first used to test whether clutter suppression and target preservation move together. The sample contains raw range-Doppler inputs and target-only reference tensors, allowing suppression quality to be evaluated against target loss rather than only against residual background energy. This distinction was essential. On `simMed`, increasing the low-rank truncation from `k=1` to `k=20` increased clutter attenuation from 2.197 dB to 11.268 dB, but target loss also increased from 0.925 dB to 13.906 dB. The same qualitative pattern appeared on `simWind` and `simNoiseOnly`.

These measurements showed that low-rank suppression was not a monotone operational improvement. Stronger suppression did remove more clutter, but it also removed weak target energy. If the evaluation objective were residual cleanliness alone, the more aggressive ranks would appear favorable. Under a detector objective, however, this result reveals a failure mode: the apparent improvement in clutter removal can be purchased by erasing the signal needed for detection.

The target-loss result motivated a change in the evaluation question. Instead of asking whether low-rank suppression makes the residual map cleaner, we asked whether a detector score improves detection probability at a fixed false-alarm target. This placed false-alarm calibration and target preservation at the centre of the method rather than leaving them as downstream checks.

### CFAR-calibrated operating analysis showed that suppression rank is regime-dependent

The dense CFAR operating analysis confirmed that the best suppression rank depends on the false-alarm regime. Across the tested Pfa grid, residual scores improved detection relative to raw maps, but no single rank dominated the entire operating surface. At `Pfa=1e-5`, the best residual operating point used `k=30` and reached `Pd=0.1628`. At `Pfa=3e-3` and `Pfa=1e-2`, the best operating point shifted to `k=8`, reaching `Pd=0.9767` and `1.0000`, respectively.

This pattern has a direct methodological implication. The rank cannot be treated as a universal denoising hyperparameter. It is part of the detector operating policy. More aggressive suppression may help in the most stringent low-Pfa tail, while a less aggressive residual can be preferable when the operating point permits more detections. This reinforces the need for CFAR-calibrated evaluation: without fixed false-alarm targets, the rank trade-off is easy to misread.

The operating-surface result also sharpened the role of TP-SSCS. Low-rank residuals are useful, but a low-rank residual alone does not solve the target-preservation problem. A target-aware branch is needed to reduce the target-loss cost while retaining the detection advantage of residual scoring under controlled false-alarm rates.

### A trainable target-preservation branch reduced target loss

The target-preservation ablation compared raw maps, low-rank residuals, oracle target-preservation diagnostics, and trainable-gate variants. On the public target-bearing items, the raw map reached mean `Pd=0.145` at zero target loss. The low-rank residual baseline increased mean `Pd` to `0.256`, but paid 6.191 dB of mean target loss. The strongest trainable branch used `rank=30`, `hidden=16`, `steps=150`, and learning rate `0.02`. It reached mean `Pd=0.253`, reduced mean target loss to 0.197 dB, and retained clutter attenuation of 7.594 dB.

The trainable branch did not exhaust the oracle headroom, but it changed the evidence class of the method. The target-preservation result was no longer only an oracle diagnostic showing what might be possible if the target mask were known. It became a concrete trainable branch that reduced the target-loss penalty while preserving useful detector behavior. A three-seed stability check over seeds `7`, `11`, and `23` kept validation `Pd=0.9767` at `Pfa=1e-2`, and perturbation stress tests showed finite, competitive behavior rather than numerical collapse.

These results support the use of target-aware gating as a detector component. They do not by themselves prove deployment readiness, because they are still tied to the public-sample training and ablation setting. They do, however, justify carrying the branch into a fixed detector policy and testing it on official full-test assets.

### A fixed detector policy passed official AISTAP-SIM full-asset validation

The fixed detector policy was evaluated on two official AISTAP-SIM full-test assets, `simMed_test.mat` and `simWind_test.mat`. Each asset contributed 105 target-bearing frames, giving 210 target-bearing full-test items. The same saved candidate state and `tpsscs_finished_detector` policy were used across both assets. Raw maps and rank-matched `low_rank_residual_k30` scores served as comparators.

Across both assets and seven Pfa operating points, TP-SSCS beat both comparators on all 14 asset-level comparisons under conservative false-alarm calibration. The combined full-asset protocol also passed on all seven operating points. At `Pfa=1e-5`, TP-SSCS reached `Pd=0.1845`, whereas raw reached `Pd=0.0800` and low-rank reached `Pd=0.1015`. At `Pfa=1e-2`, TP-SSCS reached `Pd=0.8678`, whereas raw reached `Pd=0.6551` and low-rank reached `Pd=0.8388`.

Paired bootstrap confidence intervals over the 210 target-bearing frames supported positive mean detection-probability gains at every Pfa point against both raw and low-rank residuals. Against raw, the mean delta `Pd` ranged from 0.1046 at `Pfa=1e-5` to 0.3266 at `Pfa=3e-3`, with positive 95% confidence intervals throughout. Against low-rank residuals, the mean delta remained smaller but consistently positive, ranging from 0.0290 to 0.0831 across the evaluated operating points.

The official full-asset result is the strongest in-domain evidence for TP-SSCS. It shows that the detector policy is not only a public-sample scaffold or an oracle diagnostic. It is a reproducible, fixed policy that improves low-false-alarm detection over raw and rank-matched low-rank residual baselines on two official full-test conditions.

### IPIX separated negative zero-shot transfer from positive validation-selected fusion

Dartmouth IPIX sea-clutter recordings were used as an independent weak-target radar-family test. This dataset was not treated as automatic proof of cross-domain transfer. Instead, we explicitly evaluated and bounded two different claims: direct zero-shot transfer of the AISTAP-SIM finished detector, and validation-selected residual-aware fusion.

Direct zero-shot transfer was negative. At `Pfa=1e-2`, raw reached `Pd=0.0364`, whereas the transferred `tpsscs_finished_detector` reached `Pd=0.0086`. This result is important because it prevents the in-domain full-asset success from being overstated as unmodified cross-dataset transfer.

The positive IPIX result came from a validation-selected residual-aware fusion policy. The fusion coefficient was selected on a separate validation recording and then evaluated on 12 disjoint held-out recordings. On those held-out recordings, the fusion policy passed all seven Pfa operating points against raw and low-rank residual comparators. At `Pfa=1e-2`, the fusion reached `Pd=0.1374`, compared with raw `Pd=0.0972` and low-rank `Pd=0.0096`. Recording-level bootstrap estimates supported positive mean detection-probability gains over both comparators across the evaluated operating points.

The supported IPIX claim is therefore narrow but useful. IPIX shows that residual-aware target-preserving logic can improve held-out sea-clutter detection when the fusion policy is selected on a separate validation recording. It does not show that the saved AISTAP-SIM detector state transfers directly without adaptation or validation.

### SSDD supported supervised external trainable-gate adaptation

The official SSDD SAR ship detection dataset provided a second independent radar-family test. This experiment was designed as supervised external adaptation rather than zero-shot transfer. A TP-SSCS-style pixel gate was trained on the official train split with a deterministic validation split and evaluated only on the official test split. The official test set contained 231 images and 545 ship annotations.

The selected SSDD policy used raw fallback for `Pfa <= 1e-4`, where perturbing the extreme background tail would be risky, and used a learned gate at higher Pfa points. In the aggregate official-test evaluation, the candidate produced four wins, three ties, and zero losses against raw, and seven wins against the low-rank residual comparator. At `Pfa=1e-2`, the candidate reached `Pd=0.7469`, compared with raw `Pd=0.5284` and low-rank `Pd=0.0195`.

To determine whether the SSDD gain was broad or driven only by pooled pixels, we evaluated image-level and annotation-level robustness using fixed global test thresholds. The raw fallback points tied raw by design at `Pfa <= 1e-4`. At the non-fallback operating points, image-level mean detection-probability deltas versus raw were positive with 95% bootstrap confidence intervals: 0.1222 with interval [0.0986, 0.1449] at `Pfa=3e-4`, 0.1596 with interval [0.1345, 0.1852] at `Pfa=1e-3`, 0.2448 with interval [0.2178, 0.2720] at `Pfa=3e-3`, and 0.2182 with interval [0.1962, 0.2386] at `Pfa=1e-2`. Image-level comparisons against low-rank residuals had positive 95% confidence intervals at every Pfa point, and annotation-level analyses over the 545 ship instances showed the same qualitative pattern.

The SSDD result supports supervised external trainable-gate adaptation on SAR ship imagery. It does not support a claim that the saved AISTAP-SIM detector transfers zero-shot to SSDD. The distinction matters because the evidence is strong for external adaptation, but it would be overstated if described as unqualified cross-domain generalization.

## Discussion

The main finding is that radar clutter suppression should be evaluated as target-preserving low-false-alarm detection rather than as residual cleaning alone. Low-rank suppression is a valuable baseline, but the AISTAP-SIM audits showed that stronger suppression can increase target loss substantially. A detector that removes clutter while erasing weak targets is not operationally successful, even if the residual looks cleaner.

TP-SSCS addresses this evaluation gap by making target preservation and false-alarm calibration explicit. The trainable branch reduced the target-loss penalty relative to low-rank residuals on the public target-bearing sample, while the fixed detector policy passed official AISTAP-SIM full-asset validation on two full-test conditions. The combined full-asset protocol is particularly important because it shows consistent gains over both raw and rank-matched low-rank comparators across seven low-false-alarm operating points, with positive paired bootstrap support.

The external radar-family results broaden the evidence while preserving the claim boundary. The IPIX results show that unmodified zero-shot transfer should not be claimed: direct transfer was negative. At the same time, the validation-selected residual-aware fusion result shows that target-preserving residual logic can improve held-out IPIX weak-target detection when the policy is selected without using the held-out recordings. The SSDD results show that supervised external trainable-gate adaptation can improve SAR ship detection on the official test split, and that the gains persist at image and annotation levels rather than only in pooled-pixel statistics.

These external results should be interpreted as bounded validation, not as universal transfer. IPIX supports validation-selected fusion; SSDD supports supervised adaptation. Neither result proves that the saved AISTAP-SIM detector state can be transferred unchanged to every radar family. This boundary strengthens rather than weakens the manuscript, because it separates supported detector behavior from claims that the experiments do not establish.

The study also clarifies how future clutter-suppression methods should be compared. A strong evaluation should report target loss, detection probability, empirical false-alarm behavior, and operating-regime dependence together. Reporting clutter attenuation alone can reward methods that remove target energy. Reporting detection probability without false-alarm calibration can hide threshold effects. Reporting only aggregate external results can obscure whether gains are broad across units or driven by pooled samples. The TP-SSCS evidence stack addresses these risks by combining public-sample target-loss audits, official full-asset detector validation, recording-level IPIX summaries, and image- and annotation-level SSDD robustness checks.

Several limitations remain. First, the current detector is not a production deployment claim. The evaluated protocols are reproducible experimental gates, not field-deployed operating systems. Second, SSDD is a supervised external adaptation experiment, not zero-shot saved-state transfer. Third, the IPIX positive result depends on validation-selected residual-aware fusion, while direct zero-shot transfer remains negative. Fourth, additional classical detector baselines may be useful, but only if they are implemented with identical false-alarm calibration; otherwise, they could introduce unfair comparison artifacts. Finally, the present work is strongest as a target-preserving detector-design study. It should not be generalized into universal clutter suppression without additional protocol-specific evidence.

Overall, the results show that target preservation is not a secondary diagnostic for clutter suppression. It is part of the detector objective. TP-SSCS improves low-false-alarm detection because it treats target retention, suppression, and threshold calibration as coupled design constraints. This framing is supported by official AISTAP-SIM full-asset validation and by two bounded external radar-family tests.

## Methods

### Data sources

The in-domain evaluation used public AISTAP-SIM samples and two official AISTAP-SIM full-test assets, `simMed_test.mat` and `simWind_test.mat`. The public sample was used for initial low-rank audits, target-preservation diagnostics, trainable-branch selection, and stress checks. The official full-test assets were used for the fixed detector protocol and combined full-asset validation. Each official full-test asset contributed 105 target-bearing frames, for 210 target-bearing frames in the combined protocol.

Two independent radar-family datasets were used for bounded external validation. Dartmouth IPIX sea-clutter recordings were used as a weak-target external radar test. SSDD SAR ship imagery was used as a supervised external adaptation test. Other radar-source audit files present in the workspace were not treated as TP-SSCS transfer results unless a TP-SSCS protocol was explicitly run on them.

### Low-rank residual baseline

The low-rank residual baseline was evaluated by decomposing range-Doppler maps and reconstructing a truncated low-rank component. Residual scores were computed from the difference between the raw map and the low-rank approximation. Rank sweeps were used to quantify clutter attenuation and target loss. This baseline served two purposes: it provided a natural structured-clutter comparator, and it exposed the target-loss penalty associated with increasingly aggressive suppression.

Low-rank residuals were not treated as the proposed final detector. They were used as a diagnostic baseline and as a rank-matched comparator for TP-SSCS. In the official full-asset detector protocol, `low_rank_residual_k30` served as the rank-matched low-rank comparator.

### False-alarm calibration and operating metrics

Detector scores were evaluated under fixed target false-alarm probabilities. For each score and operating point, thresholds were calibrated conservatively on background scores, and empirical Pfa was checked against the protocol tolerance. Detection probability was computed over target-bearing regions or target-bearing frames, depending on the protocol. This design asks whether a score improves detection under the same false-alarm constraint, rather than whether it produces a visually cleaner residual.

The main operating points were `Pfa=1e-5`, `3e-5`, `1e-4`, `3e-4`, `1e-3`, `3e-3`, and `1e-2`. These operating points were used consistently across the official full-asset, IPIX, and SSDD protocols whenever the dataset supported the corresponding calibration.

### TP-SSCS trainable branch

The manuscript-facing TP-SSCS branch used a saved trainable-gate candidate state with `rank=30`, `hidden=16`, `steps=150`, and learning rate `0.02`. The branch was selected because it reduced target loss while retaining useful detection behavior in the public target-bearing sample. Training stability was checked over seeds `7`, `11`, and `23`, and perturbation stress tests were used to verify finite behavior under noise, phase, and target-amplitude changes.

The trainable branch was interpreted as a concrete target-preservation branch rather than as a complete deployment system. It provided the basis for the fixed detector policy tested on official full-test assets.

### Official AISTAP-SIM full-asset detector protocol

The official full-asset protocol evaluated `simMed_test.mat` and `simWind_test.mat`. For each target-bearing frame and each Pfa operating point, TP-SSCS, raw, and rank-matched low-rank residual scores were compared under conservative empirical false-alarm calibration. The protocol required TP-SSCS to remain calibrated and to improve detection probability over both comparators.

The combined full-asset gate pooled the two official assets at the protocol level. It evaluated seven operating points and computed paired bootstrap confidence intervals over target-bearing frames for mean detection-probability deltas against raw and low-rank residual comparators.

### IPIX external validation

IPIX validation was divided into a direct zero-shot transfer test and a validation-selected residual-aware fusion test. The zero-shot test applied the AISTAP-SIM finished detector policy directly to IPIX and was reported as a negative boundary result. The residual-aware fusion policy used a separate validation recording to select the fusion coefficient and then evaluated the fixed selected policy on 12 disjoint held-out recordings.

For IPIX bootstrap summaries, held-out recordings were treated as the independent unit. This avoids treating multiple windows from the same recording as independent files. The positive IPIX claim is limited to the validation-selected residual-aware fusion policy on held-out recordings.

### SSDD supervised external adaptation

SSDD was evaluated as a supervised external adaptation experiment. A TP-SSCS-style pixel gate was trained on the official train split with a deterministic validation split and evaluated only on the official test split. The official test split contained 231 images and 545 ship annotations. Raw fallback was enforced for `Pfa <= 1e-4`, and a learned gate was used at higher Pfa points selected by validation behavior.

Aggregate SSDD curves were computed using fixed global thresholds calibrated on official-test background pixels outside dilated ship boxes. Image-level and annotation-level robustness analyses reused those fixed thresholds. Therefore, the unit-level SSDD analyses tested the distribution of gains across images and ship annotations; they did not retune the detector separately for each image.

### Bootstrap confidence intervals

Bootstrap confidence intervals were used to summarize uncertainty in paired detection-probability gains. For the official AISTAP-SIM full-asset protocol, bootstrap resampling was performed over the 210 target-bearing frames. For IPIX, bootstrap resampling was performed over the 12 held-out recordings. For SSDD, bootstrap resampling was performed separately over official-test images and over ship annotations. Confidence intervals were reported for mean detection-probability deltas relative to raw and low-rank comparators.

### Claim control

All analyses were interpreted under explicit claim boundaries. The official full-asset protocol supports in-domain AISTAP-SIM detector validation. IPIX supports validation-selected residual-aware fusion but not direct zero-shot transfer. SSDD supports supervised external trainable-gate adaptation but not zero-shot transfer of the saved AISTAP-SIM state. The experiments do not establish production deployment, universal clutter suppression, or unqualified cross-dataset superiority.

## Data Availability

This manuscript uses public AISTAP-SIM sample and full-test assets, Dartmouth IPIX sea-clutter recordings, and the official SSDD SAR ship detection dataset. The local analysis package records dataset locations, derived result files, and protocol outputs under the project `data`, `results`, and `logs` directories. The manuscript does not require private or unreleased data for the claims described here.

## Code Availability

The project contains executable scripts for AISTAP-SIM full-asset evaluation, IPIX residual-aware fusion, SSDD supervised trainable-gate adaptation, and SSDD image-level and annotation-level bootstrap analysis. The key scripts include `evaluate_aistap_combined_full_asset_protocol.py`, `evaluate_ipix_validated_residual_fusion.py`, `evaluate_ssdd_external_trainable_gate.py`, and `evaluate_ssdd_image_level_bootstrap_ci.py`.

## Acknowledgements

Acknowledgements should be added by the authors before submission.

## Author Contributions

Author contributions should be completed by the authors before submission.

## Competing Interests

The authors should declare competing interests before submission.

## References

References should be inserted during journal formatting. This draft does not invent citations. Required reference groups include radar clutter suppression and low-rank methods, CFAR detection, AISTAP-SIM, Dartmouth IPIX sea-clutter recordings, SAR ship detection benchmarks, and target-preserving detection or weak-target radar learning where appropriate.
