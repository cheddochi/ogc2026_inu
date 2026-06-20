# Recovery Checkpoint Publish Note (2026-06-21)

This checkpoint is a recovery/failure publish, not a trusted-BEST promotion.

## Why this is not a BEST publish

- The active wrapper still points to the historical rollback line:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Historical evidence for `v142` remains real:
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - `accepted_for_score=40/40`, timeout `0`, invalid `0`
- But the current source tree does not currently reproduce that trusted surface:
  - `reports/ogc2026_reboot_v001/verify_active_v142_restore_tail_20260621_001/`
  - `prob_27` timed out
  - `prob_40` regressed heavily
- The newer current-tree recovery parent `v152` once reclosed full40 scoreability:
  - `reports/ogc2026_reboot_v001/full_reboot_v152_train40_20260621_001/`
  - `accepted_for_score=40/40`
- However, the later current-tree recheck already reopened a runtime cliff on
  the same parent:
  - `reports/ogc2026_reboot_v001/verify_reboot_v158_prob31_prob33_prob40_20260621_001/`
  - `v152 prob_33` timed out at `62.243792s`

## Current candidate status

- `v158` is closed as rejected for promotion:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v158.md`
  - it improved the prob40-like family strongly, but its canonical full40 run
    failed at `accepted_for_score=39/40`

## Honest shared state after this checkpoint

- Historical accepted BEST evidence still exists and remains important:
  - `v142` is the last accepted/trusted historical line
- Current active wrapper is still only a recovery rollback line
- Current tree is in reliability recovery mode
- The next blocker to solve before any fresh BEST claim is the reopened
  prob33-like runtime cliff on the current-source delegated path

## Selected evidence bundled with this checkpoint

- Historical accepted references:
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/summary.json`
  - `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_002/summary.json`
  - `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Current-tree recovery references:
  - `reports/ogc2026_reboot_v001/full_reboot_v152_train40_20260621_001/summary.json`
  - `reports/ogc2026_reboot_v001/verify_active_v142_restore_tail_20260621_001/summary.json`
  - `reports/ogc2026_reboot_v001/full_reboot_v158_train40_20260621_001/summary.json`
  - `reports/ogc2026_reboot_v001/target_reboot_v158_prob40family_20260621_001/summary.json`
  - `reports/ogc2026_reboot_v001/verify_reboot_v158_prob31_prob33_prob40_20260621_001/summary.json`

