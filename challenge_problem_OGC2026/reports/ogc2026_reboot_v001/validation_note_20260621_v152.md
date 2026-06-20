# Validation Note: `v152` Runtime Backlog Direct Flatten

- Validation date: `2026-06-21`
- Canonical wrapper candidate:
  `ogc2026/baseline/alg_versions/reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151.py`

## Candidate closed

`reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151` is closed as
`rejected` for BEST promotion.

- Representative block-tier smoke passed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v152_tier11_20260621_001/`
- Targeted diffuse runtime-risk smoke passed:
  `reports/ogc2026_reboot_v001/target_reboot_v152_diffuse_runtime_20260621_001/`
- Short-limit `45s` stress showed residual risk:
  `reports/ogc2026_reboot_v001/stress_reboot_v152_diffuse_runtime_short45_20260621_001/`
- Full40 passed scoreable:
  `reports/ogc2026_reboot_v001/full_reboot_v152_train40_20260621_001/`

## Headline

- accepted_for_score `40/40`
- timeout `0`
- invalid `0`
- runtime max `59.53s`

## Publish stance

Do not replace the trusted active BEST with `v152`. The correct interpretation
is:

1. `v152` is a useful scoreable recovery parent on the current tree
2. historical `v142` still owns the trusted BEST claim
3. the next candidate should try to recover T quality on one family at a time
   from the `v152` surface
