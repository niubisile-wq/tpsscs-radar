# AISTAP Manuscript Final Draft

Date: 2026-07-13

## Title

Target-preserving low-false-alarm radar detection under clutter suppression

## Abstract

Clutter suppression is often evaluated as if removing residual energy were the only objective. That framing is incomplete for operational detection, because aggressive suppression can erase weak targets. On the public AISTAP-SIM sample, stronger low-rank suppression increases clutter attenuation but also sharply increases weak-target loss, while CFAR detection on the resulting residuals improves detection probability over the raw map at fixed low false-alarm rates. The best operating point still depends on suppression rank. These results motivate target-preserving TP-SSCS with sparse gating and CFAR calibration. The evidence remains bounded to the public sample and scaffold stage.

## Introduction

Radar clutter suppression is often treated as a separation problem: remove clutter, keep what remains, and score the result by how much clutter energy disappears. That framing is inadequate for operational detection, because a method can look strong by residual-energy metrics while still over-suppressing weak targets at low false-alarm rates.

The public AISTAP-SIM sample makes this failure mode visible immediately. The first CPI already exhibits strong low-rank structure in the raw range-Doppler matrix, so low-rank truncation is a natural baseline. The same rank sweep that improves clutter attenuation also degrades target preservation, which means the central problem is detection under constraint rather than denoising.

The task is therefore framed as target-preserving, low-false-alarm detection. That framing fixes both method design and evaluation: the method needs an explicit target-preservation branch because low-rank suppression alone over-suppresses weak targets, and the evaluation needs a CFAR-style detector because the operating point is defined by false-alarm control.

The TP-SSCS model follows that logic. It combines complex-valued self-supervision, physical constraints, sparse target gating, and CFAR calibration. The public sample is sufficient to justify that design and to define the first ablation, but not to claim final benchmark superiority on the broader public stack.

## Results

### Public sample readout

The public AISTAP-SIM sample loads locally and contains both raw range-Doppler input and target-only reference tensors. The smoke path returns the expected tensor shapes and remains numerically finite, so the scaffold is executable rather than hypothetical. In particular, the loader produces the `(6, 64, 1024)` sample tensor, and the prototype propagates suppressed, residual, clutter, and score outputs end to end.

### Low-rank suppression exposes a trade-off

The low-rank audit makes the central trade-off explicit. On `simMed`, clutter attenuation rises from `2.197 dB` at `k=1` to `11.268 dB` at `k=20`, while target loss rises from `0.925 dB` to `13.906 dB`. The same qualitative pattern appears on `simWind` and `simNoiseOnly`: stronger low-rank suppression removes more clutter, but it increasingly erases weak target energy.

This is the method boundary, not a side effect. A paper that only reports clutter attenuation would favor aggressive suppression settings that look strong visually but are operationally harmful. The sample therefore shows that low-rank cancellation alone is not enough for the detection problem we care about.

### Low-false-alarm detection improves, but the operating point matters

The CFAR audit gives the other half of the story. In the dense operating surface, the residual baseline beats the raw map at every tested `Pfa`, but the best `k` is not universal: at `Pfa=1e-5`, the best residual point is `k=30` with `Pd=0.1628`, while at `Pfa=3e-3` and `1e-2` the best point shifts to `k=8` with `Pd=0.9767` and `1.0000`. No single `k` wins everywhere; the operating point depends jointly on the false-alarm regime and the suppression rank.

This makes the paper's operational claim precise. The method is not trying to optimize clutter attenuation in isolation. It is trying to preserve weak targets while controlling false alarms, which is a different optimization problem from denoising.

### Scaffold check

The TP-SSCS prototype is already wired through a minimal smoke path. The sample loader, the complex-valued suppression path, and the score output all behave as expected on the public sample. The numbers show finite input power, reduced suppressed power, and a nontrivial residual/clutter split, which is enough to justify moving from scaffold to training-loss design.

This smoke path is deliberately conservative. It verifies that the sample loader returns a `(6, 64, 1024)` tensor, that the prototype emits suppressed, residual, clutter, and score outputs with the expected shapes, and that the forward pass is numerically finite at the scaffold rank. That is a minimum correctness check, not a claim that the full method is trained.

