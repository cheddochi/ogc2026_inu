# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v218_20260627_trackA_dense_fourbay_deep_chain_on_v217`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface;
  the canonical accepted `v218` bundle preserves the accepted `v217`
  long-fourbay and runtime-cliff surface, then adds one bounded dense
  four-bay deep-chain specialist that improves the residual
  `prob_11` / `prob_13` first20 subtype pocket.
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v218_20260627_trackA_dense_fourbay_deep_chain_on_v217.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - representative tier smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v218_trackA_20260627_001/`
  - official baseline_hh publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v218_baseline_hh_file_20260627_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v218_train40_20260627_001/`

- Historical evidence kept for context:
  - prior active trusted BEST:
    `reports/ogc2026_reboot_v001/full_reboot_v217_train40_20260627_revalidate_002/`
  - prior representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v217_trackA_20260627_001/`
  - prior official baseline_hh publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v217_baseline_hh_file_20260627_002/`
  - v217 prior canonical full bundle:
    `reports/ogc2026_reboot_v001/full_reboot_v217_train40_20260627_revalidate_002/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `570068514`
  - Avg Objective `14251712.850`
  - Total T `59532`
  - Avg T `1488.300`
  - Total L `105568.0`
  - Avg L `2639.200`
  - Total P `167700.0`
  - Avg P `4192.500`
  - Avg Runtime `32.40s`
  - Max Runtime `55.98s`

- Current-tree comparison versus prior active trusted `v217`:
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v217_train40_20260627_revalidate_002/`
  - Total Objective `570663294 -> 570068514`
  - Avg Objective `14266582.350 -> 14251712.850`
  - Total T `59562 -> 59532`
  - Avg T `1489.050 -> 1488.300`
  - Total L `105434.0 -> 105568.0`
  - Avg L `2635.850 -> 2639.200`
  - Total P `167694.0 -> 167700.0`
  - Avg P `4192.350 -> 4192.500`
  - Avg Runtime `32.02s -> 32.40s`
  - Max Runtime `56.30s -> 55.98s`
  - material row improvements:
    - `prob_11`: objective `8761210 -> 8565801`, `T 369 -> 360`
    - `prob_13`: objective `10783287 -> 10383916`, `T 547 -> 526`
  - worst regression: `none`
  - first20 Total T `1542 -> 1512`
  - T>0 count `33 -> 33`
  - high-T tail (`T>=1000`) sum `56718 -> 56718`

- Official baseline_hh publish recheck:
  - `accepted_for_score=18/18`
  - timeout `0`
  - invalid/error `0`
  - matched direct `v218` on objective / `T` / `L` / `P` for:
    - `prob_10`, `prob_11`, `prob_13`, `prob_19`,
      `prob_20`, `prob_33`, `prob_38`, `prob_40`
  - `prob_14` remained accepted on both direct and wrapper routes, but hit an
    existing stable-fourbay multiblock drift boundary before the `v218`
    deep-chain stage:
    - direct recheck: objective `3795716`, `T 181`
    - wrapper recheck: objective `3901754`, `T 187`
  - because the drift happens upstream of the new `v218` specialist, the
    canonical scoring evidence stays the direct full train40 accepted bundle.
