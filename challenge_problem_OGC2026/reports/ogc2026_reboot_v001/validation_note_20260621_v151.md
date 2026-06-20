# Validation Note: `v151` Prob31-like Direct Stabilizer

- Validation date: `2026-06-21`
- Canonical wrapper under review:
  `ogc2026/baseline/alg_versions/reboot_v151_20260620_prob31like_direct_stabilizer_on_v142.py`

## Candidate closed

`reboot_v151_20260620_prob31like_direct_stabilizer_on_v142` is closed as
`rejected`.

- Representative block-tier smoke passed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v151_tier9_20260620_001/`
- Targeted `prob_31` smoke passed:
  `reports/ogc2026_reboot_v001/target_reboot_v151_prob31like_20260620_001/`
- Short-limit `45s` stress stayed scoreable:
  `reports/ogc2026_reboot_v001/stress_reboot_v151_prob31_short45_20260620_001/`
- Full40 failed:
  `reports/ogc2026_reboot_v001/full_reboot_v151_train40_20260620_001/`

## Failure headline

- accepted_for_score `37/40`
- timeout `3`
- invalid `0`
- reopened timeout rows:
  - `prob_32`
  - `prob_33`
  - `prob_37`

## Publish stance

Do not promote this as a recovery line or trusted BEST. The honest takeaway is
that the isolated prob31-like family can be stabilized, but the canonical
train40 blocker has shifted to the diffuse 3-bay lowproc runtime-risk family.
