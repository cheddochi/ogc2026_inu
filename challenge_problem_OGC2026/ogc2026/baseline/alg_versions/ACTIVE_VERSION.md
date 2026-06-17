# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v050_20260617_2015_prob38like_release_aware`
- Status: trusted active BEST
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v050_20260617_2015_prob38like_release_aware.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v050_core8_20260617_001/`
    `reports/ogc2026_reboot_v001/smoke_reboot_v050_targets_20260617_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v050_train40_20260617_001/`
- Current trusted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `42.293924s`
  - avg T/obj1 `1605.55`
  - avg L/obj2 `2679.125`
  - avg P/obj3 `4204.95`
  - avg objective `15372214.675`
- Recovery note:
  - `reboot_v051_20260617_2035_prob31like_deeper_preference` was demoted from
    active BEST after re-verification on `prob_31` produced two different
    accepted rows under the same committed source:
    - `reports/ogc2026_reboot_v001/verify_reboot_v051_prob31_current_20260617_001/`
      -> T `2825`, objective `40671512`
    - `reports/ogc2026_reboot_v001/verify_current_v051_prob31_20260617_001/`
      -> T `3784`, objective `53458849`
  - Until that timing-cliff behavior is repaired and re-benchmarked, v050 is
    the last reproducible trusted active BEST.
- Rollback target:
  `reboot_v039_20260617_1304_runtime_sensitive_budget_guard`
- Canonical note:
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - current BEST is feature-based and time-aware:
    it keys off problem features plus `timelimit`, not instance identity.
