# Recovery Checkpoint Publish Note (2026-06-21, post-v166 coupled runtime plateau)

This checkpoint is a recovery/plateau publish, not a trusted-BEST promotion.

## What remains trusted

- Historical accepted BEST evidence still points to:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Trusted full evidence bundle:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - `accepted_for_score=40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15035076.025`
  - avg T `1532.125`

## Why the current active wrapper is not being published as BEST again

- The active wrapper still points to the historical rollback line:
  `ogc2026/baseline/baseline_hh.py -> v142`
- But the current tree has not re-earned trust as a freshly reproducible BEST
  surface.
- The current active metadata already reflects this:
  - `ogc2026/baseline/alg_versions/ACTIVE_VERSION.md`
  - `ogc2026/baseline/baseline_hh.py`

## What closed in this checkpoint window

- `v163` recovered the prob27-like runtime family on representative smoke, but
  still failed scoreability (`8/9`) and showed delegated non-target drift.
- `v164` proved that a pure delegate surface does not reproduce direct `v142`
  behavior on the current tree.
- `v165` proved that even a flattened main-module copy of `v142` still drifts
  materially on the current tree.
- `v166` recovered `prob_33`, but reopened `prob_27` timeout, leaving the same
  representative smoke at only `8/9 scoreable`.

## Interpretation

- The current blocker is not a single isolated row anymore.
- On the current tree, `prob27-like` and `prob33-like` behave like a coupled
  runtime-stability family.
- That makes the right next move a shared parent-stability hypothesis, not
  another one-row repair or another wrapper-stacking tweak.

## Selected evidence for teammates

- Historical team-shared benchmark report:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Historical trusted accepted evidence:
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/summary.json`
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/readable_results.csv`
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/report.html`
- Newly closed validation notes:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v163.md`
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v164.md`
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v165.md`
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v166.md`

## Next hypothesis

- Keep the active wrapper on historical `v142` rollback semantics until a fresh
  canonical revalidation closes cleanly again.
- Next candidate should target one coherent family:
  coupled `prob27-like` / `prob33-like` runtime stabilization on a direct,
  deterministic parent surface.
