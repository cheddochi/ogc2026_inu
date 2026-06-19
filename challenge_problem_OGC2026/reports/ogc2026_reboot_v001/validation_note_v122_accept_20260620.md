# Validation Note: v122 Accepted Promotion (2026-06-20)

## Candidate

- version:
  `reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117`
- parent:
  `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- subtype:
  two-bay concentrated high-proc tail

## Evidence

- representative smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v122_tier9_20260620_001/`
- targeted subtype smoke:
  `reports/ogc2026_reboot_v001/target_reboot_v122_twobay_tail_20260620_001/`
- full train40:
  `reports/ogc2026_reboot_v001/full_reboot_v122_train40_20260620_001/`
- wrapper-surface revalidation:
  `reports/ogc2026_reboot_v001/verify_v122_wrapper_surface_20260620_001/`
- active publish revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v122_publish_20260620_001/`

## Outcome

- full train40:
  - accepted_for_score `40/40`
  - timed_out `0`
  - invalid `0`
  - avg objective `15084817.5`
  - avg T `1541.65`
  - avg L `2679.875`
  - avg P `4189.425`
  - runtime max `57.913446s`
- wrapper revalidation:
  - accepted_for_score `3/3`
  - timed_out `0`
  - `prob_31`: `51.764056s`
  - `prob_37`: `49.520564s`
  - `prob_40`: `43.664123s`
- active publish revalidation:
  - accepted_for_score `3/3`
  - timed_out `0`
  - `prob_31`: `50.782691s`
  - `prob_37`: `50.511056s`
  - `prob_40`: `44.316299s`

## Comparison vs v117

- improvements:
  - total T `61684 -> 61666`
  - avg T `1542.1 -> 1541.65`
  - avg objective `15085068.575 -> 15084817.5`
  - avg L `2680.8 -> 2679.875`
  - runtime max `57.930979 -> 57.913446`
- per-instance T improvement:
  - `prob_25`: `2159 -> 2141`
- regressions:
  - no T regressions on the remaining 39 rows
  - avg P rises slightly `4186.925 -> 4189.425`, but official objective still improves

## Decision

- decision: `accepted`
- promotion:
  - `baseline_hh.py` and `ACTIVE_VERSION.md` should point to `v122`
  - the active wrapper now clears the runtime-risk publish subset directly,
    so `v122` is trusted not only as a version-file benchmark winner but also
    as the current active submission surface
