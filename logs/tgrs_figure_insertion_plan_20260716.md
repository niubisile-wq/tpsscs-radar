# TGRS figure insertion plan, 2026-07-16

Main manuscript:

- `manuscripts/tgrs_tpsscs_nofig_20260715.tex`

Expected figure files:

- `figures/submitted/figure1_paradigm_shift.png`: paradigm shift from suppression-centric processing to target-preserving detection.
- `figures/submitted/figure2_target_preserving_principle.png`: target-preserving principle for structured-clutter suppression.
- `figures/submitted/figure3_tpsscs_architecture.png`: overall TP-SSCS detector architecture.
- `figures/submitted/figure4_local_gating_mechanism.png`: local adaptive target-preservation gating mechanism.
- `figures/submitted/figure5_experimental_protocol.png`: experimental protocol and evaluation pipeline.
- `figures/submitted/figure6_evidence_hierarchy.png`: evidence hierarchy and claim boundaries across radar domains.

Source mapping from the downloaded attachment images:

- `ChatGPT Image 2026年7月16日 00_05_16 (6).png` -> `figure1_paradigm_shift.png`
- `ChatGPT Image 2026年7月16日 00_05_15 (2).png` -> `figure2_target_preserving_principle.png`
- `ChatGPT Image 2026年7月16日 00_05_15 (1).png` -> `figure3_tpsscs_architecture.png`
- `ChatGPT Image 2026年7月16日 00_05_15 (3).png` -> `figure4_local_gating_mechanism.png`
- `ChatGPT Image 2026年7月16日 00_05_15 (4).png` -> `figure5_experimental_protocol.png`
- `ChatGPT Image 2026年7月16日 00_05_16 (5).png` -> `figure6_evidence_hierarchy.png`

Placement:

- Figure 1: Introduction, after the TP-SSCS concept paragraph.
- Figure 2: Problem Setting and Motivation, after the target-preservation failure-mode discussion.
- Figure 3: TP-SSCS method overview, before feature construction.
- Figure 4: Trainable Target-Preservation Gate, before false-alarm-calibrated detection.
- Figure 5: Experimental Protocol, before dataset descriptions.
- Figure 6: Results, after the external validation synthesis and before Discussion.

Compilation behavior:

- The TeX file uses a `\FigureOrPlaceholder` macro.
- If the expected PNG exists, it is included.
- If the PNG is absent, the PDF compiles with a placeholder box showing the missing path.
