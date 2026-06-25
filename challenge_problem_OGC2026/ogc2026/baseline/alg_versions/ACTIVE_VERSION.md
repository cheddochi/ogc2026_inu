# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v194_20260626_familyA_fourbay_inline_on_v186`
- Status: current-tree trusted BEST on the tracked baseline_hh surface; this
  line is stronger than the prior trusted `v186` full40 result while
  preserving the prob_20 / prob_38 / prob_39 / prob_40 guard surface on the
  real active publish chain
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v194_20260626_familyA_fourbay_inline_on_v186.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - representative tier smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v194_trackA_20260626_001/`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v194_prob14_20260626_001/`
  - active publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v194_publish_20260626_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v194_train40_20260626_001/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `580576219`
  - Avg Objective `14514405.475`
  - Total T `60054`
  - Avg T `1501.350`
  - Total L `105781.0`
  - Avg L `2644.525`
  - Total P `167751.0`
  - Avg P `4193.775`
  - Avg Runtime `28.52s`
  - Max Runtime `56.44s`

- Current-tree comparison versus prior trusted `v186`:
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v186_train40_20260625_001/`
  - Total Objective `592407671 -> 580576219`
  - Avg Objective `14810191.775 -> 14514405.475`
  - Total T `60743 -> 60054`
  - Avg T `1518.575 -> 1501.350`
  - Total L `105539.0 -> 105781.0`
  - Avg L `2638.475 -> 2644.525`
  - Total P `167580.0 -> 167751.0`
  - Avg P `4189.500 -> 4193.775`
  - Avg Runtime `28.06s -> 28.52s`
  - Max Runtime `56.05s -> 56.44s`
  - material row improvements:
    - `prob_10`: objective `3425698 -> 1697461`, `T 214 -> 95`
    - `prob_11`: objective `15527141 -> 11154452`, `T 665 -> 473`
    - `prob_12`: objective `684586 -> 553078`, `T 14 -> 8`
    - `prob_13`: objective `17198288 -> 13873697`, `T 892 -> 713`
    - `prob_15`: objective `1661206 -> 890826`, `T 80 -> 28`
    - `prob_19`: objective `4269370 -> 2765323`, `T 347 -> 206`
  - no per-instance regressions on the full 40
  - first20 Total T `2723 -> 2034`
  - T>0 count `33 -> 33`

- Promotion note:
  - `v194` is meaningful plateau escape progress because it reduces Total T,
    Avg T, first20 Total T, and total objective while staying scoreable
    `40/40`.
  - the active publish target/guard recheck also reproduced the promoted values
    on the real `myalgorithm.py -> baseline_hh.py` surface:
    - `prob_10`: `1697461 / T=95`
    - `prob_11`: `11154452 / T=473`
    - `prob_12`: `553078 / T=8`
    - `prob_13`: `13873697 / T=713`
    - `prob_14`: `4097312 / T=198`
    - `prob_15`: `890826 / T=28`
    - `prob_19`: `2765323 / T=206`
    - `prob_20`: `8239778 / T=278`
    - `prob_38`: `151254848 / T=11120`
    - `prob_39`: `48160369 / T=3521`
    - `prob_40`: `5780789 / T=8429`
