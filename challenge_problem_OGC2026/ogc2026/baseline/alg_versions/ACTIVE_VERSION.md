# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- Status: current active recovery surface; publish trust is blocked by fresh
  revalidation timeouts on the current tracked source
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v117_tier9_20260620_001/`
  - targeted sibling guard:
    `reports/ogc2026_reboot_v001/compare_v116_v117_prob31_prob36_prob37_prob38_prob40_20260620_001/`
  - time-stress:
    `reports/ogc2026_reboot_v001/stress_v116_v117_prob31_prob40_short45_20260620_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v117_train40_20260620_001/`
- Fresh publish revalidation block:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v117_publish_20260620_001/`
  - result:
    - `accepted_for_score=1/3`
    - `timed_out=2`
    - `prob_31`: checker-feasible but runtime `61.996197s` > `60s`
    - `prob_37`: checker-feasible but runtime `60.427098s` > `60s`
    - `prob_40`: accepted_for_score `true`, runtime `52.389308s`
  - source-hash note:
    - the current `reboot_v117` file hash still matches the accepted full-run
      manifest, so the publish failure is a runtime reproducibility cliff, not
      a simple source mismatch inside the version file itself
- Current trusted accepted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `57.930979s`
  - avg T/obj1 `1542.1`
  - avg L/obj2 `2680.8`
  - avg P/obj3 `4186.925`
  - avg objective `15085068.575`
- Promotion note:
  - Compared against the former historical trusted `v096`, `v117` keeps
    `accepted_for_score=40/40` and improves the official headline metrics:
    - avg T `1558.675 -> 1542.1`
    - avg L `2718.775 -> 2680.8`
    - avg P `4160.575 -> 4186.925`
    - avg objective `15096298.7 -> 15085068.575`
    - runtime max `58.475376 -> 57.930979`
  - Row-level changes versus `v096`:
    - improvements:
      - `prob_31`: objective `39781302 -> 39589844`, T `2751 -> 2735`
      - `prob_40`: objective `6333528 -> 5910122`, T `9268 -> 8622`
      - `prob_3`: objective `213297 -> 188500`, T `1 -> 0`
    - residual regression:
      - `prob_37`: objective `17454197 -> 17644653`, T unchanged at `3961`
- Historical note:
  - `v117` still has the strongest historical accepted full-train evidence on
    this branch, but it is not safe to republish today as a trusted active
    BEST until the runtime cliff is repaired.
  - `v096` remains the last team-shared historical benchmark report reference:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Rollback target:
  `reboot_v116_20260619_2339_prob37like_early_chain_on_v115`
- Canonical note:
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - the active v117 selector stack is feature-based and time-aware.
  - inherited legacy fallback layers below some historical branches still
    contain older name-based branches; removing that legacy identity
    dependence remains future cleanup work.
