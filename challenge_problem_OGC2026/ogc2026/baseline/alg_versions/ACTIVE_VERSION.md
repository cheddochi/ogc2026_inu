# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Status: trusted accepted BEST on the current tracked baseline_hh surface
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v123_tier10_20260620_002/`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v123_threebay_highproc_20260620_001/`
  - runtime-risk subset revalidation:
    `reports/ogc2026_reboot_v001/verify_v123_runtime_subset_20260620_001/`
  - wrapper + active publish revalidation:
    `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
- Current accepted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `59.416431s`
  - avg T/obj1 `1540.65`
  - avg L/obj2 `2674.325`
  - avg P/obj3 `4187.625`
  - avg objective `15071175.65`
- Promotion note:
  - Compared against the former trusted `v122`, `v123` keeps
    `accepted_for_score=40/40` and improves the official headline metrics:
    - avg T `1541.65 -> 1540.65`
    - avg L `2679.875 -> 2674.325`
    - avg P `4189.425 -> 4187.625`
    - avg objective `15084817.5 -> 15071175.65`
    - runtime max `57.913446 -> 59.416431`
  - Row-level changes versus `v122`:
    - improvement:
      - `prob_26`: objective `32253881 -> 31708207`, T `2345 -> 2305`
    - no T regressions on the remaining 39 rows
- Historical note:
  - `v123` is now the strongest accepted full-train line on this branch.
  - `v096` remains the last team-shared historical benchmark report reference:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Rollback target:
  `reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117`
- Canonical note:
  - the direct `baseline_hh` surface is the trusted score claim.
  - `myalgorithm.py` remains scoreable on the runtime-risk revalidation set,
    but it produced a slightly weaker accepted `prob_39` than the direct
    wrapper surface during `verify_active_v123_publish_20260620_001/`.
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - the active v123 selector stack is feature-based and time-aware.
  - inherited legacy fallback layers below some historical branches still
    contain older name-based branches; removing that legacy identity
    dependence remains future cleanup work.
