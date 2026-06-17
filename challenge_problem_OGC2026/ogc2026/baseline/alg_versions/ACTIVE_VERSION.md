# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v051_20260617_2035_prob31like_deeper_preference`
- Status: trusted active BEST
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v051_20260617_2035_prob31like_deeper_preference.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v051_core8_20260617_001/`
    `reports/ogc2026_reboot_v001/smoke_reboot_v051_targets_20260617_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v051_train40_20260617_001/`
  - previous trusted full:
    `reports/ogc2026_reboot_v001/full_reboot_v050_train40_20260617_001/`
- Current trusted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `42.410634s`
  - avg T/obj1 `1605.275`
  - avg L/obj2 `2772.825`
  - avg P/obj3 `4190.9`
  - avg objective `15365077.85`
- Improvement versus prior trusted v050:
  - avg T/obj1 `1605.55 -> 1605.275`
  - avg L/obj2 `2679.125 -> 2772.825`
  - avg P/obj3 `4204.95 -> 4190.9`
  - avg objective `15372214.675 -> 15365077.85`
  - avg runtime `19.071262425 -> 19.300749275`
  - runtime max `42.293924 -> 42.410634`
  - improved row:
    - `prob_31`: T `2836 -> 2825`, objective `40956985 -> 40671512`
  - no timeout rows
  - no infeasible or unaccepted rows
  - no T regressions and no objective regressions versus v050.
- Targeted rule note:
  - The new class currently matches `prob_31` only.
  - `prob_31` improved under the official benchmark:
    - T `2836 -> 2825`
    - objective `40956985 -> 40671512`
  - `prob_38` and `prob_40` stayed unchanged:
    - `prob_38`: T `11212`, objective `152453868`
    - `prob_40`: T `9542`, objective `6517538`
- Rollback target:
  `reboot_v050_20260617_2015_prob38like_release_aware`
- Canonical note:
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - current BEST is feature-based and time-aware:
    it keys off problem features plus `timelimit`, not instance identity.
