# OGC 2026 Training Benchmark Report

## Summary

- Algorithm version: `reboot_v218_20260627_trackA_dense_fourbay_deep_chain_on_v217`
- Run id: `full_reboot_v218_train40_20260627_001`
- accepted_for_score: `40/40`
- timeout: `0`
- invalid/error: `0`
- Total Objective: `570068514`
- Avg Objective: `14251712.850`
- Total T: `59532`
- Avg T: `1488.300`
- Total L: `105568.0`
- Avg L: `2639.200`
- Total P: `167700.0`
- Avg P: `4192.500`
- Avg Runtime: `32.3985443`
- Max Runtime: `55.981264`

## Comparison vs Trusted v217

- Reference full bundle:
  `reports/ogc2026_reboot_v001/full_reboot_v217_train40_20260627_revalidate_002/`
- Total Objective: `570663294 -> 570068514`
- Avg Objective: `14266582.350 -> 14251712.850`
- Total T: `59562 -> 59532`
- Avg T: `1489.050 -> 1488.300`
- Total L: `105434.0 -> 105568.0`
- Total P: `167694.0 -> 167700.0`
- first20 Total T: `1542 -> 1512`
- T>0 count: `33 -> 33`
- high-T tail (`T>=1000`) sum: `56718 -> 56718`
- Improved rows:
  - `prob_11`: objective `8761210 -> 8565801`, `T 369 -> 360`
  - `prob_13`: objective `10783287 -> 10383916`, `T 547 -> 526`
- Worst regression: `none`

## Publish Recheck

- official baseline_hh subset bundle:
  `reports/ogc2026_reboot_v001/verify_active_v218_baseline_hh_file_20260627_001/`
- `accepted_for_score=18/18`, timeout `0`, invalid/error `0`
- direct / wrapper exact matches:
  - `prob_10`, `prob_11`, `prob_13`, `prob_19`,
    `prob_20`, `prob_33`, `prob_38`, `prob_40`
- drift note:
  - `prob_14` stayed accepted on both routes, but the inherited
    stable-fourbay multiblock branch diverged before the `v218`
    deep-chain stage:
    - direct recheck: objective `3795716`, `T 181`
    - wrapper recheck: objective `3901754`, `T 187`
  - the canonical scoring evidence therefore remains the direct full train40
    accepted bundle above.

## Decision

- Label: `accepted`
- Promotion: `promoted_to_active_baseline_hh`
- Reason:
  `v218` keeps the accepted `v217` surface intact on the long-fourbay and
  Family B guard rows while reducing first20 residual `T` on the dense
  four-bay `prob_11` / `prob_13` subtype pocket.
