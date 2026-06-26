# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v217_20260627_trackA_prob19_long_fourbay_repair_on_v212`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface;
  the canonical accepted `v217` bundle preserves the trusted `v212`
  runtime-cliff and stable Track A surface, then adds one narrow long
  four-bay tardy-repair specialist that improves the residual `prob_19`-like
  first20 subtype.
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v217_20260627_trackA_prob19_long_fourbay_repair_on_v212.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - representative tier smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v217_trackA_20260627_001/`
  - official baseline_hh publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v217_baseline_hh_file_20260627_002/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v217_train40_20260627_revalidate_002/`

- Historical evidence kept for context:
  - prior active trusted BEST:
    `reports/ogc2026_reboot_v001/full_reboot_v212_train40_20260627_001/`
  - prior representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v212_trackA_20260627_001/`
  - prior official baseline_hh publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v212_baseline_hh_20260627_001/`
  - v217 timeout-drift full run kept as non-canonical context:
    `reports/ogc2026_reboot_v001/full_reboot_v217_train40_20260627_001/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `570663294`
  - Avg Objective `14266582.350`
  - Total T `59562`
  - Avg T `1489.050`
  - Total L `105434.0`
  - Avg L `2635.850`
  - Total P `167694.0`
  - Avg P `4192.350`
  - Avg Runtime `32.02s`
  - Max Runtime `56.30s`

- Current-tree comparison versus prior active trusted `v212`:
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v212_train40_20260627_001/`
  - Total Objective `570842085 -> 570663294`
  - Avg Objective `14271052.125 -> 14266582.350`
  - Total T `59579 -> 59562`
  - Avg T `1489.475 -> 1489.050`
  - Total L `105329.0 -> 105434.0`
  - Avg L `2633.225 -> 2635.850`
  - Total P `167678.0 -> 167694.0`
  - Avg P `4191.950 -> 4192.350`
  - Avg Runtime `32.08s -> 32.02s`
  - Max Runtime `56.14s -> 56.30s`
  - material row improvements:
    - `prob_19`: objective `2325874 -> 2147083`, `T 164 -> 147`
  - worst regression: `none`
  - first20 Total T `1559 -> 1542`
  - T>0 count `33 -> 33`
  - high-T tail (`T>=1000`) sum `56718 -> 56718`

- Official baseline_hh publish recheck:
  - `accepted_for_score=16/16`
  - timeout `0`
  - invalid/error `0`
  - matched direct `v217` on objective / `T` / `L` / `P` for:
    - `prob_10`, `prob_11`, `prob_14`, `prob_19`,
      `prob_20`, `prob_33`, `prob_38`, `prob_40`
