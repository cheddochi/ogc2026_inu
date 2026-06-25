# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v178_20260625_v142_specialist_slices_on_v177`
- Status: current-tree trusted BEST on the tracked baseline_hh surface; this
  line is stronger than both the previously published `v177` full40 result and
  the old historical `v142` full40 evidence
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v178_20260625_v142_specialist_slices_on_v177.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - representative tier smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v178_tier9_20260625_001/`
  - targeted subtype / guard smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v178_v142slices_20260625_001/`
  - active wrapper publish subset recheck:
    `reports/ogc2026_reboot_v001/verify_active_v178_publish_20260625_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v178_train40_20260625_001/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `600231122`
  - Avg Objective `15005778.050`
  - Total T `61200`
  - Avg T `1530.000`
  - Total L `107226.0`
  - Avg L `2680.650`
  - Total P `167335.0`
  - Avg P `4183.375`
  - Avg Runtime `26.89s`
  - Max Runtime `55.89s`

- Current-tree comparison versus previously published trusted `v177`:
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v177_train40_20260625_001/`
  - Total Objective `615747848 -> 600231122`
  - Avg Objective `15393696.200 -> 15005778.050`
  - Total T `63287 -> 61200`
  - Avg T `1582.175 -> 1530.000`
  - Total L `111020.0 -> 107226.0`
  - Avg L `2775.500 -> 2680.650`
  - Total P `167738.0 -> 167335.0`
  - Avg P `4193.450 -> 4183.375`
  - Max Runtime `55.98s -> 55.89s`
  - material row improvements:
    - `prob_31`: objective `49464822 -> 39589844`, `T 3465 -> 2735`
    - `prob_32`: objective `13118978 -> 12781706`, `T 3076 -> 2992`
    - `prob_37`: objective `21777210 -> 17644653`, `T 5234 -> 3961`
  - no per-instance regressions on the full 40

- Historical note:
  - old historical full evidence:
    `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - `v178` now surpasses that historical `v142` anchor too:
    - Total Objective `601403041 -> 600231122`
    - Total T `61285 -> 61200`

- Active wrapper publish-subset recheck:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v178_publish_20260625_001/`
  - `accepted_for_score=8/8`; timeout `0`, invalid/error `0`
  - wrapper-sensitive target and guard rows reproduced cleanly:
    - `prob_25`: `1454484 / T=2089`
    - `prob_27`: `75028700 / T=5456`
    - `prob_31`: `39589844 / T=2735`
    - `prob_32`: `12781706 / T=2992`
    - `prob_37`: `17644653 / T=3961`
    - `prob_38`: `151254848 / T=11120`
    - `prob_39`: `48160369 / T=3521`
    - `prob_40`: `5780789 / T=8429`

- Promotion note:
  - `v178` keeps the `v177` prob27 / Family B guard behavior while grafting
    the still-live current-tree `v142` signal back onto the prob31/prob32/
    prob37 slices through a narrow feature-gated specialist dispatch
  - this is meaningful plateau escape progress because it reduces Total T,
    Avg T, and the high-T tail while staying scoreable `40/40`
