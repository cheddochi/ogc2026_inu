# OGC2026 Recovery Checkpoint 2026-06-19 13:10 KST

## Decision

- publish type: recovery/failure checkpoint
- trusted current-source accepted BEST: none established
- historical accepted BEST: `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`

## Why this is not a trusted-best publish

The historical accepted v096 evidence is still real, but the current source
tree no longer reproduces it on key runtime-risk rows.

### Historical accepted evidence

- full train40:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`
- team-readable summary:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- headline:
  - `accepted_for_score=40/40`
  - timeout `0`
  - avg objective `15096298.7`
  - avg T `1558.675`

### Current-source failure evidence

- four-bay runtime recheck:
  `reports/ogc2026_reboot_v001/target_recheck_v096_fourbay_runtime_20260619_001/`
  - `prob_31`: timeout, runtime `70.680680s`, objective `46503155`
  - `prob_36`: accepted, runtime `52.655423s`, objective `1713312`
  - `prob_40`: accepted, runtime `43.937350s`, objective `6333528`
- direct prob37 recheck:
  `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/`
  - `prob_37`: timeout, runtime `71.377730s`, objective `17644653`
- fallback recovery baseline:
  `reports/ogc2026_reboot_v001/full_recheck_v083_train40_20260619_001/`
  - accepted_for_score `39/40`
  - failing row: `prob_37`, timeout `67.648573s`

## Candidate Judgment Closed Before Publish

### `reboot_v099_20260619_1845_prob31like_runtime_flatten_on_v096`

- smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v099_core9_20260619_001/`
  - accepted `9/9`
  - timeout `0`
- targeted path:
  `reports/ogc2026_reboot_v001/target_reboot_v099_prob31like_20260619_001/`
  - `prob_31`: recovered to runtime `53.232775s`, objective `40956985`
  - `prob_36`: accepted
  - `prob_40`: accepted
  - `prob_37`: still timeout `71.357656s`
- decision:
  - rejected
  - reason:
    the prob31-like recovery worked, but the active chain stayed non-scoreable
    because the inherited prob37-like runtime cliff was untouched

## Root Cause Seen So Far

- current prob37 log:
  `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/logs/hh__reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094/prob_37.log`
- observed runtime cliff:
  - inherited `v060` `release_due` direct builder now consumes about `46s`
  - later cheap reinsertion phases (`v073`, `v084`, `v093`, `v096`) are then
    skipped because no budget remains

## Next Hypothesis

- focus subtype:
  3-bay diffuse/mid-proc prob37-like family
- intended repair:
  flatten or cap the inherited `v060 release_due` warm-start path so later
  cheap reinsertion phases still execute under the 60s official limit
