# AISTAP Low-Pfa Branch Dimension Scorecard

Date: 2026-07-13

## Branch under review

- `rank=30`
- `hidden=16`
- `steps=150`
- `lr=0.02`

## Dimension ledger

| Dimension | Current standing | Evidence anchor | What this means |
|---|---|---|---|
| Strict low-Pfa frontier | Ahead | `aistap_target_preservation_ablation_20260713.md`, `aistap_trainable_branch_strict_pfa_preference_20260713.md` | The branch is now the preferred manuscript-facing branch for the regime the paper actually studies. |
| Public-sample target-loss behavior | Ahead | `aistap_target_preservation_ablation_20260713.md`, `aistap_trainable_branch_results_discussion_paragraph_20260713.md` | The branch lowers target loss materially versus the low-rank residual baseline. |
| Stress robustness | Ahead / competitive | `aistap_stress_grid_20260713.md` | The branch stays finite and competitive under perturbation. |
| Repeat-seed stability | Ahead / competitive | `aistap_low_pfa_branch_multiseed_stability_20260713.md`, `aistap_low_pfa_branch_multiseed_paragraph_20260713.md` | The branch remains in the same bounded trainable regime across three checked seeds. |
| Trainable-branch specificity | Ahead | `aistap_trainable_branch_five_reference_verdict_20260713.md`, `aistap_trainable_branch_comparison_note_20260713.md` | The paper now has a concrete trainable branch, not only oracle diagnostics. |
| Submission closure | Behind | `aistap_final_submission_lock_20260713.md`, `aistap_objective_completion_audit_20260713.md` | The manuscript is locked, but the evidence class still does not justify a finished-detector claim. |
| Deployable target-preservation closure | Behind | `aistap_trainable_branch_five_reference_verdict_20260713.md`, `aistap_current_low_pfa_branch_comparison_summary_20260713.md` | The branch is concrete, but still scaffold-bounded. |
| Finished detector status | Behind | `tpsscs_minimal_train_note_20260713.md`, `aistap_objective_completion_audit_20260713.md` | The branch trains, but it is not a finished detector. |
| Cross-dataset victory | Behind | `aistap_five_reference_gap_audit_20260713.md`, `aistap_final_executive_comparison_summary_20260713.md` | The current work remains public-sample bounded. |

## Short verdict

The `rank=30, hidden=16, steps=150, lr=0.02` branch is the strongest current comparison asset for the low-false-alarm regime, but the paper still needs a deployable branch or finished detector result before any unconditional win claim is supportable.
