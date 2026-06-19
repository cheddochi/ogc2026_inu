# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117`
- Status: trusted accepted BEST on the current tracked source
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v122_tier9_20260620_001/`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v122_twobay_tail_20260620_001/`
  - wrapper-surface revalidation:
    `reports/ogc2026_reboot_v001/verify_v122_wrapper_surface_20260620_001/`
  - active publish revalidation:
    `reports/ogc2026_reboot_v001/verify_active_v122_publish_20260620_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v122_train40_20260620_001/`
- Fresh active publish revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v122_publish_20260620_001/`
  - result:
    - `accepted_for_score=3/3`
    - `timed_out=0`
    - `prob_31`: runtime `50.782691s`
    - `prob_37`: runtime `50.511056s`
    - `prob_40`: runtime `44.316299s`
- Current trusted accepted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `57.913446s`
  - avg T/obj1 `1541.65`
  - avg L/obj2 `2679.875`
  - avg P/obj3 `4189.425`
  - avg objective `15084817.5`
- Promotion note:
  - Compared against the former trusted `v117`, `v122` keeps
    `accepted_for_score=40/40` and improves the official headline metrics:
    - avg T `1542.1 -> 1541.65`
    - avg L `2680.8 -> 2679.875`
    - avg P `4186.925 -> 4189.425`
    - avg objective `15085068.575 -> 15084817.5`
    - runtime max `57.930979 -> 57.913446`
  - Row-level changes versus `v117`:
    - improvement:
      - `prob_25`: objective `1499211 -> 1489168`, T `2159 -> 2141`
    - no T regressions on the remaining 39 rows
- Historical note:
  - `v122` is now the strongest accepted full-train line on this branch.
  - `v096` remains the last team-shared historical benchmark report reference:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Rollback target:
  `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- Canonical note:
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - the active v122 selector stack is feature-based and time-aware.
  - inherited legacy fallback layers below some historical branches still
    contain older name-based branches; removing that legacy identity
    dependence remains future cleanup work.
