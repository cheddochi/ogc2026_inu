# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v210_20260626_trackA_latest_feasible_tardy_repair`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface;
  the canonical accepted `v210` bundle improves on the prior trusted `v207`
  BEST by keeping the Track A runtime-cliff guard and adding a smaller
  mid-size four-bay tardy-repair candidate that converts the residual
  first20 headroom without reopening the `prob_19` timeout.
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v210_20260626_trackA_latest_feasible_tardy_repair.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - representative tier smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v210_trackA_20260626_001/`
  - official baseline_hh publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v210_baseline_hh_20260626_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_revalidate_reboot_v210_train40_20260626_001/`

- Non-canonical auxiliary evidence:
  - initial direct full run before revalidation:
    `reports/ogc2026_reboot_v001/full_reboot_v210_train40_20260626_001/`
  - note:
    the initial direct full run improved `prob_20`, but a later direct
    recheck and the official baseline_hh publish recheck reproduced the
    stable non-improved `prob_20` value; the revalidated full bundle above is
    therefore treated as canonical for trust.

- Historical evidence kept for context:
  - prior active trusted BEST:
    `reports/ogc2026_reboot_v001/full_reboot_v207_train40_20260626_001/`
  - prior representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v207_trackA_20260626_001/`
  - prior official baseline_hh publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v207_baseline_hh_20260626_001/`
  - rejected structural probe:
    `reports/ogc2026_reboot_v001/smoke_reboot_v209_trackA_20260626_001/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `571093512`
  - Avg Objective `14277337.800`
  - Total T `59590`
  - Avg T `1489.750`
  - Total L `105329.0`
  - Avg L `2633.225`
  - Total P `167678.0`
  - Avg P `4191.950`
  - Avg Runtime `32.11s`
  - Max Runtime `56.63s`

- Current-tree comparison versus prior active trusted `v207`:
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v207_train40_20260626_001/`
  - Total Objective `573383982 -> 571093512`
  - Avg Objective `14334599.550 -> 14277337.800`
  - Total T `59700 -> 59590`
  - Avg T `1492.500 -> 1489.750`
  - Total L `105492.0 -> 105329.0`
  - Avg L `2637.300 -> 2633.225`
  - Total P `167720.0 -> 167678.0`
  - Avg P `4193.000 -> 4191.950`
  - Avg Runtime `31.87s -> 32.11s`
  - Max Runtime `56.16s -> 56.63s`
  - material row improvements:
    - `prob_11`: objective `10338343 -> 9012637`, `T 438 -> 380`
    - `prob_13`: objective `11552493 -> 10783287`, `T 588 -> 547`
    - `prob_14`: objective `3991274 -> 3795716`, `T 192 -> 181`
  - no full40 regressions versus canonical `v207`
  - first20 Total T `1680 -> 1570`
  - T>0 count `33 -> 33`
  - high-T tail (`T>=1000`) sum `56718 -> 56718`

- Official baseline_hh publish recheck:
  - `accepted_for_score=16/16`
  - timeout `0`
  - invalid/error `0`
  - matched direct `v210` on objective / `T` / `L` / `P` for:
    - `prob_10`, `prob_11`, `prob_14`, `prob_19`,
      `prob_20`, `prob_33`, `prob_38`, `prob_40`
