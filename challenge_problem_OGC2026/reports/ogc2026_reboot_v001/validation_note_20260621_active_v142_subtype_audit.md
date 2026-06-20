# Validation Note: active v142 subtype audit after v162 plateau

- Decision: `recovery-only checkpoint`
- Trusted active BEST status: `historical evidence only, not freshly re-trusted`

## Why this is not a BEST publish

- The active wrapper still points to the historical rollback line:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Historical accepted evidence for that line is still the best trusted record:
  - `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - `accepted_for_score=40/40`
  - timeout `0`
  - invalid `0`
- But the current source tree still has not reproduced that line as a
  trustworthy live BEST surface after the rejected `v161` and `v162` recovery
  candidates.

## New evidence from this plateau audit

### 1. Representative subtype analysis refreshed from trusted v142 full40

- Analysis bundle:
  `reports/ogc2026_reboot_v001/subtype_analysis_v142_20260621_001/`
- Useful output:
  - `analysis.md`
  - `family_summary.csv`
  - `representative_tier_smoke.csv`
  - `subtype_table.csv`
- Main use:
  - refresh tier-representative smoke rows
  - refresh current high-T/runtime-risk family grouping before the next
    candidate

### 2. xlarge-lowproc family is not the next best checkpoint target

- Direct bypass audit:
  `reports/ogc2026_reboot_v001/probe_v142_v072_xlarge_lowproc_20260621_001/`
  - `prob_37` remained unstable / timed out
  - `prob_39` got worse under direct `v072`
- Guarded headroom audit:
  `reports/ogc2026_reboot_v001/target_v142_v143_xlarge_lowproc_20260621_001/`
  - `v143` improved `prob_39` and `prob_40`
  - but still did not recover `prob_37`
- Interpretation:
  - xlarge-lowproc still has signal, but it is not the cleanest next
    checkpoint hypothesis for current-tree recovery

### 3. prob27-like is the strongest positive recovery signal

- Focused compare:
  `reports/ogc2026_reboot_v001/probe_v142_v146_prob27like_20260621_001/`
- Result:
  - `prob_27`
    - current-tree `v142`: subprocess timeout after `90s`
    - `v146`: PASS `78787221 / T=5735 / 58.677993s`
  - `prob_25`
    - current-tree `v142`: PASS `1573893 / T=2267 / 53.905406s`
    - `v146`: fail-by-time-limit `1541899 / T=2223 / 64.784196s`
- Interpretation:
  - the useful runtime fix exists
  - but the current `v146` surface is too broad for a safe promotion because it
    spills onto sibling `prob_25`

## Current conclusion

- There is still no honest basis to publish the active wrapper as a newly
  trusted accepted BEST.
- The correct checkpoint label remains recovery/failure, not BEST promotion.
- The next coherent hypothesis should be:
  - narrow `prob27-like` feature guard only
  - preserve the `v146` runtime recovery on `prob_27`
  - avoid activation on sibling `prob_25`

