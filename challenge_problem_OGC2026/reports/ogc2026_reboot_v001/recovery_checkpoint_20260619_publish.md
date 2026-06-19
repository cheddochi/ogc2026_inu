# HH Recovery Checkpoint - 2026-06-19

## Summary

- Branch: `hh_algorithm_loop`
- Publish mode: `recovery/failure checkpoint`
- Reason:
  the active HH surface still points to the historical accepted checkpoint
  `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`, but the
  current source state does not reproduce that historical trust claim.

## Why this is not a trusted BEST publish

- `baseline_hh.py` still routes the official interface to `v096` so there is
  one explicit active entrypoint.
- `ACTIVE_VERSION.md` and `VERSION_LOG.md` both record that `v096` is only a
  historical accepted checkpoint under the current source state.
- Current-source rechecks already show runtime cliffs that break the trust
  claim:
  - `reports/ogc2026_reboot_v001/target_recheck_v096_fourbay_runtime_20260619_001/`
    - `prob_31`: timeout at `70.680680s`
  - `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/`
    - `prob_37`: timeout at `71.377730s`
- No current-source `40/40` trusted accepted BEST is established right now.

## Current historical best evidence

- Historical accepted full train40:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`
- Team-sharing report:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Historical headline:
  - accepted_for_score `40/40`
  - avg objective `15096298.7`
  - avg T `1558.675`
  - avg L `2718.775`
  - avg P `4160.575`

## Current-source frontier status

- Best current-source candidate remains `v103`, not promoted:
  `reports/ogc2026_reboot_v001/full_reboot_v103_train40_20260619_001/`
  - accepted_for_score `40/40`
  - avg objective `15219539.55`
  - still worse than historical `v096` by `+123240.85`
- Latest candidate `v104` was rejected:
  `reports/ogc2026_reboot_v001/target_reboot_v104_threebay_runtime_20260619_001/`
  - targeted subtype accepted `1/3`
  - timeouts on `prob_37` and `prob_39`

## Next recovery direction

- Do not publish `v103` or `v104` as trusted BEST.
- Continue from the current recovery state and focus on the remaining 3-bay
  runtime-risk family with a runtime-flattening or guard hypothesis rather than
  deeper local search.
