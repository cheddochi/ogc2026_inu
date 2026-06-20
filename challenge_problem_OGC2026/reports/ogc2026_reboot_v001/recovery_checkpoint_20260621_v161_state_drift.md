# Recovery Checkpoint Publish Note (2026-06-21, post-v161 same-process drift)

This checkpoint is a recovery/failure publish, not a trusted-BEST promotion.

## Why this is not a BEST publish

- The active wrapper still points to the historical rollback line:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Historical accepted evidence for that line still exists and remains the
  current historical-best reference:
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - `accepted_for_score=40/40`, timeout `0`, invalid `0`
- But the current source tree is still not trustworthy enough to publish the
  active wrapper as a fresh BEST on today's tree:
  - current-tree tail rechecks had already drifted away from the historical
    `v142` numbers
  - the `v159`/`v160` cycle had already shown the parent surface reopening
    runtime cliffs on `prob_27` and `prob_33`
  - `v161` now shows that even a trusted inherited non-target path can drift
    inside the same benchmark process

## What v161 established

- `v161` is closed as rejected:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v161.md`
- The joint runtime-guard hypothesis did recover the two intended runtime-risk
  families on the same smoke run:
  - `prob_27`: TIMEOUT under the direct `v142` row -> PASS under `v161`
  - `prob_33`: TIMEOUT under the direct `v142` row -> PASS under `v161`
- But the tier-representative smoke still failed:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v161_tier9_20260621_001/`
  - non-target `prob_40` timed out under `v161`

## Why the current active surface is still not publishable as BEST

- In the same smoke run, `v161 prob_40` should have delegated to the inherited
  `v142` path, yet it still diverged materially from the direct `v142 prob_40`
  row.
- A focused same-process probe then confirmed the hidden risk directly:
  - first `v142 prob_40`: objective `14986693`, `T=22233`
  - after intervening `v161 prob_27` and `v161 prob_33`
  - second `v142 prob_40`: objective `12726360`, `T=18840`
- That means the current blocker is broader than one feature-family selector:
  inherited mutable state or same-process drift is affecting the canonical
  wrapper surface on the current tree.

## Honest shared state after this checkpoint

- Historical accepted BEST evidence still matters:
  - `v142` remains the last trusted historical accepted line
- Current active wrapper remains a recovery rollback surface only
- The current tree should not be described as a freshly re-trusted BEST until
  a new canonical wrapper revalidation reproduces a stable scoreable surface
- The next hypothesis should target state stability before more tail-specific
  score chasing:
  - isolate or reset inherited mutable state, or
  - replace drifting delegated warm-start paths with stable direct builders

## Selected evidence bundled with this checkpoint

- Historical-best reference already tracked in the repo:
  - `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Historical accepted full evidence already tracked in the repo:
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/summary.json`
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/readable_results.csv`
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/report.html`
- Current recovery-state note:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v161.md`
- Current recovery-state smoke:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v161_tier9_20260621_001/summary.json`
  - `reports/ogc2026_reboot_v001/smoke_reboot_v161_tier9_20260621_001/readable_results.csv`
  - `reports/ogc2026_reboot_v001/smoke_reboot_v161_tier9_20260621_001/report.html`
