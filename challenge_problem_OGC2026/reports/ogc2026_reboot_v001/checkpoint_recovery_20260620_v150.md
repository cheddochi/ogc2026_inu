# OGC2026 Recovery Checkpoint After `v150`

- Checkpoint date: `2026-06-20`
- Active wrapper surface: `ogc2026/baseline/baseline_hh.py`
- Active version id on the canonical wrapper surface:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Publish decision: `recovery/failure checkpoint`, not `trusted accepted BEST`

## Why this is not a BEST publish

The active wrapper is still the historical `v142` rollback line, but the
current source tree has not cleanly reproduced the historical trusted tail
behavior on a fresh canonical revalidation. The local `v150` candidate also
failed the scoreable full40 gate, so this checkpoint should document recovery
state rather than claim a new trusted BEST.

## Historical evidence that still matters

- Historical accepted BEST evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - accepted_for_score `40/40`
  - timeout `0`
  - avg objective `15035076.025`
  - avg T `1532.125`
- Team-shared historical markdown report:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`

## Current recovery evidence

- Current wrapper recovery subset:
  `reports/ogc2026_reboot_v001/verify_active_v142_recovery_subset_20260620_001/`
  - accepted_for_score `4/4`
  - timeout `0`
  - still drifted on historical tail rows (`prob_27`, `prob_33`, `prob_38`,
    `prob_40`)
- Rejected candidate full40:
  `reports/ogc2026_reboot_v001/full_reboot_v150_train40_20260620_001/`
  - accepted_for_score `37/40`
  - timeout `3`
  - invalid `0`
  - reopened runtime failures on `prob_31`, `prob_32`, `prob_37`

## Interpretation

`v150` did improve the isolated `prob33-like` repair stability relative to
`v149`, but the current tree still has a broader warm-start/runtime-risk
instability on the reopened family. That makes a recovery checkpoint the honest
publish state: historical `v142` evidence remains the last trusted accepted
reference, while the current active wrapper should still be treated as under
revalidation.

## Next repair direction

The next coherent hypothesis should target runtime-family stabilization for the
reopened lowproc/tight/runtime-risk rows before spending another iteration on
narrower `prob33-like` local repair tuning.
