# Recovery checkpoint: v149 rejected, active v142 still unre-trusted

Date: 2026-06-20

## What happened

- `reboot_v149_20260620_2215_prob33like_low_headroom_repair_on_v142`
  was tested as a feature-based `prob33-like` recovery branch on top of the
  historical `v142` rollback line.
- The representative smoke stayed scoreable:
  `reports/ogc2026_reboot_v001/smoke_reboot_v149_tier9_20260620_001/`
- But the targeted subtype smoke failed the scoreable gate:
  `reports/ogc2026_reboot_v001/target_reboot_v149_prob33like_20260620_001/`
  - `accepted_for_score = 2/3`
  - `prob_33` timed out at `60.42s`
  - `prob_38` regressed to `352190415 / T=26199`

## Why this is a recovery checkpoint, not a BEST publish

- The active wrapper remains:
  `ogc2026/baseline/baseline_hh.py -> reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- A source-hash audit of the traced `alg_versions` import chain matched the
  historical trusted `v142` manifest, and shared surfaces like `train/`,
  `ogc2026/alg_tester/`, `ogc2026/batchrunner/benchmark.py`,
  `ogc2026/baseline/baseline_greedy.py`, and `ogc2026/baseline/utils.py`
  did not explain the drift.
- Even so, the current-tree parent surface still does not reproduce the old
  trusted tail rows:
  - direct-file representative comparison:
    `reports/ogc2026_reboot_v001/smoke_reboot_v142_compare_tier9b_20260620_001/results.csv`
    - `prob_33` timed out
    - `prob_38` regressed to `342096028 / T=25434`
  - canonical wrapper recovery subset:
    `reports/ogc2026_reboot_v001/verify_active_v142_recovery_subset_20260620_001/`
    - scoreable `4/4`, but still materially worse than the historical trusted
      `v142` tail rows

## Historical-best references still worth keeping

- Historical accepted BEST full40 evidence for the rollback line:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
- Historical team-share markdown report:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`

## Current interpretation

- We should not publish the current active surface as a re-trusted accepted
  BEST yet.
- The repo is in recovery mode:
  - active wrapper stays on historical `v142`
  - `v149` is rejected
  - next work should stabilize the parent surface and re-close canonical
    wrapper validation before another subtype-local T-zero experiment
