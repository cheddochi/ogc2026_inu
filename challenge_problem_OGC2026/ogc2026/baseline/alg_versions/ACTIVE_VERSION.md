# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v050_20260617_2015_prob38like_release_aware`
- Status: active baseline, revalidated on current worktree
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v050_20260617_2015_prob38like_release_aware.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - current-source smoke:
    `reports/ogc2026_reboot_v001/smoke_active_v050_revalidate_20260617_001/`
  - current-source full:
    `reports/ogc2026_reboot_v001/full_active_v050_revalidate_20260617_001/`
  - smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v050_core8_20260617_001/`
    `reports/ogc2026_reboot_v001/smoke_reboot_v050_targets_20260617_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v050_train40_20260617_001/`
- Current trusted train40 result:
  - current-source revalidation:
    - `accepted_for_score=40/40`
    - `timed_out=0`
    - runtime max `57.853508s`
    - avg T/obj1 `3631.85`
    - avg L/obj2 `3205.7`
    - avg P/obj3 `4290.9`
    - avg objective `35310706.5`
  - historical checkpoint recorded at acceptance time:
    - runtime max `42.293924s`
    - avg T/obj1 `1605.55`
    - avg L/obj2 `2679.125`
    - avg P/obj3 `4204.95`
    - avg objective `15372214.675`
- Revalidation note:
  - The current tracked v050 source no longer matches the file hash recorded in
    the historical accepted run manifest.
  - Therefore the historical v050 checkpoint is preserved only as an archival
    benchmark reference, not as proof of current-source performance.
  - The current worktree truth for `baseline_hh.py -> v050` is the revalidated
    smoke/full evidence above, and future candidate comparisons should use that
    current-source baseline until a new source-consistent best is established.
- Recovery note:
  - `reboot_v051_20260617_2035_prob31like_deeper_preference` was demoted from
    active BEST after re-verification on `prob_31` produced two different
    accepted rows under the same committed source:
    - `reports/ogc2026_reboot_v001/verify_reboot_v051_prob31_current_20260617_001/`
      -> T `2825`, objective `40671512`
    - `reports/ogc2026_reboot_v001/verify_current_v051_prob31_20260617_001/`
      -> T `3784`, objective `53458849`
  - Until that timing-cliff behavior is repaired and re-benchmarked, v050 is
    the last selected active baseline, but its current-source behavior must be
    read from the revalidation artifacts rather than the historical acceptance
    checkpoint.
- Rollback target:
  `reboot_v039_20260617_1304_runtime_sensitive_budget_guard`
- Canonical note:
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - current BEST is feature-based and time-aware:
    it keys off problem features plus `timelimit`, not instance identity.
