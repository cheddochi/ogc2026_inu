# v118 candidate checkpoint (2026-06-20)

- candidate version:
  `reboot_v118_20260620_0835_prob31like_gap_hard_margin_on_v116`
- parent:
  `reboot_v116_20260619_2339_prob37like_early_chain_on_v115`
- active surface remains:
  `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- active publish state:
  blocked by fresh wrapper revalidation timeout cliff at
  `reports/ogc2026_reboot_v001/verify_active_v117_publish_20260620_001/`

## Why this checkpoint exists

The branch already published a recovery checkpoint for the failed active
revalidation of `v117`. Since then, `v118` was created as one coherent runtime
recovery hypothesis for the prob31-like subtype: keep the `v115` warm-start
gain, but require a harder remaining-time margin before replaying the final
`v070` concentrated-gap phase.

This note records the current candidate outcome before any next hypothesis is
started.

## Evidence

- targeted compare:
  `reports/ogc2026_reboot_v001/compare_v117_v118_prob31_prob37_prob40_20260620_001/`
- targeted prob31 rerun:
  `reports/ogc2026_reboot_v001/compare_v117_v118_prob31_rerun_20260620_001/`
- tier-representative smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v118_tier9_20260620_001/`
- full train40:
  `reports/ogc2026_reboot_v001/full_reboot_v118_train40_20260620_001/`

## Result

- smoke-9: accepted_for_score `9/9`, timeout `0`, invalid `0`
- full train40: accepted_for_score `40/40`, timeout `0`, invalid `0`
- avg objective: `15085068.575`
- avg T: `1542.1`
- avg L: `2680.8`
- avg P: `4186.925`
- runtime max: `58.311883`

## Comparison summary

- versus historical accepted `v117`:
  - objective/T/L/P rows match across full train40
  - direct reruns improve `prob_31` runtime
    (`52.80s -> 50.45s`, rerun `54.02s -> 50.90s`)
  - full train40 runtime max is slightly higher
    (`57.930979 -> 58.311883`) but still scoreable
- versus current-source `v116`:
  - only changed train40 row is `prob_31`
  - `prob_31` improves objective `40137295 -> 39589844`
  - `prob_31` improves T `2776 -> 2735`

## Current judgment

- decision: `candidate`
- not promoted to trusted accepted BEST yet

## Why not promoted yet

The underlying publish failure was an active-wrapper runtime reproducibility
cliff, not a score issue. `v118` looks promising as a recovery candidate, but
it has not yet been re-established as the trusted active surface with fresh
wrapper evidence through `baseline_hh.py` / active-source validation. Publishing
it as BEST right now would overstate what has actually been reproduced.

## Practical meaning for the next loop

- current historical strongest accepted full evidence still points to `v117`
  train40:
  `reports/ogc2026_reboot_v001/full_reboot_v117_train40_20260620_001/`
- current team-share-safe story remains:
  - active source trust is under runtime-cliff recovery
  - `v118` is the best next recovery candidate to validate/potentially promote
    before starting a different hypothesis