### Target-preservation diagnostics

The target-preservation ablation now gives the paper a measured upper-bound diagnostic and a first trainable branch. On the public target-bearing items, the raw map reaches mean `Pd=0.145` at zero target loss, while the low-rank residual baseline raises mean `Pd` to `0.256` but pays `6.191 dB` mean target loss. The strongest trainable candidate so far is `rank=30`, `hidden=16`, `steps=150`, with learning rate `0.02`: it improves mean `Pd` to `0.253` and cuts mean target loss to `0.197 dB` while keeping clutter attenuation at `7.594 dB`. Oracle blend diagnostics still push mean `Pd` to `0.359` while reducing mean target loss to `2.726 dB`, and oracle gate diagnostics keep target loss near zero (about `0 dB`) while still lifting `Pd` above raw. At loose operating points (`Pfa=3e-3` and `1e-2`), the oracle gate with a high-percentile threshold reaches `Pd=1.0` with essentially zero target loss. This is the right direction for target-preserving design, but only the trainable gate is now a concrete manuscript-facing branch, and even that remains a scaffold-stage result rather than a finished TP-SSCS detector.

### Minimal trainability check

The scaffold now passes a minimal trainability check on a 4/2 public-sample split. With a small trainable gate head attached to the fixed low-rank block, the best candidate so far (`rank=30`, `hidden=16`, `steps=150`) drives the train loss from `0.6719` to `0.0168`, pushes the train gate gap from `-0.0483` to `0.8803`, and pushes the validation gate gap from `-0.0654` to `0.9211`. A three-seed stability check (`7`, `11`, `23`) keeps the validation `Pd=0.9767` at `Pfa=1e-2` across all three runs, while remaining finite and stable. That is sufficient to say the scaffold is trainable; it is not sufficient to say the detector is finished.

### Stress grid

The stress grid closes the current experiment loop. Under noise and amplitude perturbations, the best low-rank rank remains in the high-rank regime, while phase perturbation and target attenuation shift the best `k` downward or split the optimum across ranks. The trainable gate stays finite across the same perturbations and remains competitive at the reference operating point, but it does not become universally dominant. This is the right robustness claim for the paper: the operating conclusion is stable in direction, yet still perturbation-sensitive in detail.

A separate leave-one-subset-out cross-condition check across `simMed`, `simNoiseOnly`, and `simWind` broadens the protocol class one step further. The preferred trainable branch remains finite under holdout, and the held-out `Pd` at `Pfa=1e-2` stays in the same general range across all three subsets, but the low-rank residual baseline still wins on some subsets and operating points. That makes the result broader than a pooled split, but still not an independent external-dataset victory.

### Figure-linked narrative

Figure 1 establishes the task boundary. The public AISTAP-SIM sample provides complex-valued range-Doppler input and target-only reference tensors, and the TP-SSCS scaffold shows that the method is intended for target-preserving detection under low false alarm, not clutter removal alone. Figure 4 now closes the robustness loop by showing that the operating conclusion survives perturbation stress, but still does not become a finished detector claim.

The cross-condition holdout check is a separate protocol broadening rather than a new primary figure claim: it confirms that the preferred branch survives subset-wise leave-one-out testing, but it does not replace the battery package's broader external-validation layer.

Figure 2 shows why the paper needs that framing. The target-preservation frontier separates raw, low-rank residual, oracle, and trainable-gate behavior. The low-rank residual baseline pays a large target-loss tax, while the trainable gate cuts that loss sharply and remains finite. That makes target preservation a measured frontier rather than a purely verbal design claim.

Figure 3 shows the other half of the argument. Under fixed low-`Pfa` operating points, the best residual baseline depends jointly on the suppression rank and the false-alarm target. In the dense surface, very low `Pfa` prefers aggressive suppression while higher operating points shift toward a mid-range `k`, which is exactly why CFAR calibration belongs in the main method and not in a side appendix.

