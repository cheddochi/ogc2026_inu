# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v267_20260628_trackA_spatial_primitive_reinsert_on_active_v247`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface.
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v267_20260628_trackA_spatial_primitive_reinsert_on_active_v247.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - targeted Track A smoke:
    `reports/ogc2026_reboot_v001/smoke_v267_trackA_spatial_fallbacksnapshot_20260628_001/`
  - active wrapper full:
    `reports/ogc2026_reboot_v001/full_active_v267_baseline_hh_py_20260628_001/`
  - active wrapper publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v267_baseline_hh_py_20260628_004/`

- Supporting direct-source evidence for the same v267 hypothesis:
  - direct source full:
    `reports/ogc2026_reboot_v001/full_reboot_v267_fallbacksnapshot_train40_20260628_001/`

- Prior active evidence kept for context:
  - prior active trusted BEST:
    `reports/ogc2026_reboot_v001/full_active_v247_baseline_hh_py_20260627_001/`
  - prior active wrapper reverify:
    `reports/ogc2026_reboot_v001/reverify_active_baseline_hh_py_20260628_001/`
  - prior direct source revalidation:
    `reports/ogc2026_reboot_v001/revalidate_v247_current_source_train40_20260628_001/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `569285579`
  - Avg Objective `14232139.475`
  - Total T `59488`
  - Avg T `1487.200`
  - Total L `105272.0`
  - Avg L `2631.800`
  - Total P `167853.0`
  - Avg P `4196.325`
  - Avg Runtime `33.09s`
  - Max Runtime `57.98s`

- Comparison versus prior active trusted `v247`:
  - Total Objective `569663537 -> 569285579`
  - Avg Objective `14241588.425 -> 14232139.475`
  - Total T `59512 -> 59488`
  - Avg T `1487.800 -> 1487.200`
  - Total L `105327.0 -> 105272.0`
  - Avg L `2633.175 -> 2631.800`
  - Total P `167747.0 -> 167853.0`
  - Avg P `4193.675 -> 4196.325`
  - Avg Runtime `32.00s -> 33.09s`
  - Max Runtime `56.52s -> 57.98s`
  - material row improvements:
    - `prob_13`: objective `10197866 -> 9876799`, `T 516 -> 498`
    - `prob_19`: objective `2147083 -> 2072414`, `T 147 -> 140`
  - worst regression:
    - `prob_14`: objective `3777938 -> 3795716`, `T 180 -> 181`
  - first20 Total T `1492 -> 1468`
  - first20 T>0 count `13 -> 13`
  - high-T tail (`T>=1000`) sum `56718 -> 56718`

- Stability note:
  - narrow publish rechecks remained accepted `8/8`.
  - targeted reruns showed small row-level jitter inside the accepted surface,
    so the canonical trust anchor is the active wrapper full-40 bundle above.
