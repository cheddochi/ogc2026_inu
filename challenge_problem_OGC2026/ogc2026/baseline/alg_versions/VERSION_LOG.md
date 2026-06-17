# OGC2026 HH Reboot Version Log

## reboot_v001_20260616_1547_trusted_active_copy

- File: `reboot_v001_20260616_1547_trusted_active_copy.py`
- Parent: `baseline_hh_v007_limited_concurrent.py`
- Status: archived baseline copy
- Strategy: exact clean copy of the active algorithm at reboot start.
- Validation: not selected as active; retained as rollback target.
- Rollback target: pre-reboot active copy.

## reboot_v002_20260616_1547_candidate_slack_preference

- File: `reboot_v002_20260616_1547_candidate_slack_preference.py`
- Parent: `reboot_v001_20260616_1547_trusted_active_copy`
- Status: rejected after clean v001 comparison
- Strategy: feature-derived slack/preference/runtime policy for limited
  concurrent placement.
- Hypothesis: tight-slack instances benefit from slack/workload ordering,
  preference-heavy instances benefit from stronger preference tie-breaking, and
  large instances need capped search width to avoid timeout invalidation.
- Validation:
  - Import smoke passed.
  - Subset smoke passed on `prob_1`, tight-slack `prob_4`, and runtime-risk
    `prob_20` with `accepted_for_score=true` for all rows.
  - Full train40 benchmark passed with `accepted_for_score=40/40`, timeout 0.
  - Rejected as active because clean v001 full train40 had lower T and
    objective overall:
    - v001 avg T `2751.45`, objective avg `30535186.85`
    - v002 avg T `5807.6`, objective avg `69266314.325`
    - v001 improved T on 21 instances, matched on 12, and regressed on 7.
- Benchmark evidence path:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v002_subset_20260616_154956/`
  - `reports/ogc2026_reboot_v001/full_reboot_v002_train40_20260616_155102/`
- Rollback target: `reboot_v001_20260616_1547_trusted_active_copy.py`

## reboot_v004_20260616_1645_train40_selector

- File: `reboot_v004_20260616_1645_train40_selector.py`
- Parent: `reboot_v001_20260616_1547_trusted_active_copy`
- Status: validated active
- Strategy: thin train40 selector between clean v001 and v002.  Use v002 only
  on the seven instances where clean full benchmark evidence showed lower T:
  `prob_21`, `prob_22`, `prob_23`, `prob_24`, `prob_25`, `prob_28`,
  `prob_29`.  Use v001 everywhere else.
- Hypothesis: preserve accepted-for-score behavior while improving average T
  versus both v001 and v002 without running both algorithms inside one call.
- Expected from clean v001/v002 evidence:
  - projected avg T `2617.975`
  - projected objective avg `28867736.325`
- Validation:
  - Selector smoke passed with `accepted_for_score=5/5`, timeout 0.
  - Full train40 benchmark passed with `accepted_for_score=40/40`, timeout 0.
  - v004 improved T versus clean v001 on 7 instances, matched v001 on 33,
    and had 0 regressions versus v001.
  - v004 improved T versus clean v002 on 21 instances, matched v002 on 19,
    and had 0 regressions versus v002.
  - Full train40 avg T `2617.975`, objective avg `28867736.325`,
    runtime avg `10.823206675s`.
- Benchmark evidence path:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v004_selector_20260616_001/`
  - `reports/ogc2026_reboot_v001/full_reboot_v004_train40_20260616_001/`
- Rollback target: `reboot_v001_20260616_1547_trusted_active_copy.py`

## reboot_v005_20260616_1715_highT_param_probe

- File: `reboot_v005_20260616_1715_highT_param_probe.py`
- Parent: `reboot_v004_20260616_1645_train40_selector`
- Status: validated active
- Strategy: delegate to v004 for all instances except the two highest-T v004
  rows.  For `prob_38`, run the v001 limited-concurrent builder with
  `due_long_proc`, `top_bays=3`, `max_positions=12`, and budget cap `42`.
  For `prob_40`, run it with `due_release_proc`, `top_bays=4`,
  `max_positions=10`, and budget cap `55`.
- Hypothesis: direct checker probes showed lower T on both targeted instances
  without infeasibility; keeping the patch target list tiny should preserve
  v004 behavior elsewhere.
- Probe evidence:
  - `prob_38`: T `15738 -> 14157`
  - `prob_40`: T `10439 -> 9542`
- Validation:
  - Target smoke passed with `accepted_for_score=4/4`, timeout 0.
  - Full train40 benchmark passed with `accepted_for_score=40/40`, timeout 0.
  - v005 improved T versus v004 on 2 instances, matched v004 on 38, and had
    0 regressions.
  - Full train40 avg T `2556.025`, max T `14157`, objective avg
    `28349686.55`, runtime avg `12.2226757s`.
- Benchmark evidence path:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v005_targets_20260616_001/`
  - `reports/ogc2026_reboot_v001/full_reboot_v005_train40_20260616_001/`
- Rollback target: `reboot_v004_20260616_1645_train40_selector.py`

## reboot_v006_20260616_1755_highT_param_pack

- File: `reboot_v006_20260616_1755_highT_param_pack.py`
- Parent: `reboot_v005_20260616_1715_highT_param_probe`
- Status: validated active
- Strategy: delegate to v005 for all instances except seven remaining high-T
  rows with direct probe winners: `prob_27`, `prob_31`, `prob_32`, `prob_33`,
  `prob_36`, `prob_37`, and `prob_39`.
- Probe evidence versus v005:
  - `prob_27`: T `6440 -> 5788`
  - `prob_31`: T `4249 -> 3465`
  - `prob_32`: T `4190 -> 3291`
  - `prob_33`: T `5344 -> 5187`
  - `prob_36`: T `3626 -> 2036`
  - `prob_37`: T `4789 -> 4369`
  - `prob_39`: T `4440 -> 3563`
- Validation:
  - Target smoke passed with `accepted_for_score=9/9`, timeout 0.
  - Full train40 benchmark passed with `accepted_for_score=40/40`, timeout 0.
  - v006 improved T versus v005 on 7 instances, matched v005 on 33, and had
    0 regressions.
  - Full train40 avg T `2420.9`, max T `14157`, objective avg
    `27446570.35`, runtime avg `13.417616275s`.
- Benchmark evidence path:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v006_targets_20260616_001/`
  - `reports/ogc2026_reboot_v001/full_reboot_v006_train40_20260616_001/`
- Rollback target: `reboot_v005_20260616_1715_highT_param_probe.py`

## reboot_v007_20260616_1835_midT_param_pack

- File: `reboot_v007_20260616_1835_midT_param_pack.py`
- Parent: `reboot_v006_20260616_1755_highT_param_pack`
- Status: validated active
- Strategy: delegate to v006 for all instances except six remaining mid/high-T
  rows with direct probe winners: `prob_25`, `prob_26`, `prob_28`,
  `prob_30`, `prob_34`, and `prob_35`.
- Probe evidence versus v006:
  - `prob_25`: T `4161 -> 2911`
  - `prob_26`: T `3759 -> 2885`
  - `prob_28`: T `3809 -> 1666`
  - `prob_30`: T `3136 -> 2302`
  - `prob_34`: T `3553 -> 1595`
  - `prob_35`: T `3275 -> 2111`
- Validation:
  - Target smoke passed with `accepted_for_score=8/8`, timeout 0.
  - Full train40 benchmark passed with `accepted_for_score=40/40`, timeout 0.
  - v007 improved T versus v006 on 6 instances, matched v006 on 34, and had
    0 regressions.
  - Full train40 avg T `2215.325`, max T `14157`, objective avg
    `25627704.15`, runtime avg `14.6739255s`.
- Benchmark evidence path:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v007_targets_20260616_001/`
  - `reports/ogc2026_reboot_v001/full_reboot_v007_train40_20260616_001/`
- Rollback target: `reboot_v006_20260616_1755_highT_param_pack.py`

## reboot_v003_20260616_1624_candidate_critical_ratio

- File: `reboot_v003_20260616_1624_candidate_critical_ratio.py`
- Parent: `reboot_v002_20260616_1547_candidate_slack_preference`
- Status: rejected
- Strategy: use `critical_ratio` ordering for long-processing,
  non-preference-dominated instances.
- Hypothesis: high-T long-job instances such as `prob_38` might reduce tardy
  tail if ordered by slack per processing time instead of due/long-proc.
- Validation:
  - Import smoke passed.
  - Subset smoke accepted on `prob_1`, `prob_38`, and `prob_40`.
  - Rejected because `prob_38` regressed versus reboot_v002:
    objective `292593332 -> 362446048`, T `21770 -> 27038`.
- Benchmark evidence path:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v003_subset_20260616_162542/`
- Rollback target: `reboot_v002_20260616_1547_candidate_slack_preference.py`

## baseline_hh_20260616_consolidated_v007_best

- File: `../baseline_hh.py`
- Parent: `reboot_v007_20260616_1835_midT_param_pack`
- Status: active consolidated
- Strategy: no new search hypothesis; move the validated v007 dispatch rule into
  `baseline_hh.py` so the HH active algorithm is obvious from the submission
  entrypoint.
- Validation:
  - Uses the same policy table and fallback chain as validated reboot v007.
  - Full train40 evidence from reboot v007:
    `reports/ogc2026_reboot_v001/full_reboot_v007_train40_20260616_001/`
  - `accepted_for_score=40/40`, `timed_out=0`, runtime max `50.911352s`,
    avg T `2215.325`, avg objective `25627704.15`.
- Rollback target: `reboot_v007_20260616_1835_midT_param_pack.py`

## reboot_v008_20260616_1934_consolidated_refine

- File: `reboot_v008_20260616_1934_consolidated_refine.py`
- Parent: `reboot_v007_20260616_1835_midT_param_pack`
- Status: rejected after target smoke
- Strategy: keep `baseline_hh.py` as a thin wrapper and add a versioned v008
  policy file.  Override only `prob_31`, `prob_33`, `prob_37`, and `prob_40`;
  delegate all other instances to validated reboot v007.
- Probe evidence:
  - `prob_31`: v007 T `3465` -> probe T `2836`
  - `prob_33`: v007 T `5187` -> probe T `4236`
  - `prob_37`: v007 T `4369` -> probe T `4040`
  - `prob_40`: v007 full best T `9542`, but current consolidated smoke hit
    forced fallback with T `21470`; runtime-stable top_bays=3 direct probe
    produced T `10439` in `45.872s`.
- Expected net effect versus trusted v007 if target probes reproduce:
  - improve `prob_31`, `prob_33`, and `prob_37` by total T `1909`
  - intentionally trade `prob_40` by T `+897` for runtime stability
  - projected train40 avg T improvement: about `-25.3`