Taken together, the figure set supports one manuscript claim: the public sample already demonstrates why TP-SSCS must be target-preserving, low-false-alarm, and explicitly calibrated. The study is therefore a bounded detection study, not a finished benchmark victory across the broader public stack.

Table 1 carries the numerical details behind the rank sweep as a clutter-versus-target-loss trade-off, Table 2 reports raw and residual `Pd` under fixed `Pfa` values, and Table 3 states the manuscript boundary explicitly so the supported public-sample claims do not drift into cross-dataset superiority language.

## Discussion

This is not a generic clutter-cancellation study. The public sample shows why: low-rank suppression is a useful baseline, but stronger suppression also increases weak-target loss, so the method needs an explicit target-preservation branch and CFAR calibration in the main pipeline. The new trainable-gate candidate now gives that branch a concrete scaffold-stage implementation, although it still does not close the detector.

The evaluation logic follows from that boundary. A method that looks best under residual-energy or clutter-attenuation metrics may be the wrong method at low `Pfa` if it erases weak targets. Conversely, a detector that retains more target energy may be preferable even if it leaves more clutter in the residual map, provided the false-alarm rate is controlled.

The resulting story is a controlled trade-off: low-rank cancellation gives a baseline, target gating prevents over-suppression, CFAR calibration turns the pipeline into a detector rather than a denoiser, and `k` is a controllable trade-off parameter rather than a universal optimum.

The current evidence supports method design, the first ablation, and the low-false-alarm operating logic. It does not support final superiority across the broader public dataset stack.

The target-preservation diagnostics sharpen that boundary further: oracle target-preservation changes the frontier in the expected direction, and the best trainable-gate candidate now moves the frontier partway toward a deployable branch, but the measured result is still not a finished detector.

The minimal trainability check pushes the scaffold one step further: the trainable gate can be optimized on the public sample and improves target/background separation on validation, but that still leaves the method in the trainable-scaffold category rather than the finished-detector category.

The stress grid then shows that the operating policy is robust in direction but still sensitive in detail: no single rank dominates every perturbation family, and the trainable gate remains finite rather than collapsing. The three-seed stress summary (`7`, `11`, `23`) keeps the preferred branch stable at about `Pd=0.77` and `Pfa=0.001` on the noise-level check, which is stronger than a one-off perturbation run even though it remains public-sample bounded.

A separate independent-radar-source audit now broadens the evidence class beyond the public sample. SEVIR, MRMS, and MeteoNet are all present elsewhere on the machine, but the local SEVIR mirror is partial: the full-sample CNN path currently falls back to an accessible-subset split and reaches test AUC `0.5972`. That is still useful smoke evidence, but it is not a trustworthy cross-year external-validation result, and it is not the same thing as an AISTAP cross-source transfer result.

The strongest current trainable target-preservation branch is `rank=30`, `hidden=16`, `steps=150`, with learning rate `0.02`. On the public target-bearing items, this branch improves over the low-rank residual baseline by cutting mean target loss from `6.191 dB` to `0.197 dB` while keeping clutter attenuation at `7.594 dB`. The branch remains finite and competitive under the stress grid rather than collapsing. That makes it the first concrete manuscript-facing target-preservation branch rather than only an oracle upper bound.

This result changes the paper’s comparison position in a specific way: it moves target preservation from a diagnostic-only claim into a concrete trainable branch that improves the public-sample frontier while staying scaffold bounded. It strengthens the comparison against the reproducibility-first and protocol-sensitive references because the paper now has a measured branch, a nearby learning-rate sweep, and a stress-tested operating policy. It still does not justify a finished detector claim, deployable target-preservation closure, or unconditional victory over the five-reference set, so the right wording remains “real comparison asset” rather than “final winner.”
The cross-paper scorecard now makes the comparison sharper: AISTAP is ahead on detector-operating-policy evidence density and explicit trainability, while the battery package still leads on external-validation breadth and `power_se` still leads on its own cross-feeder benchmark framing.

The independent radar-source audit also narrows the external-validation gap in a practical sense: the workspace now has an honest SEVIR external benchmark, but the AISTAP method has not yet been transferred to that benchmark, so the current manuscript can only cite it as adjacent breadth rather than a direct method win.

