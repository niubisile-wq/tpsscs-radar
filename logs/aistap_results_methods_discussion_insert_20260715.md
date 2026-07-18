# AISTAP Results / Methods / Discussion Insert

Date: 2026-07-15

## Results Insert

The fixed detector policy passed the official AISTAP-SIM full-asset protocol on both `simMed_test.mat` and `simWind_test.mat`. Together, the two assets contributed 210 target-bearing frames. Across the two assets and seven Pfa operating points, `tpsscs_finished_detector` beat both raw and `low_rank_residual_k30` on all 14 asset-level comparisons. In the combined full-asset gate, TP-SSCS also beat raw and low-rank on all seven Pfa points. At `Pfa=1e-5`, TP-SSCS reached `Pd=0.1845`, compared with raw `Pd=0.0800` and low-rank `Pd=0.1015`; at `Pfa=1e-2`, TP-SSCS reached `Pd=0.8678`, compared with raw `Pd=0.6551` and low-rank `Pd=0.8388`. Paired bootstrap confidence intervals over the 210 target-bearing frames were positive for mean delta Pd against both comparators at every Pfa point.

The IPIX external test separated unsupported zero-shot transfer from supported validation-selected fusion. Direct zero-shot transfer was negative: at `Pfa=1e-2`, raw reached `Pd=0.0364`, whereas the transferred finished detector reached `Pd=0.0086`. A residual-aware fusion policy selected on a separate validation recording passed on 12 disjoint held-out recordings, with 7/7 Pfa wins against raw and low-rank. At `Pfa=1e-2`, the fusion reached `Pd=0.1374`, compared with raw `Pd=0.0972` and low-rank `Pd=0.0096`.

The SSDD SAR test provided a second external radar-family check under supervised adaptation. The trainable-gate policy was trained on the official train split with a deterministic validation split and evaluated only on the official test split. On 231 test images and 545 ship annotations, the policy produced 4/7 wins, 3/7 ties, and 0 losses against raw, and 7/7 wins against low-rank. Image-level bootstrap analysis showed positive mean delta Pd against raw at all non-fallback Pfa points and positive mean delta Pd against low-rank at all Pfa points. Annotation-level results over the 545 ship instances showed the same qualitative pattern.

## Methods Insert

Official AISTAP-SIM full-asset validation used `simMed_test.mat` and `simWind_test.mat`. We evaluated every target-bearing frame under the same saved TP-SSCS candidate state and a fixed `tpsscs_finished_detector` policy. Raw maps and rank-matched low-rank residual maps served as comparators. For each Pfa point, thresholds were calibrated conservatively on background scores, and the protocol required empirical Pfa to remain within tolerance while improving detection probability against both comparators. The combined gate pooled the two official assets at the protocol level and computed paired bootstrap confidence intervals over target-bearing frames.

IPIX was used as an independent weak-target sea-clutter validation. We report direct zero-shot transfer as a negative boundary result. The positive IPIX protocol selected a residual-aware fusion coefficient on a validation recording and evaluated the fixed selected policy on 12 disjoint held-out recordings. Bootstrap summaries used recording-level units.

SSDD was used as a supervised external adaptation test on SAR ship imagery. A TP-SSCS-style pixel gate was trained on the official train split with a deterministic validation split and evaluated on the official test split only. Raw fallback was enforced for `Pfa <= 1e-4`; a learned gate was used at higher Pfa points. Aggregate test thresholds were calibrated globally on official-test background pixels outside dilated ship boxes. Image-level and annotation-level robustness analyses reused those fixed thresholds and therefore measured distributional robustness rather than per-image retuning.

## Discussion Insert

The added full-asset and external-validation results strengthen the paper without changing its claim boundary. The official AISTAP-SIM full-asset gate supports a finished in-domain detector protocol rather than only a public-sample scaffold. IPIX supports validation-selected residual-aware fusion but not direct zero-shot transfer. SSDD supports supervised external trainable-gate adaptation on a different radar image family, with image-level and annotation-level evidence that the gain is not only a pooled-pixel artifact. These distinctions should remain explicit in the main text because they prevent the central claim from drifting into unsupported universal transfer.

