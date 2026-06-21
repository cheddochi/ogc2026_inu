# Recovery Checkpoint 2026-06-21 after v168 rejection

## Current publish status

This is a recovery / failure checkpoint, not a trusted accepted-BEST publish.

- Active wrapper:
  `ogc2026/baseline/baseline_hh.py`
- Active line:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Current interpretation:
  historical rollback line only

## Why this is not a BEST publish

The historical accepted evidence for `v142` is still real and remains the best
trusted reference point:

- full historical evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
- historical headline:
  - `accepted_for_score=40/40`
  - timeout `0`
  - avg T `1532.125`
  - avg objective `15035076.025`

But the current source tree still should not be described as freshly
re-trusted on the canonical wrapper surface. The workspace notes already mark
the wrapper as recovery-only, and the latest current-tree recovery subset did
not reproduce the historically trusted tail rows cleanly.

## What closed in this checkpoint

`reboot_v168_20260621_0825_v158_coupled_runtime_slices` is now formally closed
as rejected.

Evidence used:

- representative smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v168_tier10_20260621_001/`
- targeted subtype smoke:
  `reports/ogc2026_reboot_v001/target_reboot_v168_coupled_runtime_20260621_001/`
- validation note:
  `reports/ogc2026_reboot_v001/validation_note_20260621_v168.md`

## Main finding

The direct `prob33-like` repair signal remains useful, but the delegated
`prob27-like` path through `v146` is not stable enough on the current tree.
The targeted subtype gate reopened `prob_27` as a timeout at `74.01s`, so the
candidate cannot advance to full40.

## Historical reference for team context

The team shareable historical-best benchmark narrative remains:

- `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`

That file is included here as historical context only. It is not the current
active wrapper claim.

## Next hypothesis

Before any new candidate starts, keep the active wrapper on the historical
rollback line and build a lighter direct `prob27-like` stabilizer that bypasses
the long inherited runtime stack while preserving the proven direct
`prob33-like` repair signal.