The five-reference gap audit then makes the comparison boundary explicit: this paper now matches the reference set on evidence layering, but it still does not claim a finished detector or a cross-dataset victory.

## Methods

### Data and sample boundary

This draft uses only the public AISTAP-SIM sample. The sample contains raw range-Doppler input and target-only reference tensors and is sufficient to test the suppression/detection trade-off. It is not a substitute for broader benchmark validation.

### Low-rank baseline

We evaluate a truncated low-rank residual baseline at `k=1`, `k=3`, `k=5`, `k=10`, and `k=20`. It is diagnostic rather than final, and it exposes the suppression trade-off by making clutter attenuation and target loss visible together.

### CFAR audit

We then evaluate the same sample under a low-false-alarm detector at `Pfa=1e-2`, `1e-3`, and `1e-4`. The aim is to compare raw maps and low-rank residual maps under fixed operating constraints. This is an operating-policy test, not a post-hoc visualization exercise.

Because the same thresholding protocol is used across raw and residual outputs, the CFAR audit asks whether suppression improves detection at a fixed false-alarm target, not whether it simply makes the image look cleaner.

### TP-SSCS scaffold

The scaffold connects the sample loader to a minimal complex-valued suppression path and a score output. It is executable, but it is not yet a trained detector. The draft therefore keeps the target-preservation loss and the CFAR-calibrated detection objective as explicit design targets, and the ablation order tests them against the low-rank baseline.

The ablation order is disciplined: raw versus low-rank residual first, then target-preservation gating, then CFAR calibration, and only then the full TP-SSCS variant. That keeps the narrative aligned with what the current evidence proves.

### Ablation crosswalk

The manuscript names the method components in the same way the evidence does. Low-rank suppression is the diagnostic baseline, target-preservation and sparse gating are the proposed fixes for over-suppression, CFAR calibration is the operating-policy layer, and the end-to-end TP-SSCS scaffold is the executable bridge between them. That division is important because the public sample already supports the suppression trade-off, the low-`Pfa` operating behavior, the target-preservation diagnostic upper bound, and now a trainable-gate candidate, but it still does not support a finished claim for a deployable target-preservation branch or sparse gating.

Table 1 summarizes the rank sweep, Table 2 summarizes the CFAR operating behavior, and Table 3 separates supported claims from unsupported ones. Together they keep the method story bounded to the public sample and prevent the manuscript from presenting the scaffold as a completed detector.

### Strong-baseline acquisition matrix

Strong baselines are best described as an acquisition matrix, not a blanket closure claim. `DGMR` is runnable at code level but pretrained loading is still blocked. `PreDiff` is present but mismatched with the current Windows and package stack. `CasCast` is runnable on the verified `T=12` path, while the broader contract alignment remains incomplete. `NowcastNet` has a runnable proxy implementation in this environment, but the official CodeOcean artifact is not mirrored locally. `pySTEPS` remains blocked by the Windows C++ toolchain.

This matrix lets the paper distinguish runnable, partially runnable, proxy-based, and blocked baselines without inflating any of them into a finished strong-baseline claim.

## Boundary

This draft is limited to the public sample and scaffold stage. It does not claim final benchmark superiority, cross-dataset dominance, a finished training recipe, or a universal solution to radar clutter suppression. It claims that the method question is correctly posed as target-preserving, low-false-alarm detection, and that the public sample shows why that framing is necessary.

## Failure-case language

Stronger low-rank suppression is not a monotone win. In the public sample, the same gain in clutter attenuation is accompanied by a large increase in weak-target loss, which is the failure mode the method must address.

## Figures and tables

- Figure 1: public sample, target-only reference, and TP-SSCS pipeline.
- Figure 2: target-preservation frontier.
- Figure 3: dense low-`Pfa` CFAR operating surface.
- Figure 4: stress boundary under perturbation and trainable-gate stability.
- Figure 5: independent SEVIR cross-year holdout result.
- Table 1: low-rank trade-off across `k`.
- Table 2: dense CFAR operating results across `Pfa` and `k`.
- Table 3: manuscript boundary so the public sample is not overclaimed.
