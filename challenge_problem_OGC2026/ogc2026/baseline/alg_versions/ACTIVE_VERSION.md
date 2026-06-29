# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v299_20260629_baseline_surface_direct_import_v298`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface.
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  direct standard import of
  `alg_versions.reboot_v298_20260629_trackA_prob11_rescue_with_familyB_tail_freeze_on_v290.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - candidate same-batch smoke:
    `reports/ogc2026_reboot_v001/smoke_compare_v298_vs_active_20260629_001/`
  - candidate same-batch full:
    `reports/ogc2026_reboot_v001/full_compare_v298_vs_active_train40_20260629_001/`
  - publish-surface recheck:
    `reports/ogc2026_reboot_v001/verify_active_v299_baseline_hh_py_20260629_001/`

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
  - Total Objective `568424872`
  - Avg Objective `14210621.800`
  - Total T `59451`
  - Avg T `1486.275`
  - Total L `104895.0`
  - Avg L `2622.375`
  - Total P `166050.0`
  - Avg P `4151.250`
  - Avg Runtime `32.43s`
  - Max Runtime `57.80s`

- Comparison versus prior trusted active `v291/v290`:
  - accepted publish-surface improvement:
    - Total Objective `568637767 -> 568424872`
    - Total T `59460 -> 59451`
    - Avg T `1486.500 -> 1486.275`
    - first20 Total T `1440 -> 1431`
    - first20 avg T `72.00 -> 71.55`
    - first20 T>0 count `12 -> 12`
    - changed rows:
      - `prob_11`: `T 351 -> 342`
      - `prob_11`: objective `8364652 -> 8151757`

- Stability note:
  - the decisive new publish guard versus `v297` is freezing the fallback
    directly on accepted `v290` rather than routing through `baseline_hh.py`,
    so the prob11 specialist can run without reopening late Family B wrapper
    drift.
