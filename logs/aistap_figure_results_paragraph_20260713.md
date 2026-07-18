# AISTAP Figure-Linked Results Paragraph

Date: 2026-07-13

Figure 1 establishes the task boundary. The public AISTAP-SIM sample provides complex-valued range-Doppler input and target-only reference tensors, and the TP-SSCS scaffold shows that the method is intended for target-preserving detection under low false alarm, not clutter removal alone. Figure 4 closes the robustness loop by showing that the operating conclusion survives perturbation stress, while the scaffold remains trainable but not finished.

Figure 2 shows why the paper needs that framing. The target-preservation frontier separates raw, low-rank residual, oracle, and trainable-gate behavior: the low-rank residual baseline pays a large target-loss tax, while the trainable gate cuts that loss sharply and remains finite. The figure therefore turns the target-preservation argument into a measured frontier rather than a purely verbal design claim.

Figure 3 shows the other half of the argument. In the dense surface, the residual baseline beats the raw map at every tested `Pfa`, but the best residual setting depends jointly on the suppression rank and the false-alarm target. Very low `Pfa` prefers aggressive suppression, while higher operating points shift toward a mid-range `k`, which is exactly why CFAR calibration belongs in the main method and not in a side appendix.

The target-preservation ablation note complements this by showing that the low-rank residual baseline still pays a material target-loss tax, while oracle blend and oracle gate diagnostics expose headroom and the best trainable-gate candidate (`rank=30`, `hidden=16`, `steps=150`, `lr=0.02`) closes part of the gap without yet becoming a deployable detector.

The minimal trainability check then shows the scaffold can be optimized without numerical collapse: the best trainable gate candidate drives the validation gate gap upward and reaches `Pd=0.9767` at `Pfa=1e-2`, which is enough to call the scaffold trainable even though it is not yet a finished detector.

The stress grid closes the robustness loop: perturbing noise, amplitude, phase, target attenuation, and clutter scaling changes the best low-rank rank, but the trainable gate stays finite and competitive at the reference operating point instead of collapsing.

Taken together, the figure set supports one manuscript claim: the public sample already demonstrates why TP-SSCS must be target-preserving, low-false-alarm, and explicitly calibrated. The study is therefore a bounded detection study, not a finished benchmark victory across the broader public stack.

## Use in manuscript

- Place Figure 1 at the opening of the results section.
- Follow with Figure 2 to establish the suppression trade-off.
- Then use Figure 3 to show the low-`Pfa` operating behavior.
- Use Table 1 and Table 2 to make the trade-off and CFAR policy explicit.
- Use Table 3 to keep the public-sample boundary visible.

## Boundary note

This paragraph remains bounded to the public sample and scaffold stage. It is not a cross-dataset superiority claim.
