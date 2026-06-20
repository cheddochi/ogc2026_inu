# Recovery Checkpoint 2026-06-20 08:54 KST

## Why this is not an accepted-BEST republish

The branch still holds a strong historical `v123` full-train result, but the
current active submission surface is not cleanly reproducing that historical
best on the publish revalidation slice. Because of that, this checkpoint is a
recovery/failure publish, not a fresh trusted-BEST promotion.

## Current active surface

- Active wrapper:
  `ogc2026/baseline/baseline_hh.py`
- Active version id:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Dispatch chain:
  `myalgorithm.py ACTIVE="hh" -> baseline_hh.py -> reboot_v123...`

## Historical best evidence kept on record

- Full-train evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
- Historical headline:
  - `accepted_for_score=40/40`
  - `avg objective=15071175.65`
  - `avg T=1540.65`
  - `avg L=2674.325`
  - `avg P=4187.625`
  - `runtime_max=59.416431s`

## Current-head revalidation

- Wrapper/active revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_003/`
- Current source hashes in the manifest now match HEAD for:
  - `ogc2026/baseline/baseline_hh.py`
  - `ogc2026/baseline/myalgorithm.py`
  - `ogc2026/baseline/alg_versions/reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122.py`
- Revalidation headline:
  - `accepted_for_score=8/8`
  - `timed_out=0`
  - wrapper and active matched exactly on all four publish rows

## Drift that blocks a trusted-BEST publish

- Historical `v123` full-train row on `prob_39`:
  - objective `48,160,369`
  - `T=3521`
  - `L=194`
  - `P=8094`
- Current active-surface revalidation row on `prob_39`:
  - objective `48,598,605`
  - `T=3553`
  - `L=314`
  - `P=8168`
- This weaker `prob_39` row has now repeated on current-head active-surface
  checks, so the branch is scoreable but not yet cleanly aligned with the
  historical-best evidence.

## Candidate status since the last checkpoint

- `v129`:
  - scoreable smoke
  - no target-family movement
  - decision: rejected
- `v130`:
  - full 40 stayed scoreable
  - `prob_40` improved
  - `prob_39` regressed
  - avg objective worsened
  - decision: rejected

## Next step

- Treat `v123` as the best historical evidence on this branch, not as a fully
  re-cleared publish target.
- Investigate why the active surface keeps replaying the weaker `prob_39` row.
- Only after that drift is resolved should the next T-tail candidate cycle
  resume.
