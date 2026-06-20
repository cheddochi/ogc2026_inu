# Publish checkpoint: v135 trusted accepted BEST (2026-06-20)

## Decision

Publish this checkpoint as the current trusted accepted BEST.

## Why

- the active source, metadata, and evidence now agree on
  `reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132`
- the line is scoreable on full train40:
  - `accepted_for_score=40/40`
  - timeout `0`
  - invalid/error `0`
- the direct `baseline_hh.py` surface also revalidated the critical publish
  subset, including the `prob_40` improvement that had previously been unstable
  under `v133`

## Trusted evidence included with this checkpoint

- active wrapper:
  `ogc2026/baseline/baseline_hh.py`
- active marker:
  `ogc2026/baseline/alg_versions/ACTIVE_VERSION.md`
- decision log:
  `ogc2026/baseline/alg_versions/VERSION_LOG.md`
- trusted source file:
  `ogc2026/baseline/alg_versions/reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132.py`
- validation note:
  `reports/ogc2026_reboot_v001/validation_note_v135_publish_20260620.md`
- representative smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v135_tier9_20260620_001/`
- targeted smoke:
  `reports/ogc2026_reboot_v001/target_reboot_v135_prob40_headroom_20260620_001/`
- short-limit stress:
  `reports/ogc2026_reboot_v001/stress_reboot_v135_prob40_short45_20260620_001/`
- direct active-surface publish revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v135_publish_20260620_001/`
- full train40 benchmark:
  `reports/ogc2026_reboot_v001/full_reboot_v135_train40_20260620_001/`

## What this checkpoint claims

- `v135` is the current trusted accepted BEST on this branch
- the improvement is modest but real:
  - avg objective improved versus trusted `v132`
  - avg T improved versus trusted `v132`
  - the only changed train40 row is `prob_40`, where T and objective both improved

## Remaining backlog after this publish

- plateau/T-zero-first follow-up should move away from `prob_40` and focus on
  the remaining high-T tail:
  - `prob_38`
  - `prob_27`
  - `prob_37`
  - `prob_33`
  - `prob_39`