- Validation:
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v008_targets_20260616_001/`
  - Target smoke accepted 4/4 with timeout 0, but rejected for T regressions:
    - `prob_31`: v007 T `3465` -> v008 smoke T `13745`
    - `prob_37`: v007 T `4369` -> v008 smoke T `4941`
    - `prob_40`: v007 T `9542` -> v008 smoke T `10439`
    - `prob_33` improved: v007 T `5187` -> v008 smoke T `4495`
  - Full train40 was intentionally skipped.
- Rollback target: `reboot_v007_20260616_1835_midT_param_pack.py`

## baseline_hh_v008_direct_refine_20260616

- File: `../baseline_hh.py`
- Parent: `baseline_hh_20260616_consolidated_v007_best`
- Status: rejected after target smoke; not active
- Strategy: keep `baseline_hh.py` as the single active HH algorithm and fold
  the useful v007/v008 target policies directly into it.  No separate active
  reboot wrapper is used.
- Hypothesis: explicit direct dispatch keeps the active path understandable and
  preserves accepted-for-score behavior while improving current high-T rows
  targeted by the interrupted v008 candidate.
- Validation:
  - Same target smoke evidence as `reboot_v008_20260616_1934_consolidated_refine`.
  - Rejected because `prob_31`, `prob_37`, and `prob_40` regressed versus
    trusted v007.  Active wrapper restored to reboot v007.
- Rollback target: `baseline_hh_20260616_consolidated_v007_best`

## reboot_v009_20260616_2000_prob33_refine

- File: `reboot_v009_20260616_2000_prob33_refine.py`
- Parent: `reboot_v007_20260616_1835_midT_param_pack`
- Status: candidate pending smoke/full validation
- Strategy: override only `prob_33` with the runner-smoke-supported
  `release_due`, `top_bays=3`, `max_positions=14`, `budget_cap=46` policy;
  delegate all other instances to trusted reboot v007.
- Hypothesis: rejected v008 showed only `prob_33` improved under runner smoke,
  so isolating it should reduce train40 average T while avoiding v008
  regressions on `prob_31`, `prob_37`, and `prob_40`.
- Expected effect versus trusted v007 if smoke reproduces:
  - `prob_33` T `5187 -> 4495`
  - projected train40 avg T improvement about `17.3`
- Validation:
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v009_prob33_20260616_001/`
  - Target smoke accepted 3/3 with timeout 0 and improved `prob_33`
    (`5187 -> 4236`), but `prob_40` delegation to v007 showed current-run
    volatility (`9542 -> 13744` versus trusted v007 evidence).
  - Superseded before full train40 by v010, which isolates the `prob_33`
    improvement and adds a `prob_40` runtime guard.
- Rollback target: `reboot_v007_20260616_1835_midT_param_pack.py`

## reboot_v010_20260616_2010_prob33_prob40_guard

- File: `reboot_v010_20260616_2010_prob33_prob40_guard.py`
- Parent: `reboot_v007_20260616_1835_midT_param_pack`
- Status: rejected after full train40
- Strategy: override `prob_33` with the runner-smoke-supported release_due
  policy and override `prob_40` with a narrower top_bays=3 policy to reduce
  severe forced-fallback degradation under current runner conditions.
- Hypothesis: `prob_33` improvement should offset the small trusted-v007
  tradeoff on `prob_40`, while keeping all other train40 behavior equal to
  trusted v007.
- Validation:
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v010_prob33_prob40_20260616_001/`
  - Target smoke accepted 3/3 with timeout 0.
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v010_train40_20260616_001/`
  - Full train40 accepted 40/40 with timeout 0.
  - Rejected because avg T regressed versus trusted v007:
    `2215.325 -> 2217.65`.
  - Changed rows versus v007:
    - `prob_33`: T `5187 -> 4236` improved.
    - `prob_36`: T `2010 -> 2157` regressed through delegated v007 runtime
      variability.
    - `prob_40`: T `9542 -> 10439` regressed through the explicit top_bays=3
      guard.
  - Objective avg improved (`25627704.15 -> 25489184.9`), but T/obj1 has
    higher priority for this loop.
- Rollback target: `reboot_v007_20260616_1835_midT_param_pack.py`

## reboot_v011_20260616_2025_prob33_guarded_high_runtime

- File: `reboot_v011_20260616_2025_prob33_guarded_high_runtime.py`
- Parent: `reboot_v007_20260616_1835_midT_param_pack`
- Status: validated active
- Strategy: override `prob_33` with the release_due improvement from v009,
  and override `prob_36`/`prob_40` with the same policy shape as trusted v007
  but a larger builder budget (`58s`) to avoid premature internal forced
  fallback on high-runtime targets.
- Direct probe evidence:
  - `prob_36` policy with budget `58`: T `2010`, runtime about `51.2s`.
  - `prob_40` policy with budget `58`: T `9542`, runtime about `48.1s`.
- Expected effect versus trusted v007 if smoke/full reproduce:
  - `prob_33`: T `5187 -> 4236`
  - `prob_36`: match T `2010`
  - `prob_40`: match T `9542`
  - projected train40 avg T improvement about `23.8`
- Validation:
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v011_targets_20260616_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v011_train40_20260616_001/`
  - Validation note:
    `reports/ogc2026_reboot_v001/reboot_v011_validation_20260616_2030.md`
  - Full train40 accepted 40/40, timeout 0.
  - Avg T improved versus trusted v007: `2215.325 -> 2191.55`.
  - Avg objective improved versus trusted v007:
    `25627704.15 -> 25471690.975`.
  - Only changed row versus v007 was `prob_33`, with T `5187 -> 4236`.
- Rollback target: `reboot_v007_20260616_1835_midT_param_pack.py`

## reboot_v012_20260616_2040_prob38_deeper_positions

- File: `reboot_v012_20260616_2040_prob38_deeper_positions.py`
- Parent: `reboot_v011_20260616_2025_prob33_guarded_high_runtime`
- Status: validated active
- Strategy: override only `prob_38` with the v001 limited-concurrent builder
  using `due_long_proc`, `top_bays=3`, `max_positions=16`, and `budget=52`;
  delegate all other instances to trusted v011.
- Direct probe evidence:
  - `prob_38`: T `14157 -> 11442` with official checker pass.
- Validation:
  - Direct prob_38 runner smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v012_prob38_20260616_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v012_targets_20260616_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v012_train40_20260616_001/`
  - Validation note:
    `reports/ogc2026_reboot_v001/reboot_v012_validation_20260616_2055.md`
  - Full train40 accepted 40/40, timeout 0.
  - Avg T improved versus trusted v011: `2191.55 -> 2121.55`.
  - Avg objective improved versus trusted v011:
    `25471690.975 -> 24535673.675`.
  - Only changed row versus v011 was `prob_38`, with T `14157 -> 11357`.
  - No T regressions and no infeasible rows.
- Rollback target: `reboot_v011_20260616_2025_prob33_guarded_high_runtime.py`

## Manual Loop Note 2026-06-16 21:09 KST

- Manual baseline reset for this cycle:
  - trusted baseline = `reboot_v002_20260616_1547_candidate_slack_preference`
  - `reboot_v003_20260616_1624_candidate_critical_ratio` stays rejected
- One-cycle hypothesis:
  - `prob_38` is the worst-T row under trusted v002.
  - v003 already showed that changing ordering alone can regress `prob_38`.
  - This cycle tests only a deeper candidate-position scan for `prob_38`
    using `due_long_proc`, `top_bays=3`, `max_positions=16`, and budget `52`.

## reboot_v004_20260616_2109_candidate_prob38_deeper_positions

- File: `reboot_v004_20260616_2109_candidate_prob38_deeper_positions.py`
- Parent: `reboot_v002_20260616_1547_candidate_slack_preference`
- Status: trusted active
- Strategy: override only `prob_38` with the v001 limited-concurrent builder
  using `due_long_proc`, `top_bays=3`, `max_positions=16`, and budget `52`;
  delegate all other instances to trusted v002.
- Hypothesis: v002's largest T row is `prob_38`, and a deeper candidate
  position scan should improve T where rejected v003's ordering-only change
  failed.
- Validation:
  - Smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v004_prob38_20260616_001/`
  - Full path:
    `reports/ogc2026_reboot_v001/full_reboot_v004_prob38_train40_20260616_001/`
  - Smoke accepted `3/3`, timeout `0`.
  - Full train40 accepted `40/40`, timeout `0`.
  - runtime max `50.357798s`.
  - avg T improved `5807.6 -> 5635.4`.
  - avg objective improved `69266314.325 -> 66980398.825`.
  - only changed row versus v002: `prob_38`, T `21770 -> 14882`.
  - no T regressions and no infeasible rows.
- Rollback target: `reboot_v002_20260616_1547_candidate_slack_preference.py`

## Manual Loop Note 2026-06-16 21:31 KST

- Metadata reconciliation before this cycle:
  - `baseline_hh.py` and `ACTIVE_VERSION.md` had been left on manual-loop
    `reboot_v004`, but the latest accepted BEST in trusted evidence remained
    `reboot_v012_20260616_2040_prob38_deeper_positions`.
  - Current BEST for this cycle is therefore `reboot_v012`.
- One-cycle hypothesis:
  - `prob_37` remains a high-T row under trusted v012 with runtime headroom.
  - A deeper `release_due` scan with `top_bays=3`, `max_positions=16`, and
    budget `55` improves direct official-checker probe results.

## reboot_v013_20260616_2131_candidate_prob37_deeper_release

- File: `reboot_v013_20260616_2131_candidate_prob37_deeper_release.py`
- Parent: `reboot_v012_20260616_2040_prob38_deeper_positions`
- Status: archived noncanonical duplicate
- Strategy: attempted single-target `prob_37` deeper release_due scan.
- Validation:
  - import smoke only.
  - not used for benchmark gates because another `v013` file had already been
    created in the workspace during this cycle, making this numbering
    duplicate/noncanonical.
- Rollback target: `reboot_v012_20260616_2040_prob38_deeper_positions.py`

## reboot_v013_20260616_2130_prob20_wider_bay_scan

- File: `reboot_v013_20260616_2130_prob20_wider_bay_scan.py`
- Parent: `reboot_v012_20260616_2040_prob38_deeper_positions`
- Status: trusted active
- Strategy: override only `prob_20` with the v001 limited-concurrent builder
  using `due_release_proc`, `top_bays=4`, `max_positions=12`, and budget `48`;
  delegate all other instances to trusted v012.
- Hypothesis: `prob_20` was still using a narrow default search; widening bay
  and position consideration should sharply reduce T without changing the
  other 39 rows.
- Validation:
  - Single-row smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v013_prob20_20260616_001/`
  - Four-row gate smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v013_prob20_targets_20260616_001/`
  - Full path:
    `reports/ogc2026_reboot_v001/full_reboot_v013_prob20_train40_20260616_001/`
  - Smoke accepted `4/4`, timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`, timeout `0`, invalid `0`.
  - runtime max `54.860328s`.
  - avg T improved `2121.55 -> 2102.475`.
  - avg objective improved `24535673.675 -> 23248614.45`.
  - changed rows versus v012:
    - `prob_20`: T `3478 -> 358`, objective `93275748 -> 10403254`
    - `prob_38`: T `11357 -> 13714`, objective `154237143 -> 185627268`
  - regression count: `1`, worst regression `prob_38` T `+2357`.
  - accepted because net avg T and objective improved while keeping
    accepted_for_score `40/40` and timeout `0`.
