# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v291_20260629_baseline_surface_direct_import_v290`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface.
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  direct standard import of
  `alg_versions.reboot_v290_20260629_trackA_frozen_v278_subprocess_split_specialists.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - candidate same-batch smoke:
    `reports/ogc2026_reboot_v001/smoke_revalidate_v290_vs_active_direct_20260629_001/`
  - candidate `prob_38` guard recheck:
    `reports/ogc2026_reboot_v001/target_recheck_v290_prob38_20260629_001/`
  - candidate same-batch full:
    `reports/ogc2026_reboot_v001/full_revalidate_v290_vs_active_train40_20260629_001/`
  - publish-surface recheck:
    `reports/ogc2026_reboot_v001/verify_active_v291_baseline_hh_py_20260629_001/`

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
  - Total Objective `568637767`
  - Avg Objective `14215944.175`
  - Total T `59460`
  - Avg T `1486.500`
  - Total L `105028.0`
  - Avg L `2625.700`
  - Total P `166097.0`
  - Avg P `4152.425`
  - Avg Runtime `32.97s`
  - Max Runtime `59.32s`

- Comparison versus prior trusted active `v280`:
  - accepted publish-surface improvement:
    - Total Objective `568931012 -> 568637767`
    - Total T `59481 -> 59460`
    - Avg T `1487.025 -> 1486.500`
    - first20 Total T `1461 -> 1440`
    - first20 avg T `73.05 -> 72.00`
    - first20 T>0 count `12 -> 12`
    - changed rows:
      - `prob_13`: `T 498 -> 488`
      - `prob_19`: `T 134 -> 123`

- Stability note:
  - the decisive publish-surface fix versus `v288` was freezing the subprocess
    fallback target on the accepted direct `v278` file instead of
    `baseline_hh.py`, which removed wrapper recursion on the late Family B
    rows.
