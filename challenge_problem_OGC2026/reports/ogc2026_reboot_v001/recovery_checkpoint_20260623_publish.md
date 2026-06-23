# Recovery Checkpoint - 2026-06-23

## Status

This checkpoint is a `recovery` publish, not a trusted-BEST publish.

- Active wrapper:
  `ogc2026/baseline/baseline_hh.py`
- Active line:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Historical accepted BEST evidence still exists for `v142`, but the current
  source tree is not being published as a freshly re-trusted BEST surface.

## Why This Is Not a BEST Publish

The current tree still carries wrapper-surface trust drift:

- `ACTIVE_VERSION.md` already marks the active wrapper as a recovery rollback
  line rather than a re-trusted canonical BEST
- recent current-tree recovery work improved some reopened slices, but has not
  yet reproduced a scoreable full40 line that is clearly trustworthy enough to
  replace the historical accepted BEST evidence

## Latest Candidate Closed In This Checkpoint

- Candidate:
  `reboot_v171_20260621_1215_twobay_concentrated_early_exit_on_v170`
- Validation note:
  `reports/ogc2026_reboot_v001/validation_note_20260623_v171.md`

Result:

- representative tier smoke passed `9/9`
- targeted runtime-family smoke failed at `7/8`
- blocker: `prob_37` TIMEOUT at `73.74s`

That means the narrow family repair is promising but still not ready for
promotion or full40 BEST evaluation.

## Historical Reference Evidence

- trusted historical accepted full40:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
- team-shared historical benchmark report:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`

## Meaningful Progress Assessment

- meaningful_progress:
  `false`
- plateau_reason:
  `The latest work repaired a narrow current-tree family, but it did not close the wider runtime-risk tail and did not produce a scoreable full40 or a T-breakthrough publish candidate.`

## Next Recovery Direction

Keep the active wrapper pinned to the historical rollback line and continue with
a bounded T-zero-first recovery cycle on the `3bay/runtime-risk/high-T tail`
family while preserving the new useful `2bay/highproc/concentrated` early-exit
behavior as candidate-only evidence.
