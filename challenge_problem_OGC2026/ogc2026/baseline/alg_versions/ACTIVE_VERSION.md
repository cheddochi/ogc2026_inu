# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v305_20260629_baseline_surface_direct_import_v304`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface.
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  direct standard import of
  `alg_versions.reboot_v304_20260629_trackA_prob13like_subprocess_fallback_on_v298.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - candidate same-batch smoke:
    `reports/ogc2026_reboot_v001/smoke_compare_v304_vs_v298_20260629_001/`
  - candidate same-batch full:
    `reports/ogc2026_reboot_v001/full_compare_v304_vs_v298_train40_20260629_001/`
  - publish-surface recheck:
    `reports/ogc2026_reboot_v001/verify_active_v305_baseline_hh_py_alias_20260629_002/`

- Earlier diagnostic evidence kept for history:
  - failed publish-path recheck before the alias fix:
    `reports/ogc2026_reboot_v001/verify_active_v305_baseline_hh_py_20260629_001/`
  - guard recovery probe after the alias fix:
    `reports/ogc2026_reboot_v001/guard_recheck_v305_alias_prob31_38_39_40_20260629_001/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `568325960`
  - Avg Objective `14208149.000`
  - Total T `59445`
  - Avg T `1486.125`
  - Total L `104892.0`
  - Avg L `2622.300`
  - Total P `166143.0`
  - Avg P `4153.575`
  - Avg Runtime `32.54s`
  - Max Runtime `58.04s`

- Comparison versus prior trusted active `v299/v298`:
  - accepted publish-surface improvement:
    - Total Objective `568424872 -> 568325960`
    - Total T `59451 -> 59445`
    - Avg T `1486.275 -> 1486.125`
    - first20 Total T `1431 -> 1425`
    - first20 avg T `71.55 -> 71.25`
    - first20 T>0 count `12 -> 12`
    - changed rows:
      - `prob_13`: `T 488 -> 482`
      - `prob_13`: objective `9695535 -> 9583645`

- Stability note:
  - the first publish-surface recheck through a tiny wrapper function reopened
    the `prob_39` runtime cliff (`60.31s`), so the active surface was thinned
    to a direct `algorithm = active.algorithm` alias.
  - the canonical alias recheck matched the promoted `v304` quality
    row-for-row while restoring `accepted_for_score=40/40`, timeout `0`,
    invalid/error `0`.
