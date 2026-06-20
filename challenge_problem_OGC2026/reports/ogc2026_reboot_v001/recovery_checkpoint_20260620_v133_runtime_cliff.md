# Recovery checkpoint: v133 runtime-cliff (2026-06-20)

## Decision

Publish this checkpoint as a recovery/failure checkpoint, not as a trusted
accepted BEST.

## Why

- `v133` has valid historical accepted evidence on full40:
  `reports/ogc2026_reboot_v001/full_reboot_v133_train40_20260620_001/`
- however, the latest direct publish revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v133_publish_20260620_002/`
  stayed scoreable but failed to reproduce the accepted `prob_40` gain
- `prob_40` reverted from:
  - objective `5860829`, `T=8549`
  to:
  - objective `5910122`, `T=8622`
- the active source still points to `v133`; the problem is not source drift but
  runtime-headroom instability around the narrow prob40-like guard

## Current interpretation of trust

- historical best evidence:
  - `v133` remains the strongest known historical accepted full40 line in this
    working branch
- current publish trust:
  - not strong enough to claim as the present trusted accepted BEST for team
    sharing, because the active wrapper did not revalidate the key `prob_40`
    improvement on the latest publish check

## Suggested next recovery paths

1. Repair the `prob_40` headroom cliff in a follow-up candidate so the
   improvement fires under repeat revalidation, not just one accepted full run.
2. If a stable publish is needed before that repair lands, roll the active
   surface back to the last plateau-stable line (`v132`) and publish it as a
   recovery plateau checkpoint instead of overstating `v133`.

## Included evidence for this checkpoint

- current state marker:
  `ogc2026/baseline/alg_versions/ACTIVE_VERSION.md`
- historical decision log:
  `ogc2026/baseline/alg_versions/VERSION_LOG.md`
- active wrapper:
  `ogc2026/baseline/baseline_hh.py`
- historical accepted full40:
  `reports/ogc2026_reboot_v001/full_reboot_v133_train40_20260620_001/summary.json`
- latest failed publish revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v133_publish_20260620_002/`
- team-shared historical report reference:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
