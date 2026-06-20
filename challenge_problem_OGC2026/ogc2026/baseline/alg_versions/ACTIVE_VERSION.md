# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Status: recovery rollback line on the current tracked baseline_hh surface; the
  last historical accepted BEST evidence is still `v142`, but the current
  source tree is under trust revalidation
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Historical accepted evidence:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v142_tier9_20260620_001/`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v142_prob40like_20260620_001/`
  - short-limit subtype stress:
    `reports/ogc2026_reboot_v001/stress_reboot_v142_prob40like_short45_20260620_001/`
  - publish-checkpoint revalidation:
    `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
- Historical accepted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `57.660195s`
  - avg T/obj1 `1532.125`
  - avg L/obj2 `2683.325`
  - avg P/obj3 `4185.775`
  - avg objective `15035076.025`
- Historical promotion note:
  - Compared against trusted `v136`, `v142` keeps `accepted_for_score=40/40`
    and improves the official headline on the direct wrapper surface:
    - avg objective `15037077.025 -> 15035076.025`
    - avg T `1535.125 -> 1532.125`
    - avg L `2683.325 -> 2683.325`
    - avg P `4185.775 -> 4185.775`
    - runtime max `56.571143 -> 57.660195`
  - Row-level change versus `v136`:
    - `prob_40`: objective `5860829 -> 5780789`,
      `T 8549 -> 8429`
- Historical publish-checkpoint revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_001/`
  - accepted `7/7`; timeout `0`, invalid `0`
  - current active wrapper reproduced the same canonical subset rows:
    - `prob_1`: objective `693901`, `T=11`
    - `prob_11`: objective `17206722`, `T=739`
    - `prob_25`: objective `1454484`, `T=2089`
    - `prob_27`: objective `76200619`, `T=5541`
    - `prob_31`: objective `39589844`, `T=2735`
    - `prob_39`: objective `48160369`, `T=3521`
    - `prob_40`: objective `5780789`, `T=8429`
- Historical trust recheck:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_002/`
  - accepted `7/7`; timeout `0`, invalid `0`
  - the current wrapper surface reproduced the same canonical subset rows again,
    including the historically sensitive tail rows:
    - `prob_27`: objective `76200619`, `T=5541`
    - `prob_40`: objective `5780789`, `T=8429`
  - interpretation:
    - exploratory tail probes showed drift signals on direct-file runs, but the
      canonical `baseline_hh.py` wrapper surface still revalidated cleanly
      under the publish subset on the current source tree
- Current recovery note:
  - `v146` direct/full evidence stayed score-improving and its publish subset
    recheck stayed scoreable, but its canonical wrapper full40 recheck reopened
    non-target regressions:
    `reports/ogc2026_reboot_v001/verify_active_v146_full40_20260621_001/`
  - after restoring the active wrapper to historical `v142`, an immediate tail
    recheck also failed to reproduce the old trusted tail rows on the current
    source tree:
    `reports/ogc2026_reboot_v001/verify_active_v142_restore_tail_20260621_001/`
    - `prob_27` timed out
    - `prob_40` passed with a large objective/T regression
  - interpretation:
    - the workspace is currently in recovery mode
    - keep the active wrapper on the historical rollback line for now, but do
      not describe the current tree as re-trusted until a fresh canonical
      revalidation closes cleanly
- Historical note:
  - `v123` remains the historical score-improving step over `v122`.
  - `v132` remains the last plateau-stable recovery line and rollback target.
  - `v133` remains a historical accepted improvement over `v132`, but only as
    non-active evidence because of the `prob_40` runtime cliff.
  - `v136` remains the accepted parent line and rollback target for the new
    prob40-like tail repair.
  - `v137` remains a training-best-only direct-file improvement over `v136`,
    but it is not the trusted active BEST because the direct
    `baseline_hh.py` surface did not reproduce the accepted `prob_40` gain.
  - `v146` remains a score-improving candidate over `v142` on direct/full and
    wrapper/publish-subset evidence, but it is not the trusted active BEST
    because the canonical wrapper full40 recheck reopened `prob_39` and
    `prob_40` regressions outside its intended target slice.
- `v096` remains the last team-shared historical benchmark report reference:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Rollback target:
  `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Canonical note:
  - the direct `baseline_hh` surface is the only canonical score-claim surface.
  - the current active wrapper is the historical `v142` rollback line, not a
    freshly re-trusted canonical BEST on the current source tree.
  - `v146` is held as candidate-only evidence until its `prob_27` gain is
    reproduced on a full canonical wrapper surface without reopening non-target
    tail regressions.
  - the `v146` selector stack is feature-based and time-aware.
  - inherited legacy fallback layers below some historical branches still
    contain older name-based branches; removing that legacy identity
    dependence remains future cleanup work.
