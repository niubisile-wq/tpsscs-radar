# AISTAP Manuscript Skeleton

Date: 2026-07-13

## Working title

Target-preserving low-false-alarm radar detection under clutter suppression

## Abstract skeleton

Public radar clutter suppression is often evaluated as a denoising problem, but the operational question is whether weak targets survive under a low-false-alarm detector. We show on the public AISTAP-SIM sample that stronger low-rank suppression can reduce clutter while sharply increasing target loss, so clutter cancellation alone is not enough. A CFAR-style audit confirms that low-rank residual baselines improve detection probability over the raw map at fixed low `Pfa`, but the best operating point depends on the suppression rank. These results motivate a target-preserving branch and a CFAR-calibrated detection head for the TP-SSCS design. The paper remains bounded to the public sample and scaffold stage until broader public datasets and cross-dataset validation are complete.

## Introduction skeleton

- Radar clutter suppression is framed as a detection problem with explicit target preservation, not as a pure separation or image-denoising task.
- In the public sample, low-rank suppression exposes a clear trade-off: more clutter attenuation also means more weak-target loss.
- Therefore, the relevant paper question is whether a method can preserve targets while holding false alarms low.
- This motivates TP-SSCS: a target-preserving branch, sparse gating, and CFAR calibration.

## Results skeleton

### 1. Public sample audit

- The AISTAP-SIM sample is locally readable and contains both raw RD input and target-only reference tensors.
- The sample already exhibits strong low-rank structure in the first CPI.

### 2. Low-rank trade-off

- On `simMed`, clutter attenuation rises from `2.197 dB` at `k=1` to `11.268 dB` at `k=20`.
- Over the same sweep, target loss rises from `0.925 dB` to `13.906 dB`.
- The same qualitative trade-off appears on `simWind` and `simNoiseOnly`.

### 3. Low-Pfa CFAR audit

- At `Pfa=1e-4`, the low-rank residual baseline improves Pd from `0.0659` on the raw map to `0.1667` at `k=20`.
- At `Pfa=1e-3`, the low-rank residual baseline improves Pd from `0.2171` to `0.3837`.
- At `Pfa=1e-2`, the best reported residual setting reaches `Pd=0.4690` at `k=5`, showing that the operating point is rank dependent.

### 4. Scaffold check

- The minimal TP-SSCS prototype runs end to end on the sample.
- The smoke path is numerically finite and returns the expected tensor shapes.

## Discussion skeleton

- Low-rank suppression is a useful baseline, but not a sufficient solution.
- Target gating is needed to prevent over-suppression of weak targets.
- CFAR calibration is what turns the method into a deployable detector instead of a denoising toy.
- The manuscript treats `k` as a controlled trade-off parameter, not as a universal optimum.

## Boundary skeleton

- This note is limited to the public AISTAP sample and scaffold stage.
- It does not claim final benchmark superiority on the full public dataset stack.
- It does not claim cross-dataset victory until the broader benchmark layer is complete.

## Manuscript status

- The skeleton already supports a proper manuscript draft with Methods, Ablations, and failure-case language.
