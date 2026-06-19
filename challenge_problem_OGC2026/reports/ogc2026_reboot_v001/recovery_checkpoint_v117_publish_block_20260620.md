# v117 Publish Recovery Checkpoint (2026-06-20)

## Decision

- This checkpoint is a recovery/failure publish, not an accepted-BEST publish.
- We are intentionally **not** publishing the current active `baseline_hh.py`
  surface as a trusted accepted BEST today.

## Why

- Historical accepted evidence for `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
  is still strong:
  - full accepted run:
    `reports/ogc2026_reboot_v001/full_reboot_v117_train40_20260620_001/`
  - headline metrics from that run:
    - accepted_for_score `40/40`
    - timeout `0`
    - invalid `0`
    - avg objective `15085068.575`
    - avg T `1542.1`
    - max runtime `57.930979s`
- However, fresh publish revalidation of the **current active wrapper** failed:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v117_publish_20260620_001/`
  - result:
    - accepted_for_score `1/3`
    - timed_out `2`
    - `prob_31`: runtime `61.996197s`
    - `prob_37`: runtime `60.427098s`
    - `prob_40`: accepted_for_score `true`

## Interpretation

- The current `reboot_v117` version file hash still matches the accepted
  full-run manifest, so this is not a simple source-file mismatch.
- The blocking issue is runtime reproducibility at publish time on guarded
  rows under the active wrapper.

## Historical references to keep with this checkpoint

- current strongest historical accepted evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v117_train40_20260620_001/`
- team-shared historical benchmark markdown:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`

## Next step

- Repair the `prob_31` / `prob_37` runtime cliff first.
- Only after a fresh scoreable revalidation should `v117` or a successor be
  republished as a trusted accepted BEST.