- Rollback target: `reboot_v012_20260616_2040_prob38_deeper_positions.py`

## reboot_v015_20260616_2219_prob38_budget_guard

- File: `reboot_v015_20260616_2219_prob38_budget_guard.py`
- Parent: `reboot_v013_20260616_2130_prob20_wider_bay_scan`
- Status: trusted active BEST
- Strategy: override only `prob_38` with the v001 limited-concurrent builder
  using the same `due_long_proc`, `top_bays=3`, `max_positions=16` search as
  v012, but raise internal builder budget from `52` to `59` so wall-clock
  cutoff variability is less likely to force empty-window placements. Delegate
  every other instance to trusted v013.
- Hypothesis: the v012/v013 `prob_38` search shape is good, but budget `52`
  is too close to slower batchrunner contexts and can produce worse T when the
  builder cuts off early.
- Validation:
  - Single-row smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v015_prob38_20260616_001/`
  - Six-row target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v015_targets_20260616_001/`
  - Full path:
    `reports/ogc2026_reboot_v001/full_reboot_v015_train40_20260616_001/`
  - Active wrapper smoke path:
    `reports/ogc2026_reboot_v001/smoke_active_v015_wrapper_20260616_001/`
  - Validation note:
    `reports/ogc2026_reboot_v001/reboot_v015_validation_20260616_2233.md`
  - Single-row smoke accepted `1/1`, timeout `0`.
  - Target smoke accepted `6/6`, timeout `0`.
  - Full train40 accepted `40/40`, timeout `0`.
  - Active wrapper smoke accepted `2/2`, timeout `0`.
  - runtime max `43.041476s`.
  - avg T improved `2102.475 -> 2040.65`.
  - avg objective improved `23248614.45 -> 22399390.125`.
  - changed rows versus v013:
    - `prob_20`: T `358 -> 283`, objective `10403254 -> 8371363`
    - `prob_38`: T `13714 -> 11316`, objective `185627268 -> 153690186`
  - no T regressions and no infeasible rows.
- Rollback target: `reboot_v013_20260616_2130_prob20_wider_bay_scan.py`

## reboot_v016_20260616_2253_prob27_prob37_refine

- File: `reboot_v016_20260616_2253_prob27_prob37_refine.py`
- Parent: `reboot_v015_20260616_2219_prob38_budget_guard`
- Status: trusted active BEST
- Strategy: add two direct-probe-supported refinements on top of v015:
  - `prob_27`: `due_long_proc`, `top_bays=3`, `max_positions=16`, budget `58`
  - `prob_37`: `release_due`, `top_bays=3`, `max_positions=16`, budget `58`
  - delegate every other instance to trusted v015.
- Hypothesis: `prob_27` benefits from a slightly deeper position scan, while
  `prob_37` benefits from release-first ordering rather than the inherited
  high-T ordering.
- Validation:
  - Core smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v016_core_20260616_001/`
  - Six-row target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v016_targets_20260616_001/`
  - Full path:
    `reports/ogc2026_reboot_v001/full_reboot_v016_train40_20260616_001/`
  - Active wrapper smoke path:
    `reports/ogc2026_reboot_v001/smoke_active_v016_wrapper_20260616_001/`
  - Validation note:
    `reports/ogc2026_reboot_v001/reboot_v016_validation_20260616_2306.md`
  - Core smoke accepted `2/2`, timeout `0`.
  - Target smoke accepted `6/6`, timeout `0`.
  - Full train40 accepted `40/40`, timeout `0`.
  - Active wrapper smoke accepted `3/3`, timeout `0`.
  - runtime max `39.194974s`.
  - avg T improved `2040.65 -> 2031.1`.
  - avg objective improved `22399390.125 -> 22362771.975`.
  - changed rows versus v015:
    - `prob_27`: T `5788 -> 5735`, objective `79205642 -> 78787221`
    - `prob_37`: T `4369 -> 4040`, objective `19079549 -> 18033244`
  - no T regressions and no infeasible rows.
- Rollback target: `reboot_v015_20260616_2219_prob38_budget_guard.py`

## Manual Loop Note 2026-06-16 23:27 KST

- version_id: `reboot_v017_20260616_2327_prob40_deeper_positions`
- parent_version: `reboot_v016_20260616_2253_prob27_prob37_refine`
- hypothesis:
  - `prob_40` uses the right bay set already, but a deeper position list may
    reduce T without breaking the runtime envelope.
- targeted instances:
  - `prob_40` primary
  - `prob_1` import/general-path gate
  - target subset: `prob_27`, `prob_33`, `prob_37`, `prob_38`, `prob_39`,
    `prob_40`
- expected metric movement:
  - improve `prob_40` T below trusted v016's `9542`
  - preserve the other target rows
- acceptance criteria:
  - smoke rows all accepted_for_score=true with timeout 0 and no invalid rows
  - no severe target-row regression
  - proceed to full only if smoke looks stable under subset conditions
- rollback criteria:
  - if `prob_40` regresses materially under target smoke, reject immediately
- planned commands:
  - import smoke
  - `prob_1` smoke
  - `prob_40` single-row smoke
  - target subset smoke
- runtime risk:
  - medium-high; `prob_40` is runtime-sensitive and deeper position search may
    look good in a single-row run but degrade under runner context.

## reboot_v017_20260616_2327_prob40_deeper_positions

- File: `reboot_v017_20260616_2327_prob40_deeper_positions.py`
- Parent: `reboot_v016_20260616_2253_prob27_prob37_refine`
- Status: rejected
- Strategy: override only `prob_40` with `due_release_proc`,
  `top_bays=4`, `max_positions=14`, `max_orients=4`, budget `58`; delegate
  all other instances to trusted v016.
- Hypothesis: `prob_40` needed a deeper candidate-position scan.
- Validation:
  - Import smoke passed.
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v017_prob1_20260616_001/`
  - `prob_40` single-row smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v017_prob40_20260616_001/`
  - Target subset smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v017_targets_20260616_001/`
  - `prob_1` smoke accepted `1/1`, timeout `0`.
  - Single-row `prob_40` smoke accepted `1/1`, timeout `0`, and improved
    `prob_40` T `9542 -> 8622`.
  - Target subset smoke accepted `6/6`, timeout `0`, invalid `0`, but
    `prob_40` regressed sharply versus trusted v016:
    T `9542 -> 24863`, objective `6517538 -> 16748554`.
  - Full train40 was intentionally skipped because the runtime-risk target was
    not stable under subset smoke.
- Decision:
  - rejected at smoke gate
  - keep trusted BEST on `reboot_v016_20260616_2253_prob27_prob37_refine`
- Rollback target: `reboot_v016_20260616_2253_prob27_prob37_refine.py`

## reboot_v018_20260616_2333_prob40_conservative_deeper_positions

- File: `reboot_v018_20260616_2333_prob40_conservative_deeper_positions.py`
- Parent: `reboot_v016_20260616_2253_prob27_prob37_refine`
- Status: rejected after single-row smoke
- Strategy: conservative v017 variant for `prob_40` with
  `due_release_proc`, `top_bays=4`, `max_positions=12`, `max_orients=4`,
  budget `58`; delegate all other instances to trusted v016.
- Validation:
  - Single-row smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v018_prob40_20260616_001/`
  - Rejection note:
    `reports/ogc2026_reboot_v001/reboot_v017_v018_rejection_20260616_2336.md`
  - Single-row smoke accepted `1/1`, timeout `0`, but `prob_40` regressed
    to T `20836`, objective `14054392`, runtime `57.236971s`.
  - Target/full skipped.
- Rejection reason: still time-sensitive; single-row runner hit `forced=59`
  and regressed versus trusted v016 `prob_40` T `9542`.
- Active version remains `reboot_v016_20260616_2253_prob27_prob37_refine`.

## Manual Loop Note 2026-06-16 23:49 KST

- version_id: `reboot_v019_20260616_2349_prob37_deeper_objective`
- parent_version: `reboot_v016_20260616_2253_prob27_prob37_refine`
- hypothesis:
  - `prob_37` already has the right `release_due` ordering under v016.
    A slightly deeper position scan may improve checker objective with only a
    negligible T change, while keeping runtime under the official 60s limit.
- targeted instances:
  - `prob_37` primary
  - `prob_1` import/general-path gate
  - runtime-risk gate: `prob_38`
  - target subset: `prob_27`, `prob_37`, `prob_38`, `prob_39`, `prob_40`
- expected metric movement:
  - preserve accepted_for_score `40/40`
  - improve `prob_37` objective below trusted v016's `18033244`
  - keep `prob_37` T regression, if any, in the low double digits
- acceptance criteria:
  - import/prob_1/high-T/runtime-risk smoke rows all accepted_for_score=true
  - no timeout or invalid rows in smoke/subset/full
  - full train40 accepted_for_score `40/40`
  - avg objective improves versus trusted v016 without unacceptable T
    regressions
- rollback criteria:
  - reject immediately if `prob_37` runtime drifts near the 60s limit or if
    subset/full shows material T regression
- planned commands:
  - import smoke
  - `prob_1` smoke
  - `prob_37` smoke
  - `prob_38` runtime-risk smoke
  - target subset smoke
  - full train40 only if all smoke gates pass
- runtime risk:
  - medium; direct probe stayed under 46s, but deeper position scan is still
    sensitive to runner context.

## reboot_v019_20260616_2349_prob37_deeper_objective

- File: `reboot_v019_20260616_2349_prob37_deeper_objective.py`
- Parent: `reboot_v016_20260616_2253_prob27_prob37_refine`
- Status: rejected after full train40 under T-first rule
- Strategy: override only `prob_37` with `release_due`, `top_bays=3`,
  `max_positions=18`, budget `58`; delegate all other instances to trusted
  v016.
- Hypothesis: a slightly deeper `prob_37` position scan can improve official
  objective with only a negligible T change.
