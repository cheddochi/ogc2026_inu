# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`
- Status: historical accepted checkpoint still wired as active surface, but not
  currently trusted under the current source state
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v096_core9_20260619_001/`
    `reports/ogc2026_reboot_v001/target_reboot_v096_xlarge_lowproc_20260619_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`
- Historical accepted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `58.475376s`
  - avg T/obj1 `1558.675`
  - avg L/obj2 `2718.775`
  - avg P/obj3 `4160.575`
  - avg objective `15096298.7`
- Historical improvement note:
  - Compared against trusted v094, v096 kept `accepted_for_score=40/40` and
    improved the xlarge 3-bay low-proc family without any train40 regressions:
    - avg T `1558.675 -> 1558.675`
    - avg L `2725.7 -> 2718.775`
    - avg P `4162.65 -> 4160.575`
    - avg objective `15097571.4 -> 15096298.7`
    - runtime max `58.993998 -> 58.475376`
  - Row-level improvement:
    - `prob_37`: objective `17505105 -> 17454197`
- Current-source recovery note:
  - Current reruns do not reproduce the historical v096 trust claim.
  - Recheck evidence:
    - `reports/ogc2026_reboot_v001/target_recheck_v096_fourbay_runtime_20260619_001/`
      - `prob_31`: timeout, runtime `70.680680s`, objective `46503155`
      - `prob_36`: accepted, runtime `52.655423s`, objective `1713312`
      - `prob_40`: accepted, runtime `43.937350s`, objective `6333528`
    - `reports/ogc2026_reboot_v001/target_recheck_v094_fourbay_runtime_20260619_001/`
      - `prob_31`: timeout, runtime about `70.434289s`
    - `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/`
      - `prob_37`: timeout, runtime `71.377730s`, objective `17644653`
  - Current-source fallback candidate recheck:
    - `reports/ogc2026_reboot_v001/full_recheck_v083_train40_20260619_001/`
    - accepted_for_score `39/40`
    - failing row: `prob_37` timeout at `67.648573s`
  - Conclusion:
    - No current-source `40/40` trusted accepted BEST is established right now.
    - `baseline_hh.py -> v096` remains the active recovery surface only so the
      worktree keeps a single explicit entrypoint while trust is being rebuilt.
- Rollback target:
  `reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093`
- Canonical note:
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - the new v096 selector stack is feature-based and time-aware.
  - inherited legacy fallback layers below the active selector still contain
    older name-based branches; removing that legacy identity dependence remains
    future cleanup work.
