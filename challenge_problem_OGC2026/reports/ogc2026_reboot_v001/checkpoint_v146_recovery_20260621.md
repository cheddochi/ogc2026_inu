# v146 Recovery Checkpoint

- Date context:
  `2026-06-21`
- Active rollback line restored to:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Candidate under review:
  `reboot_v146_20260621_0215_prob27like_efficiency_shortlist_on_v142`

## Why this is a recovery checkpoint

`v146` stayed fully scoreable, but the canonical wrapper full40 surface did not
preserve the claimed narrow-target behavior strongly enough to publish it as the
new trusted accepted BEST.

- Direct compare evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v146_train40_20260621_001/`
  - direct `v146` vs trusted `v142`
  - accepted_for_score `40/40` for both
  - avg objective `15035076.025 -> 15005778.05`
  - only changed row on that direct compare was `prob_27`

- Canonical publish-subset wrapper recheck:
  `reports/ogc2026_reboot_v001/verify_active_v146_publish_20260621_001/`
  - accepted_for_score `7/7`
  - `prob_27` reproduced at
    objective `74967337`, `T 5451`

- Canonical full wrapper recheck:
  `reports/ogc2026_reboot_v001/verify_active_v146_full40_20260621_001/`
  - accepted_for_score `40/40`
  - avg objective `15022631.925`
  - hidden-risk regressions reopened outside the intended target slice:
    - `prob_39`: `48160369 / T=3521 -> 48743275 / T=3563`
    - `prob_40`: `5780789 / T=8429 -> 5933401 / T=8658`

## Current judgment

- `v146` remains:
  `candidate`
- It is **not** published as the trusted accepted BEST.
- The last historical accepted BEST remains:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- But the current source tree is still in recovery, because an immediate tail
  recheck after restoring `v142` did not reproduce the historical trusted rows:
  `reports/ogc2026_reboot_v001/verify_active_v142_restore_tail_20260621_001/`
  - `prob_27` timed out
  - `prob_40` regressed to objective `14271151`, `T 21156`

## Historical evidence retained

- Trusted active full evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
- Trusted active publish rechecks:
  `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_001/`
  `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_002/`
- Team-shared historical benchmark report:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`

## Next work after this checkpoint

- Keep `v142` active.
- Stabilize the `v146` `prob_27` improvement so that a full canonical wrapper
  40-run keeps the gain without reopening `prob_39` and `prob_40`.