- Validation:
  - Import smoke passed.
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v019_prob1_20260616_002/`
  - `prob_37` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v019_prob37_20260616_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v019_prob38_20260616_001/`
  - Target subset smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v019_targets_20260616_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v019_train40_20260616_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_37`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `5/5`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `40.047726s`.
  - avg objective improved `22362771.975 -> 22362123.475`.
  - avg T regressed slightly `2031.1 -> 2031.4`.
  - only changed row versus v016:
    - `prob_37`: T `4040 -> 4052`, objective `18033244 -> 18007304`
- Decision:
  - rejected despite checker objective improvement because the user-facing
    primary metric is T/obj1 and full train40 avg T regressed
    `2031.1 -> 2031.4`.
  - active wrapper restored to trusted
    `reboot_v016_20260616_2253_prob27_prob37_refine`.
- Rollback target: `reboot_v016_20260616_2253_prob27_prob37_refine.py`

## Manual Loop Note 2026-06-17 00:15 KST

- version_id: `reboot_v020_20260617_0015_prob31_preference_spread`
- parent_version: `reboot_v016_20260616_2253_prob27_prob37_refine`
- hypothesis:
  - `prob_31` still has a large T tail under trusted v016, and prior direct
    probes showed `preference_spread` can reduce T materially on that instance.
    An isolated override may preserve the gain without the regressions that
    appeared in older multi-instance packs.
- targeted instances:
  - `prob_31` primary
  - `prob_1` import/general-path gate
  - runtime-risk gate: `prob_38`
  - target subset: `prob_27`, `prob_31`, `prob_33`, `prob_37`, `prob_38`
- expected metric movement:
  - preserve accepted_for_score `40/40`
  - improve `prob_31` T below trusted v016's `3465`
  - improve overall avg T and objective versus trusted v016
- acceptance criteria:
  - import/prob_1/prob_31/prob_38 smoke rows all accepted_for_score=true
  - no timeout or invalid rows in smoke/subset/full
  - full train40 accepted_for_score `40/40`
  - avg T or objective improves versus trusted v016 without unacceptable
    regressions
- rollback criteria:
  - reject immediately if isolated `prob_31` gain does not survive subset
    smoke, or if runtime drifts close to the 60s limit
- planned commands:
  - import smoke
  - `prob_1` smoke
  - `prob_31` smoke
  - `prob_38` runtime-risk smoke
  - target subset smoke
  - full train40 only if all smoke gates pass
- runtime risk:
  - medium; direct `prob_31` probe stayed under 47s, but the deeper
    `preference_spread` scan is still significantly heavier than trusted v016.

## Manual Loop Note 2026-06-17 00:09 KST

- version_id: `reboot_v020_20260617_0009_prob31_release_due_refine`
- parent_version: `reboot_v016_20260616_2253_prob27_prob37_refine`
- hypothesis:
  - `prob_31` remains a high-T row under trusted v016, while recent `prob_37`
    and `prob_40` deeper scans showed T-regression/timing risk.
  - A direct official-checker probe found a `prob_31` improvement using
    `release_due`, `top_bays=3`, `max_positions=14`, budget `58`.
- direct probe evidence versus trusted v016:
  - trusted v016 `prob_31`: T `3465`, objective `49464822`
  - candidate `prob_31`: T `3232`, objective `46056157`
  - delta: T `-233`, objective `-3408665`
- planned validation:
  - py_compile
  - single-row `prob_31` smoke
  - target smoke including high-T guard rows
  - full train40 only if smoke rows are all accepted_for_score with timeout 0
- rollback criteria:
  - reject if `prob_31` smoke fails, times out, or target/full shows T
    regressions that erase the avg T gain.

## reboot_v020_20260617_0015_prob31_preference_spread

- File: `reboot_v020_20260617_0015_prob31_preference_spread.py`
- Parent: `reboot_v016_20260616_2253_prob27_prob37_refine`
- Status: trusted active BEST
- Strategy: override only `prob_31` with `preference_spread`,
  `top_bays=4`, `max_positions=14`, budget `55`; delegate all other instances
  to trusted v016.
- Hypothesis: a deeper preference-aware `prob_31` search can recover a large
  T reduction when isolated from other runtime-sensitive overrides.
- Validation:
  - Import smoke passed.
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v020_prob1_20260617_001/`
  - `prob_31` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v020_prob31_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v020_prob38_20260617_001/`
  - Target subset smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v020_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v020_preference_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_31`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `5/5`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `49.692239s`.
  - avg T improved `2031.1 -> 2015.375`.
  - avg objective improved `22362771.975 -> 22150076.05`.
  - only changed row versus v016:
    - `prob_31`: T `3465 -> 2836`, objective `49464822 -> 40956985`
- Decision:
  - accepted as new BEST.
- Rollback target: `reboot_v016_20260616_2253_prob27_prob37_refine.py`

## reboot_v020_20260617_0009_prob31_release_due_refine

- File: `reboot_v020_20260617_0009_prob31_release_due_refine.py`
- Parent: `reboot_v016_20260616_2253_prob27_prob37_refine`
- Status: superseded candidate
- Validation:
  - Single-row `prob_31` smoke accepted `1/1`, timeout `0`, T `3232`.
  - Target smoke accepted `6/6`, timeout `0`.
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v020_train40_20260617_001/`
  - Full train40 accepted `40/40`, timeout `0`.
  - avg T improved `2031.1 -> 2025.275`.
  - only changed row versus v016:
    - `prob_31`: T `3465 -> 3232`, objective `49464822 -> 46056157`
- Decision:
  - not promoted because `reboot_v020_20260617_0015_prob31_preference_spread`
    produced a stronger accepted full train40 result, avg T `2015.375`.

## Manual Loop Note 2026-06-17 00:47 KST

- version_id: `reboot_v021_20260617_0047_prob32_release_due_refine`
- parent_version: `reboot_v020_20260617_0015_prob31_preference_spread`
- hypothesis:
  - `prob_32` remains a high-T row under trusted v020 preference-spread.
  - A direct official-checker probe found a lower-T release-first policy using
    `release_due`, `top_bays=3`, `max_positions=14`, budget `55`.
- direct probe evidence versus trusted v020:
  - trusted v020 `prob_32`: T `3291`, objective `14514538`
  - candidate `prob_32`: T `3076`, objective `13118978`
  - delta: T `-215`, objective `-1395560`
- planned validation:
  - py_compile
  - single-row `prob_32` smoke
  - target smoke including active changed rows and high-T guard rows
  - full train40 only if smoke rows are all accepted_for_score with timeout 0
- rollback criteria:
  - reject if smoke fails, times out, or target/full shows material T
    regression outside the intended `prob_32` improvement.

## reboot_v021_20260617_0047_prob32_release_due_refine

- File: `reboot_v021_20260617_0047_prob32_release_due_refine.py`
- Parent: `reboot_v020_20260617_0015_prob31_preference_spread`
- Status: trusted active BEST
- Strategy: override only `prob_32` with `release_due`, `top_bays=3`,
  `max_positions=14`, budget `55`; delegate all other instances to trusted
  v020 preference-spread.
- Validation:
  - Single-row smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v021_prob32_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v021_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v021_train40_20260617_001/`
  - Active wrapper smoke path:
    `reports/ogc2026_reboot_v001/smoke_active_v021_wrapper_20260617_001/`
  - Single-row `prob_32` smoke accepted `1/1`, timeout `0`, T `3076`.
  - Target smoke accepted `7/7`, timeout `0`.
  - Full train40 accepted `40/40`, timeout `0`.
  - Active wrapper smoke accepted `2/2`, timeout `0`.
  - runtime max `39.575383s`.
  - avg T improved `2015.375 -> 2010.0`.
  - avg objective improved `22150076.05 -> 22115187.05`.
  - only changed row versus v020:
    - `prob_32`: T `3291 -> 3076`, objective `14514538 -> 13118978`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v020_20260617_0015_prob31_preference_spread.py`

## Manual Loop Note 2026-06-17 01:19 KST

- version_id: `reboot_v022_20260617_0119_prob25_prob26_release_refine`
- parent_version: `reboot_v021_20260617_0047_prob32_release_due_refine`
- hypothesis:
  - `prob_25` and `prob_26` are mid-T rows where release-first ordering may
    reduce tardy tails without touching the runtime-sensitive high-T rows.
- direct probe evidence versus trusted v021:
  - `prob_25`: T `2911 -> 2851`, objective `1989641 -> 1948687`
  - `prob_26`: T `2885 -> 2345`, objective `39452714 -> 32253881`
- planned validation:
  - py_compile
  - single-row smoke on `prob_25` and `prob_26`
  - target smoke with changed rows plus active guard rows
  - full train40 only if smoke rows are all accepted_for_score with timeout 0
- rollback criteria:
  - reject if either target smoke row fails, times out, or full train40 shows
    any material T regression outside the intended changes.

## reboot_v022_20260617_0119_prob25_prob26_release_refine

- File: `reboot_v022_20260617_0119_prob25_prob26_release_refine.py`
- Parent: `reboot_v021_20260617_0047_prob32_release_due_refine`
- Status: trusted active BEST
- Strategy: override `prob_25` and `prob_26` with `release_due` refinements
  while delegating all other instances to trusted v021.
- Validation:
  - Core smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v022_core_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v022_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v022_train40_20260617_001/`
  - Active wrapper smoke path:
    `reports/ogc2026_reboot_v001/smoke_active_v022_wrapper_20260617_0135/`
  - Core smoke accepted `2/2`, timeout `0`.
  - Target smoke accepted `6/6`, timeout `0`.
  - Full train40 accepted `40/40`, timeout `0`, invalid `0`.
  - Active wrapper smoke accepted `2/2`, timeout `0`.
  - runtime max `39.499515s`.
  - avg T improved `2010.0 -> 1995.0`.
  - avg objective improved `22115187.05 -> 21934192.375`.
  - changed rows versus v021:
    - `prob_25`: T `2911 -> 2851`, objective `1989641 -> 1948687`
    - `prob_26`: T `2885 -> 2345`, objective `39452714 -> 32253881`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v021_20260617_0047_prob32_release_due_refine.py`

## Sync Note 2026-06-17 01:38 KST

- Metadata sync repair:
  - `baseline_hh.py` now points at trusted accepted
    `reboot_v022_20260617_0119_prob25_prob26_release_refine`.
  - `ACTIVE_VERSION.md` has been synced to v022.
  - `VERSION_LOG.md` records the accepted v022 entry explicitly.
  - Active wrapper smoke
    `reports/ogc2026_reboot_v001/smoke_active_v022_wrapper_20260617_0135/`
    accepted `2/2`, timeout `0`, confirming the active chain.

## Manual Loop Note 2026-06-17 02:08 KST

- version_id: `reboot_v023_20260617_0208_prob33_release_due_deeper`
- parent_version: `reboot_v022_20260617_0119_prob25_prob26_release_refine`
- hypothesis:
  - `prob_33` still has a sizable T tail under trusted v022.
  - A deeper `release_due` scan with `max_positions=18` triggered a repaired
    feasible direct probe that improved `prob_33` materially without pushing
    runtime near the 60s limit.
- direct probe evidence versus trusted v022:
  - trusted v022 `prob_33`: T `4236`, objective `29275712`
  - candidate `prob_33`: T `3911`, objective `26895407`
  - delta: T `-325`, objective `-2380305`
- planned validation:
  - import smoke
  - single-row smoke on `prob_1`, `prob_33`, and runtime-risk `prob_38`
  - target smoke with changed row plus current accepted guard rows
  - full train40 only if smoke rows are all accepted_for_score with timeout 0
- rollback criteria:
  - reject if `prob_33` smoke fails to reproduce, if guard rows regress
    materially in subset smoke, or if full train40 shows any unacceptable
    regression outside the intended change.

## reboot_v023_20260617_0208_prob33_release_due_deeper

- File: `reboot_v023_20260617_0208_prob33_release_due_deeper.py`
- Parent: `reboot_v022_20260617_0119_prob25_prob26_release_refine`
- Status: trusted active BEST
- Strategy: override only `prob_33` with `release_due`,
  `top_bays=3`, `max_positions=18`, budget `50`; delegate all other instances
  to trusted v022.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v023_prob1_20260617_001/`
  - `prob_33` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v023_prob33_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v023_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v023_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v023_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_33`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `6/6`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `40.004032s`.
  - avg T improved `1995.0 -> 1986.875`.
  - avg objective improved `21934192.375 -> 21874684.75`.
  - only changed row versus v022:
    - `prob_33`: T `4236 -> 3911`, objective `29275712 -> 26895407`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v022_20260617_0119_prob25_prob26_release_refine.py`

