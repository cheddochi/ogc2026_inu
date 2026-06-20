# Publish Checkpoint: v142 Plateau / Trust Recheck

- Timestamp basis:
  `2026-06-20`
- Branch:
  `hh_algorithm_loop`
- Active trusted BEST:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Active surface:
  `ogc2026/baseline/baseline_hh.py`

## What Was Rechecked

- Canonical wrapper recheck:
  `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_002/`
  - accepted_for_score `7/7`
  - timeout `0`
  - invalid `0`
  - canonical sensitive rows reproduced:
    - `prob_27`: objective `76200619`, `T=5541`
    - `prob_40`: objective `5780789`, `T=8429`
- Trusted full evidence remains:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15035076.025`
  - avg T `1532.125`

## Current Judgment

- Decision:
  accepted BEST trust retained
- Reason:
  - the active wrapper surface revalidated cleanly on the canonical publish
    subset after the later exploratory drift signal
  - no better scoreable full40 line has been promoted since `v142`

## Rejected Candidate Since Last Accepted Checkpoint

- Candidate:
  `reboot_v143_20260620_1845_threebay_xlarge_lowproc_headroom_reinsert_on_v142`
- Status:
  rejected
- Reason:
  - localized `prob_37` objective gain reproduced
  - but full-train40 replay was not stable
  - `prob_40` regressed across repeated full runs, so the line is not trusted
    for promotion

## Plateau Summary

- No new score improvement was promoted in this cycle.
- The remaining high-T frontier is still concentrated in:
  - `prob_38`
  - `prob_27`
  - `prob_37`
  - `prob_33`
  - `prob_39`
  - `prob_31`
  - `prob_40`

## Next Hypothesis

- Immediate focus:
  determinism / reliability audit before another nested family override
- Working direction:
  - isolate why exploratory direct-file probes can drift while the canonical
    wrapper subset remains stable
  - prefer a cleaner T-focused family move that does not wrap the active
    prob40-like parent inside another layer

## Historical Team Reference

- Shared historical benchmark report:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
