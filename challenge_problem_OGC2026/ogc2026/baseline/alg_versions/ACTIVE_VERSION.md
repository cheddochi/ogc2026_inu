# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Status: trusted accepted BEST on the current tracked baseline_hh surface
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v136_tier9_20260620_001/`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v136_twobay_tail_20260620_001/`
  - short-limit subtype stress:
    `reports/ogc2026_reboot_v001/stress_reboot_v136_twobay_short45_20260620_001/`
  - active-surface revalidation:
    `reports/ogc2026_reboot_v001/verify_active_v136_surface_20260620_001/`
  - publish-checkpoint revalidation:
    `reports/ogc2026_reboot_v001/verify_active_v136_publish_20260620_002/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/`
- Current accepted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `56.571143s`
  - avg T/obj1 `1535.125`
  - avg L/obj2 `2683.325`
  - avg P/obj3 `4185.775`
  - avg objective `15037077.025`
- Promotion note:
  - Compared against trusted `v135`, `v136` keeps `accepted_for_score=40/40`
    and improves the official headline without any regression rows:
    - avg objective `15069943.325 -> 15037077.025`
    - avg T `1538.825 -> 1535.125`
    - avg L `2683.325 -> 2683.325`
    - avg P `4185.775 -> 4185.775`
    - runtime max `58.418181 -> 56.571143`
  - Row-level changes versus `v135`:
    - `prob_25`: objective `1489168 -> 1454484`,
      `T 2141 -> 2089`
    - `prob_27`: objective `77480587 -> 76200619`,
      `T 5637 -> 5541`
- Active-surface revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v136_surface_20260620_001/`
  - accepted `6/6`; timeout `0`, invalid `0`
  - direct `baseline_hh.py` reproduced the accepted target-family gains:
    - `prob_25`: objective `1454484`, `T=2089`
    - `prob_27`: objective `76200619`, `T=5541`
  - representative high-T carryover rows also stayed scoreable:
    - `prob_39`: objective `48160369`, `T=3521`
    - `prob_40`: objective `5860829`, `T=8549`
- Publish-checkpoint revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v136_publish_20260620_002/`
  - accepted `6/6`; timeout `0`, invalid `0`
  - current active wrapper reproduced the same canonical subset rows:
    - `prob_25`: objective `1454484`, `T=2089`
    - `prob_27`: objective `76200619`, `T=5541`
    - `prob_39`: objective `48160369`, `T=3521`
    - `prob_40`: objective `5860829`, `T=8549`
- Historical note:
  - `v123` remains the historical score-improving step over `v122`.
  - `v132` remains the last plateau-stable recovery line and rollback target.
  - `v133` remains a historical accepted improvement over `v132`, but only as
    non-active evidence because of the `prob_40` runtime cliff.
  - `v136` remains the accepted two-bay tail repair line.
  - `v137` remains a training-best-only direct-file improvement over `v136`,
    but it is not the trusted active BEST because the direct
    `baseline_hh.py` surface did not reproduce the accepted `prob_40` gain.
- `v096` remains the last team-shared historical benchmark report reference:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Rollback target:
  `reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132`
- Canonical note:
  - the direct `baseline_hh` surface is the only canonical score-claim surface.
  - `v136` remains the active canonical score-claim surface.
  - `v137` is kept only as non-active direct-file evidence until its
    `prob_40` gain is reproduced on the direct active wrapper surface.
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - the active v136 selector stack is feature-based and time-aware.
  - inherited legacy fallback layers below some historical branches still
    contain older name-based branches; removing that legacy identity
    dependence remains future cleanup work.