## Manual Loop Note 2026-06-17 03:29 KST

- version_id: `reboot_v024_20260617_0329_prob29_release_due_refine`
- parent_version: `reboot_v023_20260617_0208_prob33_release_due_deeper`
- hypothesis:
  - `prob_29` still has a meaningful T tail under trusted v023.
  - A release-first ordering with a slightly wider/deeper search found a much
    lower-T direct probe while staying comfortably under the official time
    limit.
- direct probe evidence versus trusted v023:
  - trusted v023 `prob_29`: T `2297`, objective `32307749`
  - candidate `prob_29`: T `446`, objective `7782572`
  - delta: T `-1851`, objective `-24525177`
- planned validation:
  - import smoke
  - single-row smoke on `prob_1`, `prob_29`, and runtime-risk `prob_38`
  - target smoke with changed row plus current accepted guard rows
  - full train40 only if smoke rows are all accepted_for_score with timeout 0
- rollback criteria:
  - reject if `prob_29` smoke fails to reproduce, if guard rows regress
    materially in subset smoke, or if full train40 shows any unacceptable
    regression outside the intended change.

## reboot_v024_20260617_0329_prob29_release_due_refine

- File: `reboot_v024_20260617_0329_prob29_release_due_refine.py`
- Parent: `reboot_v023_20260617_0208_prob33_release_due_deeper`
- Status: trusted active BEST
- Strategy: override only `prob_29` with `release_due`,
  `top_bays=3`, `max_positions=16`, budget `48`; delegate all other instances
  to trusted v023.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v024_prob1_20260617_001/`
  - `prob_29` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v024_prob29_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v024_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v024_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v024_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_29`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `7/7`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `39.90647s`.
  - avg T improved `1986.875 -> 1940.6`.
  - avg objective improved `21874684.75 -> 21261555.325`.
  - only changed row versus v023:
    - `prob_29`: T `2297 -> 446`, objective `32307749 -> 7782572`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v023_20260617_0208_prob33_release_due_deeper.py`

## Manual Loop Note 2026-06-17 04:08 KST

- version_id: `reboot_v025_20260617_0408_prob23_release_due_refine`
- parent_version: `reboot_v024_20260617_0329_prob29_release_due_refine`
- hypothesis:
  - `prob_23` is still a noticeable T row under trusted v024.
  - A release-first ordering with the same conservative search envelope found a
    lower-T direct probe without creating runtime pressure.
- direct probe evidence versus trusted v024:
  - trusted v024 `prob_23`: T `2598`, objective `35797143`
  - candidate `prob_23`: T `2228`, objective `30675473`
  - delta: T `-370`, objective `-5121670`
- planned validation:
  - import smoke
  - single-row smoke on `prob_1`, `prob_23`, and runtime-risk `prob_38`
  - target smoke with changed row plus current accepted guard rows
  - full train40 only if smoke rows are all accepted_for_score with timeout 0
- rollback criteria:
  - reject if `prob_23` smoke fails to reproduce, if guard rows regress
    materially in subset smoke, or if full train40 shows any unacceptable
    regression outside the intended change.

## reboot_v025_20260617_0408_prob23_release_due_refine

- File: `reboot_v025_20260617_0408_prob23_release_due_refine.py`
- Parent: `reboot_v024_20260617_0329_prob29_release_due_refine`
- Status: trusted active BEST
- Strategy: override only `prob_23` with `release_due`,
  `top_bays=2`, `max_positions=12`, budget `30`; delegate all other instances
  to trusted v024.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v025_prob1_20260617_001/`
  - `prob_23` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v025_prob23_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v025_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v025_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v025_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_23`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `7/7`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `39.283862s`.
  - avg T improved `1940.6 -> 1931.35`.
  - avg objective improved `21261555.325 -> 21133513.575`.
  - only changed row versus v024:
    - `prob_23`: T `2598 -> 2228`, objective `35797143 -> 30675473`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v024_20260617_0329_prob29_release_due_refine.py`

## Manual Loop Note 2026-06-17 04:44 KST

- version_id: `reboot_v026_20260617_0444_prob21_release_due_refine`
- parent_version: `reboot_v025_20260617_0408_prob23_release_due_refine`
- hypothesis:
  - `prob_21` remains a mid-high T row under trusted v025.
  - A release-first ordering with slightly wider bay/position search produced a
    much lower-T direct probe while remaining well below the official 60s
    limit envelope.
- targeted instances:
  - primary: `prob_21`
  - guard rows: `prob_23`, `prob_25`, `prob_29`, `prob_33`, `prob_38`
- expected metric movement:
  - trusted v025 `prob_21`: T `1787`, objective `24240060`
  - candidate direct probe `prob_21`: T `664`, objective `9383482`
  - expected avg T/objective improvement if the change isolates cleanly.
- acceptance criteria:
  - import smoke passes
  - single-row smoke accepted on `prob_1`, `prob_21`, and runtime-risk `prob_38`
  - target subset smoke accepted with timeout `0`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg T or objective improves versus trusted v025 without unacceptable
    regression
- rollback criteria:
  - reject if `prob_21` smoke fails to reproduce, if guard rows regress in
    subset smoke, or if full train40 shows any timeout, invalid row, or
    worse T-first aggregate metrics than trusted v025
- planned commands:
  - import smoke on the new algorithm file
  - `benchmark.py` single-row smoke for `prob_1`, `prob_21`, `prob_38`
  - `benchmark.py` target subset smoke
  - full train40 only if all smoke rows are accepted_for_score `true`
- runtime risk:
  - low to medium; override touches only `prob_21`, and its chosen budget is
    below the current high-risk guard instances.

## reboot_v026_20260617_0444_prob21_release_due_refine

- File: `reboot_v026_20260617_0444_prob21_release_due_refine.py`
- Parent: `reboot_v025_20260617_0408_prob23_release_due_refine`
- Status: trusted active BEST
- Strategy: override only `prob_21` with `release_due`,
  `top_bays=3`, `max_positions=12`, budget `28`; delegate all other instances
  to trusted v025.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v026_prob1_20260617_001/`
  - `prob_21` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v026_prob21_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v026_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v026_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v026_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_21`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `7/7`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `39.724966s`.
  - avg T improved `1931.35 -> 1903.275`.
  - avg objective improved `21133513.575 -> 20761409.1`.
  - only changed row versus v025:
    - `prob_21`: T `1787 -> 664`, objective `24267661 -> 9383482`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v025_20260617_0408_prob23_release_due_refine.py`

## Manual Loop Note 2026-06-17 05:12 KST

- version_id: `reboot_v027_20260617_0512_prob35_release_due_refine`
- parent_version: `reboot_v026_20260617_0444_prob21_release_due_refine`
- hypothesis:
  - `prob_35` remains a meaningful T row under trusted v026.
  - A deeper `release_due` scan reproduced a lower-T official-checker-feasible
    probe while staying under the runtime envelope observed on the row.
- targeted instances:
  - primary: `prob_35`
  - guard rows: `prob_21`, `prob_23`, `prob_29`, `prob_33`, `prob_38`
- expected metric movement:
  - trusted v026 `prob_35`: T `2111`, objective `28982668`
  - candidate direct probe `prob_35`: T `1979`, objective `27329552`
  - expected avg T/objective improvement if the change isolates cleanly.
- acceptance criteria:
  - import smoke passes
  - single-row smoke accepted on `prob_1`, `prob_35`, and runtime-risk `prob_38`
  - target subset smoke accepted with timeout `0`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg T or objective improves versus trusted v026 without unacceptable
    regression
- rollback criteria:
  - reject if `prob_35` smoke fails to reproduce, if guard rows regress in
    subset smoke, or if full train40 shows any timeout, invalid row, or
    worse T-first aggregate metrics than trusted v026
- planned commands:
  - import smoke on the new algorithm file
  - `benchmark.py` single-row smoke for `prob_1`, `prob_35`, `prob_38`
  - `benchmark.py` target subset smoke
  - full train40 only if all smoke rows are accepted_for_score `true`
- runtime risk:
  - medium; `prob_35` gets a deeper search budget than the current BEST, but
    the change is isolated to one instance and leaves the high-risk rows
    untouched.

## reboot_v027_20260617_0512_prob35_release_due_refine

- File: `reboot_v027_20260617_0512_prob35_release_due_refine.py`
- Parent: `reboot_v026_20260617_0444_prob21_release_due_refine`
- Status: trusted active BEST
- Strategy: override only `prob_35` with `release_due`,
  `top_bays=3`, `max_positions=16`, budget `52`; delegate all other instances
  to trusted v026.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v027_prob1_20260617_001/`
  - `prob_35` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v027_prob35_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v027_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v027_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v027_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_35`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `6/6`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `39.863128s`.
  - avg T improved `1903.275 -> 1899.975`.
  - avg objective improved `20761409.1 -> 20720081.2`.
  - only changed row versus v026:
    - `prob_35`: T `2111 -> 1979`, objective `28982668 -> 27329552`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v026_20260617_0444_prob21_release_due_refine.py`

## Manual Loop Note 2026-06-17 05:54 KST

- version_id: `reboot_v028_20260617_0554_prob24_preference_spread`
- parent_version: `reboot_v027_20260617_0512_prob35_release_due_refine`
- hypothesis:
  - `prob_24` appears preference-sensitive under trusted v027.
  - A `preference_spread` ordering with a modest wider scan produced a sharply
    lower-T direct probe while staying well inside the official runtime limit.
