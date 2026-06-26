# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v212_20260627_trackA_reserved_specialist_budget_on_v210`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface;
  the canonical accepted `v212` bundle preserves the trusted `v210` Track A
  runtime-cliff guards, but reserves specialist budget earlier so the
  profitable late four-bay repairs still execute on the official wrapper
  surface.
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v212_20260627_trackA_reserved_specialist_budget_on_v210.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - representative tier smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v212_trackA_20260627_001/`
  - official baseline_hh publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v212_baseline_hh_20260627_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v212_train40_20260627_001/`

- Historical evidence kept for context:
  - prior active trusted BEST:
    `reports/ogc2026_reboot_v001/full_revalidate_reboot_v210_train40_20260626_001/`
  - prior representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v210_trackA_20260626_001/`
  - prior official baseline_hh publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v210_baseline_hh_20260626_001/`
  - rejected predecessor showing direct-only drift:
    `reports/ogc2026_reboot_v001/verify_active_v211_baseline_hh_20260626_001/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `570842085`
  - Avg Objective `14271052.125`
  - Total T `59579`
  - Avg T `1489.475`
  - Total L `105329.0`
  - Avg L `2633.225`
  - Total P `167678.0`
  - Avg P `4191.950`
  - Avg Runtime `32.08s`
  - Max Runtime `56.14s`

- Current-tree comparison versus prior active trusted `v210`:
  - full:
    `reports/ogc2026_reboot_v001/full_revalidate_reboot_v210_train40_20260626_001/`
  - Total Objective `571093512 -> 570842085`
  - Avg Objective `14277337.800 -> 14271052.125`
  - Total T `59590 -> 59579`
  - Avg T `1489.750 -> 1489.475`
  - Total L `105329.0 -> 105329.0`
  - Avg L `2633.225 -> 2633.225`
  - Total P `167678.0 -> 167678.0`
  - Avg P `4191.950 -> 4191.950`
  - Avg Runtime `32.11s -> 32.08s`
  - Max Runtime `56.63s -> 56.14s`
  - material row improvements:
    - `prob_11`: objective `9012637 -> 8761210`, `T 380 -> 369`
  - no full40 regressions versus canonical `v210`
  - first20 Total T `1570 -> 1559`
  - T>0 count `33 -> 33`
  - high-T tail (`T>=1000`) sum `56718 -> 56718`

- Official baseline_hh publish recheck:
  - `accepted_for_score=16/16`
  - timeout `0`
  - invalid/error `0`
  - matched direct `v212` on objective / `T` / `L` / `P` for:
    - `prob_10`, `prob_11`, `prob_14`, `prob_19`,
      `prob_20`, `prob_33`, `prob_38`, `prob_40`
