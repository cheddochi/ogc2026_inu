# Checkpoint: v145 Plateau, v142 Still Trusted

- Date: 2026-06-20
- Branch: `hh_algorithm_loop`
- Trusted active BEST:
  `ogc2026/baseline/baseline_hh.py -> reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Trusted full evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15035076.025`
  - avg T `1532.125`

## What closed in this checkpoint

- Candidate:
  `reboot_v145_20260621_0045_prob38like_bounded_pair_quantile_on_v142.py`
- Family:
  prob38-like `3-bay xlarge high-proc concentrated`
- Decision:
  rejected as plateau / no-op

## Why it was rejected

- Representative smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v145_tier10_20260621_001/`
  - accepted_for_score `20/20`
  - timeout `0`
  - invalid `0`
  - `prob_38` unchanged at `151254848 / T=11120`
  - `prob_40` unchanged at `5780789 / T=8429`
- Target subtype smoke:
  `reports/ogc2026_reboot_v001/target_reboot_v145_prob38like_20260621_001/`
  - accepted_for_score `6/6`
  - timeout `0`
  - invalid `0`
  - `prob_26`, `prob_33`, `prob_38` all unchanged
- Net effect:
  the bounded pair repair stayed scoreable but did not improve objective or T,
  and it added small runtime overhead on the activated rows

## Publish interpretation

- This is not a new BEST publish.
- The trusted accepted BEST remains `v142`.
- This checkpoint exists to preserve the closed rejection evidence, keep the
  active/trusted story reproducible, and document the next search direction.

## Next hypothesis

- Stop spending more budget on the current prob38-like pair-removal line.
- Pivot back to the `2-bay concentrated high-tail` family, where the trusted
  `v136` trace still showed scoreable intermediate improvements before the
  current `v142` final move.