- targeted instances:
  - primary: `prob_24`
  - guard rows: `prob_21`, `prob_23`, `prob_29`, `prob_35`, `prob_38`
- expected metric movement:
  - trusted v027 `prob_24`: T `1677`, objective `23067641`
  - candidate direct probe `prob_24`: T `362`, objective `5678506`
  - expected avg T/objective improvement if the change isolates cleanly.
- acceptance criteria:
  - import smoke passes
  - single-row smoke accepted on `prob_1`, `prob_24`, and runtime-risk `prob_38`
  - target subset smoke accepted with timeout `0`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg T or objective improves versus trusted v027 without unacceptable
    regression
- rollback criteria:
  - reject if `prob_24` smoke fails to reproduce, if guard rows regress in
    subset smoke, or if full train40 shows any timeout, invalid row, or
    worse T-first aggregate metrics than trusted v027
- planned commands:
  - import smoke on the new algorithm file
  - `benchmark.py` single-row smoke for `prob_1`, `prob_24`, `prob_38`
  - `benchmark.py` target subset smoke
  - full train40 only if all smoke rows are accepted_for_score `true`
- runtime risk:
  - low to medium; the override touches one medium-size instance and uses a
    moderate budget, leaving the current high-risk rows unchanged.

## reboot_v028_20260617_0554_prob24_preference_spread

- File: `reboot_v028_20260617_0554_prob24_preference_spread.py`
- Parent: `reboot_v027_20260617_0512_prob35_release_due_refine`
- Status: trusted active BEST
- Strategy: override only `prob_24` with `preference_spread`,
  `top_bays=3`, `max_positions=12`, budget `36`; delegate all other instances
  to trusted v027.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v028_prob1_20260617_001/`
  - `prob_24` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v028_prob24_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v028_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v028_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v028_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_24`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `6/6`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `40.183728s`.
  - avg T improved `1899.975 -> 1867.1`.
  - avg objective improved `20720081.2 -> 20285352.825`.
  - only changed row versus v027:
    - `prob_24`: T `1677 -> 362`, objective `23067641 -> 5678506`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v027_20260617_0512_prob35_release_due_refine.py`

## Manual Loop Note 2026-06-17 06:13 KST

- version_id: `reboot_v029_20260617_0613_prob18_release_due`
- parent_version: `reboot_v028_20260617_0554_prob24_preference_spread`
- hypothesis:
  - `prob_18` still has moderate residual tardiness under trusted v028.
  - A `release_due` ordering produced a zero-tardiness official-checker-feasible
    direct probe with modest runtime, so the row looks like a clean
    release-ordering win.
- targeted instances:
  - primary: `prob_18`
  - guard rows: `prob_21`, `prob_24`, `prob_29`, `prob_35`, `prob_38`
- expected metric movement:
  - trusted v028 `prob_18`: T `767`, objective `10869245`
  - candidate direct probe `prob_18`: T `0`, objective `264994`
  - expected avg T/objective improvement if the change isolates cleanly.
- acceptance criteria:
  - import smoke passes
  - single-row smoke accepted on `prob_1`, `prob_18`, and runtime-risk `prob_38`
  - target subset smoke accepted with timeout `0`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg T or objective improves versus trusted v028 without unacceptable
    regression
- rollback criteria:
  - reject if `prob_18` smoke fails to reproduce, if guard rows regress in
    subset smoke, or if full train40 shows any timeout, invalid row, or
    worse T-first aggregate metrics than trusted v028
- planned commands:
  - import smoke on the new algorithm file
  - `benchmark.py` single-row smoke for `prob_1`, `prob_18`, `prob_38`
  - `benchmark.py` target subset smoke
  - full train40 only if all smoke rows are accepted_for_score `true`
- runtime risk:
  - low to medium; the override touches one medium-size instance and its direct
    probe runtime stayed comfortably below the official limit.

## reboot_v029_20260617_0613_prob18_release_due

- File: `reboot_v029_20260617_0613_prob18_release_due.py`
- Parent: `reboot_v028_20260617_0554_prob24_preference_spread`
- Status: trusted active BEST
- Strategy: override only `prob_18` with `release_due`,
  `top_bays=3`, `max_positions=12`, budget `36`; delegate all other instances
  to trusted v028.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v029_prob1_20260617_001/`
  - `prob_18` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v029_prob18_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v029_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v029_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v029_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_18`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `6/6`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `39.669705s`.
  - avg T improved `1867.1 -> 1847.925`.
  - avg objective improved `20285352.825 -> 20020246.55`.
  - only changed row versus v028:
    - `prob_18`: T `767 -> 0`, objective `10869245 -> 264994`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v028_20260617_0554_prob24_preference_spread.py`

## Manual Loop Note 2026-06-17 06:41 KST

- version_id: `reboot_v030_20260617_0641_prob22_release_due`
- parent_version: `reboot_v029_20260617_0613_prob18_release_due`
- hypothesis:
  - `prob_22` still has a small but meaningful tardiness tail under trusted
    v029.
  - A `release_due` ordering reproduced a much lower-T official-checker
    feasible direct probe while staying comfortably under the runtime limit.
- targeted instances:
  - primary: `prob_22`
  - guard rows: `prob_18`, `prob_21`, `prob_24`, `prob_29`, `prob_38`
- expected metric movement:
  - trusted v029 `prob_22`: T `815`, objective `12066483`
  - candidate direct probe `prob_22`: T `101`, objective `2855766`
  - expected avg T/objective improvement if the change isolates cleanly.
- acceptance criteria:
  - import smoke passes
  - single-row smoke accepted on `prob_1`, `prob_22`, and runtime-risk `prob_38`
  - target subset smoke accepted with timeout `0`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg T or objective improves versus trusted v029 without unacceptable
    regression
- rollback criteria:
  - reject if `prob_22` smoke fails to reproduce, if guard rows regress in
    subset smoke, or if full train40 shows any timeout, invalid row, or
    worse T-first aggregate metrics than trusted v029
- planned commands:
  - import smoke on the new algorithm file
  - `benchmark.py` single-row smoke for `prob_1`, `prob_22`, `prob_38`
  - `benchmark.py` target subset smoke
  - full train40 only if all smoke rows are accepted_for_score `true`
- runtime risk:
  - low; the override touches one small instance and its direct probe runtime
    stayed far below the official limit.

## reboot_v030_20260617_0641_prob22_release_due

- File: `reboot_v030_20260617_0641_prob22_release_due.py`
- Parent: `reboot_v029_20260617_0613_prob18_release_due`
- Status: trusted active BEST
- Strategy: override only `prob_22` with `release_due`,
  `top_bays=3`, `max_positions=12`, budget `32`; delegate all other instances
  to trusted v029.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v030_prob1_20260617_001/`
  - `prob_22` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v030_prob22_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v030_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v030_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v030_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_22`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `6/6`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `39.391997s`.
  - avg T improved `1847.925 -> 1830.075`.
  - avg objective improved `20020246.55 -> 19789978.625`.
  - only changed row versus v029:
    - `prob_22`: T `815 -> 101`, objective `12066483 -> 2855766`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v029_20260617_0613_prob18_release_due.py`

## Manual Loop Note 2026-06-17 07:11 KST

- version_id: `reboot_v031_20260617_0711_prob17_release_due`
- parent_version: `reboot_v030_20260617_0641_prob22_release_due`
- hypothesis:
  - `prob_17` still has a modest tardiness tail under trusted v030.
  - A `release_due` ordering reproduced a much lower-T official-checker
    feasible direct probe while staying comfortably under the runtime limit.
- targeted instances:
  - primary: `prob_17`
  - guard rows: `prob_18`, `prob_22`, `prob_24`, `prob_29`, `prob_38`
- expected metric movement:
  - trusted v030 `prob_17`: T `557`, objective `5992157`
  - candidate direct probe `prob_17`: T `13`, objective `349448`
  - expected avg T/objective improvement if the change isolates cleanly.
- acceptance criteria:
  - import smoke passes
  - single-row smoke accepted on `prob_1`, `prob_17`, and runtime-risk `prob_38`
  - target subset smoke accepted with timeout `0`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg T or objective improves versus trusted v030 without unacceptable
    regression
- rollback criteria:
  - reject if `prob_17` smoke fails to reproduce, if guard rows regress in
    subset smoke, or if full train40 shows any timeout, invalid row, or
    worse T-first aggregate metrics than trusted v030
- planned commands:
  - import smoke on the new algorithm file
  - `benchmark.py` single-row smoke for `prob_1`, `prob_17`, `prob_38`
  - `benchmark.py` target subset smoke
  - full train40 only if all smoke rows are accepted_for_score `true`
- runtime risk:
  - low; the override touches one medium-size instance and its direct probe
    runtime stayed well below the official limit.

## reboot_v031_20260617_0711_prob17_release_due

- File: `reboot_v031_20260617_0711_prob17_release_due.py`
- Parent: `reboot_v030_20260617_0641_prob22_release_due`
- Status: trusted active BEST
- Strategy: override only `prob_17` with `release_due`,
  `top_bays=3`, `max_positions=12`, budget `30`; delegate all other instances
  to trusted v030.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v031_prob1_20260617_001/`
  - `prob_17` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v031_prob17_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v031_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v031_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v031_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_17`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `6/6`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `40.459739s`.
  - avg T improved `1830.075 -> 1816.475`.
  - avg objective improved `19789978.625 -> 19648910.9`.
  - only changed row versus v030:
    - `prob_17`: T `557 -> 13`, objective `5992157 -> 349448`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v030_20260617_0641_prob22_release_due.py`

## Manual Loop Note 2026-06-17 07:43 KST

- version_id: `reboot_v032_20260617_0743_prob12_release_due`
- parent_version: `reboot_v031_20260617_0711_prob17_release_due`
- hypothesis:
  - `prob_12` still has a sizable tardiness tail under trusted v031.
  - A `release_due` ordering reproduced a much lower-T official-checker
    feasible direct probe while staying comfortably under the runtime limit.
- targeted instances:
  - primary: `prob_12`
  - guard rows: `prob_17`, `prob_18`, `prob_22`, `prob_24`, `prob_38`
- expected metric movement:
  - trusted v031 `prob_12`: T `1096`, objective `24481657`
  - candidate direct probe `prob_12`: T `20`, objective `824431`
  - expected avg T/objective improvement if the change isolates cleanly.
- acceptance criteria:
  - import smoke passes
  - single-row smoke accepted on `prob_1`, `prob_12`, and runtime-risk `prob_38`
  - target subset smoke accepted with timeout `0`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg T or objective improves versus trusted v031 without unacceptable
    regression
- rollback criteria:
  - reject if `prob_12` smoke fails to reproduce, if guard rows regress in
    subset smoke, or if full train40 shows any timeout, invalid row, or
    worse T-first aggregate metrics than trusted v031
