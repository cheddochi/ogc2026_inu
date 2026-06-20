# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v133_20260620_1705_prob40like_narrow_quantile_on_v132`
- Status: active working line under recovery validation; historical accepted evidence exists, but the latest publish revalidation did not reproduce the `prob_40` gain consistently enough for a trusted BEST publish checkpoint
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v133_20260620_1705_prob40like_narrow_quantile_on_v132.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v133_tier9_20260620_001/`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v133_prob40like_20260620_001/`
  - short-limit subtype stress:
    `reports/ogc2026_reboot_v001/stress_reboot_v133_prob40like_short45_20260620_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v133_train40_20260620_001/`
- Current accepted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `56.899351s`
  - avg T/obj1 `1538.825`
  - avg L/obj2 `2683.325`
  - avg P/obj3 `4185.775`
  - avg objective `15069943.325`
- Latest publish revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v133_publish_20260620_002/`
  - accepted `12/12`; timeout `0`, invalid `0`
  - representative rows stayed scoreable and `prob_39` kept the strong row
  - `prob_40` reverted from the accepted full-train row
    `5860829 / T=8549` back to `5910122 / T=8622`
  - log evidence shows the direct `baseline_hh.py` surface skipped the
    narrow quantile move on that rerun because runtime headroom fell short:
    `skip_prob40like_guard ... remaining=12.48s reserve=4.80s`
- Promotion note:
  - Compared against former active `v132`, `v133` keeps
    `accepted_for_score=40/40` and improves the headline score metrics:
    - avg objective `15071175.65 -> 15069943.325`
    - avg T `1540.65 -> 1538.825`
    - avg P `4187.625 -> 4185.775`
    - runtime max `56.951463 -> 56.899351`
    - avg L worsened `2674.325 -> 2683.325`, but the official objective still improved
  - Row-level change versus `v132`:
    - `prob_40`: objective `5910122 -> 5860829`,
      `T 8622 -> 8549`, `L 4587 -> 4947`, `P 11897 -> 11823`
- Historical note:
  - `v123` remains the historical score-improving step over `v122`.
  - `v132` remains the stabilized recovery line that removed the active-surface
    `prob_39` drift.
  - `v133` is the next accepted score-improving line on top of that recovery.
  - `v096` remains the last team-shared historical benchmark report reference:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Rollback target:
  `reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123`
- Canonical note:
  - the direct `baseline_hh` surface is the only canonical score-claim surface.
  - wrapper and `myalgorithm.py` were revalidated against the v133 active
    surface in:
    `reports/ogc2026_reboot_v001/verify_active_v133_publish_20260620_001/`
  - the earlier direct `baseline_hh.py` revalidation reproduced the accepted
    `prob_40` improvement, but the later publish revalidation
    `verify_active_v133_publish_20260620_002` did not.
  - `myalgorithm.py` had already missed that move in the earlier wrapper check
    because the extra dispatch overhead left less headroom before the narrow
    prob40-like guard.
  - together, those reruns mean the current v133 line is historically accepted
    but not stable enough to publish right now as a trusted accepted BEST.
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - the active v133 selector stack is feature-based and time-aware.
  - inherited legacy fallback layers below some historical branches still
    contain older name-based branches; removing that legacy identity
    dependence remains future cleanup work.
