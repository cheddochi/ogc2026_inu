# Recovery Checkpoint Publish Note (2026-06-21, post-v160 runtime drift)

This checkpoint is a recovery/failure publish, not a trusted-BEST promotion.

## Why this is not a BEST publish

- The active wrapper still points to the historical rollback line:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Historical accepted evidence for that line still exists:
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - `accepted_for_score=40/40`, timeout `0`, invalid `0`
- But the current source tree is not trustworthy enough to publish the active
  wrapper as a fresh BEST:
  - `v152` had once reclosed current-tree scoreability at:
    `reports/ogc2026_reboot_v001/full_reboot_v152_train40_20260621_001/`
  - later live rechecks reopened the same runtime cliff:
    - `reports/ogc2026_reboot_v001/diag_reboot_v159_prob33direct_20260621_001/`
      showed `v141/v142/v152` all timing out on direct `prob_33` reruns
    - `reports/ogc2026_reboot_v001/smoke_reboot_v160_tier9_20260621_001/`
      showed `v152 prob_33` timing out again at `61.470279s`

## What the latest recovery cycle established

- `v159` is closed as rejected:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v159.md`
  - it repaired the `prob33-like` slice itself, but the inherited `v158`
    parent still timed out on untouched `prob_27`
- `v160` is closed as rejected:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v160.md`
  - it preserved both targeted direct-slice gains:
    - `prob_33`: PASS with large runtime margin
    - `prob_40`: PASS with the strong narrow-builder T gain
  - but untouched `prob_27` still timed out, so the surrounding current-tree
    parent surface remains unreliable

## Honest shared state after this checkpoint

- Historical accepted BEST evidence still matters:
  - `v142` remains the last trusted historical accepted line
- Current active wrapper remains a recovery rollback surface only
- Current tree does not currently have a trustworthy scoreable parent surface,
  even at tier-representative smoke level
- The next blocker is not a single row anymore:
  - `prob27-like 2-bay high-proc heavy-tail`
  - `prob33-like 3-bay moderate-highproc`
  must be stabilized together before any renewed BEST claim

## Selected evidence bundled with this checkpoint

- Historical-best reference:
  - `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Current recovery-state notes:
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v159.md`
  - `reports/ogc2026_reboot_v001/validation_note_20260621_v160.md`
- Current recovery-state summaries:
  - `reports/ogc2026_reboot_v001/diag_reboot_v159_prob33family_20260621_001/summary.json`
  - `reports/ogc2026_reboot_v001/diag_reboot_v159_prob33direct_20260621_001/summary.json`
  - `reports/ogc2026_reboot_v001/smoke_reboot_v159_tier9_20260621_001/summary.json`
  - `reports/ogc2026_reboot_v001/smoke_reboot_v160_tier9_20260621_001/summary.json`

