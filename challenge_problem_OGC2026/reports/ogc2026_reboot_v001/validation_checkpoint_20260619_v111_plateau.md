# Validation Checkpoint for v110 and v111

This checkpoint closes the post-`v109` recovery cycle without promoting a new
BEST.

## Closed hypothesis 1: `v110`

- version:
  `reboot_v110_20260619_2115_prob37like_fast_single_on_v109`
- intent:
  recover some of the remaining historical gap on the diffuse prob37-like row
  without reopening the broader 3-bay xlarge low-proc family
- outcome:
  rejected

Evidence:

1. targeted guard
   - path:
     `reports/ogc2026_reboot_v001/compare_v109_v110_prob37_prob38_prob39_long60_20260619_001/`
   - accepted_for_score `6/6`
   - target row:
     - `prob_37` objective unchanged at `17949088`
     - T unchanged at `4040`
   - off-target regression:
     - `prob_38` objective `166615156 -> 186785357`
     - T `12268 -> 13779`

Interpretation:

- the cheap prob37-like move no longer improves the `v109` warm start
- because the target stayed flat and a neighboring high-T family drifted worse,
  this branch should not proceed further

## Closed hypothesis 2: `v111`

- version:
  `reboot_v111_20260619_2130_prob31like_stable_direct_cap_on_v109`
- intent:
  stabilize the prob31-like direct builder by finishing the direct phase earlier
  and leaving more budget for the inherited repair chain
- outcome:
  plateau-side candidate only, not promoted

Evidence:

1. representative smoke
   - path:
     `reports/ogc2026_reboot_v001/smoke_reboot_v111_tier9_20260619_001/`
   - accepted_for_score `9/9`
   - timeout `0`
   - invalid `0`

2. targeted sibling guard
   - path:
     `reports/ogc2026_reboot_v001/compare_v109_v111_prob31_prob36_prob40_20260619_001/`
   - accepted_for_score `6/6`
   - target row:
     - `prob_31` objective held at `40328756`
     - T held at `2792`
   - siblings:
     - `prob_36` unchanged
     - `prob_40` unchanged

3. short-limit stress
   - path:
     `reports/ogc2026_reboot_v001/stress_v109_v111_prob31_short45_20260619_001/`
   - accepted_for_score `2/2`
   - `prob_31 @ 45s`:
     - `v109`: objective `40956985`, T `2836`
     - `v111`: objective `40935865`, T `2836`

Interpretation:

- `v111` is clean and scoreable
- it slightly improves the short-limit current-source row
- but at the official `60s` limit it only holds the already-good `v109` row
- without a real target-row breakthrough, a fresh full train40 would just spend
  benchmark budget without moving the frontier

## Publish conclusion

- no-score-improvement promotion this cycle
- keep `v109` as the leading current-source recovery candidate
- keep historical `v096` only as historical accepted evidence, not as a
  currently trusted active BEST

## Next T-first hypothesis direction

- do not reopen the prob37-like branch immediately
- do not claim a prob31-like promotion on stability alone
- next cycle should start from the plateau backlog:
  - either a prob33-like runtime-risk flatten that can safely support later T
    moves
  - or another feature-based structural family with stronger official-limit
    breakthrough evidence than `v111`
