# Recovery Checkpoint Publish Note (2026-06-21, post-v162 delegated-budget audit)

This checkpoint is a recovery/failure publish, not a trusted-BEST promotion.

## Why this is not a BEST publish

- The active wrapper still points to the historical rollback line:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Historical accepted evidence for that line still exists and remains the
  current historical-best reference:
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - `accepted_for_score=40/40`, timeout `0`, invalid `0`
- But the current source tree still does not reproduce that line as a fresh
  trustworthy BEST surface:
  - direct current-tree representative smoke reopened timeouts on
    `prob_27` and `prob_33`
  - `v161` recovered those target rows but timed out on non-target `prob_40`
  - `v162` repaired the non-target inherited budget cliff, but `prob_27`
    still timed out and `prob_6` regressed badly

## What v162 established

- `v162` is closed as rejected:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v162.md`
- The delegated-budget hypothesis was still informative:
  - `prob_33`: TIMEOUT under direct `v142` row -> PASS under `v162`
  - `prob_40`: PASS under both, with `v162` improving
    `18230025 / T=27087 -> 17499131 / T=25996`
- But the smoke still failed:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v162_tier9_20260621_001/`
  - `prob_27` remained TIMEOUT at `65.196941s`
  - `prob_6` regressed from `3991577 / T=118` to `16554568 / T=542`

## Honest shared state after this checkpoint

- Historical accepted BEST evidence still matters:
  - `v142` remains the last trusted historical accepted line
- Current active wrapper remains a recovery rollback surface only
- Current-tree wrapper behavior is still not trustworthy enough to publish as
  a revalidated BEST
- The next hypothesis should focus on the remaining `prob27-like` guarded path
  rather than claiming the parent surface is recovered

## Selected evidence bundled with this checkpoint

- Historical-best team-share reference:
  - `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Historical accepted full evidence already tracked in the repo:
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/summary.json`
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/readable_results.csv`
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/report.html`
- Current validation note:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v162.md`
- Current recovery-state smoke:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v162_tier9_20260621_001/summary.json`
  - `reports/ogc2026_reboot_v001/smoke_reboot_v162_tier9_20260621_001/readable_results.csv`
  - `reports/ogc2026_reboot_v001/smoke_reboot_v162_tier9_20260621_001/report.html`
