# v123 accepted promotion note

- Promoted version:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Promotion basis:
  - full train40 accepted:
    `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
  - representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v123_tier10_20260620_002/`
  - targeted subtype compare:
    `reports/ogc2026_reboot_v001/target_reboot_v123_threebay_highproc_20260620_001/`
  - runtime-risk subset revalidation:
    `reports/ogc2026_reboot_v001/verify_v123_runtime_subset_20260620_001/`
  - wrapper + active publish revalidation:
    `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_001/`

## Headline delta vs trusted v122

- accepted_for_score: `40/40 -> 40/40`
- timeout: `0 -> 0`
- avg objective: `15084817.5 -> 15071175.65`
- total T / obj1 sum: `61666 -> 61626`
- avg T / obj1 avg: `1541.65 -> 1540.65`
- avg L / obj2 avg: `2679.875 -> 2674.325`
- avg P / obj3 avg: `4189.425 -> 4187.625`
- runtime max: `57.913446 -> 59.416431`

## Per-instance movement vs v122

- improvement:
  - `prob_26`: objective `32253881 -> 31708207`, T `2345 -> 2305`
- T regressions:
  - none on the remaining 39 rows

## Hidden-risk note

- The official wrapper surface `baseline_hh.py` is scoreable on runtime-risk
  rows `prob_31`, `prob_37`, `prob_39`, `prob_40`.
- The `myalgorithm.py` active chain is also scoreable on the same set, but it
  returned a slightly weaker accepted `prob_39` result than the direct wrapper
  surface:
  - wrapper `prob_39`: objective `48160369`, T `3521`
  - active `prob_39`: objective `48598605`, T `3553`
- Since the requested official interface is `baseline_hh.algorithm(prob_info,
  timelimit)`, the direct wrapper surface remains the trusted score claim.
