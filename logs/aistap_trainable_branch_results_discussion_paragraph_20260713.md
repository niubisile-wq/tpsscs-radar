# AISTAP Trainable-Branch Results/Discussion Paragraph

## Results paragraph

The strongest current trainable target-preservation branch for the low-false-alarm regime is `rank=30`, `hidden=16`, `steps=150`, with learning rate `0.02`. On the public target-bearing items, this branch cuts mean target loss from `6.191 dB` to `0.197 dB` and keeps clutter attenuation at `7.594 dB`; in the minimal trainability check, validation `Pd` at `Pfa=1e-2` rises from `0.9070` to `0.9767`, while the branch remains finite and competitive under the stress grid rather than collapsing. That makes it the first concrete manuscript-facing target-preservation branch rather than only an oracle upper bound.

## Discussion paragraph

This result changes the paper’s comparison position in a specific way: it moves target preservation from a diagnostic-only claim into a concrete trainable branch that improves the public-sample frontier while staying scaffold bounded. It strengthens the comparison against the reproducibility-first and protocol-sensitive references because the paper now has a measured branch, a nearby learning-rate sweep, and a stress-tested operating policy. It still does not justify a finished detector claim, deployable target-preservation closure, or unconditional victory over the five-reference set, so the right wording remains “real comparison asset” rather than “final winner.”
