# v117 recovery plateau checkpoint after v119/v120 (2026-06-20)

## Decision

- This is a recovery/plateau checkpoint, not a trusted-accepted-BEST publish.
- The active surface remains:
  `ogc2026/baseline/baseline_hh.py -> reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- We are intentionally **not** republishing that active surface as a trusted
  BEST because fresh wrapper revalidation is still blocked.

## Trusted historical reference

- strongest historical accepted full evidence on the current branch:
  `reports/ogc2026_reboot_v001/full_reboot_v117_train40_20260620_001/`
  - accepted_for_score `40/40`
  - timed_out `0`
  - invalid `0`
  - avg objective `15085068.575`
  - avg T `1542.1`
  - avg L `2680.8`
  - avg P `4186.925`
  - runtime max `57.930979s`
- team-shared historical benchmark markdown:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`

## Why active publish is still blocked

- fresh wrapper revalidation path:
  `reports/ogc2026_reboot_v001/verify_active_v117_publish_20260620_001/`
- result:
  - accepted_for_score `1/3`
  - checker_feasible `3/3`
  - timed_out `2`
  - `prob_31`: runtime `61.996197s`
  - `prob_37`: runtime `60.427098s`
  - `prob_40`: accepted_for_score `true`

## Candidate outcome since the last checkpoint

- `reboot_v119_20260620_0635_highproc_pressure_shallow_portfolio_on_v117`
  - result: rejected
  - reason: stale selector; the candidate never actually fired on the intended
    high-proc tail family
- `reboot_v120_20260620_0705_highproc_tail_shallow_portfolio_on_v117`
  - result: rejected
  - reason: corrected selector fired, but the shallow direct-order rebuild
    hypothesis itself failed badly on the intended family
  - representative diagnostics:
    - `prob_25`: `T 2159 -> 8033`
    - `prob_27`: `5637 -> 19363`
    - `prob_38`: `11120 -> 124423`
    - `prob_26`: `2345 -> 14735`
    - `prob_40`: `8622 -> 106467`

## Minimal evidence for this plateau checkpoint

- active publish block:
  `reports/ogc2026_reboot_v001/verify_active_v117_publish_20260620_001/`
- trusted historical accepted full:
  `reports/ogc2026_reboot_v001/full_reboot_v117_train40_20260620_001/`
- v119 smoke / target:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v119_tier9_20260620_001/`
  - `reports/ogc2026_reboot_v001/target_reboot_v119_highproc_pressure_20260620_001/`
- v120 smoke / completion:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v120_tier9_20260620_001/`
  - `reports/ogc2026_reboot_v001/target_reboot_v120_prob26_prob40_20260620_001/`

## Next hypothesis boundary

- Do not start another fresh direct-order rebuild for the residual high-proc
  tail family.
- The next coherent hypothesis should stay warm-start-preserving and focus on
  bounded local moves / local repair on top of the `v117` solution.
