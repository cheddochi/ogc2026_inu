# OGC 2026 Training Benchmark Report - Recovery Checkpoint

> Recovery checkpoint on branch `hh_algorithm_loop`
>
> Active wrapper remains
> `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
> as a rollback line only; this is not a trusted-BEST promotion.

---

## Headline

- Feasible pass on latest representative smoke: `9/9`
- Feasible pass on latest targeted runtime-family smoke: `7/8`
- timed_out count on targeted runtime-family smoke: `1`
- invalid/error count on targeted runtime-family smoke: `1 / 0`
- meaningful_progress: `false`
- checkpoint mode: `recovery`

## Current Historical Reference

- Historical accepted BEST evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
  - accepted_for_score `40/40`
  - Total Objective `601,403,041`
  - Avg Objective `15,035,076.025`
  - Total T `61,285`
  - Avg T `1,532.125`
  - Total L `107,333`
  - Avg L `2,683.325`
  - Total P `167,431`
  - Avg P `4,185.775`

## Latest Candidate Closed

- Candidate:
  `reboot_v171_20260621_1215_twobay_concentrated_early_exit_on_v170`
- Decision:
  `rejected`

Representative tier smoke:

- path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v171_tier9_20260621_001/`
- result:
  - accepted_for_score `9/9`
  - timeout `0`

Targeted runtime-family smoke:

- path:
  `reports/ogc2026_reboot_v001/target_reboot_v171_runtime_family_20260621_001/`
- result:
  - accepted_for_score `7/8`
  - timeout `1`
  - blocking row:
    - `prob_37`: `90944439 / T=25911 / 73.74s`

Recovered narrow-family rows:

- `prob_25`: `1537897 / T=2217 / 35.85s`
- `prob_27`: `78787221 / T=5735 / 36.04s`
- `prob_33`: `59704468 / T=8814 / 32.73s`

Remaining guard-tail rows:

- `prob_31`: `295623767 / T=21938 / 44.29s`
- `prob_38`: `1120394778 / T=83806 / 51.70s`
- `prob_39`: `251183395 / T=18737 / 59.79s`
- `prob_40`: `8026436 / T=11795 / 59.93s`

## Interpretation

`v171` repaired a useful narrow current-tree slice, but it did not close the
runtime-risk Family B tail. Because the targeted guard still failed and there
is no scoreable full40 evidence, this cycle does not justify BEST promotion.

## Next Direction

Stay in T-zero-first recovery mode:

- preserve the useful `2bay/highproc/concentrated` early exits as
  candidate-only evidence
- move the next bounded improvement cycle to the
  `3bay/runtime-risk/high-T tail` family
- keep the active wrapper pinned to the historical rollback line until a fresh
  scoreable full40 line is re-established
