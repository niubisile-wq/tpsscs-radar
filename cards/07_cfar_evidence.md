# CFAR Evidence

## Current result on the public AISTAP sample

The sample-level CFAR audit shows that a simple low-rank residual baseline improves detection probability over the raw RD map at fixed false-alarm rates, but the improvement is not free: target loss increases as the suppression rank grows.

## Quantitative pattern

- At `Pfa=1e-3`, the raw map is weaker than the low-rank residual variants.
- At `Pfa=1e-4`, the low-rank residual baseline still helps Pd, but the gains are smaller and target loss becomes a sharper concern.
- Larger `k` values improve clutter suppression while making target retention progressively worse.

## Paper implication

- The TP-SSCS design needs an explicit target-preserving branch.
- Detection must be evaluated at fixed low Pfa, not just by image quality or clutter attenuation.
