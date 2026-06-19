# Validation Checkpoint for v115

This checkpoint closes the prob31-like recovery cycle around
`reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114`.

## Closed hypothesis: `v115`

- version:
  `reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114`
- intent:
  take the runtime-stable `v114` prob31-like parent and reapply one tightly
  bounded displaced-block earlier-entry move so the official-limit row finally
  improves again without reopening the heavier `v111` chain
- outcome:
  candidate, not promoted to trusted BEST

Evidence:

1. target sanity
   - path:
     `reports/ogc2026_reboot_v001/target_reboot_v115_prob31_20260620_001/`
   - accepted_for_score `1/1`
   - `prob_31`: objective `40137295`, T `2776`, runtime `50.343847s`

2. representative smoke
   - path:
     `reports/ogc2026_reboot_v001/smoke_reboot_v115_tier9_20260620_001/`
   - accepted_for_score `9/9`
   - timeout `0`
   - invalid `0`

3. targeted sibling guard
   - path:
     `reports/ogc2026_reboot_v001/compare_v109_v115_prob31_prob36_prob40_20260620_001/`
   - accepted_for_score `6/6`
   - target row:
     - `prob_31`: objective `40328756 -> 40137295`
     - T `2792 -> 2776`
     - runtime about `49.71s -> 44.91s`
   - siblings:
     - `prob_36` unchanged at objective `1499988`
     - `prob_40` unchanged at objective `5910122`

4. short-limit stress
   - path:
     `reports/ogc2026_reboot_v001/stress_v109_v115_prob31_short45_20260620_001/`
   - accepted_for_score `2/2`
   - `prob_31 @ 45s`:
     - `v109`: objective `67601421`, runtime `36.621772s`
     - `v115`: objective `45309349`, runtime `36.787646s`

5. full train40
   - path:
     `reports/ogc2026_reboot_v001/full_reboot_v115_train40_20260620_001/`
   - accepted_for_score `40/40`
   - timeout `0`
   - invalid `0`
   - averages:
     - avg objective `15106365.725`
     - avg T `1545.1`
     - avg L `2616.85`
     - avg P `4189.15`
   - max runtime `58.029289s`

Interpretation:

- `v115` is the first current-source branch after the historical `v096` drift
  cycle that both keeps train40 `40/40` scoreability and improves the intended
  prob31-like official-limit row
- versus the prior current-source line `v109`, only one row changes and it
  changes in the intended direction
- however, the historical trusted `v096` checkpoint still holds the better avg
  objective:
  - historical `v096`: `15096298.7`
  - current-source `v115`: `15106365.725`

## Publish conclusion

- `v115` should be published as the leading current-source recovery candidate
- `v115` should not be published as a trusted accepted BEST
- `baseline_hh.py` should remain unchanged because the active wrapper is still
  reserved for accepted BEST only

## Next T-zero-first direction

- after the publish checkpoint, the next subtype should shift toward the
  residual prob37-like diffuse xlarge-lowproc gap on top of `v115`
- keep the new prob31-like recovery row intact while testing that next branch