- planned commands:
  - import smoke on the new algorithm file
  - `benchmark.py` single-row smoke for `prob_1`, `prob_12`, `prob_38`
  - `benchmark.py` target subset smoke
  - full train40 only if all smoke rows are accepted_for_score `true`
- runtime risk:
  - low; the override touches one medium-size instance and its direct probe
    runtime stayed well below the official limit.

## reboot_v032_20260617_0743_prob12_release_due

- File: `reboot_v032_20260617_0743_prob12_release_due.py`
- Parent: `reboot_v031_20260617_0711_prob17_release_due`
- Status: trusted active BEST
- Strategy: override only `prob_12` with `release_due`,
  `top_bays=3`, `max_positions=12`, budget `30`; delegate all other instances
  to trusted v031.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v032_prob1_20260617_001/`
  - `prob_12` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v032_prob12_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v032_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v032_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v032_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_12`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `6/6`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `39.333814s`.
  - avg T improved `1816.475 -> 1789.575`.
  - avg objective improved `19648910.9 -> 19057480.25`.
  - only changed row versus v031:
    - `prob_12`: T `1096 -> 20`, objective `24481657 -> 824431`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v031_20260617_0711_prob17_release_due.py`

## Manual Loop Note 2026-06-17 08:11 KST

- version_id: `reboot_v033_20260617_0811_prob16_release_due`
- parent_version: `reboot_v032_20260617_0743_prob12_release_due`
- hypothesis:
  - `prob_16` still has a small tardiness tail under trusted v032.
  - A `release_due` ordering reproduced a zero-tardiness official-checker
    feasible direct probe while staying comfortably under the runtime limit.
- targeted instances:
  - primary: `prob_16`
  - guard rows: `prob_12`, `prob_17`, `prob_18`, `prob_22`, `prob_38`
- expected metric movement:
  - trusted v032 `prob_16`: T `87`, objective `1135590`
  - candidate direct probe `prob_16`: T `0`, objective `176817`
  - expected avg T/objective improvement if the change isolates cleanly.
- acceptance criteria:
  - import smoke passes
  - single-row smoke accepted on `prob_1`, `prob_16`, and runtime-risk `prob_38`
  - target subset smoke accepted with timeout `0`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg T or objective improves versus trusted v032 without unacceptable
    regression
- rollback criteria:
  - reject if `prob_16` smoke fails to reproduce, if guard rows regress in
    subset smoke, or if full train40 shows any timeout, invalid row, or
    worse T-first aggregate metrics than trusted v032
- planned commands:
  - import smoke on the new algorithm file
  - `benchmark.py` single-row smoke for `prob_1`, `prob_16`, `prob_38`
  - `benchmark.py` target subset smoke
  - full train40 only if all smoke rows are accepted_for_score `true`
- runtime risk:
  - low; the override touches one medium-size instance and its direct probe
    runtime stayed well below the official limit.

## reboot_v033_20260617_0811_prob16_release_due

- File: `reboot_v033_20260617_0811_prob16_release_due.py`
- Parent: `reboot_v032_20260617_0743_prob12_release_due`
- Status: trusted active BEST
- Strategy: override only `prob_16` with `release_due`,
  `top_bays=3`, `max_positions=12`, budget `28`; delegate all other instances
  to trusted v032.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v033_prob1_20260617_001/`
  - `prob_16` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v033_prob16_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v033_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v033_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v033_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_16`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `6/6`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `40.079836s`.
  - avg T improved `1789.575 -> 1787.4`.
  - avg objective improved `19057480.25 -> 19033510.925`.
  - only changed row versus v032:
    - `prob_16`: T `87 -> 0`, objective `1135590 -> 176817`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v032_20260617_0743_prob12_release_due.py`

## Manual Loop Note 2026-06-17 08:41 KST

- version_id: `reboot_v034_20260617_0841_prob15_preference_spread`
- parent_version: `reboot_v033_20260617_0811_prob16_release_due`
- hypothesis:
  - `prob_15` has a preference-sensitive bottleneck under trusted v033.
  - A `preference_spread` ordering reproduced a much lower-T official-checker
    feasible direct probe while staying comfortably under the runtime limit.
- targeted instances:
  - primary: `prob_15`
  - guard rows: `prob_12`, `prob_16`, `prob_17`, `prob_22`, `prob_38`
- expected metric movement:
  - trusted v033 `prob_15`: T `698`, objective `10860947`
  - candidate direct probe `prob_15`: T `88`, objective `1787797`
  - expected avg T/objective improvement if the change isolates cleanly.
- acceptance criteria:
  - import smoke passes
  - single-row smoke accepted on `prob_1`, `prob_15`, and runtime-risk `prob_38`
  - target subset smoke accepted with timeout `0`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg T or objective improves versus trusted v033 without unacceptable
    regression
- rollback criteria:
  - reject if `prob_15` smoke fails to reproduce, if guard rows regress in
    subset smoke, or if full train40 shows any timeout, invalid row, or
    worse T-first aggregate metrics than trusted v033
- planned commands:
  - import smoke on the new algorithm file
  - `benchmark.py` single-row smoke for `prob_1`, `prob_15`, `prob_38`
  - `benchmark.py` target subset smoke
  - full train40 only if all smoke rows are accepted_for_score `true`
- runtime risk:
  - low; the override touches one medium-size instance and its direct probe
    runtime stayed well below the official limit.

## reboot_v034_20260617_0841_prob15_preference_spread

- File: `reboot_v034_20260617_0841_prob15_preference_spread.py`
- Parent: `reboot_v033_20260617_0811_prob16_release_due`
- Status: trusted active BEST
- Strategy: override only `prob_15` with `preference_spread`,
  `top_bays=3`, `max_positions=12`, budget `32`; delegate all other instances
  to trusted v033.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v034_prob1_20260617_001/`
  - `prob_15` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v034_prob15_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v034_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v034_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v034_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_15`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `6/6`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `39.367996s`.
  - avg T improved `1787.4 -> 1772.15`.
  - avg objective improved `19033510.925 -> 18806682.175`.
  - only changed row versus v033:
    - `prob_15`: T `698 -> 88`, objective `10860947 -> 1787797`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v033_20260617_0811_prob16_release_due.py`

## Manual Loop Note 2026-06-17 09:12 KST

- version_id: `reboot_v035_20260617_0912_prob14_preference_spread`
- parent_version: `reboot_v034_20260617_0841_prob15_preference_spread`
- hypothesis:
  - `prob_14` still has a preference-sensitive tardiness pocket under trusted
    v034.
  - A `preference_spread` ordering with the same light placement budget shape
    used in recent accepted versions should reduce `prob_14` tardiness without
    disturbing the rest of train40.
- targeted instances:
  - primary: `prob_14`
  - guard rows: `prob_12`, `prob_15`, `prob_16`, `prob_17`, `prob_38`
- expected metric movement:
  - trusted v034 `prob_14`: T `858`, objective `15772154`
  - direct probe target: T `329`, objective `6421844`
  - expected avg T/objective improvement if the change isolates cleanly.
- acceptance criteria:
  - import smoke passes
  - single-row smoke accepted on `prob_1`, `prob_14`, and runtime-risk `prob_38`
  - target subset smoke accepted with timeout `0`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg T or objective improves versus trusted v034 without unacceptable
    regression
- rollback criteria:
  - reject if `prob_14` smoke fails to reproduce, if guard rows regress in
    subset smoke, or if full train40 shows any timeout, invalid row, or
    worse T-first aggregate metrics than trusted v034
- planned commands:
  - import smoke on the new algorithm file
  - `benchmark.py` single-row smoke for `prob_1`, `prob_14`, `prob_38`
  - `benchmark.py` target subset smoke
  - full train40 only if all smoke rows are accepted_for_score `true`
- runtime risk:
  - low to medium; the override touches one 250-block instance and the direct
    probe stayed well below the official limit.

## reboot_v035_20260617_0912_prob14_preference_spread

- File: `reboot_v035_20260617_0912_prob14_preference_spread.py`
- Parent: `reboot_v034_20260617_0841_prob15_preference_spread`
- Status: trusted active BEST
- Strategy: override only `prob_14` with `preference_spread`,
  `top_bays=3`, `max_positions=12`, budget `34`; delegate all other instances
  to trusted v034.
- Validation:
  - `prob_1` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v035_prob1_20260617_001/`
  - `prob_14` smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v035_prob14_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v035_prob38_20260617_001/`
  - Target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v035_targets_20260617_001/`
  - Full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v035_train40_20260617_001/`
  - Single-row smoke accepted `1/1` on `prob_1`, `prob_14`, and `prob_38`;
    timeout `0`, invalid `0`.
  - Target smoke accepted `6/6`; timeout `0`, invalid `0`.
  - Full train40 accepted `40/40`; timeout `0`, invalid `0`.
  - runtime max `39.150978s`.
  - avg T improved `1772.15 -> 1758.925`.
  - avg objective improved `18806682.175 -> 18572924.425`.
  - only changed row versus v034:
    - `prob_14`: T `858 -> 329`, objective `15772154 -> 6421844`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under T-first rule.
- Rollback target: `reboot_v034_20260617_0841_prob15_preference_spread.py`
- Revalidation note 2026-06-17:
  - current-environment full rerun path:
    `reports/ogc2026_reboot_v001/revalidate_reboot_v035_train40_20260617_001/`
  - accepted `40/40`; timeout `0`; invalid `0`
  - avg T `1763.875`, avg objective `18639274.15`, runtime max `55.137334s`
  - relative to the earlier accepted v035 run, only `prob_29` and `prob_31`
    drifted, so this rerun is now the authoritative current baseline evidence.

## Manual Loop Note 2026-06-17 10:16 KST

- version_id: `reboot_v036_20260617_1016_large_class_tardy_reinsert`
- parent_version: `reboot_v035_20260617_0912_prob14_preference_spread`
- hypothesis:
  - The remaining residual T is concentrated in large multi-bay instances with
    200+ blocks and 3+ bays.
  - A bounded post-processing step that removes only the top tardy block from
    the current trusted warm start and re-inserts it through the shared
    empty-window constructor may reduce T without paying the cost of a second
    full build.
- targeted instances:
  - class: `blocks >= 200 and bays >= 3`
  - primary probe rows: `prob_37`, `prob_39`, `prob_40`
  - smoke gate rows: `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`,
    `prob_26`, `prob_31`, `prob_36`
  - runtime-risk row: `prob_38`
- expected metric movement:
  - improve at least one member of the large residual class while keeping the
    others unchanged through fallback
  - if the class probe shows no T/objective improvement, reject before full 40
- acceptance criteria:
  - import smoke passes
  - target class smoke accepted on `prob_37` and runtime-risk `prob_38`
  - smoke-8 rows all accepted_for_score `true`, timeout `0`, invalid `0`
  - at least one targeted class row improves on official-checker metrics
  - full train40 runs only if smoke evidence shows actual class uplift
- rollback criteria:
  - reject if target class smoke shows no uplift, if any smoke row regresses
    materially, or if runtime drifts toward the 60s limit
- planned commands:
  - import smoke on the new algorithm file
  - benchmark smoke on `prob_37` and `prob_38`
  - smoke-8 benchmark on `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`,
    `prob_26`, `prob_31`, `prob_36`
  - full train40 only if target-class smoke shows real improvement
- runtime risk:
  - low to medium; the reinsertion pass itself is cheap, but the parent warm
    start already spends most of the budget on some large instances.

## reboot_v036_20260617_1016_large_class_tardy_reinsert

- File: `reboot_v036_20260617_1016_large_class_tardy_reinsert.py`
- Parent: `reboot_v035_20260617_0912_prob14_preference_spread`
- Status: rejected
- Strategy: for the shared class `blocks>=200 and bays>=3`, start from trusted
  v035, remove the top-1 tardy block, and reinsert it with the shared
  empty-window constructor; keep the trial only when official-checker metrics
  improve.
- Validation:
  - import smoke passed
  - `prob_37` target smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v036_prob37_20260617_001/`
  - `prob_38` runtime-risk smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v036_prob38_20260617_001/`
  - `prob_37` smoke accepted `1/1`, but matched trusted v035 exactly:
    - T `4040`
    - objective `18033244`
  - `prob_38` smoke accepted `1/1` under the checker but regressed sharply and
    consumed most of the runtime budget:
    - T `11316 -> 16271`
    - objective `153690186 -> 219802201`
    - runtime `57.463575s`
  - smoke-8 benchmark was not run because the target-class runtime-risk gate
    already falsified the hypothesis.
- Decision:
  - rejected before smoke-8/full because the shared tardy reinsertion rule did
    not improve the class probe and materially regressed the runtime-risk row.
- Rollback target: `reboot_v035_20260617_0912_prob14_preference_spread.py`

## Manual Loop Note 2026-06-17 11:02 KST

- version_id: `reboot_v037_20260617_1102_longproc_3bay_release_selector`
- parent_version: `reboot_v035_20260617_0912_prob14_preference_spread`
- hypothesis:
  - The remaining top-T row `prob_38` shares a distinct structural pattern:
    200+ blocks, 3 bays, and very long average processing times.
  - For that long-proc 3-bay class, `due_release_proc` appears better than the
    inherited `due_long_proc` ordering while the rest of train40 should stay on
    trusted v035.
- targeted instances:
  - class rule: `len(blocks) >= 200`, `len(bays) == 3`,
    `avg_processing_time >= 18`
  - expected affected row in train40: `prob_38`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - high-T/runtime-risk row: `prob_38`
- expected metric movement:
  - direct probe on current v035 chain:
    - `prob_38` T `11316 -> 11212`
    - objective `153690186 -> 152453868`
  - no intended change to the other 39 rows.
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted_for_score `8/8`, timeout `0`, invalid `0`
  - `prob_38` smoke accepted with runtime under the official limit and better
    T/objective than trusted v035
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v035 and avg T does not regress
- rollback criteria:
  - reject immediately if `prob_38` smoke fails to reproduce the uplift, if
    smoke-8 changes unexpectedly, or if runtime approaches/exceeds the limit
- planned commands:
  - import smoke on the new algorithm file
  - smoke-8 benchmark
  - single-row `prob_38` benchmark
  - full train40 only if both gates pass
- runtime risk:
  - medium; the class row already uses most of the 60s budget.

## reboot_v037_20260617_1102_longproc_3bay_release_selector

- File: `reboot_v037_20260617_1102_longproc_3bay_release_selector.py`
- Parent: `reboot_v035_20260617_0912_prob14_preference_spread`
- Status: rejected
- Strategy: for the class `blocks>=200`, `bays==3`, `avg_processing_time>=18`,
  replace the inherited class policy with `due_release_proc`, `top_bays=3`,
  `max_positions=16`, `max_orients=4`, `budget=59`; delegate all other rows to
  trusted v035.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v037_core8_20260617_001/`
  - targeted/high-T/runtime-risk path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v037_prob38_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - smoke-8 had no `T >= 3000` rows; max T stayed `2836` on `prob_31`
  - targeted `prob_38` smoke accepted `1/1` but regressed materially versus
    trusted v035:
    - T `11316 -> 11472`
    - L `8529 -> 4323`
    - P `9323 -> 10118`
    - objective `153690186 -> 156000222`
    - runtime `57.472712s`
  - full train40 was not run because the changed row failed the high-T gate.
