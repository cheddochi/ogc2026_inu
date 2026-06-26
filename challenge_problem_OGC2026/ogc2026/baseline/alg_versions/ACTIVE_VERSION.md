# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v194_20260626_familyA_fourbay_inline_on_v186`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface;
  `v195` is accepted because it improves full40 Total T and objective versus
  the prior historical `v194` line, preserves `accepted_for_score=40/40`, and
  passes a wrapper stability recheck on the official baseline_hh surface
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
    `reports/ogc2026_reboot_v001/smoke_reboot_v195_trackA_20260626_001/`
  - active publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v195_publish_20260626_001/`
  - wrapper stability recheck:
    `reports/ogc2026_reboot_v001/stability_v195_wrapper_dual_20260626_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v195_train40_20260626_002/`

- Historical evidence kept for context:
  - representative tier smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v194_trackA_20260626_001/`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v194_prob14_20260626_001/`
  - active publish recheck:
    `reports/ogc2026_reboot_v001/verify_active_v194_publish_20260626_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v194_train40_20260626_001/`
  - v194 recovery / drift evidence:
    - `reports/ogc2026_reboot_v001/recheck_active_v194_vs_wrapper_20260626_001/`
    - `reports/ogc2026_reboot_v001/stability_v194_wrapper_dual_20260626_001/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `577544688`
  - Avg Objective `14438617.200`
  - Total T `59959`
  - Avg T `1498.975`
  - Total L `105961.0`
  - Avg L `2649.025`
  - Total P `167845.0`
  - Avg P `4196.125`
  - Avg Runtime `30.08s`
  - Max Runtime `57.92s`

- Current-tree comparison versus prior active historical `v194`:
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v194_train40_20260626_001/`
  - Total Objective `580576219 -> 577544688`
  - Avg Objective `14514405.475 -> 14438617.200`
  - Total T `60054 -> 59959`
  - Avg T `1501.350 -> 1498.975`
  - Total L `105781.0 -> 105961.0`
  - Avg L `2644.525 -> 2649.025`
  - Total P `167751.0 -> 167845.0`
  - Avg P `4193.775 -> 4196.125`
  - Avg Runtime `28.52s -> 30.08s`
  - Max Runtime `56.44s -> 57.92s`
  - material row improvements:
    - `prob_10`: objective `1697461 -> 1552011`, `T 95 -> 85`
    - `prob_20`: objective `8239778 -> 5199740`, `T 278 -> 164`
  - hidden-risk regression to monitor:
    - `prob_32`: objective `12781706 -> 12935663`, `T 2992 -> 3021`
  - first20 Total T `2034 -> 1910`
  - T>0 count `33 -> 33`
  - high-T tail (`T>=1000`) sum `56718 -> 56747`

- Acceptance note:
  - `v195` qualifies for promotion because it preserves `40/40` accepted runs
    and materially improves Total T, Avg T, first20 Total T, and total
    objective by more than the promotion threshold.
  - wrapper stability on the official `baseline_hh.py` surface was rechecked on
    `prob_32`, `prob_38`, `prob_39`, and `prob_40`, and the duplicated wrapper
    runs matched exactly on objective / `T` / `L` / `P`.
  - a `myalgorithm.py` active-chain probe showed a one-off better `prob_32`
    value than the direct wrapper line; because the official contract is
    `baseline_hh.py`, the stable wrapper evidence is treated as canonical.
