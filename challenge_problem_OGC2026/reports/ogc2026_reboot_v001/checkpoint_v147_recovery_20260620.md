# v147 Recovery / Failure Checkpoint

- Date context:
  `2026-06-20`
- Branch:
  `hh_algorithm_loop`
- Active wrapper line kept at:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Current trust state:
  historical accepted BEST evidence still belongs to `v142`, but the current
  source tree is under trust revalidation and must not be published as a fresh
  trusted BEST yet

## Why this checkpoint is not a BEST promotion

There was no overlapping OGC benchmark/probe/test process at checkpoint time.
The current tree still fails the trust requirement for a truthful BEST publish.

- `v146` remains candidate-only:
  - canonical wrapper full40 evidence improved avg objective versus historical
    `v142`
  - but it reopened non-target regressions on `prob_39` and `prob_40`
  - therefore it is not a trusted accepted BEST on the wrapper surface

- restored `v142` is still not freshly re-trusted on the current tree:
  - `reports/ogc2026_reboot_v001/verify_active_v142_restore_tail_20260621_001.csv`
    shows the restored wrapper tail recheck failed:
    - `prob_27` timed out
    - `prob_40` regressed badly
  - `reports/ogc2026_reboot_v001/verify_active_v142_restore_tail_90s_20260621_001.csv`
    shows the issue is not only a 60s budget artifact:
    - `prob_27` stayed weak
    - `prob_40` got worse

## v147 outcome

- Version:
  `reboot_v147_20260621_0915_prob40like_v001base_narrow_on_v146`
- Purpose:
  isolate the current-tree `prob40`-like Family B cliff by replacing the
  inherited warm-start chain with direct `v001` warm start plus bounded `v130`
  narrow repair
- Evidence:
  `reports/ogc2026_reboot_v001/smoke_reboot_v147_tier9_20260621_001/`
- Result:
  - the intended Family B row improved strongly:
    - `prob_40`: `15338466 / T=22755 -> 7117822 / T=10439`
  - but the representative smoke violated the scoreable gate:
    - `prob_27` timed out
    - `prob_31` timed out
- Judgment:
  `v147` is rejected at smoke gate and is preserved only as audit evidence, not
  as publishable active logic

## Additional small evidence retained in this checkpoint

- Warm-start decomposition summary:
  `reports/ogc2026_reboot_v001/diag_warmstart_v005_v006_v001_v142_tail_20260621_001.csv`
- Team-shared historical benchmark reference:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`

## What this checkpoint means

- This push records the current recovery truth honestly.
- It does **not** claim the current wrapper surface is a re-trusted BEST.
- The next hypothesis should first rebuild a runtime-stable parent on the
  current tree, especially for the Family A/runtime-risk rows, before replaying
  any Family B recovery attempt.
