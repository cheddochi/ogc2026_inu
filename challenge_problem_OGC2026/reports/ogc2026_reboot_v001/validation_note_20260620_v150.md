# Validation Note: `v150` Rejection And Recovery Publish State

- Validation date: `2026-06-20`
- OGC python benchmark/probe/test overlap check: no active matching process was
  running at checkpoint time
- Canonical wrapper under review:
  `ogc2026/baseline/baseline_hh.py`

## Candidate closed

`reboot_v150_20260620_2315_prob33like_thin_gap_on_v142` is closed as
`rejected`.

- Representative smoke passed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v150_tier9_20260620_001/`
- Targeted `prob_33` rerun passed:
  `reports/ogc2026_reboot_v001/target_reboot_v150_prob33like_20260620_002/`
- Short-limit `45s` stress stayed scoreable:
  `reports/ogc2026_reboot_v001/stress_reboot_v150_prob33_short45_20260620_001/`
- Full40 failed:
  `reports/ogc2026_reboot_v001/full_reboot_v150_train40_20260620_001/`

## Failure headline

- accepted_for_score `37/40`
- timeout `3`
- invalid `0`
- reopened timeout rows:
  - `prob_31` at `75.27s`
  - `prob_32` at `66.25s`
  - `prob_37` at `90.03s`

## Publish stance

Do not publish the current active wrapper as a newly trusted BEST. The correct
team-visible state is:

1. historical accepted evidence still belongs to `v142`
2. the current tree is in recovery/revalidation mode
3. `v150` is documented as a rejected local attempt, not as a promoted line
