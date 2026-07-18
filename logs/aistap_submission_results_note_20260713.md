# AISTAP Submission Results Note

Date: 2026-07-13

## Core claim

The public AISTAP-SIM sample supports a bounded claim: stronger low-rank suppression improves clutter attenuation, but it also increases weak-target loss, so the correct problem framing is target-preserving detection at low false-alarm rates.

## Quantitative anchors

- `simMed`: clutter attenuation rises from `2.197 dB` at `k=1` to `11.268 dB` at `k=20`, while target loss rises from `0.925 dB` to `13.906 dB`.
- `simWind`: clutter attenuation rises from `2.012 dB` at `k=1` to `9.339 dB` at `k=20`, while target loss rises from `0.925 dB` to `13.906 dB`.
- `Pfa=1e-4`: raw `Pd=0.0659`, low-rank residual `Pd=0.1667` at `k=20`.
- `Pfa=1e-3`: raw `Pd=0.2171`, low-rank residual `Pd=0.3837` at `k=20`.
- `Pfa=1e-2`: raw `Pd=0.3140`, low-rank residual `Pd=0.4690` at `k=5`.

## Manuscript use

- Use the low-rank sweep as the baseline evidence for target loss.
- Use the CFAR audit as the evidence for low-false-alarm operating behavior.
- Keep the public-sample boundary explicit.
- Do not write the sample as a final benchmark victory or a cross-dataset claim.

## Publication-facing wording

The public sample already shows why TP-SSCS needs an explicit target-preservation branch and CFAR calibration. Low-rank suppression alone is not a safe endpoint, because the gain in clutter attenuation comes with a large loss of weak-target energy. The new target-preservation diagnostics make that branch argument measurable: low-rank residuals still pay a target-loss tax, while oracle blend and oracle gate diagnostics show headroom and the best trainable-gate candidate (`rank=20`, `hidden=16`, `steps=150`) closes part of the gap, but all of them remain upper-bound or scaffold-bounded evidence rather than a finished detector. The minimal trainability check goes one step further: the scaffold can be optimized on a public-sample split, with loss decreasing and gate separation improving on validation, even though the resulting detector is still not finished. The stress grid closes the current experiment loop by showing that best `k` shifts under perturbation while the trainable gate remains finite and competitive. The manuscript presents the method as a target-preserving detector under a low-false-alarm operating point, not as a generic clutter canceller.

The five-reference gap audit then puts this evidence stack into comparison context: the paper is now closer to the strongest reference packages on evidence layering, but it still stops short of finished-detector closure or cross-dataset victory.
That comparison boundary is now carried through the manuscript draft, submission package, section-evidence map, README, STATUS, and claim matrix so the final package stays aligned with the measured evidence.
