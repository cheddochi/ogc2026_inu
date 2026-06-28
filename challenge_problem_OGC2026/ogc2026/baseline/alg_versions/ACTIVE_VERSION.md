# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v280_20260628_baseline_surface_direct_import_v278`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface.
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  direct standard import of
  `alg_versions.reboot_v278_20260628_trackA_coarse_gate_lazy_prob20_plus_lowproc_replay_on_active_v267.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - publish-surface probe:
    `reports/ogc2026_reboot_v001/probe_active_v280_baseline_hh_py_20260628_001/`
  - targeted active smoke:
    `reports/ogc2026_reboot_v001/smoke_active_v280_baseline_hh_py_20260628_001/`
  - supporting direct candidate full:
    `reports/ogc2026_reboot_v001/full_reboot_v278_train40_20260628_001/`
  - active wrapper full / recheck:
    `reports/ogc2026_reboot_v001/verify_active_v280_baseline_hh_py_20260628_001/`

- Earlier diagnostic evidence kept for history:
  - `reports/ogc2026_reboot_v001/smoke_v275_trackA_specialist_first_20260628_001/`
  - `reports/ogc2026_reboot_v001/full_reboot_v275_train40_20260628_001/`
  - `reports/ogc2026_reboot_v001/verify_active_v275_baseline_hh_py_20260628_001/`
  - `reports/ogc2026_reboot_v001/full_reboot_v276_train40_20260628_001/`
  - `reports/ogc2026_reboot_v001/verify_active_v276_baseline_hh_py_20260628_001/`
  - `reports/ogc2026_reboot_v001/full_reboot_v277_train40_20260628_001/`
  - `reports/ogc2026_reboot_v001/smoke_v278_trackA_coarse_gate_20260628_001/`
  - `reports/ogc2026_reboot_v001/verify_active_v278_baseline_hh_py_20260628_001/`
  - `reports/ogc2026_reboot_v001/smoke_active_v279_baseline_hh_py_20260628_001/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `568931012`
  - Avg Objective `14223275.300`
  - Total T `59481`
  - Avg T `1487.025`
  - Total L `104780.0`
  - Avg L `2619.500`
  - Total P `166030.0`
  - Avg P `4150.750`
  - Avg Runtime `32.02s`
  - Max Runtime `57.39s`

- Comparison versus prior trusted active `v267`:
  - Total Objective `569285579 -> 568931012`
  - Avg Objective `14232139.475 -> 14223275.300`
  - Total T `59488 -> 59481`
  - Avg T `1487.200 -> 1487.025`
  - Total L `105272.0 -> 104780.0`
  - Avg L `2631.800 -> 2619.500`
  - Total P `167853.0 -> 166030.0`
  - Avg P `4196.325 -> 4150.750`
  - Avg Runtime `33.09s -> 32.02s`
  - Max Runtime `57.98s -> 57.39s`
  - changed rows:
    - `prob_2`: objective `76910 -> 51940`, `T 0 -> 0`
    - `prob_3`: objective `188500 -> 156780`, `T 0 -> 0`
    - `prob_5`: objective `169685 -> 139455`, `T 0 -> 0`
    - `prob_6`: objective `715812 -> 577115`, `T 7 -> 7`
    - `prob_7`: objective `242600 -> 131191`, `T 0 -> 0`
    - `prob_8`: objective `85472 -> 74968`, `T 0 -> 0`
    - `prob_9`: objective `180488 -> 237200`, `T 1 -> 0`
    - `prob_19`: objective `2072414 -> 2008665`, `T 140 -> 134`
  - first20 Total T `1468 -> 1461`
  - first20 T>0 count `13 -> 12`

- Stability note:
  - the accepted `baseline_hh.py` surface now exactly matches the strongest
    known direct `v278` train40 result on the official wrapper path.
  - the decisive publish-surface fix was replacing the old importlib-loaded
    active chain with a direct standard import of the accepted `v278` logic.
