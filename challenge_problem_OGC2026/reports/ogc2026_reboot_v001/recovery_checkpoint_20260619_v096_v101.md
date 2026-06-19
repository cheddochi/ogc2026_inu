# OGC2026 Recovery Checkpoint 2026-06-19

## Publication type

- recovery/failure checkpoint
- not a trusted accepted BEST publish

## Why this checkpoint exists

The branch currently contains a historical accepted frontier at
`reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`, but the
current source tree does not revalidate that trust claim. Before starting the
next candidate, this checkpoint records the evidence gap and the latest
source-consistent recovery attempt.

## Historical best evidence

- active historical frontier id:
  `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`
- historical full evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`
- historical accepted result:
  - accepted_for_score `40/40`
  - timeout `0`
  - avg objective `15096298.7`
  - avg T `1558.675`
  - avg L `2718.775`
  - avg P `4160.575`
  - runtime max `58.475376s`
- human-readable historical summary:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`

## Why current active is not published as trusted BEST

Current-source rechecks show runtime drift on the active chain:

- four-bay runtime recheck:
  `reports/ogc2026_reboot_v001/target_recheck_v096_fourbay_runtime_20260619_001/`
  - `prob_31`: timeout, runtime `70.680680s`, accepted_for_score `false`
- prob37 single-row recheck:
  `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/`
  - `prob_37`: timeout, runtime `71.377730s`, accepted_for_score `false`
- fallback current-source recheck:
  `reports/ogc2026_reboot_v001/full_recheck_v083_train40_20260619_001/`
  - accepted_for_score `39/40`
  - failing row: `prob_37`

Because of those rechecks, `baseline_hh.py -> v096` is treated as a recovery
surface only. It is not being published as a currently trusted active BEST.

## Latest recovery candidate

- candidate id:
  `reboot_v101_20260619_1425_prob38like_feature_budget_restore_on_v100`
- full evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v101_train40_20260619_001/`
- current-source train40 result:
  - accepted_for_score `40/40`
  - timeout `0`
  - avg objective `15291654.45`
  - avg T `1584.475`
  - avg L `2781.575`
  - avg P `4171.9`
  - runtime max `59.738994s`

## Recovery verdict

v101 is a successful scoreability recovery candidate, not a promotion
candidate.

- vs rejected recovery parent v100:
  - avg objective improved by `-2057448.925`
  - avg T improved by `-155.65`
- vs historical trusted v096:
  - avg objective worsened by `+195355.75`
  - avg T worsened by `+25.8`
  - dominant remaining regressions:
    - `prob_9`: `+2838679`
    - `prob_38`: `+2435338`
    - `prob_31`: `+1175683`
    - `prob_37`: `+504595`

## Next-step implication

The branch is back to a source-consistent `40/40` recovery candidate, but the
frontier is still below the historical accepted best. The next hypothesis
should preserve the v101 prob38 repair and target the new residual regression
cluster led by `prob_9`, while keeping the prob31/prob37 runtime recovery
intact.