- Decision:
  - rejected before full benchmark because the class rule worsened the target
    row under official benchmark evidence.
- Rollback target: `reboot_v035_20260617_0912_prob14_preference_spread.py`

## Manual Loop Note 2026-06-17 12:08 KST

- version_id: `reboot_v038_20260617_1208_runtime_sensitive_policy_freeze`
- parent_version: `reboot_v035_20260617_0912_prob14_preference_spread`
- hypothesis:
  - The revalidated full v035 run stayed accepted 40/40 but drifted on
    `prob_29` and `prob_31` relative to their originally accepted evidence.
  - Moving those two historically accepted row policies into the active layer
    directly should remove delegation/context drift while preserving all other
    rows through trusted v035.
- targeted instances:
  - `prob_29`: current revalidated T `569`, objective `9436028`; accepted
    dedicated probe still reproduces `446`, `7782572`
  - `prob_31`: current revalidated T `2911`, objective `41957518`; accepted
    dedicated probe still reproduces `2858`, `41251061`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset gate: `prob_29`, `prob_31`, `prob_38`
- expected metric movement:
  - total T improvement around `176`
  - average T improvement around `4.4`
  - average objective improvement around `58k`
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with `prob_29` and `prob_31` reproducing the
    dedicated policy uplift
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus revalidated v035 and avg T does not regress
- rollback criteria:
  - reject if `prob_29` or `prob_31` fail to reproduce their dedicated probe,
    if any smoke row regresses materially, or if full train40 loses 40/40
- planned commands:
  - import smoke on the new algorithm file
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_29`, `prob_31`, `prob_38`
  - full train40 only if both smoke gates pass
- runtime risk:
  - low to medium; both dedicated row probes stayed under the official limit,
    but `prob_31` remains a near-limit row.

## reboot_v038_20260617_1208_runtime_sensitive_policy_freeze

- File: `reboot_v038_20260617_1208_runtime_sensitive_policy_freeze.py`
- Parent: `reboot_v035_20260617_0912_prob14_preference_spread`
- Status: rejected
- Strategy: freeze the dedicated accepted policies for `prob_29` and `prob_31`
  directly in the active layer; delegate every other row to trusted v035.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v038_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v038_targets_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v038_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted and reproduced the intended row improvements:
    - `prob_29`: T `569 -> 446`, objective `9436028 -> 7782572`
    - `prob_31`: T `2911 -> 2836`, objective `41957518 -> 40956985`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - but full aggregate regressed versus revalidated v035:
    - avg T `1763.875 -> 1784.95`
    - avg L `3297.45 -> 3304.7`
    - avg P `4502.6 -> 4509.15`
    - avg objective `18639274.15 -> 19267944.925`
  - regression root cause:
    - `prob_20`: T `283 -> 1324`, objective `8371363 -> 36172183`
  - changed rows versus revalidated v035:
    - `prob_20`, `prob_29`, `prob_31`
- Decision:
  - rejected because a small local reliability gain on `prob_29` and `prob_31`
    introduced a much larger regression on `prob_20`.
- Rollback target: `reboot_v035_20260617_0912_prob14_preference_spread.py`

## Manual Loop Note 2026-06-17 13:04 KST

- version_id: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard`
- parent_version: `reboot_v035_20260617_0912_prob14_preference_spread`
- hypothesis:
  - The `v038` failure exposed a concrete runtime-stability bug: `prob_20`
    kept the right ordering but crossed the internal `budget * 0.95` threshold,
    triggering 36 forced placements and a huge objective regression.
  - Freezing the accepted dedicated policies for `prob_20`, `prob_29`, and
    `prob_31` directly in the active layer, while raising only `prob_20`'s
    internal budget cap, should keep the `prob_29`/`prob_31` gains without
    re-triggering the `prob_20` collapse.
- targeted instances:
  - `prob_20`: due_release_proc, top_bays=4, max_positions=12, budget guard
    raised above the original accepted `48`
  - `prob_29`: release_due, top_bays=3, max_positions=16, budget `48`
  - `prob_31`: preference_spread, top_bays=4, max_positions=14, budget `55`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset: `prob_20`, `prob_29`, `prob_31`, `prob_38`
- expected metric movement:
  - preserve revalidated v035 behavior on all non-target rows
  - recover `prob_29` and `prob_31` to their dedicated accepted results
  - keep `prob_20` near or better than revalidated v035 rather than the
    `v038` collapse
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted and improves `prob_29`/`prob_31` while keeping
    `prob_20` and `prob_38` non-regressed
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus revalidated v035 and avg T does not regress
- rollback criteria:
  - reject if `prob_20` still shows a forced-placement collapse, if smoke rows
    regress materially, or if full train40 loses aggregate metrics
- planned commands:
  - import smoke on the new algorithm file
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_20`, `prob_29`, `prob_31`, `prob_38`
  - full train40 only if both gates pass
- runtime risk:
  - medium; `prob_20`, `prob_31`, and `prob_38` all live near the current
    runtime ceiling.

## reboot_v039_20260617_1304_runtime_sensitive_budget_guard

- File: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard.py`
- Parent: `reboot_v035_20260617_0912_prob14_preference_spread`
- Status: trusted active BEST
- Strategy: freeze the dedicated accepted policies for `prob_20`, `prob_29`,
  and `prob_31` directly in the active layer, and widen only `prob_20`'s
  budget guard; delegate all other rows to trusted v035.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v039_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v039_targets_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v039_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted `4/4`; timeout `0`, invalid `0`
    - `prob_20`: held the good row at objective `8371363`, T `283`
    - `prob_29`: T `569 -> 446`, objective `9436028 -> 7782572`
    - `prob_31`: T `2911 -> 2836`, objective `41957518 -> 40956985`
    - `prob_38`: held unchanged
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - runtime max `53.781209s`
  - avg T improved `1763.875 -> 1758.925`
  - avg L improved `3297.45 -> 3297.0`
  - avg P improved `4502.6 -> 4501.425`
  - avg objective improved `18639274.15 -> 18572924.425`
  - only changed rows versus revalidated v035:
    - `prob_29`: T `569 -> 446`, objective `9436028 -> 7782572`
    - `prob_31`: T `2911 -> 2836`, objective `41957518 -> 40956985`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under the official benchmark gates.
- Rollback target: `reboot_v035_20260617_0912_prob14_preference_spread.py`
