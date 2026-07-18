# Second External Source Feasibility

Date: 2026-07-15

## Purpose

The remaining top-readiness hard failure is local-reference superiority, mainly because the local battery paper still has broader external-validation breadth. This audit checks whether a second independent radar source can be added immediately after the successful IPIX validation.

## RASPNet

- Main page probe succeeds: `logs/raspnet_page_20260715.html`.
- The public RASPNet page states that CVNN and EXAMPLES data are available for immediate download.
- The actual public-data-list endpoints redirect to a Public SDMS account login page:
  - `logs/raspnet_public_cvnn_list_20260715.html`
  - `logs/raspnet_public_examples_list_20260715.html`
- The GitHub Croissant metadata was also checked:
  - `logs/raspnet_examples_croissant_20260715.json`
  - `logs/raspnet_globus_root_index_20260715.html`
  - `logs/raspnet_globus_examples_index_20260715.html`
- Current status: not a one-click scriptable source in this shell without SDMS public-account login; the Globus guest collection currently returns `LOGIN_DENIED`.

## NetRAD

- The public dataset is visible in prior audit notes as a large UCL/Figshare dataset with a 122.73 GB download.
- The Figshare API was checked in `logs/netrad_figshare_api_20260715.json`; it exposes one file, `NetRAD.zip`, with size `131,781,942,836` bytes.
- Current status: feasible as a future large-data external source, but not a quick incremental validation in this turn.

## SSDD

- Official SSDD was downloaded through the official Google Drive link listed by the SSDD release page and unpacked locally under `data/downloads/ssdd/`.
- The official COCO-style train/test split is available locally.
- Validation result:
  - `logs/ssdd_external_trainable_gate_20260715.md`
  - `results/ssdd_external/ssdd_external_trainable_gate_20260715.json`
- Current status: successful second independent radar-family validation. The official-test result covers `231` images and `545` ship annotations, with 4/7 wins and 3/7 ties against raw, 0/7 losses against raw, and 7/7 wins against low-rank.

## IPIX

- IPIX is immediately scriptable and has already yielded one positive independent 12-recording held-out validation layer:
  - `logs/ipix_validated_residual_fusion_20260715.md`
  - `results/ipix_external/ipix_validated_residual_fusion_20260715.json`
- The result is positive across 12 held-out recordings but still one external dataset family.

## Conclusion

- The second independent external radar-family slot is now filled by SSDD.
- Future optional upgrades are:
  1. Add authenticated RASPNet public-account download and run a RASPNet external validation.
  2. Allocate storage/time for a NetRAD subset and run a third non-AISTAP external validation.
  3. Expand beyond the current IPIX 12-recording held-out suite only if a second IPIX protocol answers a distinct reviewer concern.

The current evidence is now enough to test the local-reference-superiority gate with two independent external radar families: IPIX and SSDD.
