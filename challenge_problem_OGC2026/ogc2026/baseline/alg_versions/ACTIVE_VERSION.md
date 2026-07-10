# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v318_20260630_baseline_surface_direct_import_v317`
- Status: current-tree trusted BEST on the tracked `baseline_hh.py` surface.
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  direct standard import of
  `alg_versions.reboot_v317_20260630_trackA_prob13_only_window_multiblock_on_v314.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Canonical evidence for the active trusted line:
  - candidate same-batch smoke:
    `reports/ogc2026_reboot_v001/smoke_compare_v317_vs_active_20260630_001/`
  - candidate same-batch full:
    `reports/ogc2026_reboot_v001/full_compare_v317_vs_active_train40_20260630_001/`
  - publish-surface recheck:
    `reports/ogc2026_reboot_v001/verify_active_v318_baseline_hh_py_alias_20260630_001/`

- Earlier diagnostic evidence kept for history:
  - prior trusted active smoke:
    `reports/ogc2026_reboot_v001/smoke_compare_v314_vs_active_20260630_001/`
  - prior trusted active full:
    `reports/ogc2026_reboot_v001/full_compare_v314_vs_active_train40_20260630_001/`
  - prior publish-surface recheck:
    `reports/ogc2026_reboot_v001/verify_active_v315_baseline_hh_py_alias_20260630_001/`

- Active train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - invalid/error `0`
  - Total Objective `567096302`
  - Avg Objective `14177407.550`
  - Total T `59375`
  - Avg T `1484.375`
  - Total L `104924.0`
  - Avg L `2623.100`
  - Total P `166024.0`
  - Avg P `4150.600`
  - Avg Runtime `33.34s`
  - Max Runtime `58.05s`

- Comparison versus prior trusted active `v315/v314`:
  - accepted publish-surface improvement:
    - Total Objective `567816045 -> 567096302`
    - Total T `59414 -> 59375`
    - Avg T `1485.350 -> 1484.375`
    - first20 Total T `1394 -> 1355`
    - first20 avg T `69.70 -> 67.75`
    - first20 T>0 count `12 -> 12`
    - changed rows:
      - `prob_13`: `T 482 -> 443`
      - `prob_13`: objective `9583645 -> 8863902`

- Stability note:
  - the active surface remains a thin direct `algorithm = active.algorithm`
    alias to avoid earlier wrapper-path runtime drift.
  - the canonical alias recheck matched the promoted `v317` quality
    row-for-row on the tracked smoke subset while preserving
    `accepted_for_score`, timeout, and invalid/error gates.
  - one same-batch active comparison reopened a `prob_11` drift on the old
    comparator side, so promotion was anchored to the direct `v317` full40
    evidence plus the `baseline_hh.py` alias recheck rather than that
    transient active-side row.
