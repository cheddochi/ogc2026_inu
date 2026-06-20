# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132`
- Status: trusted accepted BEST on the current tracked baseline_hh surface
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v135_tier9_20260620_001/`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v135_prob40_headroom_20260620_001/`
  - short-limit subtype stress:
    `reports/ogc2026_reboot_v001/stress_reboot_v135_prob40_short45_20260620_001/`
  - active-surface publish revalidation:
    `reports/ogc2026_reboot_v001/verify_active_v135_publish_20260620_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v135_train40_20260620_001/`
- Current accepted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `58.418181s`
  - avg T/obj1 `1538.825`
  - avg L/obj2 `2683.325`
  - avg P/obj3 `4185.775`
  - avg objective `15069943.325`
- Promotion note:
  - Compared against trusted recovery `v132`, `v135` keeps
    `accepted_for_score=40/40` and improves the headline score metrics:
    - avg objective `15071175.65 -> 15069943.325`
    - avg T `1540.65 -> 1538.825`
    - avg P `4187.625 -> 4185.775`
    - avg L worsened `2674.325 -> 2683.325`, but the official objective still improved
    - runtime max `56.951463 -> 58.418181`
  - Row-level change versus `v132`:
    - `prob_40`: objective `5910122 -> 5860829`,
      `T 8622 -> 8549`, `L 4587 -> 4947`, `P 11897 -> 11823`
- Active-surface revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v135_publish_20260620_001/`
  - accepted `12/12`; timeout `0`, invalid `0`
  - representative rows remained scoreable
  - `prob_39` kept the stronger `v132` row:
    - objective `48160369`
    - `T=3521`
  - `prob_40` reproduced the accepted improvement:
    - objective `5860829`
    - `T=8549`
- Historical note:
  - `v123` remains the historical score-improving step over `v122`.
  - `v132` remains the last plateau-stable recovery line and rollback target.
  - `v133` remains a historical accepted improvement over `v132`, but only as
    non-active evidence because of the `prob_40` runtime cliff.
  - `v135` keeps the same train40 headline as historical `v133`, but with a
    direct active-surface revalidation that reproduced the `prob_40` gain.
- `v096` remains the last team-shared historical benchmark report reference:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Rollback target:
  `reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123`
- Canonical note:
  - the direct `baseline_hh` surface is the only canonical score-claim surface.
  - `v135` cleared direct active-surface revalidation on the representative
    publish subset.
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - the active v135 selector stack is feature-based and time-aware.
  - inherited legacy fallback layers below some historical branches still
    contain older name-based branches; removing that legacy identity
    dependence remains future cleanup work.
