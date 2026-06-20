# Recovery Checkpoint Publish Note (2026-06-21, post-v162 subtype audit)

This checkpoint is a recovery/plateau publish, not a trusted-BEST promotion.

## What remains trusted

- Historical accepted BEST evidence still points to:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Trusted full evidence bundle:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - `accepted_for_score=40/40`
  - timeout `0`
  - invalid `0`

## Why we are not publishing that active wrapper as BEST again

- Fresh current-tree recovery work has not revalidated the active wrapper as a
  live trustworthy BEST surface.
- `v161` and `v162` both stayed rejected on representative smoke:
  - `v161`: fixed target runtime rows but reopened non-target `prob_40`
  - `v162`: recovered `prob_33` and helped `prob_40`, but `prob_27` still
    timed out and `prob_6` regressed badly
- New subtype probes after `v162` still show recovery is incomplete:
  - `probe_v142_v072_xlarge_lowproc_20260621_001`
  - `target_v142_v143_xlarge_lowproc_20260621_001`
  - `probe_v142_v146_prob27like_20260621_001`

## Plateau summary

- No score-improving accepted candidate was promoted in this checkpoint window.
- Current useful signals:
  - delegated remaining-budget propagation is real and worth keeping as a tool
  - `prob27-like` has the cleanest direct recovery signal on the current tree
- Current blockers:
  - no current-tree canonical wrapper line has yet reproduced the historical
    trusted `v142` stability
  - sibling spillover remains the hidden-risk issue on narrow family repairs

## Next hypothesis

- Next T-first/runtime-first recovery hypothesis:
  - build a narrow `prob27-like`-only guard on top of the current rollback line
  - preserve the `v146` recovery on `prob_27`
  - explicitly avoid activating the same path on sibling `prob_25`

## Selected evidence bundled with this checkpoint

- Historical-best share note:
  - `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Historical trusted accepted evidence:
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/summary.json`
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/readable_results.csv`
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/report.html`
- Latest rejected candidate note:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v162.md`
- Latest current-tree active validation note:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_active_v142_subtype_audit.md`
- Plateau audit artifacts:
  - `reports/ogc2026_reboot_v001/subtype_analysis_v142_20260621_001/analysis.md`
  - `reports/ogc2026_reboot_v001/probe_v142_v146_prob27like_20260621_001/readable_results.csv`
  - `reports/ogc2026_reboot_v001/target_v142_v143_xlarge_lowproc_20260621_001/readable_results.csv`
