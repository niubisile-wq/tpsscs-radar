# AISTAP Low-Pfa Branch Multi-Seed Paragraph

## Results paragraph

The preferred low-false-alarm branch, `rank=30`, `hidden=16`, `steps=150`, `lr=0.02`, remains finite and competitive across three seeds (`7`, `11`, and `23`). Seed 7 gives train loss `0.0168`, validation gate gap `0.9211`, and mean Pd over `Pfa <= 1e-3` of `0.3442`; seed 11 is weaker but still stable, with train loss `0.0350`, validation gate gap `0.5006`, and mean Pd over `Pfa <= 1e-3` of `0.2930`; seed 23 returns to the stronger regime, with train loss `0.0169`, validation gate gap `0.9130`, and mean Pd over `Pfa <= 1e-3` of `0.3349`. Across all three seeds, `Pd` at `Pfa=1e-2` remains `0.9767`, so the branch is not a one-off seed artifact.

## Discussion paragraph

This repeat-seed check makes the current trainable branch a more credible comparison asset: it is not only preferred on a single run, but also remains in the same bounded trainable regime when the random seed changes. That strengthens the manuscript's strict low-Pfa evidence and reduces the risk that the preferred branch is an accidental local optimum. It still does not establish a finished detector or unconditional victory over the five-reference set, but it does make the trainable-branch comparison more robust than a single-seed result would.

