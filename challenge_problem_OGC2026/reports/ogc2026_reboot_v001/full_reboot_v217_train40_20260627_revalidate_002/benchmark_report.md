# OGC 2026 Training Benchmark Report

## Summary

- Algorithm version: `reboot_v217_20260627_trackA_prob19_long_fourbay_repair_on_v212`
- Run id: `full_reboot_v217_train40_20260627_revalidate_002`
- accepted_for_score: `40/40`
- timeout: `0`
- invalid/error: `0`
- Total Objective: `570663294`
- Avg Objective: `14266582.350`
- Total T: `59562`
- Avg T: `1489.050`
- Total L: `105434.0`
- Avg L: `2635.850`
- Total P: `167694.0`
- Avg P: `4192.350`
- Avg Runtime: `32.0249097`
- Max Runtime: `56.301089`

## Comparison vs Trusted v212

- Reference full bundle:
  `reports/ogc2026_reboot_v001/full_reboot_v212_train40_20260627_001/`
- Total Objective: `570842085 -> 570663294`
- Avg Objective: `14271052.125 -> 14266582.350`
- Total T: `59579 -> 59562`
- Avg T: `1489.475 -> 1489.050`
- Total L: `105329.0 -> 105434.0`
- Total P: `167678.0 -> 167694.0`
- first20 Total T: `1559 -> 1542`
- T>0 count: `33 -> 33`
- high-T tail (`T>=1000`) sum: `56718 -> 56718`
- Improved rows:
  - `prob_19`: objective `2325874 -> 2147083`, `T 164 -> 147`
- Worst regression: `none`

## Revalidation

- Initial full run drift bundle:
  `reports/ogc2026_reboot_v001/full_reboot_v217_train40_20260627_001/`
- The first full run hit a one-off `prob_39` timeout.
- Targeted recheck bundle:
  `reports/ogc2026_reboot_v001/recheck_v217_prob39_20260627_001/`
- The targeted recheck brought both trusted `v212` and candidate `v217` back
  under the official 60s limit on `prob_39`, so this revalidated full bundle is
  the canonical evidence.

## Decision

- Label: `accepted`
- Promotion: `promoted_to_active_baseline_hh`
- Reason:
  `v217` preserves the trusted `v212` surface outside the targeted long
  four-bay subtype and reduces residual first20 `T` on `prob_19` while
  revalidating at `40/40` accepted_for_score.
