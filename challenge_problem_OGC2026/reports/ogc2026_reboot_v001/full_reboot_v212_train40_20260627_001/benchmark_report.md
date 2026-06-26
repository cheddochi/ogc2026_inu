# OGC 2026 Training Benchmark Report

## Summary

- Algorithm version: `reboot_v212_20260627_trackA_reserved_specialist_budget_on_v210`
- Run id: `full_reboot_v212_train40_20260627_001`
- accepted_for_score: `40/40`
- timeout: `0`
- invalid/error: `0`
- Total Objective: `570842085`
- Avg Objective: `14271052.125`
- Total T: `59579`
- Avg T: `1489.475`
- Total L: `105329.0`
- Avg L: `2633.225`
- Total P: `167678.0`
- Avg P: `4191.950`
- Avg Runtime: `32.082798225`
- Max Runtime: `56.143512`

## Comparison vs Trusted v210

- Reference full bundle:
  `reports/ogc2026_reboot_v001/full_revalidate_reboot_v210_train40_20260626_001/`
- Total Objective: `571093512 -> 570842085`
- Avg Objective: `14277337.800 -> 14271052.125`
- Total T: `59590 -> 59579`
- Avg T: `1489.750 -> 1489.475`
- Total L: `105329.0 -> 105329.0`
- Total P: `167678.0 -> 167678.0`
- first20 Total T: `1570 -> 1559`
- T>0 count: `33 -> 33`
- high-T tail (`T>=1000`) sum: `56718 -> 56718`
- Improved rows:
  - `prob_11`: objective `9012637 -> 8761210`, `T 380 -> 369`
- Worst regression: `none`

## Decision

- Label: `accepted`
- Promotion: `promoted_to_active_baseline_hh`
- Reason:
  `v212` preserves the trusted `v210` runtime-cliff guards while making the
  earlier specialist budget reservation reproducible on the official wrapper
  surface, so the small Track A `T` gain is now publish-trustworthy.
