# Recovery Checkpoint 2026-06-21

This checkpoint is intentionally **not** a trusted accepted-BEST publish.

## What is still historically trusted

- Active rollback line in `baseline_hh.py`:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Historical accepted BEST full evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
- Historical publish-subset wrapper rechecks:
  - `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_001/`
  - `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_002/`

Those runs established the historical score claim for `v142`.

## Why the current tree is not being published as a re-trusted BEST

- `baseline_hh.py` still points to the historical `v142` rollback line, but
  the current source tree remains in recovery mode.
- `ACTIVE_VERSION.md` records that newer wrapper/full rechecks reopened drift on
  the canonical surface.
- Current-tree recovery subset evidence remained scoreable, but did not
  reproduce the trusted tail values on rows such as `prob_27`, `prob_33`,
  `prob_38`, and `prob_40`.

## Current recovery evidence

- `v152` restored a fully scoreable current-tree train40 surface:
  `reports/ogc2026_reboot_v001/full_reboot_v152_train40_20260621_001/`
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - but materially worse than trusted historical `v142` on avg objective and
    avg T
- `v153` was rejected at representative smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v153_tier12_20260621_001/`
  - accepted_for_score `11/12`
  - reopened non-target timeout on `prob_27`
  - no improvement on intended `prob_33-like` target row

## Publish decision

Publish this checkpoint as **recovery / failure evidence**, not as a claim that
the current active wrapper has been re-trusted as the accepted BEST.

## Next hypothesis

- Keep `baseline_hh.py` on historical `v142`
- Use `v152` as the scoreable recovery parent
- Pivot to a single-family `prob38-like` high-T-tail hypothesis instead of
  continuing the failed `prob33-like` replay line
