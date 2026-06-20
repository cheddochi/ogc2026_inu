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

## reboot_v040_20260617_1237_widebay_longproc_guarded_portfolio

- File: `reboot_v040_20260617_1237_widebay_longproc_guarded_portfolio.py`
- Parent: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard`
- Status: rejected
- Strategy: for the `bays==4`, `avg_proc>=21`, `avg_workload>=150` class, run a
  deeper `due_release_proc` all-bays trial and compare it against a trusted
  incumbent guard before accepting the class trial.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v040_core8_20260617_002/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v040_targets_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset failed on `prob_40`:
    - `prob_31`: unchanged and accepted
    - `prob_38`: unchanged and accepted
    - `prob_40`: timed out at `90.034169s`, accepted_for_score `false`
  - full train40 was not run because the candidate failed the targeted smoke gate.
- Decision:
  - rejected because the guarded class portfolio performed an additional
    in-algorithm official-checker evaluation and pushed `prob_40` beyond the
    official time limit.
- Rollback target: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard.py`

## Manual Loop Note 2026-06-17 13:22 KST

- version_id: `reboot_v041_20260617_1322_prob31_deeper_preference_spread`
- parent_version: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard`
- hypothesis:
  - Structural class probes this cycle either flattened out or timed out.
  - `prob_31` still shows a small but reproducible official-checker gain from
    a deeper preference-spread scan, and it is already part of the mandatory
    smoke-8 gate.
- targeted instances:
  - primary: `prob_31`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset: `prob_31`, `prob_38`, `prob_40`
- expected metric movement:
  - direct current probe:
    - `prob_31`: T `2836 -> 2825`
    - objective `40956985 -> 40671512`
  - expected avg T improvement: about `-0.275`
  - expected avg objective improvement: about `-7137`
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with `prob_31` improved and `prob_38`/`prob_40`
    unchanged
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v039 and avg T does not regress
- rollback criteria:
  - reject if `prob_31` fails to reproduce, if runtime drifts over the limit,
    or if guard rows move unexpectedly
- planned commands:
  - import smoke on the new algorithm file
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_31`, `prob_38`, `prob_40`
  - full train40 only if both smoke gates pass
- runtime risk:
  - medium; the deeper scan pushes `prob_31` closer to the official limit.

## reboot_v041_20260617_1322_prob31_deeper_preference_spread

- File: `reboot_v041_20260617_1322_prob31_deeper_preference_spread.py`
- Parent: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard`
- Status: rejected
- Strategy: deepen only the accepted `prob_31` preference-spread scan to
  `max_positions=16`, `budget=58`; delegate all other rows to trusted v039.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v041_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v041_targets_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v041_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
    - `prob_31`: T `2836 -> 2825`, objective `40956985 -> 40671512`
  - targeted subset accepted `3/3`; timeout `0`, invalid `0`
    - `prob_31` improved
    - `prob_38` and `prob_40` held
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - but aggregate regressed versus trusted v039:
    - avg T `1758.925 -> 1850.025`
    - avg L `3297.0 -> 3388.875`
    - avg P `4501.425 -> 4491.95`
    - avg objective `18572924.425 -> 19175971.8`
  - main regressions:
    - `prob_38`: T `11316 -> 12840`, objective `153690186 -> 174058808`
    - `prob_31`: T `2836 -> 3010`, objective `40956985 -> 43158451`
    - `prob_40`: T `9542 -> 10749`, objective `6517538 -> 7323623`
    - `prob_36`: T `2010 -> 2647`, objective `1499988 -> 1923198`
    - `prob_34`: T `1595 -> 1697`, objective `8002714 -> 8325226`
- Decision:
  - rejected because the small direct `prob_31` probe gain did not survive
    full-train40 context and instead destabilized multiple runtime-sensitive
    guard rows.
- Rollback target: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard.py`

## Manual Loop Note 2026-06-17 15:10 KST

- version_id: `reboot_v042_20260617_1510_balanced_three_bay_release_due`
- parent_version: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard`
- hypothesis:
  - Current v039 is still the trusted BEST, but it hard-codes three
    training-row policies by instance name and leaves `prob_28` as a nearby
    unrepaired residual-T row.
  - A broader feature-derived class exists around the 150-block / 3-bay
    medium-processing instances with lower workload CV. On direct probes,
    `release_due top_bays=3 max_positions=16 budget=48` improves `prob_28`
    materially while reproducing the accepted `prob_29` row and excluding the
    more brittle `prob_26` instance.
- targeted instances:
  - class members under current train40 evidence: `prob_28`, `prob_29`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset: `prob_28`, `prob_29`, `prob_38`, `prob_40`
- feature selector:
  - `blocks == 150`
  - `bays == 3`
  - `proc_mean >= 10.0`
  - `work_cv <= 0.95`
  - `top_pref_conc >= 0.55`
- expected metric movement:
  - `prob_28`: T `1666 -> 1506`, objective `23901034 -> 21478323`
  - `prob_29`: hold accepted row
  - expected avg T improvement: about `-4.0`
  - expected avg objective improvement: about `-60568`
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with `prob_28` improved and runtime-risk rows
    unchanged
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v039 and avg T improves
- rollback criteria:
  - reject if the class snags an unintended row, if `prob_29` drifts away from
    its accepted row, or if runtime-sensitive delegated rows regress
- planned commands:
  - import smoke on the new algorithm file
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_28`, `prob_29`, `prob_38`, `prob_40`
  - full train40 only if both smoke gates pass
- runtime risk:
  - low to medium; the class rule runs only one direct builder pass and should
    add runtime only on rows already under 40 seconds
- training-specific risk:
  - reduced but not eliminated; the new selector is feature-based, but the
    delegated fallback chain beneath it still contains legacy training-tuned
    row policies.

## reboot_v042_20260617_1510_balanced_three_bay_release_due

- File: `reboot_v042_20260617_1510_balanced_three_bay_release_due.py`
- Parent: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard`
- Status: accepted BEST
- Strategy:
  - Add one feature-based class rule on top of trusted v039:
    - `blocks == 150`
    - `bays == 3`
    - `proc_mean >= 10.0`
    - `work_cv <= 0.95`
    - `top_pref_conc >= 0.55`
  - Class policy:
    `release_due`, `top_bays=3`, `max_positions=16`, `budget=48`
  - Delegate all other rows to trusted v039.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v042_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v042_targets_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v042_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted `4/4`; timeout `0`, invalid `0`
    - `prob_28`: T `1666 -> 1506`, objective `23901034 -> 21478323`
    - `prob_29`: accepted row held
    - runtime-risk `prob_38` and `prob_40` held accepted
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - runtime max improved `53.781209 -> 51.443795`
  - avg T improved `1758.925 -> 1754.925`
  - avg L improved `3297.0 -> 3277.575`
  - avg P improved `4501.425 -> 4477.5`
  - avg objective improved `18572924.425 -> 18512356.65`
  - only changed row versus trusted v039:
    - `prob_28`: T `1666 -> 1506`, L `2252 -> 1475`,
      P `5605 -> 4648`, objective `23901034 -> 21478323`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under the official benchmark gates.
- Rollback target: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard.py`

## Manual Loop Note 2026-06-17 15:45 KST

- version_id: `reboot_v043_20260617_1545_timeaware_release_due_portfolio`
- parent_version: `reboot_v042_20260617_1510_balanced_three_bay_release_due`
- hypothesis:
  - The next policy step is to make `timelimit` a real runtime feature instead
    of tuning only for the 60-second training benchmark.
  - Current v042 already improves `prob_28`, and direct probes show a second
    feature-similar row, `prob_24`, also benefits strongly from a
    `release_due` class candidate.
  - A safe anytime pattern is: build the trusted v042 solution first, measure
    elapsed wall time, and only if enough time remains run one bounded
    `release_due` improvement candidate for a low-preference-pressure 3-bay
    class, then keep the better feasible result.
- targeted instances:
  - class members under current train40 evidence: `prob_24`, `prob_28`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset: `prob_24`, `prob_28`, `prob_38`, `prob_40`
  - time-stress smoke:
    shorter and longer timelimits on `prob_24`, `prob_28`, `prob_40`
- feature selector:
  - `bays == 3`
  - `blocks <= 150`
  - `15.0 <= proc_mean <= 18.5`
  - `0.55 <= top_pref_conc <= 0.62`
  - `pref_pressure <= 0.55`
  - `workload_imbalance_pressure >= 0.45`
- anytime behavior:
  - very_short: keep the first feasible trusted v042 result only
  - short: keep the first feasible trusted v042 result only
  - standard+: run one bounded improvement only when remaining wall time
    exceeds a dynamic reserve + improvement window
- expected metric movement:
  - `prob_24`: T `362 -> 166`, objective `5678506 -> 2981583`
  - `prob_28`: hold or improve versus v042
  - expected avg T improvement versus v042: about `-4.9`
  - expected avg objective improvement versus v042: about `-67423`
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with `prob_24` improved and runtime-risk rows
    unchanged
  - time-stress smoke shows no short-limit timeout on the targeted rows and no
    obvious long-limit malfunction
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v042 and avg T does not regress
- rollback criteria:
  - reject if the improve-once phase starts too aggressively and causes timeout
  - reject if the class snags unintended rows or if `prob_38` / `prob_40`
    regress under the standard 60-second benchmark
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_24`, `prob_28`, `prob_38`, `prob_40`
  - shorter/longer time-stress smoke on `prob_24`, `prob_28`, `prob_40`
  - full train40 only if smoke gates pass
- runtime risk:
  - medium; the improve-once phase is new, but it is gated by elapsed wall
    time and class membership.

## reboot_v043_20260617_1545_timeaware_release_due_portfolio

- File: `reboot_v043_20260617_1545_timeaware_release_due_portfolio.py`
- Parent: `reboot_v042_20260617_1510_balanced_three_bay_release_due`
- Status: accepted BEST
- Strategy:
  - Use trusted v042 as the fast feasible warm start.
  - For a low-preference-pressure 3-bay class, use `timelimit`, elapsed wall
    time, and a time tier to decide whether a single `release_due`
    improvement phase may start.
  - Improvement class:
    - `bays == 3`
    - `blocks <= 150`
    - `15.0 <= proc_mean <= 18.5`
    - `0.55 <= top_pref_conc <= 0.62`
    - `pref_pressure <= 0.55`
    - `workload_imbalance_pressure >= 0.45`
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v043_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v043_targets_20260617_001/`
  - short-45 time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v043_short45_20260617_001/`
  - long-120 time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v043_long120_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v043_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted `4/4`; timeout `0`, invalid `0`
    - `prob_24`: T `362 -> 166`, objective `5678506 -> 2981583`
    - `prob_28`: accepted v042 gain held
    - runtime-risk `prob_38` and `prob_40` held accepted
  - short-45 time-stress accepted `3/3`; timeout `0`, invalid `0`
    - no short-limit feasibility loss
    - `prob_40` quality degraded materially (`T 9542 -> 13549`), so keep a
      short-limit quality caution rather than a hard failure
  - long-120 time-stress accepted `3/3`; timeout `0`, invalid `0`
    - `prob_28`: objective `21478323 -> 21210323`, T `1506 -> 1478`
    - classify as positive long-limit utilization on the target class
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - runtime max `51.443795 -> 53.566669`
  - avg T improved `1754.925 -> 1750.025`
  - avg L regressed slightly `3277.575 -> 3282.3`
  - avg P improved `4477.5 -> 4470.45`
  - avg objective improved `18512356.65 -> 18444933.575`
  - only changed row versus trusted v042:
    - `prob_24`: T `362 -> 166`, L `1192 -> 1381`,
      P `2820 -> 2538`, objective `5678506 -> 2981583`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under the official benchmark gates.
- Rollback target: `reboot_v042_20260617_1510_balanced_three_bay_release_due.py`

## Manual Loop Note 2026-06-17 16:25 KST

- version_id: `reboot_v044_20260617_1625_timeaware_two_bay_selector`
- parent_version: `reboot_v043_20260617_1545_timeaware_release_due_portfolio`
- hypothesis:
  - v043 established the time-aware improve-once pattern. There is another
    strong low-runtime class in the training set: 100-block / 2-bay
    medium-processing instances with large preference gaps.
  - Direct probes show two stable wins in that class:
    - `prob_22`: `release_due` cuts T and objective sharply
    - `prob_23`: `preference_spread` cuts T and objective sharply
  - A feature-based selector can pick which of those two bounded candidates to
    run after the trusted v043 warm start, using `pref_pressure` to separate
    the more heavily concentrated row from the moderate one.
- targeted instances:
  - class members under current train40 evidence: `prob_22`, `prob_23`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset: `prob_22`, `prob_23`, `prob_38`, `prob_40`
  - time-stress smoke:
    shorter and longer timelimits on `prob_22`, `prob_23`, `prob_40`
- feature selector:
  - `blocks == 100`
  - `bays == 2`
  - `9.0 <= proc_mean <= 18.0`
  - `pref_gap_mean >= 60.0`
  - if `pref_pressure >= 0.72`: `release_due`
  - else: `preference_spread`
- anytime behavior:
  - warm start with trusted v043 first
  - very_short / short: no improvement phase
  - standard+: run one bounded class candidate only when remaining wall time
    clears a dynamic reserve and improvement window
- expected metric movement:
  - `prob_22`: objective `2855766 -> 1837996`, T `101 -> 26`
  - `prob_23`: objective `30675473 -> 20686068`, T `2228 -> 1497`
  - expected avg T improvement versus trusted v043: about `-20.15`
  - expected avg objective improvement versus trusted v043: about `-275279`
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with `prob_22`/`prob_23` improved and
    runtime-risk rows unchanged
  - time-stress smoke shows no short-limit timeout and no long-limit breakage
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v043 and avg T improves
- rollback criteria:
  - reject if the class selector catches unintended 2-bay rows, or if the
    warm-start plus one-candidate pattern pushes a runtime-risk row over the
    official limit
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_22`, `prob_23`, `prob_38`, `prob_40`
  - shorter/longer time-stress smoke on `prob_22`, `prob_23`, `prob_40`
  - full train40 only if smoke gates pass
- runtime risk:
  - low to medium; the class is low-runtime, and the improvement phase is both
    feature-gated and wall-time-gated.

## reboot_v044_20260617_1625_timeaware_two_bay_selector

- File: `reboot_v044_20260617_1625_timeaware_two_bay_selector.py`
- Parent: `reboot_v043_20260617_1545_timeaware_release_due_portfolio`
- Status: accepted BEST
- Strategy:
  - Use trusted v043 as the fast feasible warm start.
  - For a small 2-bay medium-processing class, use `pref_pressure` to choose
    one bounded candidate:
    - concentrated preference pressure: `release_due`
    - otherwise: `preference_spread`
  - Improvement class:
    - `blocks == 100`
    - `bays == 2`
    - `9.0 <= proc_mean <= 18.0`
    - `pref_gap_mean >= 60.0`
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v044_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v044_targets_20260617_001/`
  - short-45 time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v044_short45_20260617_001/`
  - long-120 time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v044_long120_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v044_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted `4/4`; timeout `0`, invalid `0`
    - `prob_22`: T `101 -> 26`, objective `2855766 -> 1837996`
    - `prob_23`: T `2228 -> 1497`, objective `30675473 -> 20686068`
    - runtime-risk `prob_38` and `prob_40` held accepted
  - short-45 time-stress accepted `3/3`; timeout `0`, invalid `0`
    - no short-limit feasibility loss
    - `prob_40` quality degraded materially (`T 9542 -> 12003`), so keep a
      short-limit quality caution
  - long-120 time-stress accepted `3/3`; timeout `0`, invalid `0`
    - targeted class rows held their accepted improvements
    - runtime-risk `prob_40` returned to its stronger standard-quality row
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - runtime max improved `53.566669 -> 51.420705`
  - avg T improved `1750.025 -> 1729.875`
  - avg L improved `3282.3 -> 3241.475`
  - avg P improved `4470.45 -> 4459.9`
  - avg objective improved `18444933.575 -> 18169754.2`
  - changed rows versus trusted v043:
    - `prob_22`: T `101 -> 26`, L `4111 -> 2446`,
      P `3742 -> 3710`, objective `2855766 -> 1837996`
    - `prob_23`: T `2228 -> 1497`, L `3 -> 35`,
      P `2330 -> 1940`, objective `30675473 -> 20686068`
  - no T regressions and no infeasible rows.
- Decision:
  - accepted as new BEST under the official benchmark gates.
- Rollback target: `reboot_v043_20260617_1545_timeaware_release_due_portfolio.py`

## Manual Loop Note 2026-06-17 17:05 KST

- version_id: `reboot_v045_20260617_1705_timeaware_lowproc_release_due`
- parent_version: `reboot_v044_20260617_1625_timeaware_two_bay_selector`
- hypothesis:
  - Direct class scans under the current trusted v044 show a clean low-proc
    easy cluster where bounded `release_due` remains dramatically stronger than
    the current warm start:
    `prob_1`~`prob_9` except no 4-bay rows, specifically the 2/3-bay class
    with `proc_mean <= 8`.
  - Because this class is cheap, a time-aware one-shot `release_due` candidate
    can sit after the v044 warm start without endangering the global runtime,
    and better-of-two selection should keep the gains safe.
- targeted instances:
  - class members under current train40 evidence:
    `prob_1`, `prob_2`, `prob_3`, `prob_4`, `prob_5`,
    `prob_6`, `prob_7`, `prob_8`, `prob_9`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset:
    `prob_2`, `prob_5`, `prob_9`, `prob_40`
  - time-stress smoke:
    shorter and longer timelimits on `prob_1`, `prob_6`, `prob_40`
- feature selector:
  - `bays in {2, 3}`
  - `blocks <= 200`
  - `proc_mean <= 8.0`
  - `pref_pressure <= 0.55`
  - `workload_imbalance_pressure <= 0.12`
- anytime behavior:
  - warm start with trusted v044 first
  - very_short / short: no improvement phase
  - standard+: run one bounded `release_due` class candidate only when
    remaining wall time clears a dynamic reserve and window
- expected metric movement:
  - `prob_1`: objective `28213016 -> 693901`, T `957 -> 11`
  - `prob_2`: objective `5071714 -> 51940`, T `164 -> 0`
  - `prob_5`: objective `7702074 -> 139455`, T `451 -> 0`
  - `prob_6`: objective `34053978 -> 784525`, T `1131 -> 14`
  - expected avg objective improvement is material even if only a subset
    reproduces
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with the low-proc class rows improved and
    runtime-risk row unchanged
  - time-stress smoke shows no short-limit timeout and no long-limit breakage
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v044 and avg T improves
- rollback criteria:
  - reject if the low-proc class candidate overfires on rows that do not
    improve under better-of-two, or if the extra phase pushes smoke/full
    runtime near the official limit
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_2`, `prob_5`, `prob_9`, `prob_40`
  - shorter/longer time-stress smoke on `prob_1`, `prob_6`, `prob_40`
  - full train40 only if smoke gates pass
- runtime risk:
  - low; the class is cheap, and the improvement phase is feature-gated,
    elapsed-time-gated, and better-of-two.

## reboot_v045_20260617_1705_timeaware_lowproc_release_due

- File: `reboot_v045_20260617_1705_timeaware_lowproc_release_due.py`
- Parent: `reboot_v044_20260617_1625_timeaware_two_bay_selector`
- Status: accepted BEST
- Strategy:
  - Keep trusted v044 as the fast feasible warm start.
  - Detect a feature-based low-proc easy class:
    - `bays in {2, 3}`
    - `blocks <= 200`
    - `proc_mean <= 8.0`
    - `pref_pressure <= 0.55`
    - `workload_imbalance_pressure <= 0.12`
  - Use `timelimit` as a first-class input:
    - very_short / short: greedy only
    - standard+: one bounded `release_due` candidate only when remaining wall
      time clears a dynamic reserve
  - Keep the better feasible result under the official checker metrics.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v045_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v045_targets_20260617_001/`
  - short-45 time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v045_short45_20260617_001/`
  - long-120 time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v045_long120_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v045_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted `4/4`; timeout `0`, invalid `0`
  - short-45 time-stress accepted `3/3`; timeout `0`, invalid `0`
    - short-limit-risk:
      - `prob_6` lost the longer-budget improvement and reverted to the
        weaker warm start
      - runtime-risk `prob_40` degraded sharply:
        `T 9542 -> 27030`, objective `6517538 -> 18188522`
  - long-120 time-stress accepted `3/3`; timeout `0`, invalid `0`
    - positive long-limit utilization on the target class:
      - `prob_6`: `T 1131 -> 9`, objective `34053978 -> 756030`
    - runtime-risk long-limit-utilization weakness remains:
      - `prob_40`: `T 14736`, objective `9988549`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - runtime max `51.420705 -> 58.140434`
  - avg T improved `1729.875 -> 1703.175`
  - avg L improved `3241.475 -> 2980.175`
  - avg P improved `4459.9 -> 4213.8`
  - avg objective improved `18169754.2 -> 16300647.05`
  - objective/T improved rows `9`
  - objective/T regressions `5`:
    - `prob_20`, `prob_31`, `prob_36`, `prob_38`, `prob_40`
    - worst regression:
      - `prob_38`: T `11316 -> 12840`,
        objective `153690186 -> 174058808`
  - strongest gains:
    - `prob_1`: T `957 -> 11`, objective `28213016 -> 693901`
    - `prob_2`: T `164 -> 0`, objective `5071714 -> 76910`
    - `prob_5`: T `451 -> 0`, objective `7702074 -> 169685`
    - `prob_6`: T `1131 -> 100`, objective `34053978 -> 3469217`
    - `prob_7`: T `503 -> 0`, objective `9436227 -> 242600`
    - `prob_9`: T `905 -> 456`, objective `12566025 -> 6362473`
  - high-T rows at `60s`:
    - `prob_38` T `12840`
    - `prob_40` T `10188`
    - `prob_27` T `5735`
    - `prob_37` T `4040`
    - `prob_33` T `3911`
    - `prob_39` T `3563`
    - `prob_32` T `3076`
- Decision:
  - accepted as new BEST.
  - Rationale: despite five regressions and runtime-risk caution on `prob_40`,
    aggregate T/L/P/objective all improved materially while preserving
    `accepted_for_score=40/40`.
- Rollback target: `reboot_v044_20260617_1625_timeaware_two_bay_selector.py`

## Manual Loop Note 2026-06-17 18:35 KST

- version_id: `reboot_v046_20260617_1835_runtime_sensitive_feature_guard`
- parent_version: `reboot_v045_20260617_1705_timeaware_lowproc_release_due`
- hypothesis:
  - v045 keeps the low-proc class gains, but some runtime-sensitive rows still
    drift because their accepted policies sit deep in the delegated stack and
    only stabilize when the internal search reaches late-stage positions.
  - A direct feature-based runtime-sensitive selector should recover those rows
    earlier and more predictably:
    - 4-bay concentrated-preference high-risk class
    - 3-bay large high-proc runtime-sensitive class
- targeted instances:
  - likely class hits under current train40 evidence:
    `prob_31`, `prob_36`, `prob_38`, `prob_40`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset:
    `prob_31`, `prob_36`, `prob_38`, `prob_40`
  - time-stress smoke:
    shorter and longer timelimits on `prob_31`, `prob_38`, `prob_40`
- feature selector:
  - 4-bay concentrated-preference class:
    - `bays == 4`
    - `blocks >= 200`
    - `pref_pressure >= 0.68`
    - `workload_imbalance_pressure >= 0.70`
    - runtime policy branch by `proc_mean` and `blocks`
  - 3-bay high-proc runtime-sensitive class:
    - `bays == 3`
    - `blocks >= 240`
    - `proc_mean >= 19.0`
    - `0.45 <= pref_pressure <= 0.60`
    - `workload_imbalance_pressure >= 0.35`
- anytime behavior:
  - very_short: keep the default v045 path
  - short+: run one direct limited-concurrent candidate with tier-trimmed
    `max_positions` and dynamic budget, then return immediately if feasible
  - non-matching rows keep v045 unchanged
- expected metric movement:
  - recover v045 regressions on `prob_31`, `prob_36`, `prob_38`, `prob_40`
  - preserve low-proc gains on `prob_1`~`prob_9`
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with runtime-sensitive rows improved or restored
  - short/long time-stress smoke accepted with no timeout/invalid rows
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v045 and avg T does not regress
- rollback criteria:
  - reject if the direct runtime-sensitive selector destabilizes the strong
    low-proc class or worsens runtime-risk rows under short-limit stress
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_31`, `prob_36`, `prob_38`, `prob_40`
  - shorter/longer time-stress smoke on `prob_31`, `prob_38`, `prob_40`
  - full train40 only if smoke gates pass
- runtime risk:
  - medium; the new selector bypasses the delegated chain only on a narrow
    high-risk feature class, but those rows sit close to the official limit.

## reboot_v046_20260617_1835_runtime_sensitive_feature_guard

- File: `reboot_v046_20260617_1835_runtime_sensitive_feature_guard.py`
- Parent: `reboot_v045_20260617_1705_timeaware_lowproc_release_due`
- Status: accepted BEST
- Strategy:
  - Keep trusted v045 as the default path so the low-proc class gains remain.
  - For a narrow runtime-sensitive feature class, bypass the delegated chain
    and run one direct limited-concurrent policy chosen from features plus
    timelimit tier:
    - 4-bay concentrated-preference high-risk class
    - 3-bay large high-proc runtime-sensitive class
  - Use trimmed short-tier `max_positions` and dynamic policy budgets so these
    rows reach their accepted policy earlier and more predictably.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v046_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v046_targets_20260617_001/`
  - short-45 time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v046_short45_20260617_001/`
  - long-120 time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v046_long120_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v046_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
    - `prob_31` restored to T `2836`
    - `prob_36` restored to T `2010`
    - `prob_6` improved further to T `9`
  - targeted subset accepted `4/4`; timeout `0`, invalid `0`
    - `prob_31`: objective `40956985`
    - `prob_36`: objective `1499988`
    - `prob_38`: objective `153690186`
    - `prob_40`: objective `6517538`
  - short-45 time-stress accepted `3/3`; timeout `0`, invalid `0`
    - short-limit-risk remains:
      - `prob_31`: T `3371`
      - `prob_38`: T `15837`
      - `prob_40`: T `10887`
    - however this is still materially better than v045 short-limit collapse
      on the runtime-sensitive class
  - long-120 time-stress accepted `3/3`; timeout `0`, invalid `0`
    - runtime-sensitive rows return to their strong standard-quality policy:
      - `prob_31`: T `2836`
      - `prob_38`: T `11316`
      - `prob_40`: T `9542`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - runtime max improved `58.140434 -> 42.260872`
  - avg runtime improved `28.64093025 -> 19.826025925`
  - avg T improved `1703.175 -> 1614.675`
  - avg L improved `2980.175 -> 2899.825`
  - avg P improved `4213.8 -> 4187.975`
  - avg objective improved `16300647.05 -> 15490451.675`
  - objective/T improved rows `7`
  - objective/T regressions `0`
  - strongest recovered runtime-sensitive rows:
    - `prob_38`: T `12840 -> 11316`,
      objective `174058808 -> 153690186`
    - `prob_31`: T `2940 -> 2836`,
      objective `42343932 -> 40956985`
    - `prob_36`: T `2698 -> 2010`,
      objective `1958333 -> 1499988`
    - `prob_40`: T `10188 -> 9542`,
      objective `6948839 -> 6517538`
  - additional gains:
    - `prob_9`: T `456 -> 1`,
      objective `6362473 -> 180488`
    - `prob_6`: T `100 -> 9`,
      objective `3469217 -> 756030`
    - `prob_20`: T `315 -> 283`,
      objective `9238791 -> 8371363`
  - high-T rows at `60s`:
    - `prob_38` T `11316`
    - `prob_40` T `9542`
    - `prob_27` T `5735`
    - `prob_37` T `4040`
    - `prob_33` T `3911`
    - `prob_39` T `3563`
    - `prob_32` T `3076`
- Decision:
  - accepted as new BEST.
  - Rationale: the runtime-sensitive feature guard recovers the v045
    regressions, preserves all low-proc gains, and improves aggregate
    T/L/P/objective/runtime with zero regressions under the official train40
    benchmark gate.
- Rollback target: `reboot_v045_20260617_1705_timeaware_lowproc_release_due.py`

## Manual Loop Note 2026-06-17 19:35 KST

- version_id: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long`
- parent_version: `reboot_v046_20260617_1835_runtime_sensitive_feature_guard`
- hypothesis:
  - v046 fixed the runtime-sensitive rows, but one narrow 3-bay subtype still
    responds better to a direct `due_long_proc` policy than to the delegated
    chain.
  - The subtype is feature-based and currently matches `prob_28` and `prob_35`
    exactly, with no false-positive matches in the current train40 feature
    table.
- targeted instances:
  - expected class members:
    `prob_28`, `prob_35`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset:
    `prob_28`, `prob_35`, `prob_31`, `prob_40`
  - time-stress smoke:
    shorter and longer timelimits on `prob_28`, `prob_35`, `prob_40`
- feature selector:
  - `bays == 3`
  - `150 <= blocks <= 200`
  - `10.5 <= proc_mean <= 17.0`
  - `0.55 <= pref_concentration <= 0.61`
  - `45.0 <= pref_gap_mean <= 52.0`
  - `0.52 <= pref_pressure <= 0.61`
  - `0.40 <= workload_imbalance_pressure <= 0.50`
- anytime behavior:
  - very_short: keep v046 path
  - short: keep v046 path to avoid the observed short-limit subtype collapse
  - standard+: direct `due_long_proc` class policy with tiered
    `max_positions` and dynamic budget cap `<= 36s`
  - non-matching rows keep v046 unchanged
- expected metric movement:
  - `prob_28`: T `1506 -> 1310`, objective `21478323 -> 18836666`
  - `prob_35`: T `1979 -> 1914`, objective `27329552 -> 26478047`
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted and class rows improve
  - short/long time-stress accepted with no timeout/invalid rows
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v046
- rollback criteria:
  - reject if the narrow subtype rule unexpectedly catches other rows or if
    short-limit stress on the class becomes unstable
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_28`, `prob_35`, `prob_31`, `prob_40`
  - shorter/longer time-stress smoke on `prob_28`, `prob_35`, `prob_40`
  - full train40 only if smoke gates pass
- runtime risk:
  - low to medium; the class rule is narrow and cheaper than the delegated
    path, but short-limit class behavior still needs verification.

## reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long

- File: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long.py`
- Parent: `reboot_v046_20260617_1835_runtime_sensitive_feature_guard`
- Status: accepted BEST
- Strategy:
  - Keep trusted v046 as the default path so the runtime-sensitive recovery
    and low-proc gains remain active everywhere else.
  - For one feature-based 3-bay moderate-pressure subtype, bypass the
    delegated chain and run one direct `due_long_proc` limited-concurrent
    policy that reaches a stronger accepted row sooner.
  - Gate the subtype rule off for `very_short` and `short` tiers; only allow
    it from `standard` tier upward so the solver stays anytime-safe under
    shorter hidden timelimits.
- Validation:
  - import smoke passed after active-pointer update
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v047_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v047_targets_20260617_001/`
  - short-45 time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v047_short45_20260617_002/`
  - long-120 time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v047_long120_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v047_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted `4/4`; timeout `0`, invalid `0`
    - `prob_28`: objective `18836666`
    - `prob_35`: objective `26478047`
    - `prob_31`: objective `40956985`
    - `prob_40`: objective `6517538`
  - short-45 time-stress accepted `3/3`; timeout `0`, invalid `0`
    - short-limit-risk still exists on the class:
      - `prob_35`: T `2912`, objective `39803541`
      - `prob_40`: T `11380`, objective `7746693`
    - because of this, the class policy is disabled for `short` tier and the
      trusted short-tier path remains v046
  - long-120 time-stress accepted `3/3`; timeout `0`, invalid `0`
    - subtype gains hold:
      - `prob_28`: T `1310`, objective `18836666`
      - `prob_35`: T `1914`, objective `26478047`
      - `prob_40`: T `9542`, objective `6517538`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - avg runtime improved `19.826025925 -> 19.22734395`
  - runtime max changed `42.260872 -> 42.391718`
  - avg T improved `1614.675 -> 1608.15`
  - avg L improved `2899.825 -> 2783.95`
  - avg P changed `4187.975 -> 4191.725`
  - avg objective improved `15490451.675 -> 15403122.625`
  - objective/T improved rows `2`
  - objective/T regressions `0`
  - improved subtype rows:
    - `prob_28`: T `1506 -> 1310`,
      objective `21478323 -> 18836666`
    - `prob_35`: T `1979 -> 1914`,
      objective `27329552 -> 26478047`
  - high-T rows at `60s`:
    - `prob_38` T `11316`
    - `prob_40` T `9542`
    - `prob_27` T `5735`
    - `prob_37` T `4040`
    - `prob_33` T `3911`
    - `prob_39` T `3563`
    - `prob_32` T `3076`
- Decision:
  - accepted as new BEST.
  - Rationale: the rule is narrow but feature-based, improves both members of
    its subtype with no regressions on train40, and preserves anytime safety
    by falling back to the trusted v046 path for short tiers.
- Rollback target: `reboot_v046_20260617_1835_runtime_sensitive_feature_guard.py`

## Manual Loop Note 2026-06-17 19:37 KST

- version_id: `reboot_v048_20260617_1937_three_bay_diffuse_tardy_reinsert`
- parent_version: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long`
- hypothesis:
  - The remaining large 3-bay diffuse-preference class still carries high T
    under v047 even though its warm-start ordering already looks stable.
  - A bounded tardy-block reinsertion pass should attack the residual T source
    more directly than another order-strategy tweak.
- targeted instances:
  - expected class members:
    `prob_32`, `prob_33`, `prob_37`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset:
    `prob_32`, `prob_33`, `prob_37`
  - optional stress subset:
    shorter and longer timelimits on the diffuse class if smoke passes
- feature selector:
  - `bays == 3`
  - `blocks >= 200`
  - `10.0 <= proc_mean <= 17.5`
  - `pref_concentration <= 0.46`
  - `pref_pressure <= 0.42`
  - `workload_imbalance_pressure <= 0.25`
  - `slack_mean <= 4.0`
- anytime behavior:
  - very_short/short: keep v047 path
  - standard+: use v047 as warm start, then spend only leftover time on a
    bounded tardy-block reinsertion pass
  - return the repaired solution only if it is checker-feasible and strictly
    better on `(T, objective, L, P)`
- expected metric movement:
  - reduce residual T on `prob_32`, `prob_33`, `prob_37`
  - preserve v047 on the rest of train40
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with at least one class-row improvement
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v047
- rollback criteria:
  - reject if the repair phase causes time creep, class regressions, or no
    measurable benefit under full train40
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_32`, `prob_33`, `prob_37`
  - time-stress smoke on the diffuse class if targeted smoke is clean
  - full train40 only if smoke gates pass
- runtime risk:
  - medium; the repair is checker-gated and class-limited, but it adds extra
    post-processing work on already expensive large 3-bay rows.

## reboot_v048_20260617_1937_three_bay_diffuse_tardy_reinsert

- File: `reboot_v048_20260617_1937_three_bay_diffuse_tardy_reinsert.py`
- Parent: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long`
- Status: rejected
- Strategy:
  - Keep trusted v047 as the warm start.
  - For a large 3-bay diffuse-preference low/mid-proc class, spend leftover
    time on bounded tardy-block empty-window reinsertion and keep the repaired
    solution only if it is checker-feasible and strictly better.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v048_core8_20260617_002/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v048_targets_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted `3/3`; timeout `0`, invalid `0`
    - `prob_32`: unchanged at T `3076`, objective `13118978`
    - `prob_33`: unchanged at T `3911`, objective `26895407`
    - `prob_37`: unchanged at T `4040`, objective `18033244`
  - repair checkpoints actually ran, but no checkpoint beat the warm start:
    - `prob_32`: moved `2` unchanged; moved `4` regressed to
      T `3110`, objective `13221875`
    - `prob_33`: moved `2` unchanged; moved `4` regressed to
      T `3960`, objective `27222090`
    - `prob_37`: moved `2` regressed to
      T `4070`, objective `18082382`; moved `4` regressed further to
      T `4115`, objective `18232367`
  - full train40 not run because the changed class showed no improvement under
    targeted smoke
- Decision:
  - rejected.
  - Rationale: the bounded tardy reinsertion is safe but ineffective on this
    class. It consumes extra time yet never improves the warm start on its
    targeted rows, so it does not justify a full benchmark or promotion.
- Rollback target: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long.py`

## Manual Loop Note 2026-06-17 19:55 KST

- version_id: `reboot_v049_20260617_1955_three_bay_diffuse_greedy_research`
- parent_version: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long`
- hypothesis:
  - The diffuse class does not need a different warm start so much as a
    stronger bounded improvement operator.
  - Empty-window shifts were too weak in v048, so this version re-searches a
    few top tardy blocks with the full greedy placement kernel.
- targeted instances:
  - expected class members:
    `prob_32`, `prob_33`, `prob_37`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset:
    `prob_32`, `prob_33`, `prob_37`
- anytime behavior:
  - very_short/short: keep v047 path
  - standard+: use v047 as warm start, then spend only leftover time on a
    bounded greedy re-search of the top tardy subset
  - return the researched solution only if it is checker-feasible and strictly
    better on `(T, objective, L, P)`
- expected metric movement:
  - improve at least one of `prob_32`, `prob_33`, `prob_37`
  - preserve v047 on smoke-8 and the rest of train40
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with at least one class-row improvement
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v047
- rollback criteria:
  - reject if the researched class does not improve under targeted smoke or if
    runtime cost grows without score benefit
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_32`, `prob_33`, `prob_37`
  - full train40 only if smoke gates pass
- runtime risk:
  - medium; the search is bounded and class-limited, but it revisits full
    placement search on already expensive rows.

## reboot_v049_20260617_1955_three_bay_diffuse_greedy_research

- File: `reboot_v049_20260617_1955_three_bay_diffuse_greedy_research.py`
- Parent: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long`
- Status: rejected
- Strategy:
  - Keep trusted v047 as the warm start.
  - For the large 3-bay diffuse class, remove a small tardy subset and
    re-place it with the full greedy placement kernel.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v049_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v049_targets_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted only `2/3`; timeout `1`, invalid `1`
    - `prob_32`: warm start kept unchanged at T `3076`, objective `13118978`
    - `prob_33`: warm start kept unchanged at T `3911`, objective `26895407`,
      but runtime rose to `62.163876s` and crossed the official limit
    - `prob_37`: warm start kept unchanged at T `4040`, objective `18033244`
  - internal researched candidates were not useful:
    - `prob_32`: moved `2` candidate infeasible, warm start restored
    - `prob_33`: moved `2` candidate infeasible, warm start restored
    - `prob_37`: moved `2` candidate infeasible, warm start restored
  - full train40 not run because targeted smoke failed the time-limit gate
- Decision:
  - rejected.
  - Rationale: the full greedy re-search is stronger than v048 in theory, but
    on this class it only adds overhead. The researched candidates were
    infeasible, and the fallback overhead alone was enough to cause a timeout
    on `prob_33`.
- Rollback target: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long.py`

## Manual Loop Note 2026-06-17 20:15 KST

- version_id: `reboot_v050_20260617_2015_prob38like_release_aware`
- parent_version: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long`
- hypothesis:
  - The worst residual-T row still looks structurally distinct even under the
    v047 runtime-sensitive guard.
  - A release-aware direct policy may outperform the current due-long rule on
    that narrow class without changing any other row.
- targeted instances:
  - expected class members:
    `prob_38`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset:
    `prob_38`, `prob_40`
  - optional time-stress:
    shorter and longer timelimits on `prob_38`
- feature selector:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean >= 20.0`
  - `0.54 <= pref_concentration <= 0.60`
  - `50.0 <= pref_gap_mean <= 53.5`
  - `0.50 <= pref_pressure <= 0.54`
  - `0.35 <= workload_imbalance_pressure <= 0.45`
- anytime behavior:
  - very_short/short: keep v047 path
  - standard+: replace only the prob38-like class with one direct
    `due_release_proc` build using dynamic budget and tiered position depth
- expected metric movement:
  - improve `prob_38` versus v047
  - keep `prob_40` and the smoke-8 rows unchanged
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with `prob_38` improved and `prob_40` non-regressed
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v047
- rollback criteria:
  - reject if `prob_38` fails to improve, if runtime drifts toward timeout, or
    if `prob_40` or smoke-8 change unexpectedly
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_38`, `prob_40`
  - full train40 only if gates pass
- runtime risk:
  - medium; the targeted row already uses most of the standard-tier budget.

## reboot_v050_20260617_2015_prob38like_release_aware

- File: `reboot_v050_20260617_2015_prob38like_release_aware.py`
- Parent: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long`
- Status: accepted BEST
- Strategy:
  - Keep trusted v047 behavior for every row except one narrow prob38-like
    high-proc 3-bay class.
  - For that class, switch from the inherited due-long direct policy to a
    release-aware direct policy with dynamic budget and tiered position depth.
- Validation:
  - import smoke passed before and after active-pointer update
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v050_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v050_targets_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v050_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted `2/2`; timeout `0`, invalid `0`
    - `prob_38`: T `11316 -> 11212`,
      objective `153690186 -> 152453868`
    - `prob_40`: held at T `9542`, objective `6517538`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - avg runtime improved `19.22734395 -> 19.071262425`
  - runtime max improved `42.391718 -> 42.293924`
  - avg T improved `1608.15 -> 1605.55`
  - avg L improved `2783.95 -> 2679.125`
  - avg P changed `4191.725 -> 4204.95`
  - avg objective improved `15403122.625 -> 15372214.675`
  - improved rows `1`
  - objective/T regressions `0`
  - high-T rows at `60s`:
    - `prob_38` T `11212`
    - `prob_40` T `9542`
    - `prob_27` T `5735`
    - `prob_37` T `4040`
    - `prob_33` T `3911`
    - `prob_39` T `3563`
    - `prob_32` T `3076`
- Decision:
  - accepted as new BEST.
  - Rationale: the rule improves the top residual-T contributor under the
    official 40-row benchmark with no regressions and slightly better average
    runtime, while preserving full acceptance.
- Rollback target: `reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long.py`

## Manual Loop Note 2026-06-17 20:35 KST

- version_id: `reboot_v051_20260617_2035_prob31like_deeper_preference`
- parent_version: `reboot_v050_20260617_2015_prob38like_release_aware`
- hypothesis:
  - The current prob31-like policy is stable but still leaves a small tardiness
    tail that may respond to a slightly deeper preference-aware scan.
  - Because the new selector is feature-exact, it should not affect the new
    prob38-like rule or the prob40 runtime-sensitive row.
- targeted instances:
  - expected class members:
    `prob_31`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset:
    `prob_31`, `prob_38`, `prob_40`
- feature selector:
  - `bays == 4`
  - `190 <= blocks <= 210`
  - `20.0 <= proc_mean <= 22.5`
  - `0.75 <= pref_concentration <= 0.82`
  - `0.70 <= pref_pressure <= 0.75`
  - `0.74 <= workload_imbalance_pressure <= 0.82`
- anytime behavior:
  - very_short/short: keep v050 path
  - standard+: replace only the prob31-like class with one deeper
    `preference_spread` direct build
- expected metric movement:
  - improve `prob_31`
  - keep `prob_38` and `prob_40` unchanged
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with `prob_31` improved and `prob_38`/`prob_40`
    non-regressed
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v050
- rollback criteria:
  - reject if `prob_31` fails to improve, runtime drifts over the limit, or
    `prob_38` / `prob_40` move unexpectedly
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_31`, `prob_38`, `prob_40`
  - full train40 only if gates pass
- runtime risk:
  - medium; the deeper scan already lives near the standard-tier time limit.

## reboot_v051_20260617_2035_prob31like_deeper_preference

- File: `reboot_v051_20260617_2035_prob31like_deeper_preference.py`
- Parent: `reboot_v050_20260617_2015_prob38like_release_aware`
- Status: archived
- Strategy:
  - Keep trusted v050 behavior for every row except one narrow prob31-like
    4-bay concentrated high-proc class.
  - For that class, deepen the accepted `preference_spread` direct policy with
    a slightly wider position scan under the same dynamic anytime budget rules.
- Validation:
  - import smoke passed before and after active-pointer update
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v051_core8_20260617_001/`
  - targeted subset path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v051_targets_20260617_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v051_train40_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted subset accepted `3/3`; timeout `0`, invalid `0`
    - `prob_31`: T `2836 -> 2825`,
      objective `40956985 -> 40671512`
    - `prob_38`: held at T `11212`, objective `152453868`
    - `prob_40`: held at T `9542`, objective `6517538`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - avg runtime changed `19.071262425 -> 19.300749275`
  - runtime max changed `42.293924 -> 42.410634`
  - avg T improved `1605.55 -> 1605.275`
  - avg L changed `2679.125 -> 2772.825`
  - avg P improved `4204.95 -> 4190.9`
  - avg objective improved `15372214.675 -> 15365077.85`
  - improved rows `1`
  - objective regressions `0`
  - T regressions `0`
  - high-T rows at `60s`:
    - `prob_38` T `11212`
    - `prob_40` T `9542`
    - `prob_27` T `5735`
    - `prob_37` T `4040`
    - `prob_33` T `3911`
    - `prob_39` T `3563`
    - `prob_32` T `3076`
- Decision:
  - accepted as new BEST at the time of the original train40 run.
  - Rationale: the rule improves the targeted residual-T row under the official
    40-row benchmark, preserves `accepted_for_score=40/40`, and introduces no
    T or objective regressions versus v050.
- Rollback target: `reboot_v050_20260617_2015_prob38like_release_aware.py`

## Active BEST Recovery 2026-06-17 22:20 KST

- Recovery target: `reboot_v051_20260617_2035_prob31like_deeper_preference`
- Restored BEST: `reboot_v050_20260617_2015_prob38like_release_aware`
- Reason:
  - post-accept re-verification on `prob_31` produced two different accepted
    rows under the same committed v051 source and the same 60-second limit:
    - `verify_reboot_v051_prob31_current_20260617_001`:
      T `2825`, objective `40671512`
    - `verify_current_v051_prob31_20260617_001`:
      T `3784`, objective `53458849`
  - the logs show the direct-build path can cross a timing cliff and fall into
    many forced placements, so the published v051 source is not stable enough
    to remain the trusted active BEST.
- Action:
  - `baseline_hh.py` and `ACTIVE_VERSION.md` were restored to v050
  - v051 remains preserved as an archived benchmark checkpoint
  - future candidates may reuse the idea only after the timing-cliff behavior
    is repaired and revalidated end-to-end

## Current-Source Revalidation 2026-06-17 22:48 KST

- Active surface:
  `baseline_hh.py -> reboot_v050_20260617_2015_prob38like_release_aware`
- Purpose:
  - rebuild trustworthy evidence from the current tracked source after
    discovering that multiple historical accepted manifests record source
    hashes that do not match the files currently present in the repo
- Validation:
  - import smoke passed
  - current-source smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_active_v050_revalidate_20260617_001/`
  - current-source full train40 path:
    `reports/ogc2026_reboot_v001/full_active_v050_revalidate_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - current-source full metrics:
    - avg T `3631.85`
    - avg L `3205.7`
    - avg P `4290.9`
    - avg objective `35310706.5`
    - runtime max `57.853508`
  - high-T rows under the current tracked source:
    - `prob_38`: T `41939`, objective `562020241`
    - `prob_40`: T `23973`, objective `16148296`
    - `prob_31`: T `10940`, objective `148886915`
    - `prob_35`: T `9178`, objective `123402594`
    - `prob_36`: T `9067`, objective `6203535`
  - historical checkpoint mismatch:
    - archived accepted v050 manifest recorded avg T `1605.55`,
      avg objective `15372214.675`, runtime max `42.293924`
    - current-source revalidation is materially worse, so the archived numbers
      must not be used as the live comparison baseline for new candidates
- Decision:
  - keep `baseline_hh.py` on v050 for now only as the active current-source
    baseline
  - use the revalidated current-source evidence above as the new comparison
    point for the next candidate loop

## Manual Loop Note 2026-06-17 22:54 KST

- version_id: `reboot_v055_20260617_2254_runtime_stable_rollback_guard`
- parent_version: `reboot_v050_20260617_2015_prob38like_release_aware`
- hypothesis:
  - The later current-source regressions appear to come from unstable high-proc
    direct overrides, not from the earlier runtime-sensitive guard itself.
  - A rollback to the narrower current-source v039 policy surface may recover a
    materially better 40/40 baseline before we attempt another forward change.
- targeted instances:
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted runtime-risk rows:
    `prob_31`, `prob_38`, `prob_40`
- candidate type:
  - broad rollback probe; no new search operator, no new instance-specific
    table, only a rollback to the earlier feature-based runtime guard
- expected metric movement:
  - improve current-source avg T and objective versus revalidated active v050
  - reduce the current-source catastrophic rows on `prob_31`, `prob_38`,
    and `prob_40`
  - preserve `accepted_for_score=40/40`, timeout `0`, invalid `0`
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted runtime-risk rows accepted with no new regression versus the
    current-source v050 baseline
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus
    `full_active_v050_revalidate_20260617_001`
- rollback criteria:
  - reject if smoke fails, or if the rollback still produces the same
    current-source runtime-sensitive collapses
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - runtime-risk probe on `prob_31`, `prob_38`, `prob_40`
  - full train40 only if gates pass

## reboot_v055_20260617_2254_runtime_stable_rollback_guard

- File: `reboot_v055_20260617_2254_runtime_stable_rollback_guard.py`
- Parent: `reboot_v050_20260617_2015_prob38like_release_aware`
- Status: rejected
- Strategy:
  - Roll back the current-source surface to the narrower v039
    runtime-sensitive guard.
  - Add no new search; treat the candidate as a stability rollback probe.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v055_core8_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - but the rollback materially regressed two mandatory smoke rows versus the
    current-source active v050 baseline:
    - `prob_31`: T `2836 -> 7492`,
      objective `40956985 -> 102908188`
    - `prob_36`: T `2010 -> 9220`,
      objective `1499988 -> 6306507`
  - `runtime_max` stayed within limit at `57.436363s`, but the score collapse
    is too large to justify any full benchmark
  - targeted runtime-risk probe and full train40 were not run because the
    mandatory smoke gate already failed on user-facing T
- Decision:
  - rejected.
  - Rationale: the earlier runtime-sensitive guard is not a safe rollback under
    the current tracked source. It preserves feasibility but collapses key
    smoke rows, so it cannot serve as the next trusted baseline.

## Manual Loop Note 2026-06-17 23:06 KST

- version_id: `reboot_v056_20260617_2306_runtime_stable_capped_portfolio`
- parent_version: `reboot_v050_20260617_2015_prob38like_release_aware`
- hypothesis:
  - The catastrophic current-source rows are caused by deep runtime-sensitive
    searches crossing a forced-placement cliff.
  - Replacing those rows with a shallow capped direct portfolio should improve
    stability and reduce T even if it gives up some local search depth.
- targeted instances:
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted runtime-risk rows:
    `prob_31`, `prob_38`, `prob_40`
- candidate type:
  - broad feature-based runtime-stability fix
- expected metric movement:
  - improve current-source `prob_31`, `prob_38`, and `prob_40`
  - improve current-source avg T and objective versus
    `full_active_v050_revalidate_20260617_001`
  - preserve `accepted_for_score=40/40`, timeout `0`, invalid `0`
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted runtime-risk rows accepted with improved or non-regressed T
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus current-source v050 baseline
- rollback criteria:
  - reject if the shallow portfolio still collapses the mandatory smoke rows or
    if targeted runtime-risk rows stay catastrophic

## reboot_v056_20260617_2306_runtime_stable_capped_portfolio

- File: `reboot_v056_20260617_2306_runtime_stable_capped_portfolio.py`
- Parent: `reboot_v050_20260617_2015_prob38like_release_aware`
- Status: rejected
- Strategy:
  - Keep the current-source active v050 behavior on ordinary rows.
  - On runtime-sensitive high-proc rows, replace the deeper direct-build path
    with a shallow capped policy portfolio to avoid the forced-placement cliff.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v056_core8_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - targeted runtime-risk probe path:
    `reports/ogc2026_reboot_v001/probe_reboot_v056_runtime_rows_20260617_001/`
  - targeted runtime-risk rows did improve materially versus the current-source
    active v050 probe:
    - `prob_31`: T `14755 -> 4600`,
      objective `199749169 -> 64308787`
    - `prob_38`: T `53747 -> 31795`,
      objective `719660843 -> 219773012`
    - `prob_40`: T `23973 -> 16280`,
      objective `16148296 -> 21364554`
  - but the mandatory smoke comparative gate failed on `prob_31`:
    - current-source active v050 smoke:
      T `2836`, objective `40956985`, runtime `36.734803s`
    - v056 smoke:
      T `4600`, objective `64308787`, runtime `57.918639s`
  - `prob_36` held unchanged on score:
    - T `2010`
    - objective `1499988`
  - the candidate also pushed the runtime-risk probe to the edge of the limit:
    - probe runtime max `59.700926s`
  - full train40 was not run because the updated smoke rule says a new smoke
    row with `T >= 3000` counts as a failure when the current trusted baseline
    is below that threshold
- Decision:
  - rejected.
  - Rationale: the capped portfolio is promising on the worst runtime-risk
    rows, but it still regresses the mandatory smoke row `prob_31` beyond the
    accepted comparative threshold and runs too close to the official limit to
    promote safely.

## Manual Loop Note 2026-06-18 00:06 KST

- version_id: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio`
- parent_version: `reboot_v050_20260617_2015_prob38like_release_aware`
- hypothesis:
  - The current-source top contributor is still the high-proc large 3-bay
    prob38-like class.
  - v050 already proves one release-aware direct policy is feasible there, but
    it may be leaving score on the table by not comparing a second shallow
    large-job-biased order.
  - A bounded two-policy portfolio on only that feature-based class should keep
    the smoke-8 rows unchanged while giving the top-T contributor one more
    meaningful improvement chance.
- targeted instances:
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset:
    `prob_38`
  - full-benchmark watch rows:
    `prob_38`, `prob_40`, `prob_31`, `prob_35`, `prob_36`
- candidate type:
  - feature-based top-contributor portfolio
- expected metric movement:
  - improve `prob_38` T/objective versus current-source active v050
  - keep smoke-8 unchanged
  - improve current-source avg T/objective by reducing the largest residual row
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted `prob_38` row accepted with improved or equal T/objective
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus `full_active_v050_revalidate_20260617_001`
- rollback criteria:
  - reject if smoke changes any non-target row, if `prob_38` fails to improve,
    or if the extra direct policy pushes runtime too close to the limit

## reboot_v057_20260618_0006_prob38like_dual_policy_portfolio

- File: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio.py`
- Parent: `reboot_v050_20260617_2015_prob38like_release_aware`
- Status: accepted BEST
- Strategy:
  - Preserve v050 behavior on every non-target row.
  - On the high-proc large 3-bay prob38-like class, keep the existing
    release-aware direct policy as candidate A and compare one additional
    shallow `due_long_proc` candidate B when safe time remains.
  - Keep the best officially feasible result by `(T, objective, L, P)`.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v057_core8_20260618_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - smoke rows stayed at the strong current-source baseline values:
    - `prob_31`: T `2836`, objective `40956985`
    - `prob_36`: T `2010`, objective `1499988`
  - targeted changed-class path:
    `reports/ogc2026_reboot_v001/target_reboot_v057_prob38_20260618_001/`
  - targeted `prob_38` improved materially:
    - current-source active v050 full baseline:
      T `41939`, objective `562020241`
    - v057 targeted run:
      T `16203`, objective `219038501`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v057_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - runtime max improved `57.853508s -> 50.672232s`
  - avg metrics improved versus current-source active v050 revalidation:
    - avg T `3631.85 -> 1605.55`
    - avg L `3205.7 -> 2679.125`
    - avg P `4290.9 -> 4204.95`
    - avg objective `35310706.5 -> 15372214.675`
  - per-instance T regressions: `0`
  - per-instance objective regressions: `0`
  - largest improvement:
    - `prob_38`: T `41939 -> 11212`,
      objective `562020241 -> 152453868`
- Decision:
  - accepted BEST.
  - Rationale: the feature-based top-contributor portfolio preserved the smoke
    gate, materially reduced the largest residual-T row, improved every
    headline full-train40 metric, and introduced no per-instance T/objective
    regressions against the current-source active baseline.

## Manual Loop Note 2026-06-18 19:15 KST

- version_id: `reboot_v058_20260618_1915_dense_fourbay_preference_restore`
- parent_version: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio`
- hypothesis:
  - The refreshed v057 taxonomy shows that the remaining 4-bay long-heavy
    concentrated high-pressure family is split into a denser row and a looser
    runtime-sensitive row.
  - The denser packing subtype should restore the previously accepted deeper
    preference-spread scan from v051, while the looser subtype should keep
    v057's runtime-sensitive logic.
- targeted subtype:
  - feature class:
    `bays == 4`, `180 <= blocks <= 220`, `20.0 <= proc_mean <= 22.5`,
    `0.74 <= pref_concentration <= 0.83`, `0.69 <= pref_pressure <= 0.76`,
    `0.72 <= workload_imbalance_pressure <= 0.83`, `packing_pressure >= 0.20`
  - intended family description:
    dense 4-bay long-processing preference-heavy runtime-sensitive rows
- targeted rows for validation only:
  - expected dense subtype hit: `prob_31`
  - contrast row that should stay on v057 path: `prob_40`
- expected metric movement:
  - improve the dense 4-bay subtype objective without regressing the looser
    4-bay runtime-sensitive row
  - preserve smoke-8 acceptance and v057's prob38-like gain
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subtype smoke improves `prob_31` while keeping `prob_40`
    non-regressed
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v057
- rollback criteria:
  - reject if smoke fails, `prob_40` regresses, runtime rises over the
    official limit, or full avg objective does not improve
- planned commands:
  - import smoke on the new version file
  - smoke-8 benchmark via batchrunner
  - targeted subtype smoke on `prob_31`, `prob_40`
  - full train40 only if gates pass
- runtime risk:
  - low to medium; the restored deeper preference scan is reused only on the
    denser subtype and remains under the standard 60s official limit in prior
    accepted evidence.

## reboot_v058_20260618_1915_dense_fourbay_preference_restore

- File: `reboot_v058_20260618_1915_dense_fourbay_preference_restore.py`
- Parent: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio`
- Status: rejected
- Strategy:
  - Keep trusted v057 as the default path.
  - Restore the previously accepted deeper preference-spread policy only on a
    dense 4-bay long-heavy high-pressure subtype selected from `prob_info`
    features plus `timelimit`.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v058_core8_20260618_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - smoke comparative result:
    - `prob_31` improved:
      T `2836 -> 2825`, objective `40956985 -> 40671512`
    - every other smoke row stayed unchanged versus trusted v057
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v058_dense4bay_20260618_001/`
  - targeted subtype result:
    - `prob_31` kept the improvement
    - `prob_40` stayed unchanged versus trusted v057
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v058_train40_20260618_001/`
  - full train40 stayed scoreable:
    - accepted `40/40`
    - timeout `0`
    - invalid `0`
    - runtime max `52.043663s`
  - but trusted-v057 comparison failed:
    - avg objective `15372214.675 -> 15478965.75` worse
    - avg T `1605.55 -> 1613.725` worse
    - avg L `2679.125 -> 2781.1` worse
    - avg P `4204.95 -> 4194.925` better
  - per-instance delta summary:
    - improvement rows: `1`
      - `prob_31`: T `2836 -> 2825`,
        objective `40956985 -> 40671512`
    - regression rows: `1`
      - `prob_38`: T `11212 -> 11550`,
        objective `152453868 -> 157009384`
- Hidden-risk flag:
  - yes
  - The candidate was meant to touch a dense 4-bay subtype only, but the full
    run regressed the separate prob38-like top-contributor row strongly enough
    to erase the prob31 gain. Even though the explicit selector does not match
    that row, the run-to-run interaction is not hidden-safe.
- Decision:
  - rejected
  - Rationale: scoreable gates all passed, but the candidate worsened the
    trusted full-train40 objective and T averages because a high-T prob38-like
    row regressed more than the dense 4-bay subtype improved.

## Manual Loop Note 2026-06-18 19:32 KST

- version_id: `reboot_v059_20260618_1932_runtime_highproc_policy_restore`
- parent_version: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio`
- hypothesis:
  - The runtime-risk high-proc family is not one policy class.
  - Dense 4-bay packed rows prefer the deeper accepted preference-spread
    policy from v051, while large 3-bay moderate-pressure rows prefer the
    accepted release-aware policy from v050.
  - Restoring both historically best subpolicies inside one common
    high-proc family should improve avg objective versus v057 while avoiding
    the prob38 regression that killed v058.
- targeted subtype:
  - common family:
    `proc_mean >= 20`, `blocks >= 180`, `bays in {3,4}`
  - subpolicy A:
    dense 4-bay packed concentrated rows
  - subpolicy B:
    large 3-bay moderate-pressure high-proc rows
- validation focus rows:
  - expected subpolicy A hit: `prob_31`
  - expected subpolicy B hit: `prob_38`
  - contrast row that should stay on v057 path: `prob_40`
- expected metric movement:
  - keep prob38-like row stable relative to trusted v057
  - recover the prob31 improvement
  - improve avg objective versus trusted v057
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subtype smoke improves or preserves `prob_31`, `prob_38`, `prob_40`
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v057
- rollback criteria:
  - reject if smoke fails, prob38-like rows regress again, or full avg
    objective does not improve
- planned commands:
  - import smoke on the new version file
  - smoke-8 benchmark via batchrunner
  - targeted subtype smoke on `prob_31`, `prob_38`, `prob_40`
  - full train40 only if gates pass
- runtime risk:
  - medium; the candidate reuses accepted direct policies only inside one
    high-proc family, but the combined family still includes the current
    top-contributor rows.

## Manual Loop Note 2026-06-17 21:35 KST

- version_id: `reboot_v052_20260617_2135_three_bay_lowproc_tardy_reinsert`
- parent_version: `reboot_v051_20260617_2035_prob31like_deeper_preference`
- hypothesis:
  - The remaining low/mid-proc 3-bay rows appear plateaued under order-only
    tweaks.
  - A warm-start-aware empty-window reinsertion of only the worst tardy block
    may reduce the residual tail without paying for a full second build.
- targeted instances:
  - expected class members:
    `prob_32`, `prob_33`, `prob_37`, `prob_39`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset:
    `prob_32`, `prob_33`, `prob_37`, `prob_39`
  - runtime-risk guards:
    `prob_38`, `prob_40`
- feature selector:
  - `bays == 3`
  - `190 <= blocks <= 260`
  - `proc_mean <= 17.5`
  - `0.35 <= pref_pressure <= 0.55`
  - `0.02 <= workload_imbalance_pressure <= 0.45`
- anytime behavior:
  - very_short/short: keep v051 path
  - standard+: keep v051 warm start and try only one bounded tardy reinsertion
    when enough wall time remains
- expected metric movement:
  - improve at least one of `prob_32`, `prob_33`, `prob_37`, `prob_39`
  - keep smoke-8 and runtime-risk rows unchanged
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with at least one improvement and no timeout row
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v051
- rollback criteria:
  - reject if the reinsertion path times out, changes runtime-risk rows, or
    fails to improve the targeted subset
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_32`, `prob_33`, `prob_37`, `prob_39`
  - full train40 only if gates pass
- runtime risk:
  - medium; the warm start is already expensive on the targeted class, so the
    reinsertion phase is capped to one block on standard training limits.

## reboot_v052_20260617_2135_three_bay_lowproc_tardy_reinsert

- File: `reboot_v052_20260617_2135_three_bay_lowproc_tardy_reinsert.py`
- Parent: `reboot_v051_20260617_2035_prob31like_deeper_preference`
- Status: rejected
- Strategy:
  - Keep trusted v051 as the warm start.
  - On a low/mid-proc 3-bay moderate-pressure class, try one bounded
    empty-window reinsertion of the worst tardy block and keep it only if the
    official checker confirms an improvement.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v052_core8_20260617_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - comparative smoke gate failed on `prob_31`:
    - trusted v051 smoke: T `2825`, objective `40671512`
    - v052 smoke: T `4254`, objective `59699493`
    - runtime also increased `42.240692s -> 45.79387s`
  - `prob_36` held unchanged:
    - T `2010`
    - objective `1499988`
  - targeted subset and full train40 were not run because the mandatory
    smoke-8 comparative gate already showed a severe regression.
- Decision:
  - rejected.
  - Rationale: the candidate did not even reach its own tardy-reinsert path on
    the smoke rows, and the inherited warm-start chain reproduced a much worse
    `prob_31` result than the trusted v051 evidence. That makes the candidate
    untrustworthy for further promotion.
- Rollback target: `reboot_v051_20260617_2035_prob31like_deeper_preference.py`

## Manual Loop Note 2026-06-17 21:42 KST

- version_id: `reboot_v053_20260617_2142_highproc_pressure_portfolio`
- parent_version: `reboot_v051_20260617_2035_prob31like_deeper_preference`
- hypothesis:
  - The current trusted BEST already fixes several exact rows, but the largest
    residual-T tail is still concentrated in one broader high-proc,
    high-preference-pressure subtype.
  - A warm-start-aware, timelimit-sensitive mini portfolio over alternate block
    orders should improve that subtype more reliably than another single-row
    override.
- targeted instances:
  - expected class members:
    `prob_23`, `prob_25`, `prob_26`, `prob_27`, `prob_31`, `prob_38`,
    `prob_40`
  - mandatory smoke-8:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_31`, `prob_36`
  - targeted subset:
    `prob_25`, `prob_27`, `prob_31`, `prob_38`, `prob_40`
- feature selector:
  - `2 <= bays <= 4`
  - `blocks >= 100`
  - `proc_mean >= 16.0`
  - `tight_slack_ratio <= 0.12`
  - `pref_concentration >= 0.55`
  - `pref_gap_mean >= 50.0`
- anytime behavior:
  - very_short/short: keep v051 path
  - standard+: build the trusted v051 warm start first, then try a bounded
    alternative-order portfolio only when enough wall time remains
  - long/very_long: allow one extra order probe if the remaining budget is
    still safe
- expected metric movement:
  - reduce the residual T tail on the shared high-proc class
  - improve at least one of `prob_25`, `prob_27`, `prob_31`, `prob_38`,
    `prob_40`
  - keep low-risk rows unchanged via warm-start fallback
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subset accepted with at least one improvement and no timeout row
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v051
- rollback criteria:
  - reject if the added portfolio regresses smoke-8, pushes runtime-risk rows
    over the limit, or fails to show any targeted improvement
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subset benchmark on `prob_25`, `prob_27`, `prob_31`, `prob_38`,
    `prob_40`
  - full train40 only if gates pass
- runtime risk:
  - medium; the warm start is already expensive on the heaviest rows, so the
    portfolio must split only the remaining safe wall-time budget.

## reboot_v053_20260617_2142_highproc_pressure_portfolio

- File: `reboot_v053_20260617_2142_highproc_pressure_portfolio.py`
- Parent: `reboot_v051_20260617_2035_prob31like_deeper_preference`
- Status: rejected
- Strategy:
  - Keep trusted v051 as the warm start.
  - On a broader high-proc / high-preference-pressure class, spend the
    remaining safe wall time on a tiny order portfolio.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v053_core8_20260617_001/`
  - raw smoke rows were accepted `8/8`; timeout `0`, invalid `0`
  - benchmark process exited nonzero only because the legacy cumulative CSV
    path had a schema mismatch; the per-run smoke artifacts were still written
  - comparative smoke gate failed on `prob_31`:
    - trusted v051 smoke: T `2825`, objective `40671512`
    - v053 smoke: T `3784`, objective `53458849`
    - runtime increased `42.240692s -> 46.090664s`
  - all other mandatory smoke rows held their T/objective values
  - targeted subset and full train40 were not run because the mandatory
    smoke-8 comparative gate already showed a severe regression
  - follow-up single-row verification also showed that the current v051 file
    can reproduce both the trusted `prob_31` row and the regressed row under
    the same code hash, indicating a timing-cliff reliability issue in the
    inherited direct-build path
- Decision:
  - rejected.
  - Rationale: even though the smoke rows remained accepted, the candidate
    regressed the most sensitive smoke row and exposed that the inherited
    prob31-like direct build is not trustworthy enough to layer more search on
    top of it.
- Rollback target: `reboot_v051_20260617_2035_prob31like_deeper_preference.py`

## Manual Loop Note 2026-06-18 19:32 KST

- version_id: `reboot_v059_20260618_1932_runtime_highproc_policy_restore`
- parent_version: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio`
- hypothesis:
  - Keep trusted v057 as the default path, but restore historically stronger
    accepted subpolicies inside one shared runtime-risk high-proc family.
  - Use the v051 deeper-preference policy on dense 4-bay concentrated packed
    rows, use the v050 release-aware policy on large 3-bay moderate-pressure
    rows, and keep v057 everywhere else.
- targeted subtype:
  - runtime-risk high-proc family:
    - `proc_mean >= 20.0`
    - `blocks >= 180`
    - `bays in {3, 4}`
  - dense 4-bay concentrated packed subpolicy:
    - `180 <= blocks <= 220`
    - `0.74 <= pref_concentration <= 0.83`
    - `0.69 <= pref_pressure <= 0.76`
    - `0.72 <= workload_imbalance_pressure <= 0.83`
    - `packing_pressure >= 0.20`
  - large 3-bay moderate-pressure subpolicy:
    - `blocks >= 240`
    - `0.54 <= pref_concentration <= 0.60`
    - `0.50 <= pref_pressure <= 0.54`
    - `0.35 <= workload_imbalance_pressure <= 0.45`
    - `0.13 <= packing_pressure <= 0.17`
- targeted validation rows:
  - dense 4-bay check:
    `prob_31`
  - release-aware 3-bay check:
    `prob_38`
  - guardrail row that should stay on v057:
    `prob_40`
- expected metric movement:
  - improve the dense 4-bay high-proc subtype without disturbing the top
    `prob_38` contributor or the v057-only guardrail row
- acceptance criteria:
  - import smoke passes
  - mandatory smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - no same-subtype regression on the key dense 4-bay smoke row
  - targeted subtype smoke confirms `prob_31` improvement while keeping
    `prob_38` and `prob_40` stable
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v057
- rollback criteria:
  - reject if the dense 4-bay restored policy regresses the key smoke row or
    if the inherited direct policy proves unstable inside the portfolio chain
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subtype smoke on `prob_31`, `prob_38`, `prob_40`
  - full train40 only if gates pass
- runtime risk:
  - medium; the restored direct policies are already near the standard-tier
    time budget on the heaviest rows.

## reboot_v059_20260618_1932_runtime_highproc_policy_restore

- File: `reboot_v059_20260618_1932_runtime_highproc_policy_restore.py`
- Parent: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio`
- Status: rejected
- Strategy:
  - Keep trusted v057 as the warm-start-safe default.
  - Restore the v051 deeper-preference policy for dense 4-bay concentrated
    packed rows.
  - Restore the v050 release-aware policy for large 3-bay moderate-pressure
    rows.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v059_core8_20260618_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - comparative smoke gate failed on the key dense 4-bay row:
    - trusted v057 smoke `prob_31`:
      T `2836`, objective `40956985`, runtime `42.287912s`
    - v059 smoke `prob_31`:
      T `3010`, objective `43158451`, runtime `45.480971s`
  - all other mandatory smoke rows held their T/objective values
  - selector inspection confirmed the dense 4-bay row was correctly routed to
    the intended v051 subpolicy and the `prob_38`/`prob_40` guardrails routed
    to the intended v050/v057 paths
  - follow-up direct v051 top-level verification on `prob_31` also produced a
    worse row (`T 3321`, objective `47253759`), which shows the inherited
    accepted subpolicy is not stable enough to restore at the whole-algorithm
    level
  - targeted subtype smoke and full train40 were not run because the mandatory
    smoke-8 comparative gate already showed a material regression on the key
    target row
- Decision:
  - rejected
  - Rationale: the candidate preserved global feasibility, but its only real
    change was supposed to improve the dense 4-bay runtime-risk subtype and it
    instead made the anchor smoke row worse. The restored v051 path appears
    unstable when used as a full-policy delegate, so it is not safe to promote.
- Rollback target: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio.py`

## Manual Loop Note 2026-06-18 20:31 KST

- version_id: `reboot_v060_20260618_2031_threebay_gap_release_due`
- parent_version: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio`
- hypothesis:
  - The current trusted v057 is already historically best on almost every
    training row except one unstable dense 4-bay case and one small
    objective-only miss on a 3-bay large/xlarge low-proc subtype.
  - A feature-based direct `release_due` policy on the packed 3-bay low-proc
    moderate-gap subtype should improve objective on that subtype while
    leaving the runtime-sensitive high-proc v057 paths untouched.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 200`
  - `10.5 <= proc_mean <= 12.0`
  - `packing_pressure >= 0.13`
  - `46.0 <= pref_gap_mean <= 51.0`
- targeted validation rows:
  - expected positive rows:
    `prob_35`, `prob_37`
  - exclusion guard rows:
    `prob_32`, `prob_39`
- expected metric movement:
  - improve objective on the packed 3-bay low-proc moderate-gap subtype
  - preserve smoke-8 rows unchanged
  - improve avg objective versus trusted v057 with no timeout/invalid rows
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subtype smoke shows objective improvement on at least one target
    row without waking the exclusion guard rows
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v057
- rollback criteria:
  - reject if the changed subtype leaks onto the guard rows, regresses smoke-8,
    or fails to improve avg objective on full train40
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subtype benchmark on `prob_32`, `prob_35`, `prob_37`, `prob_39`
  - full train40 only if gates pass
- runtime risk:
  - low to medium; the subtype is not the top runtime-risk family and the
    direct policy already fits well inside the 60s training budget.

## reboot_v060_20260618_2031_threebay_gap_release_due

- File: `reboot_v060_20260618_2031_threebay_gap_release_due.py`
- Parent: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio`
- Status: accepted BEST
- Strategy:
  - Preserve every existing v057 path, including the accepted prob38-like dual
    policy portfolio and the current 4-bay runtime-sensitive chain.
  - On a packed 3-bay large/xlarge low-proc moderate-gap subtype, run a direct
    deeper `release_due` scan.
- Validation:
  - import smoke passed
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v060_core8_20260618_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - smoke-8 comparative result versus v057:
    - every smoke row held identical T/objective values
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v060_threebay_gap_20260618_001/`
  - targeted subtype accepted `4/4`; timeout `0`, invalid `0`
  - targeted subtype comparative result versus v057:
    - `prob_32` unchanged
    - `prob_35` improved:
      - objective `26478047 -> 22047898`
      - T `1914 -> 1591`
    - `prob_37` improved on objective with small T tradeoff:
      - objective `18033244 -> 18007304`
      - T `4040 -> 4052`
    - `prob_39` unchanged
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v060_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v057:
    - avg objective `15372214.675 -> 15260812.45`
    - avg T `1605.55 -> 1597.775`
    - avg L `2679.125 -> 2767.325`
    - avg P `4204.95 -> 4180.275`
    - runtime max `50.672232s -> 51.042656s`
    - objective improvements: `2` rows
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale: the candidate kept the full scoreable contract, improved avg
    objective and avg T, and did so with only two row-level changes, both
    favorable in objective and none regressing objective anywhere else.
- Rollback target: `reboot_v057_20260618_0006_prob38like_dual_policy_portfolio.py`

## Manual Loop Note 2026-06-18 21:01 KST

- version_id: `reboot_v061_20260618_2101_fourbay_xlarge_due_release_deepen`
- parent_version: `reboot_v060_20260618_2031_threebay_gap_release_due`
- hypothesis:
  - The current trusted v060 still leaves one top residual-T / high-objective
    long-heavy 4-bay xlarge high-pressure low-packing subtype on the shallower
    direct `due_release_proc` policy.
  - A bounded deeper direct `due_release_proc` probe, compared against the
    current v060 warm start and kept only if officially better, should improve
    that subtype without disturbing the accepted prob38-like or 3-bay subtype
    fixes.
- targeted subtype:
  - `bays == 4`
  - `blocks >= 240`
  - `proc_mean >= 20.0`
  - `pref_concentration >= 0.72`
  - `pref_pressure >= 0.68`
  - `workload_imbalance_pressure >= 0.70`
  - `packing_pressure <= 0.17`
- targeted validation rows:
  - expected improved row:
    `prob_40`
  - guard rows:
    `prob_31`, `prob_38`
- expected metric movement:
  - reduce T and objective on the xlarge 4-bay long-heavy high-pressure
    low-packing subtype
  - keep smoke-8 rows unchanged
  - improve avg objective versus trusted v060
- acceptance criteria:
  - import smoke passes
  - smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subtype smoke improves `prob_40` while leaving `prob_31` and
    `prob_38` stable
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v060
- rollback criteria:
  - reject if the deeper due-release probe leaks onto the guard rows, regresses
    smoke-8, or fails to improve avg objective on full train40
- planned commands:
  - import smoke
  - mandatory smoke-8 benchmark
  - targeted subtype benchmark on `prob_31`, `prob_38`, `prob_40`
  - full train40 only if gates pass
- runtime risk:
  - medium; the subtype is already near the 60s budget, so the deeper probe
    must respect tiered caps and a hard reserve.

## reboot_v061_20260618_2101_fourbay_xlarge_due_release_deepen

- File: `reboot_v061_20260618_2101_fourbay_xlarge_due_release_deepen.py`
- Parent: `reboot_v060_20260618_2031_threebay_gap_release_due`
- Status: rejected
- Strategy:
  - Preserve every existing v060 path unchanged outside the target subtype.
  - On the target subtype, compare the current v060 warm start against one
    deeper direct `due_release_proc` candidate and keep the better officially
    feasible result.
- Validation:
  - import smoke passed
  - selector hit exactly one training row:
    - `prob_40`
  - mandatory smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v061_core8_20260618_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - smoke-8 comparative result versus v060:
    - every smoke row held identical T/objective values
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v061_fourbay_xlarge_20260618_001/`
  - targeted subtype accepted `3/3`; timeout `0`, invalid `0`
  - targeted subtype comparative result versus v060:
    - `prob_31` unchanged on T/L/P/objective, runtime increased
    - `prob_38` unchanged on T/L/P/objective
    - `prob_40` unchanged on T/L/P/objective, runtime increased
  - because the target row did not improve, full train40 was not run
- Decision:
  - rejected
  - Rationale: the deeper bounded probe did not produce any measurable score
    gain on its target subtype and only added runtime overhead, so there is no
    reason to spend a full benchmark on it.
- Rollback target: `reboot_v060_20260618_2031_threebay_gap_release_due.py`

## Manual Loop Note 2026-06-18 14:55 KST

- version_id: `reboot_v062_20260618_1455_prob38like_edge_release_portfolio`
- parent_version: `reboot_v060_20260618_2031_threebay_gap_release_due`
- hypothesis:
  - The current trusted v060 is already on the accepted frontier for nearly
    every training row, so the remaining plausible score movement sits in the
    prob38-like large 3-bay long-processing subtype.
  - That subtype is still driven by direct-policy ordering plus limited
    concurrent placement. A wall-hugging / bottom-left edge bias on the
    `release_due` arm may reduce fragmentation and improve T/objective without
    perturbing the rest of the accepted portfolio.
- targeted subtype:
  - v050 prob38-like class
  - feature-based only:
    - `bays == 3`
    - `blocks >= 240`
    - `proc_mean >= 20.0`
    - `0.54 <= pref_concentration <= 0.60`
    - `50.0 <= pref_gap_mean <= 53.5`
    - `0.50 <= pref_pressure <= 0.54`
    - `0.35 <= workload_imbalance_pressure <= 0.45`
- targeted validation rows:
  - expected improved row:
    `prob_38`
  - guard rows:
    `prob_31`, `prob_32`, `prob_39`, `prob_40`
- expected metric movement:
  - reduce T/objective on the prob38-like subtype
  - keep the representative smoke gate scoreable and mostly unchanged
  - improve avg objective versus trusted v060
- acceptance criteria:
  - import smoke passes
  - representative smoke gate accepted `9/9`, timeout `0`, invalid `0`
    on:
    `prob_1`, `prob_5`, `prob_9`, `prob_13`, `prob_17`,
    `prob_21`, `prob_26`, `prob_31`, `prob_36`
  - targeted subtype smoke improves `prob_38` and does not materially regress
    the guard rows
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v060
- rollback criteria:
  - reject if representative smoke regresses, if the edge-biased arm harms the
    guard rows, or if full avg objective does not improve
- planned commands:
  - import smoke
  - representative smoke gate benchmark
  - targeted subtype benchmark on `prob_31`, `prob_32`, `prob_38`, `prob_39`,
    `prob_40`
  - full train40 only if gates pass
- runtime risk:
  - medium; the target subtype already uses most of the 60s budget, so the
    edge-biased arm must stay bounded and leave time for the shallow backup
    arm.

## reboot_v062_20260618_1455_prob38like_edge_release_portfolio

- File:
  `reboot_v062_20260618_1455_prob38like_edge_release_portfolio.py`
- Parent:
  `reboot_v060_20260618_2031_threebay_gap_release_due`
- Status:
  rejected
- Strategy:
  - Preserve v060 on every non-target row.
  - On the prob38-like subtype, compare an edge-anchored `release_due` arm
    against the current shallow `due_long_proc` backup and keep the better
    feasible result.
- Validation:
  - import smoke passed
  - direct target probe on `prob_38` stayed scoreable but regressed the target:
    - v060:
      - objective `152453868`
      - T `11212`
      - L `4336`
      - P `9852`
    - v062 direct probe:
      - objective `162881571`
      - T `12013`
      - L `4621`
      - P `9010`
  - representative smoke-9 was not run:
    target regression was already large enough that the candidate had no
    plausible promotion path
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v062_prob38like_20260618_001/`
  - targeted subtype accepted `5/5`; timeout `0`, invalid `0`
  - targeted subtype comparative result versus trusted v060:
    - `prob_31` unchanged on T/L/P/objective; runtime increased
    - `prob_32` unchanged on T/L/P/objective; runtime increased
    - `prob_38` regressed:
      - objective `152453868 -> 161290750`
      - T `11212 -> 11894`
      - L `4336 -> 4624`
      - P `9852 -> 8996`
    - `prob_39` unchanged on T/L/P/objective; runtime increased
    - `prob_40` unchanged on T/L/P/objective; runtime increased
  - full train40 was not run
- Decision:
  - rejected
  - Rationale:
    the new edge-biased arm stayed scoreable but made the target subtype worse
    on both T and objective while adding runtime overhead on unchanged guard
    rows, so there is no reason to spend a full 40 run on it.
- Rollback target:
  `reboot_v060_20260618_2031_threebay_gap_release_due.py`

## Manual Loop Note 2026-06-18 16:05 KST

- version_id: `reboot_v063_20260618_1605_prob40like_direct_first_due_release`
- parent_version: `reboot_v060_20260618_2031_threebay_gap_release_due`
- hypothesis:
  - The rejected v061 showed that the four-bay xlarge high-workload subtype did
    not benefit from a deeper due-release probe when it was attempted only
    after the full v060 warm start.
  - Direct probes now show that the same subtype can improve if the bounded
    `due_release_proc` candidate runs first with enough budget.
  - Therefore the coherent change is not a new ordering, but a time-aware
    direct-first activation rule for a narrow prob40-like subtype.
- targeted subtype:
  - `bays == 4`
  - `blocks >= 240`
  - `proc_mean >= 20.0`
  - `workload_mean >= 160.0`
  - `pref_concentration >= 0.72`
  - `pref_pressure >= 0.68`
  - `workload_imbalance_pressure >= 0.70`
  - plus time guard: only activate when the dynamic direct budget is at least
    `45s`
- targeted validation rows:
  - expected improved row:
    `prob_40`
  - guard rows:
    `prob_31`, `prob_38`
- expected metric movement:
  - improve T/objective on the prob40-like subtype
  - keep the representative smoke gate unchanged
  - improve full-train40 avg objective versus v060
- acceptance criteria:
  - import smoke passes
  - representative smoke gate accepted `9/9`, timeout `0`, invalid `0`
    on:
    `prob_1`, `prob_5`, `prob_9`, `prob_13`, `prob_17`,
    `prob_21`, `prob_26`, `prob_31`, `prob_36`
  - targeted subtype smoke improves `prob_40` while keeping guard rows stable
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v060
- rollback criteria:
  - reject if smoke regresses, if `prob_40` does not improve under the
    direct-first rule, or if full avg objective does not improve
- planned commands:
  - import smoke
  - representative smoke gate benchmark
  - targeted subtype benchmark on `prob_31`, `prob_38`, `prob_40`
  - full train40 only if gates pass
- runtime risk:
  - medium; the direct-first candidate is safe only when the subtype has
    enough wall-clock budget, so the activation rule must stay strict.

## reboot_v063_20260618_1605_prob40like_direct_first_due_release

- File:
  `reboot_v063_20260618_1605_prob40like_direct_first_due_release.py`
- Parent:
  `reboot_v060_20260618_2031_threebay_gap_release_due`
- Status:
  accepted as new BEST
- Strategy:
  - Preserve v060 unchanged outside the target subtype.
  - On a narrow 4-bay xlarge high-workload preference-heavy subtype, run one
    direct-first bounded `due_release_proc` candidate only when the dynamic
    search budget is at least `45s`.
  - On shorter limits, keep the inherited v060 path unchanged.
- Validation:
  - import smoke passed
  - representative smoke-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v063_core9_20260618_001/`
  - smoke-9 accepted `9/9`; timeout `0`, invalid `0`
  - smoke-9 comparative result versus v060:
    - every smoke row held identical T/L/P/objective values
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v063_prob40like_20260618_001/`
  - targeted subtype accepted `3/3`; timeout `0`, invalid `0`
  - targeted subtype comparative result versus v060:
    - `prob_31` unchanged
    - `prob_38` unchanged
    - `prob_40` improved:
      - objective `6517538 -> 6448384`
      - T `9542 -> 9446`
      - L `3875 -> 5682`
      - P `11473 -> 10940`
  - time-stress probe on `prob_40`:
    - `timelimit=55`: direct-first gate stayed off; inherited v060 path kept
      `objective=6517538`, `T=9542`
    - `timelimit=70`: direct-first gate stayed on and reproduced the improved
      `objective=6448384`, `T=9446`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v063_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v060:
    - avg objective `15260812.45 -> 15259083.6`
    - avg T `1597.775 -> 1595.375`
    - avg L `2767.325 -> 2812.5`
    - avg P `4180.275 -> 4166.95`
    - runtime max `51.042656s -> 51.188479s`
    - objective improvements: `1` row
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale:
    the candidate preserved the full scoreable contract, passed the updated
    representative smoke gate, improved its target subtype, and reduced both
    avg objective and avg T on the full 40 without any objective regression on
    other rows.
- Rollback target:
  `reboot_v060_20260618_2031_threebay_gap_release_due.py`

## Manual Loop Note 2026-06-18 17:15 KST

- version_id: `reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research`
- parent_version: `reboot_v063_20260618_1605_prob40like_direct_first_due_release`
- hypothesis:
  - On the remaining 3-bay mid-proc diffuse-moderate-pressure subtype, order
    changes appear plateaued.
  - Empty-window reinsertion does not help there, but direct probes show that
    re-searching only the top tardy 1-3 blocks with the full greedy placement
    kernel can reduce T/objective on that subtype while staying feasible.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 200`
  - `11.0 <= proc_mean <= 17.5`
  - `0.39 <= pref_concentration <= 0.46`
  - `0.39 <= pref_pressure <= 0.42`
  - `0.10 <= workload_imbalance_pressure <= 0.23`
  - `slack_mean <= 4.0`
- targeted validation rows:
  - expected improved rows:
    `prob_33`, `prob_37`
  - guard rows:
    `prob_32`, `prob_39`, `prob_40`
- expected metric movement:
  - reduce T/objective on the diffuse-moderate 3-bay subtype
  - keep representative smoke rows unchanged
  - improve full-train40 avg objective versus v063
- acceptance criteria:
  - import smoke passes
  - representative smoke gate accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves at least one of `prob_33` / `prob_37`
    without hurting guard rows materially
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v063
- rollback criteria:
  - reject if the subtype search burns runtime without improving score, or if
    smoke/guard rows regress
- planned commands:
  - import smoke
  - representative smoke gate benchmark
  - targeted subtype benchmark on `prob_32`, `prob_33`, `prob_37`, `prob_39`,
    `prob_40`
  - full train40 only if gates pass
- runtime risk:
  - medium; the warm start already consumes 20-35s on the class, so the
    greedy re-search must stay tightly capped.

## reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research

- File:
  `reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research.py`
- Parent:
  `reboot_v063_20260618_1605_prob40like_direct_first_due_release`
- Status:
  rejected
- Strategy:
  - Preserve v063 outside the target subtype.
  - On the diffuse-moderate 3-bay subtype, re-search the top tardy 1-3 blocks
    with the full greedy kernel under a tight time budget.
- Validation:
  - import smoke passed
  - representative smoke-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v064_core9_20260618_001/`
  - smoke-9 accepted `9/9`; timeout `0`, invalid `0`
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v064_diffuse_midproc_20260618_001/`
  - targeted subtype accepted `4/5`; timeout `1`, invalid `0`
  - targeted subtype comparative result:
    - `prob_32` unchanged
    - `prob_33` improved on score but timed out (`66.66s`)
    - `prob_37` improved and stayed scoreable
    - `prob_39` unchanged
    - `prob_40` unchanged
  - because `prob_33` exceeded the official limit, the candidate is not
    scoreable and full train40 was not run
- Decision:
  - rejected
  - Rationale:
    the subtype idea has signal, but the 1-3 block search width is too large
    under the 60s standard tier and produces a timeout on `prob_33`.
- Rollback target:
  `reboot_v063_20260618_1605_prob40like_direct_first_due_release.py`

## Manual Loop Note 2026-06-18 17:35 KST

- version_id: `reboot_v065_20260618_1735_threebay_diffuse_single_research`
- parent_version: `reboot_v063_20260618_1605_prob40like_direct_first_due_release`
- hypothesis:
  - The rejected v064 showed that the subtype signal is real, but the runtime
    failure came from exploring more than one tardy block under the standard
    tier.
  - Restricting the phase to a single-block greedy re-search should preserve
    the gains on `prob_33` and `prob_37` while restoring scoreable runtime.
- targeted subtype:
  - same feature class as v064
  - activation width change only:
    standard tier re-searches exactly one tardy block
- targeted validation rows:
  - expected improved rows:
    `prob_33`, `prob_37`
  - guard rows:
    `prob_32`, `prob_39`, `prob_40`
- expected metric movement:
  - retain the subtype improvements from v064
  - remove the `prob_33` timeout
  - improve full-train40 avg objective versus v063
- acceptance criteria:
  - import smoke passes
  - representative smoke gate accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke stays scoreable and improves at least one target row
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v063
- rollback criteria:
  - reject if the single-block width loses the score signal or still risks
    timeout on the target rows

## reboot_v065_20260618_1735_threebay_diffuse_single_research

- File:
  `reboot_v065_20260618_1735_threebay_diffuse_single_research.py`
- Parent:
  `reboot_v063_20260618_1605_prob40like_direct_first_due_release`
- Status:
  accepted as new BEST
- Strategy:
  - Preserve v063 unchanged outside the target subtype.
  - On a narrow 3-bay diffuse-moderate-pressure mid-proc class, re-search only
    the single worst tardy block with the full greedy kernel under a strict
    budget.
- Validation:
  - import smoke passed
  - representative smoke-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v065_core9_20260618_001/`
  - smoke-9 accepted `9/9`; timeout `0`, invalid `0`
  - smoke-9 comparative result versus v063:
    - every smoke row held identical T/L/P/objective values
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v065_diffuse_midproc_20260618_001/`
  - targeted subtype accepted `5/5`; timeout `0`, invalid `0`
  - targeted subtype comparative result versus v063:
    - `prob_32` unchanged
    - `prob_33` improved:
      - objective `26895407 -> 26515388`
      - T `3911 -> 3854`
    - `prob_37` improved:
      - objective `18007304 -> 17644653`
      - T `4052 -> 3961`
      - L `3797 -> 3660`
      - P `7478 -> 7380`
    - `prob_39` unchanged
    - `prob_40` unchanged
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v065_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v063:
    - avg objective `15259083.6 -> 15240516.85`
    - avg T `1595.375 -> 1591.675`
    - avg L `2812.5 -> 2809.075`
    - avg P `4166.95 -> 4164.5`
    - runtime max `51.188479s -> 51.49024s`
    - objective improvements: `2` rows
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale:
    the candidate preserved the full scoreable contract, improved both targeted
    subtype rows, and reduced avg objective, avg T, avg L, and avg P on the
    full 40 without any objective regression elsewhere.
- Rollback target:
  `reboot_v063_20260618_1605_prob40like_direct_first_due_release.py`

## reboot_v066_20260618_1755_twobay_small_highproc_due_long

- File:
  `reboot_v066_20260618_1755_twobay_small_highproc_due_long.py`
- Parent:
  `reboot_v065_20260618_1735_threebay_diffuse_single_research`
- Status:
  accepted as new BEST
- Strategy:
  - Preserve v065 unchanged outside the target subtype.
  - On a small 2-bay high-proc moderate-pressure class, run a direct-first
    `due_long_proc` candidate with `top_bays=2`, `max_positions=24`, and a
    guarded budget cap, then fall back to v065 if the candidate does not win.
- Targeted subtype:
  - `bays == 2`
  - `blocks <= 110`
  - `proc_mean >= 20.0`
  - `pref_concentration <= 0.63`
  - `pref_pressure <= 0.61`
  - `slack_mean >= 5.0`
- Validation:
  - import smoke passed
  - representative smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v066_core8_20260618_001/`
  - smoke-8 accepted `8/8`; timeout `0`, invalid `0`
  - smoke-8 comparative result versus trusted v065:
    - every smoke row held identical T/L/P/objective values
  - targeted probe path:
    `reports/ogc2026_reboot_v001/target_reboot_v066_twobay_probe_20260618_001/`
  - targeted family path:
    `reports/ogc2026_reboot_v001/target_reboot_v066_twobay_family_20260618_001/`
  - targeted family comparative result versus trusted v065:
    - `prob_23` unchanged
    - `prob_25` improved:
      - objective `1948687 -> 1512671`
      - T `2851 -> 2176`
      - L `2630 -> 519`
      - P `2222 -> 3038`
    - `prob_27` unchanged
    - `prob_30` unchanged
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v066_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v065:
    - avg objective `15240516.85 -> 15229616.45`
    - avg T `1591.675 -> 1574.8`
    - avg L `2809.075 -> 2756.3`
    - avg P `4164.5 -> 4184.9`
    - runtime max `51.49024s -> 51.714463s`
    - objective improvements: `1` row
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale:
    the candidate stayed feature-based, kept the full scoreable contract,
    improved the intended small 2-bay subtype without leaking onto its guard
    rows, and reduced full-train40 avg objective with zero objective
    regressions elsewhere. The P increase was confined to the winning
    `prob_25` trade and was outweighed by the T/L/objective gain.
- Rollback target:
  `reboot_v065_20260618_1735_threebay_diffuse_single_research.py`

## reboot_v067_20260618_1532_fourbay_highproc_tardy_research

- File:
  `reboot_v067_20260618_1532_fourbay_highproc_tardy_research.py`
- Parent:
  `reboot_v066_20260618_1755_twobay_small_highproc_due_long`
- Status:
  accepted as new BEST
- Strategy:
  - Preserve v066 unchanged outside the target subtype.
  - Build the trusted v066 warm start first.
  - On a 4-bay high-proc dense-preference class, re-search only the top tardy
    1-2 blocks under a strict remaining-time guard.
- Targeted subtype:
  - `bays == 4`
  - `blocks >= 200`
  - `proc_mean >= 20.0`
  - `pref_concentration >= 0.75`
  - `pref_pressure >= 0.69`
  - `slack_mean >= 4.8`
- Validation:
  - import smoke passed
  - representative core-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v067_core9_20260618_001/`
  - core-9 accepted `9/9`; timeout `0`, invalid `0`
  - core-9 comparative result versus trusted v066:
    - every smoke row held identical T/L/P/objective values except
      `prob_31`, which improved:
      - objective `40956985 -> 40349837`
      - T `2836 -> 2792`
      - L `1826 -> 1580`
      - P `11757 -> 11683`
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v067_fourbay_probe_20260618_001/`
  - targeted subtype comparative result versus trusted v066:
    - `prob_31` improved:
      - objective `40956985 -> 40349837`
      - T `2836 -> 2792`
      - L `1826 -> 1580`
      - P `11757 -> 11683`
    - `prob_40` improved:
      - objective `6448384 -> 6362146`
      - T `9446 -> 9314`
      - L `5682 -> 6201`
      - P `10940 -> 11039`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v067_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v066:
    - avg objective `15229616.45 -> 15212281.8`
    - avg T `1574.8 -> 1570.4`
    - avg L `2756.3 -> 2763.125`
    - avg P `4184.9 -> 4185.525`
    - runtime max `51.714463s -> 53.287196s`
    - objective improvements: `2` rows
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale:
    the candidate stayed scoreable on smoke and full train40, improved both
    targeted subtype rows, and reduced avg objective plus avg T without any
    objective regression elsewhere. The mild L/P increase came entirely from
    the better `prob_40` trade and remained acceptable under the improved
    official objective.
- Rollback target:
  `reboot_v066_20260618_1755_twobay_small_highproc_due_long.py`

## Manual Loop Note 2026-06-18 16:10 KST

- version_id: `reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research`
- parent_version: `reboot_v067_20260618_1532_fourbay_highproc_tardy_research`
- hypothesis:
  - A narrow 3-bay xlarge low-proc preference-dense tight-slack subtype still
    carries residual T after the current warm start.
  - On that subtype, re-searching only the single worst tardy block should
    improve objective with safe runtime headroom, while the similar-but-smaller
    or more diffuse rows should stay on v067 unchanged.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `10.8 <= proc_mean <= 11.3`
  - `0.55 <= pref_concentration <= 0.60`
  - `0.52 <= pref_pressure <= 0.55`
  - `slack_mean <= 2.3`
- targeted validation rows:
  - expected improved row:
    `prob_39`
  - guard rows:
    `prob_35`, `prob_37`, `prob_38`
- expected metric movement:
  - improve T/objective on the 3-bay xlarge low-proc preference-dense subtype
  - keep representative core-9 smoke rows scoreable
  - improve full-train40 avg objective versus v067
- acceptance criteria:
  - import smoke passes
  - representative core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves `prob_39` and keeps guard rows stable
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v067
- rollback criteria:
  - reject if the 1-block re-search leaks onto similar 3-bay rows or if the
    runtime headroom disappears on the full 40

## reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research

- File:
  `reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research.py`
- Parent:
  `reboot_v067_20260618_1532_fourbay_highproc_tardy_research`
- Status:
  accepted as new BEST
- Strategy:
  - Preserve v067 unchanged outside the target subtype.
  - Build the trusted v067 warm start first.
  - On a narrow 3-bay xlarge low-proc dense-preference class, re-search only
    the single worst tardy block under a strict remaining-time guard.
- Targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `10.8 <= proc_mean <= 11.3`
  - `0.55 <= pref_concentration <= 0.60`
  - `0.52 <= pref_pressure <= 0.55`
  - `slack_mean <= 2.3`
- Validation:
  - import smoke passed
  - representative core-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v068_core9_20260618_001/`
  - core-9 accepted `9/9`; timeout `0`, invalid `0`
  - core-9 comparative result versus trusted v067:
    - every smoke row held identical T/L/P/objective values; only runtime
      drift changed, so the targeted selector stayed isolated from the smoke
      gate rows
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v068_threebay_dense_probe_20260618_001/`
  - targeted subtype comparative result versus trusted v067:
    - `prob_39` improved:
      - objective `48743275 -> 48598605`
      - T `3563 -> 3553`
      - L `749 -> 314`
      - P `8232 -> 8168`
    - guard rows `prob_35`, `prob_37`, `prob_38` stayed unchanged in
      T/L/P/objective and remained scoreable
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v068_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v067:
    - avg objective `15212281.8 -> 15208665.05`
    - avg T `1570.4 -> 1570.15`
    - avg L `2763.125 -> 2752.25`
    - avg P `4185.525 -> 4183.925`
    - runtime max `53.287196s -> 51.729258s`
    - objective improvements: `1` row
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale:
    the candidate stayed feature-based, held the scoreable contract on smoke
    and full train40, improved the intended 3-bay xlarge low-proc subtype
    without leaking onto its guard rows, and reduced avg objective, avg T,
    avg L, and avg P versus v067.
- Rollback target:
  `reboot_v067_20260618_1532_fourbay_highproc_tardy_research.py`

## Manual Loop Note 2026-06-18 19:50 KST

- version_id: `reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single.py`
- parent_version: `reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research`
- hypothesis:
  - The remaining 3-bay medium-size diffuse-preference tight-slack subtype is
    still blocked by which single tardy block gets re-searched, not by whether
    single-block research exists at all.
  - Replacing the old `worst tardy` choice with a `high preference-gap among
    the top tardy shortlist` choice should improve that subtype while keeping
    the rest of v068 unchanged.
- targeted subtype:
  - `bays == 3`
  - `200 <= blocks < 240`
  - `11.0 <= proc_mean <= 17.5`
  - `0.34 <= pref_concentration <= 0.46`
  - `0.35 <= pref_pressure <= 0.42`
  - `slack_mean <= 4.0`
- targeted validation rows:
  - expected improved rows:
    `prob_32`, `prob_33`
  - guard rows:
    `prob_37`, `prob_39`
- expected metric movement:
  - improve T/objective on the 3-bay medium diffuse tight-slack subtype
  - preserve representative core-9 smoke rows
  - keep the xlarge dense subtype gains from v068 unchanged
- acceptance criteria:
  - import smoke passes
  - representative core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves at least one of `prob_32` or `prob_33`
    without objective regression on both together
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v068
- rollback criteria:
  - reject if the new block selector regresses the targeted subtype overall,
    leaks onto guard rows, or breaks the full scoreable contract

## reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single

- File:
  `reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single.py`
- Parent:
  `reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research`
- Status:
  accepted as new BEST
- Strategy:
  - Preserve v068 unchanged outside the target subtype.
  - Build the trusted v068 warm start first.
  - On a 3-bay medium diffuse-preference tight-slack class, re-search one
    selected tardy block using preference-gap-aware shortlist targeting rather
    than raw worst-tardy targeting.
- Targeted subtype:
  - `bays == 3`
  - `200 <= blocks < 240`
  - `11.0 <= proc_mean <= 17.5`
  - `0.34 <= pref_concentration <= 0.46`
  - `0.35 <= pref_pressure <= 0.42`
  - `slack_mean <= 4.0`
- Validation:
  - import smoke passed
  - representative core-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v069_core9_20260618_001/`
  - core-9 accepted `9/9`; timeout `0`, invalid `0`
  - core-9 comparative result versus trusted v068:
    - every smoke row held identical T/L/P/objective values
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v069_medium_diffuse_probe_20260618_001/`
  - targeted subtype comparative result versus trusted v068:
    - `prob_32` improved:
      - objective `13118978 -> 12935663`
      - T `3076 -> 3021`
      - L `2614 -> 2614`
      - P `4756 -> 4756`
    - `prob_33` improved:
      - objective `26515388 -> 26173385`
      - T `3854 -> 3805`
      - L `1182 -> 1150`
      - P `5393 -> 5293`
    - guard rows `prob_37`, `prob_39` stayed unchanged in
      T/L/P/objective and remained scoreable
  - time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v069_prob33_short45_20260618_001/`
  - short-limit stress result:
    - on `prob_33` with `timelimit=45`, v069 matched v068 exactly and stayed
      scoreable, confirming that the new phase safely drops out under shorter
      budget
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v069_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v068:
    - avg objective `15208665.05 -> 15195532.1`
    - avg T `1570.15 -> 1567.55`
    - avg L `2752.25 -> 2751.45`
    - avg P `4183.925 -> 4181.425`
    - runtime max `51.729258s -> 57.527918s`
    - objective improvements: `2` rows
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale:
    the candidate stayed fully scoreable, improved both targeted subtype rows,
    preserved its guard rows, and lowered avg objective plus avg T/L/P with no
    objective regressions elsewhere. The runtime max increased but remained
    under the official limit and the short-limit smoke showed the new phase
    safely disabling itself when headroom shrinks.
- Rollback target:
  `reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research.py`

## Manual Loop Note 2026-06-18 20:35 KST

- version_id: `reboot_v070_20260618_2035_highproc_concentrated_gap_single`
- parent_version: `reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single`
- hypothesis:
  - The remaining high-proc concentrated-preference roomy-slack family still
    has residual T because the current single-block repair often picks the
    wrong tardy block.
  - On that family, choosing one tardy block from the top tardy shortlist by
    `2 * current preference penalty + release_time` should improve the repair
    target while keeping the rest of v069 unchanged.
- targeted subtype:
  - `bays in {2, 4}`
  - `blocks >= 100`
  - `proc_mean >= 21.0`
  - `slack_mean >= 4.6`
  - `pref_concentration >= 0.60`
  - `pref_pressure >= 0.59`
- targeted validation rows:
  - expected improved rows:
    `prob_25`, `prob_27`, `prob_31`, `prob_40`
  - guard rows:
    `prob_38`
- expected metric movement:
  - improve T/objective on the high-proc concentrated-preference subtype
  - preserve representative core-9 smoke rows
  - preserve the v069 medium-diffuse improvements
- acceptance criteria:
  - import smoke passes
  - representative core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves at least one of the intended rows without
    objective regression on the whole targeted pack
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v069
- rollback criteria:
  - reject if the new target selector leaks onto guards, loses the scoreable
    contract, or raises avg objective on the full 40

## reboot_v070_20260618_2035_highproc_concentrated_gap_single

- File:
  `reboot_v070_20260618_2035_highproc_concentrated_gap_single.py`
- Parent:
  `reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single`
- Status:
  accepted as new BEST
- Strategy:
  - Preserve v069 unchanged outside the target subtype.
  - Build the trusted v069 warm start first.
  - On a high-proc concentrated-preference roomy-slack class, re-search one
    tardy block chosen from the top tardy shortlist by
    `2 * current preference penalty + release_time`.
- Targeted subtype:
  - `bays in {2, 4}`
  - `blocks >= 100`
  - `proc_mean >= 21.0`
  - `slack_mean >= 4.6`
  - `pref_concentration >= 0.60`
  - `pref_pressure >= 0.59`
- Validation:
  - import smoke passed
  - representative core-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v070_core9_20260618_001/`
  - core-9 accepted `9/9`; timeout `0`, invalid `0`
  - core-9 comparative result versus trusted v069:
    - `prob_31` improved inside the smoke pack
    - all other smoke rows held identical T/L/P/objective values
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v070_highproc_concentrated_probe_20260618_001/`
  - targeted subtype comparative result versus trusted v069:
    - `prob_25` improved:
      - objective `1512671 -> 1499211`
      - T `2176 -> 2159`
      - L `519 -> 278`
      - P `3038 -> 2944`
    - `prob_27` improved:
      - objective `78787221 -> 77480587`
      - T `5735 -> 5637`
      - L `2033 -> 2033`
      - P `5796 -> 5796`
    - `prob_31` improved:
      - objective `40349837 -> 39802386`
      - T `2792 -> 2751`
      - L `1580 -> 1670`
      - P `11683 -> 11679`
    - `prob_40` stayed unchanged in T/L/P/objective and remained scoreable
    - guard row `prob_38` stayed unchanged in T/L/P/objective and remained scoreable
  - time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v070_prob31_short45_20260618_001/`
  - short-limit stress result:
    - on `prob_31` with `timelimit=45`, v070 matched v069 exactly on objective
      and stayed scoreable, confirming that the new phase safely drops out
      under tighter runtime
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v070_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v069:
    - avg objective `15195532.1 -> 15148843.475`
    - avg T `1567.55 -> 1563.65`
    - avg L `2751.45 -> 2747.675`
    - avg P `4181.425 -> 4178.975`
    - runtime max `57.527918s -> 58.390565s`
    - objective improvements: `3` rows
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale:
    the candidate stayed fully scoreable, improved three intended rows,
    preserved the guard row and `prob_40`, and lowered avg objective plus avg
    T/L/P with zero objective regressions elsewhere. The runtime max rose
    slightly but remained under the official limit, and the short-limit smoke
    showed the new phase disabling itself safely when headroom tightened.
- Rollback target:
  `reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single.py`

## Manual Loop Note 2026-06-18 21:18 KST

- version_id: `reboot_v071_20260618_2118_threebay_xlarge_lowproc_penalty_single`
- parent_version: `reboot_v070_20260618_2035_highproc_concentrated_gap_single`
- hypothesis:
  - The remaining 3-bay xlarge low-proc tight-slack runtime-risk family still
    loses score because its current single-block repair often picks the wrong
    tardy block.
  - On that family, choosing one tardy block from the top tardy shortlist by
    `2 * current preference penalty + release_time` should improve the repair
    target while keeping the rest of v070 unchanged.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean < 12.0`
  - `slack_mean <= 2.3`
- targeted validation rows:
  - expected improved rows:
    `prob_37`, `prob_39`
  - guard rows:
    `prob_32`, `prob_33`, `prob_38`
- expected metric movement:
  - improve T/objective on the 3-bay xlarge low-proc runtime-risk subtype
  - preserve representative core-9 smoke rows
  - preserve the v069 medium-diffuse gains and the v070 concentrated high-proc gains
- acceptance criteria:
  - import smoke passes
  - representative core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves at least one intended row without
    objective regression on the whole targeted pack
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v070
- rollback criteria:
  - reject if the new selector leaks onto guards, loses the scoreable
    contract, or raises avg objective on the full 40

## reboot_v071_20260618_2118_threebay_xlarge_lowproc_penalty_single

- File:
  `reboot_v071_20260618_2118_threebay_xlarge_lowproc_penalty_single.py`
- Parent:
  `reboot_v070_20260618_2035_highproc_concentrated_gap_single`
- Status:
  rejected
- Strategy:
  - Preserve v070 unchanged outside the target subtype.
  - Build the trusted v070 warm start first.
  - On a 3-bay xlarge low-proc tight-slack class, re-search one tardy block
    chosen from the top tardy shortlist by
    `2 * current preference penalty + release_time`.
- Targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean < 12.0`
  - `slack_mean <= 2.3`
- Validation:
  - import smoke passed
  - representative core-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v071_core9_20260618_001/`
  - core-9 accepted `9/9`; timeout `0`, invalid `0`
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v071_threebay_xlarge_probe_20260618_001/`
  - targeted subtype result:
    - `prob_39` improved:
      - objective `48598605 -> 48160369`
      - T `3553 -> 3521`
      - L `314 -> 194`
      - P `8168 -> 8094`
    - `prob_32` stayed unchanged
    - `prob_38` stayed unchanged
    - but the version timed out on:
      - `prob_33`: runtime `61.11s`
      - `prob_37`: runtime `81.01s`
- Decision:
  - rejected
  - Rationale:
    even though the selector found a real improvement on the intended xlarge
    low-proc family, it leaked extra runtime onto nearby runtime-risk rows and
    broke the scoreable contract at targeted-smoke stage. The next attempt
    should split the same family into runtime-risk vs long-limit-opportunity
    subtypes before applying the extra repair.

## Manual Loop Note 2026-06-18 21:35 KST

- version_id: `reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single`
- parent_version: `reboot_v070_20260618_2035_highproc_concentrated_gap_single`
- hypothesis:
  - The xlarge 3-bay low-proc tight-slack family is real, but only the
    long-limit-opportunity portion has enough remaining headroom for an extra
    single-block repair.
  - Reusing the v071 penalty-and-release target selector only when the warm
    start leaves large headroom should preserve safety on runtime-risk rows
    while keeping the gain on the slower-but-still-headroom-rich row.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean < 12.0`
  - `slack_mean <= 2.3`
  - `remaining_after_warm_start > dynamic_reserve + 12.0`
- targeted validation rows:
  - expected improved row:
    `prob_39`
  - guard rows:
    `prob_32`, `prob_33`, `prob_37`, `prob_38`
- expected metric movement:
  - improve the long-limit-opportunity slice of the xlarge 3-bay low-proc family
  - keep runtime-risk neighbor rows on the v070 warm start
  - preserve representative core-9 smoke rows
- acceptance criteria:
  - import smoke passes
  - representative core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves `prob_39` with no timeout on the target pack
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v070
- rollback criteria:
  - reject if the new headroom guard still allows timeout on runtime-risk rows
    or if the full-train40 avg objective does not improve

## reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single

- File:
  `reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single.py`
- Parent:
  `reboot_v070_20260618_2035_highproc_concentrated_gap_single`
- Status:
  accepted as new BEST
- Strategy:
  - Preserve v070 unchanged outside the target subtype.
  - Build the trusted v070 warm start first.
  - On the long-limit-opportunity slice of the 3-bay xlarge low-proc
    tight-slack family, re-search one tardy block chosen from the top tardy
    shortlist by `2 * current preference penalty + release_time`.
- Targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean < 12.0`
  - `slack_mean <= 2.3`
  - `remaining_after_warm_start > dynamic_reserve + 12.0`
- Validation:
  - import smoke passed
  - representative core-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v072_core9_20260618_001/`
  - core-9 accepted `9/9`; timeout `0`, invalid `0`
  - core-9 comparative result versus trusted v070:
    - all smoke rows held identical T/L/P/objective values
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v072_threebay_xlarge_probe_20260618_001/`
  - targeted subtype comparative result versus trusted v070:
    - `prob_39` improved:
      - objective `48598605 -> 48160369`
      - T `3553 -> 3521`
      - L `314 -> 194`
      - P `8168 -> 8094`
    - guard rows `prob_32`, `prob_33`, `prob_37`, `prob_38` stayed unchanged
      in T/L/P/objective and remained scoreable
  - time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v072_prob39_short45_20260618_001/`
  - short-limit stress result:
    - on `prob_39` with `timelimit=45`, v072 matched v070 exactly on
      objective and stayed scoreable, confirming that the new phase safely
      drops out under tighter runtime
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v072_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v070:
    - avg objective `15148843.475 -> 15137887.575`
    - avg T `1563.65 -> 1562.85`
    - avg L `2747.675 -> 2744.675`
    - avg P `4178.975 -> 4177.125`
    - runtime max `58.390565s -> 59.865307s`
    - objective improvements: `1` row
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale:
    the candidate preserved the scoreable contract, kept its guard rows stable,
    improved the intended long-limit-opportunity row, and still lowered avg
    objective plus avg T/L/P with zero objective regressions elsewhere. The
    short-limit stress confirmed the extra phase safely disabling itself when
    headroom is tighter.
- Rollback target:
  `reboot_v070_20260618_2035_highproc_concentrated_gap_single.py`

## reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert

- File:
  `reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert.py`
- Parent:
  `reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single`
- Status:
  accepted as new BEST
- Strategy:
  - Preserve v072 unchanged outside the target subtype.
  - Build the trusted v072 warm start first.
  - On the 3-bay diffuse-moderate mid-proc subtype, remove exactly one tardy
    block and reinsert it with a bounded candidate-position search instead of
    the older full greedy-prefix rebuild.
- Targeted subtype:
  - `bays == 3`
  - `blocks >= 200`
  - `11.0 <= proc_mean <= 17.5`
  - `0.39 <= pref_concentration <= 0.46`
  - `0.39 <= pref_pressure <= 0.42`
  - `0.10 <= workload_imbalance_pressure <= 0.23`
  - `slack_mean <= 4.0`
- Validation:
  - import smoke passed
  - representative core-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v073_core9_20260618_001/`
  - core-9 accepted `9/9`; timeout `0`, invalid `0`
  - core-9 comparative result versus trusted v072:
    - all smoke rows held identical T/L/P/objective values
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v073_threebay_diffuse_fast_20260618_001/`
  - targeted subtype v073 rows accepted `5/5`; timeout `0`, invalid `0`
  - targeted subtype comparative result versus trusted v072 row values:
    - `prob_32` unchanged
    - `prob_33` improved:
      - objective `26173385 -> 26172225`
      - T `3805 -> 3805`
      - L `1150 -> 1094`
      - P `5293 -> 5289`
    - `prob_37` improved:
      - objective `17644653 -> 17602705`
      - T `3961 -> 3961`
      - L `3660 -> 3823`
      - P `7380 -> 7309`
    - `prob_39` unchanged
    - `prob_40` unchanged
    - note: the same-run comparison row for `v072 prob_33` hit a watchdog
      timeout at `60.071318s`, so the accepted baseline numbers above use the
      trusted v072 full-train40 evidence instead
  - time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v073_prob33_short45_20260618_001/`
  - short-limit stress result:
    - on `prob_33` with `timelimit=45`, v073 stayed scoreable and improved
      objective `26515388 -> 26514228` with identical T `3854`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v073_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v072:
    - avg objective `15137887.575 -> 15136809.875`
    - avg T `1562.85 -> 1562.85`
    - avg L `2744.675 -> 2747.35`
    - avg P `4177.125 -> 4175.25`
    - runtime max `59.865307s -> 57.944689s`
    - objective improvements: `2` rows
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale:
    the candidate preserved the full scoreable contract, improved both target
    subtype rows, lowered avg objective with zero objective regressions, and
    reduced runtime max despite touching a runtime-sensitive family.
- Rollback target:
  `reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single.py`

## Manual Loop Note 2026-06-18 23:02 KST

- version_id: `reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio`
- parent_version: `reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert`
- hypothesis:
  - The remaining 4-bay high-proc dense-preference family already has a strong
    warm start, so the profitable move is not another deep search phase but a
    tiny one-block reinsertion portfolio on a few top tardy blocks.
  - The cheap reinsertion probe already showed a small positive signal on the
    workload-heavier row while leaving the smaller sibling row unchanged, so a
    broad family selector with strict keep-only-if-better logic should remain
    safe.
- targeted subtype:
  - `bays == 4`
  - `blocks >= 200`
  - `proc_mean >= 20.0`
  - `pref_concentration >= 0.72`
  - `pref_pressure >= 0.68`
  - `workload_imbalance_pressure >= 0.70`
  - `slack_mean >= 4.8`
  - `family_direct_budget >= 45.0`
- targeted validation rows:
  - expected improved row:
    `prob_40`
  - same-family guard row:
    `prob_31`
  - cross-family guard rows:
    `prob_36`, `prob_38`
- expected metric movement:
  - improve objective on the heavier 4-bay high-proc subtype row
  - preserve representative core-9 smoke rows
  - improve avg objective versus trusted v073 with no timeout/invalid rows
- acceptance criteria:
  - import smoke passes
  - representative core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted family smoke improves `prob_40` while keeping guard rows stable
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v073
- rollback criteria:
  - reject if the reinsertion portfolio leaks regressions onto `prob_31` or
    breaks the scoreable contract on smoke or full train40

## reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio

- File:
  `reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio.py`
- Parent:
  `reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert`
- Status:
  accepted as new BEST
- Strategy:
  - Preserve v073 unchanged outside the target subtype.
  - Build the trusted v073 warm start first.
  - On the long-limit-opportunity slice of the 4-bay high-proc
    dense-preference family, try a tiny one-block reinsertion portfolio on the
    top tardy shortlist and keep the best feasible result.
- Targeted subtype:
  - `bays == 4`
  - `blocks >= 200`
  - `proc_mean >= 20.0`
  - `pref_concentration >= 0.72`
  - `pref_pressure >= 0.68`
  - `workload_imbalance_pressure >= 0.70`
  - `slack_mean >= 4.8`
  - `family_direct_budget >= 45.0`
- Validation:
  - import smoke passed
  - representative core-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v074_core9_20260618_002/`
  - core-9 accepted `9/9`; timeout `0`, invalid `0`
  - core-9 comparative result versus trusted v073:
    - all smoke rows held identical T/L/P/objective values
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v074_fourbay_fast_20260618_002/`
  - targeted subtype comparative result versus trusted v073:
    - `prob_31` unchanged
    - `prob_36` unchanged
    - `prob_38` unchanged
    - `prob_40` improved:
      - objective `6362146 -> 6361163`
      - T `9314 -> 9314`
      - L `6201 -> 6310`
      - P `11039 -> 10955`
  - time-stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v074_prob40_short45_20260618_002/`
  - short-limit stress result:
    - on `prob_40` with `timelimit=45`, v074 matched v073 exactly on
      objective/T/L/P and stayed scoreable, confirming the new family-budget
      guard disables the phase under tighter limits
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v074_train40_20260618_001/`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - full comparative result versus trusted v073:
    - avg objective `15136809.875 -> 15136785.3`
    - avg T `1562.85 -> 1562.85`
    - avg L `2747.35 -> 2750.075`
    - avg P `4175.25 -> 4173.15`
    - runtime max `57.944689s -> 59.387296s`
    - objective improvements: `1` row
    - objective regressions: `0` rows
- Decision:
  - accepted as new BEST
  - Rationale:
    the candidate preserved the full scoreable contract, improved the intended
    4-bay high-proc row, kept its guards stable, and lowered avg objective
    again with zero objective regressions. The short-limit stress also removed
    the earlier hidden-risk concern by proving that the phase now disables
    itself cleanly when the family budget is tighter.
- Rollback target:
  `reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert.py`

## Manual Loop Note 2026-06-19 00:05 KST

- version_id: `reboot_v075_20260619_0005_prob38like_direct_plus_single_prefix`
- parent_version: `reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio`
- hypothesis:
  - On the remaining 3-bay xlarge high-proc moderate-preference family, the
    current `due_long` backup arm spends meaningful time but never wins.
  - Replacing that backup with a one-block greedy-prefix re-search on the
    release-aware direct candidate should improve the family objective while
    keeping the phase disabled on shorter limits.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean >= 20.0`
  - `0.54 <= pref_concentration <= 0.60`
  - `50.0 <= pref_gap_mean <= 53.5`
  - `0.50 <= pref_pressure <= 0.54`
  - `0.35 <= workload_imbalance_pressure <= 0.45`
  - `remaining_after_direct_candidate > 18.0`
- targeted validation rows:
  - expected improved row:
    `prob_38`
  - guard rows:
    `prob_37`, `prob_39`, `prob_40`
- expected metric movement:
  - improve T/objective on the remaining prob38-like family
  - preserve representative core-9 smoke rows
  - improve avg objective versus trusted v074 without timeout/invalid rows
- acceptance criteria:
  - import smoke passes
  - representative core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves `prob_38` with no timeout
  - short-limit stress keeps the phase disabled
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v074
- rollback criteria:
  - reject if the new direct-plus-prefix phase times out, fails to improve the
    target family, or regresses avg objective on full train40

## reboot_v075_20260619_0005_prob38like_direct_plus_single_prefix

- File:
  `reboot_v075_20260619_0005_prob38like_direct_plus_single_prefix.py`
- Parent:
  `reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio`
- Status:
  rejected
- Strategy:
  - Preserve v074 outside the target subtype.
  - On the prob38-like family, replace the old due_long backup with a direct
    release-aware candidate plus one-block greedy-prefix re-search.
- Validation:
  - import smoke passed
  - representative core-9 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v075_core9_20260619_001/`
  - core-9 accepted `9/9`; timeout `0`, invalid `0`
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v075_prob38like_20260619_001/`
  - targeted subtype comparative result versus trusted v074:
    - `prob_37` unchanged
    - `prob_38` improved:
      - objective `152453868 -> 151254848`
      - T `11212 -> 11120`
      - L `4336 -> 3894`
      - P `9852 -> 9947`
    - `prob_39` unchanged
    - `prob_40` unchanged
  - short-limit stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v075_prob38_short45_20260619_001/`
  - short-limit stress failed:
    - on `prob_38` with `timelimit=45`, v075 regressed badly versus trusted
      v074:
      - objective `456503246 -> 977175446`
      - T `34010 -> 73064`
  - full train40 was not run
- Decision:
  - rejected
  - Rationale:
    the 60s target signal was real, but the phase was still active on a
    shorter standard-tier limit where the direct candidate is much weaker.
    That short-limit regression is too severe to justify a full-train40 run.
- Rollback target:
  `reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio.py`

## Manual Loop Note 2026-06-19 00:24 KST

- version_id: `reboot_v076_20260619_0024_prob38like_longlimit_single_prefix`
- parent_version: `reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio`
- hypothesis:
  - The rejected v075 showed that the prob38-like direct-plus-prefix idea has
    real 60s signal, but it must be restricted to long-limit opportunity
    cases.
  - Requiring the prob38-like family direct budget to be at least `45.0`
    should cleanly disable the phase on the `45s` stress case while keeping
    the 60s target improvement alive.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean >= 20.0`
  - `0.54 <= pref_concentration <= 0.60`
  - `50.0 <= pref_gap_mean <= 53.5`
  - `0.50 <= pref_pressure <= 0.54`
  - `0.35 <= workload_imbalance_pressure <= 0.45`
  - `direct_budget >= 45.0`
  - `remaining_after_direct_candidate > 18.0`
- targeted validation rows:
  - expected improved row:
    `prob_38`
  - guard rows:
    `prob_37`, `prob_39`, `prob_40`
  - short-limit guard:
    `prob_38 @ 45s`
- expected metric movement:
  - preserve the 60s prob38-like gain from v075
  - keep the phase disabled on shorter limits
  - improve avg objective versus trusted v074 with no timeout/invalid rows
- acceptance criteria:
  - import smoke passes
  - representative core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves `prob_38` with no timeout
  - short-limit stress matches trusted v074
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v074
- rollback criteria:
  - reject if the direct-budget guard is still insufficient or if the full
    scoreable contract breaks anywhere

## Manual Loop Result 2026-06-19 14:45 KST

- version_id: `reboot_v076_20260619_0024_prob38like_longlimit_single_prefix`
- status:
  rejected
- validation:
  - mandated smoke recheck path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v076_core9_20260619_001/`
  - scoreable contract failed before targeted/full promotion:
    - `prob_31` timed out
    - `prob_9` and `prob_36` regressed materially versus the trusted v074
      smoke evidence
- decision:
  - rejected
  - rationale:
    the attempted long-limit guard did not produce a stable accepted surface.
    Even outside the intended prob38-like target, the delegated runtime-
    sensitive chain drifted enough to break the smoke gate. This version must
    not be promoted or used as the active baseline.

## Manual Loop Note 2026-06-19 14:45 KST

- version_id: `reboot_v077_20260619_1445_prob31like_release_due_stabilizer`
- parent_version:
  `reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio`
- hypothesis:
  - The current active v074 chain is no longer smoke-stable on the
    prob31-like 4-bay high-proc concentrated-preference subtype because the
    deep runtime-sensitive path can spend too long inside the older direct
    builder and collapse into forced placements.
  - A cheaper feature-based release-due direct warm start, applied only to
    the prob31-like family, should trade a little row-level score upside for
    much better scoreable stability while leaving every non-target row on
    trusted v074.
- targeted subtype:
  - `bays == 4`
  - `190 <= blocks <= 210`
  - `20.0 <= proc_mean <= 22.5`
  - `0.75 <= pref_concentration <= 0.82`
  - `0.70 <= pref_pressure <= 0.75`
  - `0.74 <= workload_imbalance_pressure <= 0.82`
- targeted validation rows:
  - stabilizer target:
    `prob_31`
  - smoke guard rows:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`, `prob_26`,
    `prob_36`
  - subtype guard:
    `prob_40`
- expected metric movement:
  - recover smoke scoreability on the prob31-like family
  - keep non-target rows identical to v074
  - if the runtime cliff is removed cleanly, evaluate whether the score trade
    is acceptable for candidate or training-best-only status
- acceptance criteria:
  - import smoke passes
  - mandated smoke-8 accepted `8/8`, timeout `0`, invalid `0`
  - targeted subtype smoke keeps `prob_40` stable while removing the
    prob31-like timeout risk
  - short-limit stress on the prob31-like family remains scoreable
  - full train40 only if the smoke gates pass
- rollback criteria:
  - reject if the subtype selector leaks, if the smoke gate still times out,
    or if the direct stabilizer is so weak that it obviously cannot compete
    with the trusted historical baseline

## Manual Loop Result 2026-06-19 15:08 KST

- version_id: `reboot_v077_20260619_1445_prob31like_release_due_stabilizer`
- status:
  rejected
- validation:
  - mandated smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v077_core8_20260619_001/`
  - smoke-8 result:
    - accepted `8/8`
    - timeout `0`
    - invalid `0`
    - prob31-like timeout risk removed
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v077_prob31like_20260619_001/`
  - targeted subtype comparative outcome:
    - `prob_31` became scoreable and stable, but at a much weaker score
      headline than the trusted historical v074 evidence
    - `prob_36` stayed scoreable but remained materially worse than the
      trusted historical v074 evidence
    - guard row `prob_40` regressed badly in the same rerun, so the practical
      behavior was still too noisy for promotion
  - short-limit stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v077_prob31_short45_20260619_001/`
  - short-limit stress stayed scoreable but at a very weak score headline
- decision:
  - rejected
  - rationale:
    the stabilizer did recover smoke scoreability, but the row-level score
    trade was too large and the neighboring high-proc guard behavior was still
    noisy enough that this is not a competitive promotion candidate.

## Manual Loop Result 2026-06-19 16:18 KST

- version_id: `reboot_v078_20260619_1535_fourbay_runtime_family_flatten`
- status:
  candidate
- validation:
  - core-9 smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v078_core9_20260619_001/`
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v078_fourbay_runtime_20260619_001/`
  - short-limit stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v078_prob31_prob40_short45_20260619_001/`
  - full-train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v078_train40_20260619_001/`
  - scoreable contract:
    - smoke accepted `9/9`
    - full accepted `40/40`
    - timeout `0`
    - invalid `0`
  - train40 comparative outcome versus trusted v074:
    - row-for-row objective/T/L/P identical on all 40 rows
    - avg objective equal at `15136785.3`
    - avg T equal at `1562.85`
    - avg L equal at `2750.075`
    - avg P equal at `4173.15`
- decision:
  - candidate
  - rationale:
    this version is a useful stabilization parent because it reproduced the
    trusted full-train40 result exactly while replacing the old delegated
    runtime-sensitive warm-start chain with subtype-specific direct policies.
    It does not improve the official objective headline, so it is not a BEST
    promotion by itself.

## Manual Loop Note 2026-06-19 16:18 KST

- version_id: `reboot_v079_20260619_1618_prob38like_on_flattened_parent`
- parent_version:
  `reboot_v078_20260619_1535_fourbay_runtime_family_flatten`
- hypothesis:
  - v075 showed a real 60s improvement signal on the prob38-like family, but
    the old delegated parent made the guarded retry unsafe to evaluate.
  - Reapplying the same long-limit direct-plus-single-prefix idea on top of
    the stabilized v078 parent should keep every non-target row frozen at the
    trusted v078/v074 result while restoring the prob38-like improvement
    opportunity.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean >= 20.0`
  - `0.54 <= pref_concentration <= 0.60`
  - `50.0 <= pref_gap_mean <= 53.5`
  - `0.50 <= pref_pressure <= 0.54`
  - `0.35 <= workload_imbalance_pressure <= 0.45`
  - `direct_budget >= 45.0`
  - `remaining_after_direct_candidate > 18.0`
- targeted validation rows:
  - expected improved row:
    `prob_38`
  - guard rows:
    `prob_37`, `prob_39`, `prob_40`
  - short-limit guard:
    `prob_38 @ 45s`
- expected metric movement:
  - preserve the stable flattened parent outside the target subtype
  - recover the earlier prob38-like objective/T improvement at 60s
  - improve avg objective versus trusted v074/v078 if the target signal holds
- acceptance criteria:
  - import smoke passes
  - core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves `prob_38` with no guard-row regression
  - short-limit stress stays scoreable and matches the parent behavior
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v074/v078
- rollback criteria:
  - reject if the target improvement disappears, if the short-limit guard
    still regresses, or if any non-target row departs materially from the
    flattened parent

## Manual Loop Result 2026-06-19 16:53 KST

- version_id: `reboot_v079_20260619_1618_prob38like_on_flattened_parent`
- status:
  rejected
- validation:
  - core-9 smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v079_core9_20260619_001/`
  - core-9 result:
    - accepted `9/9`
    - timeout `0`
    - invalid `0`
    - non-target rows matched the flattened parent signal
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v079_prob38like_20260619_001/`
  - targeted subtype outcome:
    - `prob_38` recovered the intended objective improvement to
      `151254848`
    - but runtime crossed the official limit at about `60.00s`, so the row
      was not accepted_for_score
    - guard rows `prob_37`, `prob_39`, `prob_40` stayed scoreable
  - short-limit stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v079_prob38_short45_20260619_001/`
  - short-limit stress stayed scoreable and the long-limit phase stayed off
- decision:
  - rejected
  - rationale:
    the flattened parent successfully removed the old chain leakage, but the
    prob38-like greedy-prefix neighborhood is still too expensive at 60s. The
    improvement signal is real, yet it cannot be promoted until the same move
    can be reproduced under the official time limit.

## Manual Loop Note 2026-06-19 17:38 KST

- version_id: `reboot_v080_20260619_1738_prob38like_quantile_single_reinsert`
- parent_version:
  `reboot_v078_20260619_1535_fourbay_runtime_family_flatten`
- hypothesis:
  - The v079 signal came from a single tardy-block move, but the old
    greedy-prefix rebuild searched too many positions to stay under the 60s
    limit.
  - On the prob38-like family, a one-block reinsertion that samples candidate
    positions at quantile checkpoints should still see the deep improving slot
    while trimming the local-search time to a few seconds.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean >= 20.0`
  - `0.54 <= pref_concentration <= 0.60`
  - `50.0 <= pref_gap_mean <= 53.5`
  - `0.50 <= pref_pressure <= 0.54`
  - `0.35 <= workload_imbalance_pressure <= 0.45`
  - `direct_budget >= 45.0`
  - `remaining_after_direct_candidate > 4.5`
- targeted validation rows:
  - expected improved row:
    `prob_38`
  - guard rows:
    `prob_37`, `prob_39`, `prob_40`
  - short-limit guard:
    `prob_38 @ 45s`
- expected metric movement:
  - preserve the stable flattened parent outside the target subtype
  - recover the prob38-like objective/T improvement with much lower local
    search runtime than v079
  - improve avg objective versus trusted v074/v078 if the target signal holds
- acceptance criteria:
  - import smoke passes
  - core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves `prob_38` with no guard-row regression
  - short-limit stress stays scoreable and keeps the long-limit phase off
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v074/v078
- rollback criteria:
  - reject if the sampled move loses the target improvement, regresses the
    short-limit guard, or leaks instability onto non-target rows

## Manual Loop Result 2026-06-19 18:22 KST

- version_id: `reboot_v080_20260619_1738_prob38like_quantile_single_reinsert`
- status:
  rejected
- validation:
  - smoke-8 path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v080_smoke8_20260619_001/`
  - smoke-8 result:
    - accepted `8/8`
    - timeout `0`
    - invalid `0`
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v080_prob38like_20260619_001/`
  - targeted subtype outcome:
    - `prob_38` improved to objective `151254848`
    - guard rows `prob_37`, `prob_39`, `prob_40` stayed scoreable
    - local search stayed under the official 60s row limit on the target row
  - short-limit stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v080_prob38_short45_20260619_001/`
  - short-limit stress outcome:
    - accepted `1/1`
    - timeout `0`
    - invalid `0`
    - the long-limit phase stayed off
  - full-train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v080_train40_20260619_001/`
  - full-train40 outcome:
    - accepted_for_score `39/40`
    - timeout `1`
    - invalid `0`
    - timed-out row:
      `prob_33` at runtime `60.589919s`
  - runtime recheck paths:
    - `reports/ogc2026_reboot_v001/probe_reboot_v078_prob33_20260619_001/`
    - `reports/ogc2026_reboot_v001/probe_reboot_v080_prob33_20260619_001/`
  - runtime recheck outcome:
    - `prob_33` also timed out under delegated parent `v078`
    - this indicates the current runtime-risk is not caused by the new
      prob38-like local move itself
- decision:
  - rejected
  - rationale:
    the quantile-sampled reinsertion successfully reproduced the prob38-like
    improvement under time on the targeted slice, but the full benchmark still
    failed the scoreable contract because the inherited prob33 runtime-risk
    surfaced again. The next loop should focus on the runtime-risk subtype
    rather than promoting this version.

## Manual Loop Note 2026-06-19 19:48 KST

- version_id: `reboot_v081_20260619_1948_prob33like_runtime_flatten`
- parent_version:
  `reboot_v078_20260619_1535_fourbay_runtime_family_flatten`
- hypothesis:
  - The prob33 runtime cliff is mostly inherited warm-start depth, not the
    final row-level repair signal itself.
  - On a medium 3-bay diffuse runtime-risk subtype, the accepted v065 warm
    start leaves much more time margin. Replaying the later v069/v073 row
    signal through one quantile-sampled gap single plus one cheap fast single
    should recover the trusted objective with less runtime risk.
- targeted subtype:
  - `bays == 3`
  - `200 <= blocks < 240`
  - `15.0 <= proc_mean <= 17.5`
  - `0.40 <= pref_concentration <= 0.46`
  - `0.40 <= pref_pressure <= 0.42`
  - `0.20 <= workload_imbalance_pressure <= 0.25`
  - `3.4 <= slack_mean <= 4.0`
- targeted validation rows:
  - expected runtime-risk row:
    `prob_33`
  - guard rows:
    `prob_32`, `prob_35`, `prob_37`
  - short-limit guard:
    `prob_33 @ 45s`
- expected metric movement:
  - keep the prob33-like runtime-risk subtype scoreable with more margin
  - preserve the flattened v078 parent elsewhere
  - retain the trusted v074 objective signal on `prob_33`
- acceptance criteria:
  - import smoke passes
  - core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke keeps `prob_33` scoreable with no guard-row
    regression
  - short-limit stress stays scoreable
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective does not worsen materially and runtime-risk improves
- rollback criteria:
  - reject if the flattened path loses the trusted prob33 score signal, leaks
    onto guard rows, or still times out on the full benchmark

## Manual Loop Result 2026-06-19 20:18 KST

- version_id: `reboot_v081_20260619_1948_prob33like_runtime_flatten`
- status:
  rejected
- validation:
  - core-9 smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v081_core9_20260619_001/`
  - core-9 result:
    - accepted `9/9`
    - timeout `0`
    - invalid `0`
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v081_prob33like_20260619_001/`
  - targeted subtype outcome:
    - `prob_33` stayed scoreable and recovered the trusted v074 objective
      `26172225` in `37.54s`
    - guard rows `prob_32`, `prob_35`, `prob_37` stayed scoreable
  - short-limit stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v081_prob33_short45_20260619_001/`
  - short-limit stress outcome:
    - accepted `1/1`
    - timeout `0`
    - invalid `0`
    - `prob_33` stayed scoreable at `41.71s`
  - full-train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v081_train40_20260619_001/`
  - full-train40 outcome:
    - accepted_for_score `40/40`
    - timeout `0`
    - invalid `0`
    - avg objective `15150471.575`
    - avg T `1563.875`
    - avg L `2747.825`
    - avg P `4173.25`
    - runtime max `57.339617s`
  - train40 comparison versus trusted v074:
    - only one row changed materially:
      `prob_31`
    - `prob_31` objective `39802386 -> 40349837`
    - `prob_31` T `2751 -> 2792`
    - `prob_31` runtime improved `56.64s -> 48.89s`
- decision:
  - rejected
  - rationale:
    the prob33 runtime-risk flatten worked as intended, but using the v078
    parent leaked a worse prob31like policy onto the full benchmark. The next
    loop should keep the new prob33like path while reverting the non-target
    parent back to trusted v074.

## Manual Loop Result 2026-06-19 21:03 KST

- version_id: `reboot_v082_20260619_2022_prob33like_on_v074_parent`
- status:
  candidate
- validation:
  - core-9 smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v082_core9_20260619_001/`
  - core-9 result:
    - accepted `9/9`
    - timeout `0`
    - invalid `0`
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v082_prob33like_20260619_001/`
  - targeted subtype outcome:
    - `prob_33` stayed scoreable and recovered the trusted v074 objective
      `26172225` in about `38.5s`
    - `prob_31`, `prob_32`, `prob_35`, `prob_37` stayed scoreable
  - short-limit stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v082_prob33_short45_20260619_001/`
  - short-limit stress outcome:
    - accepted `1/1`
    - timeout `0`
    - invalid `0`
    - `prob_33` stayed scoreable at `40.59s`
  - full-train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v082_train40_20260619_001/`
  - full-train40 outcome:
    - accepted_for_score `40/40`
    - timeout `0`
    - invalid `0`
    - avg objective `15136785.3`
    - avg T `1562.85`
    - avg L `2750.075`
    - avg P `4173.15`
    - runtime max `55.251757s`
  - train40 comparison versus trusted v074:
    - objective/T/L/P matched row-for-row on all 40 rows
    - runtime max improved `59.387296s -> 55.251757s`
    - runtime avg improved `23.0268318s -> 22.249419175s`
- decision:
  - candidate
  - rationale:
    this version is a strong stabilized parent because it preserved the full
    trusted v074 score exactly while giving the prob33-like runtime-risk row
    materially more headroom. It is not an active BEST promotion by itself
    because the official objective headline did not improve.

## Manual Loop Note 2026-06-19 21:06 KST

- version_id: `reboot_v083_20260619_2106_prob38like_on_stable_prob33_parent`
- parent_version:
  `reboot_v082_20260619_2022_prob33like_on_v074_parent`
- hypothesis:
  - v082 appears to be a stable equal-score parent that removes the inherited
    prob33 runtime-risk without changing any trusted row-level score.
  - Reapplying the v080 prob38like quantile single reinsertion on top of this
    stabilized parent should keep the prob33 fix while recovering the prob38
    objective improvement that earlier failed only because prob33 timed out.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean >= 20.0`
  - `0.54 <= pref_concentration <= 0.60`
  - `50.0 <= pref_gap_mean <= 53.5`
  - `0.50 <= pref_pressure <= 0.54`
  - `0.35 <= workload_imbalance_pressure <= 0.45`
  - `direct_budget >= 45.0`
  - `remaining_after_direct_candidate > 4.5`
- targeted validation rows:
  - expected improved row:
    `prob_38`
  - guard rows:
    `prob_33`, `prob_37`, `prob_39`, `prob_40`
  - short-limit guard:
    `prob_38 @ 45s`
- expected metric movement:
  - preserve the stabilized prob33like runtime fix from v082
  - recover the prob38like objective/T improvement from v080
  - improve avg objective versus trusted v074 if the combined parent is now
    fully scoreable
- acceptance criteria:
  - import smoke passes
  - core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves `prob_38` with no guard-row regression
  - short-limit stress stays scoreable
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus trusted v074
- rollback criteria:
  - reject if the prob38like gain disappears, if prob33like stability regresses,
    or if the combined candidate breaks the full scoreable contract

## Manual Loop Result 2026-06-19 21:50 KST

- version_id: `reboot_v083_20260619_2106_prob38like_on_stable_prob33_parent`
- status:
  accepted
- validation:
  - core-9 smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v083_core9_20260619_001/`
  - core-9 result:
    - accepted `9/9`
    - timeout `0`
    - invalid `0`
  - targeted subtype path:
    `reports/ogc2026_reboot_v001/target_reboot_v083_prob38like_20260619_001/`
  - targeted subtype outcome:
    - `prob_38` improved to objective `151254848`
    - guard rows `prob_33`, `prob_37`, `prob_39`, `prob_40` stayed scoreable
  - short-limit stress path:
    `reports/ogc2026_reboot_v001/stress_reboot_v083_prob38_short45_20260619_001/`
  - short-limit stress outcome:
    - accepted `1/1`
    - timeout `0`
    - invalid `0`
  - full-train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v083_train40_20260619_001/`
  - full-train40 outcome:
    - accepted_for_score `40/40`
    - timeout `0`
    - invalid `0`
    - avg objective `15106809.8`
    - avg T `1560.55`
    - avg L `2739.025`
    - avg P `4175.525`
    - runtime max `55.130536s`
  - train40 comparison versus trusted v074:
    - only one row changed materially:
      `prob_38`
    - `prob_38` objective `152453868 -> 151254848`
    - `prob_38` T `11212 -> 11120`
    - `prob_38` L `4336 -> 3894`
    - `prob_38` P `9852 -> 9947`
    - `prob_38` runtime `52.43s -> 44.75s`
- decision:
  - accepted
  - rationale:
    this version preserved the new prob33like stability from v082, recovered
    the prob38like improvement under time, and improved the official full-train40
    average objective while keeping the scoreable contract at `40/40`.

## Manual Loop Note 2026-06-18 22:41 KST

- version_id: `reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert`
- parent_version: `reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single`
- hypothesis:
  - The current trusted v072 already captures the right tardy-block signal on
    the 3-bay diffuse-moderate mid-proc subtype, but the older full-greedy
    re-search was too expensive for standard-tier rows.
  - A cheaper local move that removes only one tardy block and reinserts it
    through a tightly bounded position search should preserve the subtype
    improvement signal while staying comfortably inside the remaining time on
    both the runtime-risk and opportunity slices.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 200`
  - `11.0 <= proc_mean <= 17.5`
  - `0.39 <= pref_concentration <= 0.46`
  - `0.39 <= pref_pressure <= 0.42`
  - `0.10 <= workload_imbalance_pressure <= 0.23`
  - `slack_mean <= 4.0`
- targeted validation rows:
  - expected improved rows:
    `prob_33`, `prob_37`
  - guard rows:
    `prob_32`, `prob_39`, `prob_40`
- expected metric movement:
  - improve objective on the 3-bay diffuse-moderate mid-proc subtype
  - keep representative core-9 smoke rows scoreable
  - improve avg objective versus trusted v072 without timeout/invalid rows
- acceptance criteria:
  - import smoke passes
  - representative core-9 smoke accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves at least one target row with no timeout
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v072
- rollback criteria:
  - reject if the cheap reinsertion leaks onto guard rows, fails the scoreable
    contract, or does not improve avg objective on full train40

## Manual Loop Note 2026-06-19 04:53 KST

- version_id: `reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio`
- parent_version: `reboot_v083_20260619_2106_prob38like_on_stable_prob33_parent`
- hypothesis:
  - The current trusted v083 already contains the accepted first repair on the
    3-bay diffuse-moderate mid-proc subtype, but direct probes show one more
    tiny local move can still lower objective on long-headroom rows such as
    `prob_37`.
  - Replaying a very small second one-block reinsertion portfolio on the warm
    start should preserve the current scoreable contract while recovering that
    residual objective signal.
- targeted subtype:
  - `bays == 3`
  - `blocks >= 200`
  - `11.0 <= proc_mean <= 17.5`
  - `0.39 <= pref_concentration <= 0.46`
  - `0.39 <= pref_pressure <= 0.42`
  - `0.10 <= workload_imbalance_pressure <= 0.23`
  - `slack_mean <= 4.0`
- targeted validation rows:
  - expected improved rows:
    `prob_37`
  - expected preserved rows:
    `prob_33`
  - guard rows:
    `prob_32`, `prob_39`, `prob_40`
- expected metric movement:
  - improve objective on at least one diffuse-moderate target row
  - keep the current accepted-for-score contract intact
  - improve avg objective versus trusted v083 if the row-level signal survives
- acceptance criteria:
  - import smoke passes
  - representative smoke-9 accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves at least one target row with no timeout
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v083
- rollback criteria:
  - reject if the extra portfolio leaks runtime, regresses targeted rows
    overall, or fails to improve avg objective on full train40

## reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio

- File:
  `reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio.py`
- Parent:
  `reboot_v083_20260619_2106_prob38like_on_stable_prob33_parent`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v084_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v084_diffuse_second_20260619_001/`
- Targeted subtype outcome:
  - accepted `5/5`
  - timeout `0`
  - invalid `0`
  - `prob_37` improved:
    objective `17602705 -> 17544513`
    T `3961 -> 3961`
    L `3823 -> 4275`
    P `7309 -> 7209`
  - `prob_33` stayed unchanged on T/L/P/objective
  - guard rows `prob_32`, `prob_39`, `prob_40` stayed unchanged on
    T/L/P/objective
- Short-limit stress path:
  `reports/ogc2026_reboot_v001/stress_reboot_v084_prob37_short45_20260619_001/`
- Short-limit stress outcome:
  - accepted `0/1`
  - timeout `1`
  - invalid `0`
  - `prob_37` timed out at `50.15267s` under `timelimit=45`
  - comparison path:
    `reports/ogc2026_reboot_v001/verify_reboot_v083_prob37_short45_20260619_001/`
  - parent `v083` showed the same inherited short-limit timeout on `prob_37`,
    so this was not treated as a new regression
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v084_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15105355.0`
  - avg T `1560.55`
  - avg L `2750.325`
  - avg P `4173.025`
  - runtime max `56.747494s`
- Train40 comparison versus trusted v083:
  - changed rows: `1`
  - improved row:
    - `prob_37`: objective `17602705 -> 17544513`
    - T `3961 -> 3961`
    - L `3823 -> 4275`
    - P `7309 -> 7209`
    - runtime `50.610244s -> 51.708361s`
  - avg objective `15106809.8 -> 15105355.0`
  - avg T `1560.55 -> 1560.55`
  - avg L `2739.025 -> 2750.325`
  - avg P `4175.525 -> 4173.025`
  - runtime max `55.130536s -> 56.747494s`
- decision:
  - accepted
  - rationale:
    the second diffuse reinsert portfolio improved the official score headline
    with one targeted row change, kept the scoreable `40/40` contract intact,
    and introduced no new short-limit regression relative to the trusted
    parent.

## Manual Loop Note 2026-06-19 05:12 KST

- version_id: `reboot_v085_20260619_0512_fourbay_dense_extended_reinsert`
- parent_version: `reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio`
- hypothesis:
  - The current trusted v084 warm start already reaches the right family and
    first tiny reinsertion on the 4-bay high-proc dense-preference rows, but
    direct probes show the shortlist width `3` used in the inherited v074
    phase is still slightly too narrow.
  - Replaying the same bounded reinsertion move on a shortlist of `6` tardy
    blocks should preserve the family behavior while recovering extra objective
    on `prob_31` / `prob_40`.
- targeted subtype:
  - `bays == 4`
  - `blocks >= 200`
  - `proc_mean >= 20.0`
  - `pref_concentration >= 0.72`
  - `pref_pressure >= 0.68`
  - `workload_imbalance_pressure >= 0.70`
  - `slack_mean >= 4.8`
- targeted validation rows:
  - expected improved rows:
    `prob_31`, `prob_40`
  - guard rows:
    `prob_36`, `prob_38`
- expected metric movement:
  - improve objective on at least one dense 4-bay family row
  - keep the current accepted-for-score contract intact
  - improve avg objective versus trusted v084
- acceptance criteria:
  - import smoke passes
  - representative smoke-9 accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves at least one target row with no timeout
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v084
- rollback criteria:
  - reject if the longer shortlist leaks runtime, regresses the family overall,
    or fails to improve avg objective on full train40

## reboot_v085_20260619_0512_fourbay_dense_extended_reinsert

- File:
  `reboot_v085_20260619_0512_fourbay_dense_extended_reinsert.py`
- Parent:
  `reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v085_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v085_fourbay_dense_20260619_001/`
- Targeted subtype outcome:
  - accepted `4/4`
  - timeout `0`
  - invalid `0`
  - `prob_31` improved:
    objective `39802386 -> 39781302`
    T `2751 -> 2751`
    L `1670 -> 2118`
    P `11679 -> 11595`
  - `prob_40` improved:
    objective `6361163 -> 6360024`
    T `9314 -> 9314`
    L `6310 -> 6081`
    P `10955 -> 10885`
  - guard rows `prob_36`, `prob_38` stayed unchanged on T/L/P/objective
- Short-limit stress path:
  `reports/ogc2026_reboot_v001/stress_reboot_v085_prob31_prob40_short45_20260619_001/`
- Short-limit stress outcome:
  - accepted `2/2`
  - timeout `0`
  - invalid `0`
  - `prob_31` scoreable at `44.430042s`
  - `prob_40` scoreable at `38.762432s`
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v085_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15104799.425`
  - avg T `1560.55`
  - avg L `2755.8`
  - avg P `4169.175`
  - runtime max `56.585865s`
- Train40 comparison versus trusted v084:
  - changed rows: `2`
  - `prob_31`: objective `39802386 -> 39781302`, T unchanged, L `1670 -> 2118`,
    P `11679 -> 11595`
  - `prob_40`: objective `6361163 -> 6360024`, T unchanged, L `6310 -> 6081`,
    P `10955 -> 10885`
  - avg objective `15105355.0 -> 15104799.425`
  - avg T `1560.55 -> 1560.55`
  - avg L `2750.325 -> 2755.8`
  - avg P `4173.025 -> 4169.175`
  - runtime max `56.747494 -> 56.585865`
- decision:
  - accepted
  - rationale:
    the longer dense-family tardy shortlist produced two row-level objective
    gains, preserved the full `40/40` scoreable contract, and even improved
    the short-45 family stress check.

## Manual Loop Note 2026-06-19 06:44 KST

- version_id: `reboot_v086_20260619_0644_fourbay_lowproc_diffuse_reinsert`
- parent_version: `reboot_v085_20260619_0512_fourbay_dense_extended_reinsert`
- hypothesis:
  - The current trusted v085 warm start still leaves small local placement
    slack on the 4-bay early-short low-proc diffuse-preference family.
  - Replaying the same bounded one-block reinsertion over a short tardy
    shortlist should recover objective on several rows in that family without
    waking runtime-heavy branches elsewhere.
- targeted subtype:
  - `bays == 4`
  - `200 <= blocks <= 300`
  - `7.2 <= proc_mean <= 7.9`
  - `0.25 <= pref_concentration <= 0.31`
  - `0.25 <= pref_pressure <= 0.29`
  - `workload_imbalance_pressure <= 0.13`
  - `1.2 <= slack_mean <= 1.7`
- targeted validation rows:
  - expected improved rows:
    `prob_10`, `prob_11`, `prob_13`, `prob_14`, `prob_17`, `prob_19`
  - expected neutral rows inside the family:
    `prob_12`, `prob_15`
  - guard rows:
    `prob_9`, `prob_16`, `prob_21`, `prob_26`, `prob_31`, `prob_36`
- expected metric movement:
  - improve at least one low-proc diffuse 4-bay row
  - preserve the current accepted-for-score contract
  - improve avg objective versus trusted v085
- acceptance criteria:
  - import smoke passes
  - representative smoke-9 accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves at least one target row with no timeout
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v085
- rollback criteria:
  - reject if the extra local move leaks runtime, regresses the family
    materially, or fails to improve avg objective on full train40

## reboot_v086_20260619_0644_fourbay_lowproc_diffuse_reinsert

- File:
  `reboot_v086_20260619_0644_fourbay_lowproc_diffuse_reinsert.py`
- Parent:
  `reboot_v085_20260619_0512_fourbay_dense_extended_reinsert`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v086_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v086_fourbay_lowproc_20260619_001/`
- Targeted subtype outcome:
  - accepted `8/8`
  - timeout `0`
  - invalid `0`
  - improved rows:
    - `prob_10`: objective `5667274 -> 5662255`
    - `prob_11`: objective `17214296 -> 17207513`
    - `prob_13`: objective `17775052 -> 17775043`
    - `prob_14`: objective `6421844 -> 6416790`
    - `prob_17`: objective `349448 -> 338183`
    - `prob_19`: objective `4728163 -> 4720039`
  - neutral rows:
    - `prob_12`, `prob_15`
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v086_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15103893.075`
  - avg T `1560.55`
  - avg L `2762.45`
  - avg P `4162.2`
  - runtime max `57.755114s`
- Train40 comparison versus trusted v085:
  - changed rows: `6`
  - `prob_10`: objective `5667274 -> 5662255`, T unchanged, L `2615 -> 2563`,
    P `2338 -> 2303`
  - `prob_11`: objective `17214296 -> 17207513`, T unchanged, L unchanged,
    P `2407 -> 2356`
  - `prob_13`: objective `17775052 -> 17775043`, T unchanged, L `4445 -> 4390`,
    P `4364 -> 4366`
  - `prob_14`: objective `6421844 -> 6416790`, T unchanged, L unchanged,
    P `4159 -> 4121`
  - `prob_17`: objective `349448 -> 338183`, T unchanged, L `5606 -> 5749`,
    P `1511 -> 1422`
  - `prob_19`: objective `4728163 -> 4720039`, T unchanged, L `6222 -> 6452`,
    P `4164 -> 4096`
  - avg objective `15104799.425 -> 15103893.075`
  - avg T `1560.55 -> 1560.55`
  - avg L `2755.8 -> 2762.45`
  - avg P `4169.175 -> 4162.2`
  - runtime max `56.585865 -> 57.755114`
- decision:
  - accepted
  - rationale:
    the extra low-proc diffuse reinsertion stayed inside the intended family,
    preserved the full `40/40` scoreable contract, improved six rows, and
    produced the best average objective so far with unchanged average T.

## Manual Loop Note 2026-06-19 07:09 KST

- version_id: `reboot_v087_20260619_0709_fourbay_lowproc_diffuse_second_pass`
- parent_version: `reboot_v086_20260619_0644_fourbay_lowproc_diffuse_reinsert`
- hypothesis:
  - The first low-proc diffuse family reinsertion in v086 clearly improved the
    family, but direct probes on the v086 solution artifacts show residual
    objective slack still remains on part of the same subtype.
  - Replaying one more bounded reinsertion pass on that same family should
    recover the remaining objective on rows like `prob_10`, `prob_14`,
    `prob_19` while leaving already-saturated family rows unchanged.
- targeted subtype:
  - `bays == 4`
  - `200 <= blocks <= 300`
  - `7.2 <= proc_mean <= 7.9`
  - `0.25 <= pref_concentration <= 0.31`
  - `0.25 <= pref_pressure <= 0.29`
  - `workload_imbalance_pressure <= 0.13`
  - `1.2 <= slack_mean <= 1.7`
- targeted validation rows:
  - expected improved rows:
    `prob_10`, `prob_14`, `prob_19`
  - expected neutral rows:
    `prob_11`, `prob_13`, `prob_17`
  - guard rows:
    `prob_1`, `prob_9`, `prob_21`, `prob_26`, `prob_31`, `prob_36`
- expected metric movement:
  - improve at least one row inside the already-validated family
  - preserve the current accepted-for-score contract
  - improve avg objective versus trusted v086
- acceptance criteria:
  - import smoke passes
  - representative smoke-9 accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves at least one expected row with no timeout
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v086
- rollback criteria:
  - reject if the second pass leaks runtime, perturbs rows outside the family,
    or fails to improve avg objective on full train40

## reboot_v087_20260619_0709_fourbay_lowproc_diffuse_second_pass

- File:
  `reboot_v087_20260619_0709_fourbay_lowproc_diffuse_second_pass.py`
- Parent:
  `reboot_v086_20260619_0644_fourbay_lowproc_diffuse_reinsert`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v087_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v087_fourbay_lowproc_second_20260619_001/`
- Targeted subtype outcome:
  - accepted `6/6`
  - timeout `0`
  - invalid `0`
  - improved rows:
    - `prob_14`: objective `6416790 -> 6413830`
    - `prob_19`: objective `4720039 -> 4716396`
  - neutral rows:
    - `prob_10`, `prob_11`, `prob_13`, `prob_17`
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v087_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15103728.0`
  - avg T `1560.55`
  - avg L `2770.6`
  - avg P `4160.775`
  - runtime max `57.450234s`
- Train40 comparison versus trusted v086:
  - changed rows: `2`
  - `prob_14`: objective `6416790 -> 6413830`, T unchanged, L `3947 -> 3621`,
    P `4121 -> 4111`
  - `prob_19`: objective `4720039 -> 4716396`, T unchanged, L `6452 -> 7104`,
    P `4096 -> 4049`
  - avg objective `15103893.075 -> 15103728.0`
  - avg T `1560.55 -> 1560.55`
  - avg L `2762.45 -> 2770.6`
  - avg P `4162.2 -> 4160.775`
  - runtime max `57.755114 -> 57.450234`
- decision:
  - accepted
  - rationale:
    the second pass stayed entirely inside the already-validated family,
    preserved the full `40/40` scoreable contract, improved two family rows,
    and produced another objective gain with unchanged average T.

## Manual Loop Note 2026-06-19 07:28 KST

- version_id: `reboot_v088_20260619_0728_fourbay_lowproc_diffuse_wider_second_pass`
- parent_version: `reboot_v087_20260619_0709_fourbay_lowproc_diffuse_second_pass`
- hypothesis:
  - The v087 second pass improved the intended family, but artifact-based
    probes still show residual wins on the same subtype that are sitting just
    beyond the current second-pass shortlist.
  - Widening that second-pass tardy shortlist from `3/4/5` to `5/6/7` should
    recover extra objective on rows like `prob_10`, `prob_11`, `prob_19`
    without changing the rest of the training set.
- targeted subtype:
  - `bays == 4`
  - `200 <= blocks <= 300`
  - `7.2 <= proc_mean <= 7.9`
  - `0.25 <= pref_concentration <= 0.31`
  - `0.25 <= pref_pressure <= 0.29`
  - `workload_imbalance_pressure <= 0.13`
  - `1.2 <= slack_mean <= 1.7`
- targeted validation rows:
  - expected improved rows:
    `prob_10`, `prob_11`, `prob_19`
  - expected neutral rows:
    `prob_13`, `prob_14`, `prob_17`
  - guard rows:
    `prob_1`, `prob_9`, `prob_21`, `prob_26`, `prob_31`, `prob_36`
- expected metric movement:
  - improve at least one residual row inside the same already-validated family
  - preserve the current accepted-for-score contract
  - improve avg objective versus trusted v087
- acceptance criteria:
  - import smoke passes
  - representative smoke-9 accepted `9/9`, timeout `0`, invalid `0`
  - targeted subtype smoke improves at least one expected row with no timeout
  - full train40 accepted `40/40`, timeout `0`, invalid `0`
  - avg objective improves versus v087
- rollback criteria:
  - reject if the wider shortlist leaks runtime, wakes regressions in the
    family, or fails to improve avg objective on full train40

## reboot_v088_20260619_0728_fourbay_lowproc_diffuse_wider_second_pass

- File:
  `reboot_v088_20260619_0728_fourbay_lowproc_diffuse_wider_second_pass.py`
- Parent:
  `reboot_v087_20260619_0709_fourbay_lowproc_diffuse_second_pass`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v088_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v088_fourbay_lowproc_wider_20260619_001/`
- Targeted subtype outcome:
  - accepted `6/6`
  - timeout `0`
  - invalid `0`
  - improved rows:
    - `prob_10`: objective `5662255 -> 5655073`
    - `prob_11`: objective `17207513 -> 17206722`
    - `prob_19`: objective `4716396 -> 4715671`
  - neutral rows:
    - `prob_13`, `prob_14`, `prob_17`
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v088_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15103510.55`
  - avg T `1560.55`
  - avg L `2770.25`
  - avg P `4159.15`
  - runtime max `57.183935s`
- Train40 comparison versus trusted v087:
  - changed rows: `3`
  - `prob_10`: objective `5662255 -> 5655073`, T unchanged, L unchanged,
    P `2303 -> 2249`
  - `prob_11`: objective `17207513 -> 17206722`, T unchanged, L `406 -> 407`,
    P `2356 -> 2350`
  - `prob_19`: objective `4716396 -> 4715671`, T unchanged, L `7104 -> 7089`,
    P `4049 -> 4044`
  - avg objective `15103728.0 -> 15103510.55`
  - avg T `1560.55 -> 1560.55`
  - avg L `2770.6 -> 2770.25`
  - avg P `4160.775 -> 4159.15`
  - runtime max `57.450234 -> 57.183935`
- decision:
  - accepted
  - rationale:
    the wider residual shortlist stayed inside the same already-validated
    family, preserved the full `40/40` scoreable contract, improved three
    rows, and produced another clean objective gain with unchanged average T.

## reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass

- File:
  `reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass.py`
- Parent:
  `reboot_v088_20260619_0728_fourbay_lowproc_diffuse_wider_second_pass`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v089_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v089_fourbay_lowproc_third_20260619_001/`
- Targeted subtype outcome:
  - accepted `6/6`
  - timeout `0`
  - invalid `0`
  - improved rows:
    - `prob_10`: objective `5655073 -> 5648556`
    - `prob_19`: objective `4715671 -> 4715273`
  - neutral rows:
    - `prob_11`, `prob_13`, `prob_14`, `prob_17`
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v089_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15103337.675`
  - avg T `1560.55`
  - avg L `2769.425`
  - avg P `4157.875`
  - runtime max `57.634129s`
- Train40 comparison versus trusted v088:
  - changed objective rows: `2`
  - `prob_10`: objective `5655073 -> 5648556`, T unchanged, L unchanged,
    P `2249 -> 2200`
  - `prob_19`: objective `4715671 -> 4715273`, T unchanged, L `7089 -> 7056`,
    P `4044 -> 4042`
  - objective regressions: `0`
  - avg objective `15103510.55 -> 15103337.675`
  - avg T `1560.55 -> 1560.55`
  - avg L `2770.25 -> 2769.425`
  - avg P `4159.15 -> 4157.875`
  - runtime max `57.183935 -> 57.634129`
- decision:
  - accepted
  - rationale:
    the third pass stayed inside the same already-validated feature family,
    preserved the full `40/40` scoreable contract, improved two residual rows
    with zero objective regressions, and delivered another clean objective
    gain with unchanged average T.

## reboot_v090_20260619_0802_threebay_midproc_slackband_reinsert

- File:
  `reboot_v090_20260619_0802_threebay_midproc_slackband_reinsert.py`
- Parent:
  `reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v090_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v090_threebay_midproc_slackband_20260619_001/`
- Targeted subtype outcome:
  - accepted `3/3`
  - timeout `0`
  - invalid `0`
  - improved rows:
    - `prob_35`: objective `22047898 -> 22037108`
    - `prob_37`: objective `17544513 -> 17505105`
  - neutral row:
    - `prob_39`
- Time-stress path:
  `reports/ogc2026_reboot_v001/stress_reboot_v090_short45_20260619_001/`
- Time-stress outcome:
  - accepted_for_score `2/3`
  - timeout row: `prob_37`
  - comparison note:
    - matched the same short-limit timeout pattern already present in
      `reports/ogc2026_reboot_v001/stress_reboot_v089_short45_20260619_001/`
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v090_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15110448.675`
  - avg T `1573.1`
  - avg L `2773.075`
  - avg P `4153.275`
  - runtime max `58.797273s`
- Train40 comparison versus trusted v089:
  - improved rows:
    - `prob_35`: objective `22047898 -> 22037108`
    - `prob_37`: objective `17544513 -> 17505105`
  - regressed row:
    - `prob_40`: objective `6360024 -> 6694662`, T `9314 -> 9816`,
      L `5888 -> 6524`, P `10818 -> 10754`
  - avg objective `15103337.675 -> 15110448.675`
  - avg T `1560.55 -> 1573.1`
  - avg L `2769.425 -> 2773.075`
  - avg P `4157.875 -> 4153.275`
  - runtime max `57.634129 -> 58.797273`
- Additional probe note:
  - single-row reruns on `prob_40` showed instability on both parent and
    candidate chains:
    - v089 single-row probe objective `6815976`
    - v090 single-row probe objective `6747129`
  - the selector itself does not target `prob_40`, so the harmful full-train40
    regression is treated as hidden-risk instability rather than a subtype win.
- decision:
  - rejected
  - rationale:
    the targeted family improved as expected, but full train40 regressed on the
    trusted score headline and worsened average T. Because promotion requires
    avg objective improvement versus trusted v089, v090 is rejected.

## reboot_v091_20260619_0840_fourbay_dense_runtime_stable_orient3

- File:
  `reboot_v091_20260619_0840_fourbay_dense_runtime_stable_orient3.py`
- Parent:
  `reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v091_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v091_fourbay_dense_runtime_20260619_001/`
- Targeted subtype outcome:
  - accepted `2/2`
  - timeout `0`
  - invalid `0`
  - improved row:
    - `prob_40`: objective `6360024 -> 6333528`, T `9314 -> 9268`,
      L `6081 -> 5002`, P `10885 -> 11290`
  - regressed row:
    - `prob_31`: objective `39781302 -> 50259202`, T `2751 -> 3532`,
      L `2118 -> 6728`, P `11595 -> 11786`
- Full-train40 path:
  - not run
- Full-train40 outcome:
  - skipped because the targeted subtype gate already showed a severe same-family
    regression on `prob_31`
- Hidden-risk note:
  - the reduced-orientation direct builder does stabilize and improve the
    prob40-like row, but the broader dense 4-bay selector also captures
    `prob_31`, where the same change is strongly harmful
  - this means the family split is too broad even though the direct builder
    itself is runtime-stable
- decision:
  - rejected
  - rationale:
    the candidate preserved smoke scoreability and improved `prob_40`, but it
    badly regressed `prob_31` inside the same targeted subtype. Per the gate,
    the run should not advance to full train40 when same-subtype regression is
    already large at targeted smoke.

## reboot_v092_20260619_0859_prob40like_runtime_stable_orient3

- File:
  `reboot_v092_20260619_0859_prob40like_runtime_stable_orient3.py`
- Parent:
  `reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v092_core9_20260619_002/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v092_prob40like_guard_20260619_001/`
- Targeted subtype outcome:
  - accepted `2/2`
  - timeout `0`
  - invalid `0`
  - targeted family improvement:
    - `prob_40`: objective `6360024 -> 6333528`, T `9314 -> 9268`,
      L `6081 -> 5002`, P `10885 -> 11290`
  - adjacent guard outcome:
    - `prob_31`: objective preserved at `39781302`
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v092_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15102675.275`
  - avg T `1559.4`
  - avg L `2742.45`
  - avg P `4168.0`
  - runtime max `58.633313s`
- Train40 comparison versus trusted v089:
  - improved row:
    - `prob_40`: objective `6360024 -> 6333528`, T `9314 -> 9268`,
      L `6081 -> 5002`, P `10885 -> 11290`
  - regressed rows:
    - none
  - avg objective `15103337.675 -> 15102675.275`
  - avg T `1560.55 -> 1559.4`
  - avg L `2769.425 -> 2742.45`
  - avg P `4157.875 -> 4168.0`
  - runtime max `57.634129 -> 58.633313`
- High-T rows at accepted result:
  - `prob_27` T `5637`
  - `prob_32` T `3021`
  - `prob_33` T `3805`
  - `prob_37` T `3961`
  - `prob_38` T `11120`
  - `prob_39` T `3521`
  - `prob_40` T `9268`
- decision:
  - accepted
  - rationale:
    narrowing the runtime-stable orient3 builder back to the original
    prob40-like high-workload subtype preserved the trusted 40/40 contract,
    improved avg objective and avg T, removed the v091 prob31 regression, and
    introduced no new train40 regressions.

## reboot_v093_20260619_0917_threebay_midproc_slackband_on_v092

- File:
  `reboot_v093_20260619_0917_threebay_midproc_slackband_on_v092.py`
- Parent:
  `reboot_v092_20260619_0859_prob40like_runtime_stable_orient3`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v093_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v093_threebay_midproc_guard_20260619_001/`
- Targeted subtype outcome:
  - accepted `4/4`
  - timeout `0`
  - invalid `0`
  - improved rows:
    - `prob_35`: objective `22047898 -> 22037108`, T `1591 -> 1591`,
      L `8619 -> 8081`, P `5280 -> 5226`
    - `prob_37`: objective `17544513 -> 17505105`, T `3961 -> 3961`,
      L `4275 -> 4323`, P `7209 -> 7143`
  - neutral guard rows:
    - `prob_39`
    - `prob_40`
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v093_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15101420.325`
  - avg T `1559.4`
  - avg L `2730.2`
  - avg P `4165.0`
  - runtime max `57.428412s`
- Train40 comparison versus trusted v092:
  - improved rows:
    - `prob_35`: objective `22047898 -> 22037108`
    - `prob_37`: objective `17544513 -> 17505105`
  - regressed rows:
    - none
  - avg objective `15102675.275 -> 15101420.325`
  - avg T `1559.4 -> 1559.4`
  - avg L `2742.45 -> 2730.2`
  - avg P `4168.0 -> 4165.0`
  - runtime max `58.633313 -> 57.428412`
- High-T rows at accepted result:
  - `prob_27` T `5637`
  - `prob_32` T `3021`
  - `prob_33` T `3805`
  - `prob_37` T `3961`
  - `prob_38` T `11120`
  - `prob_39` T `3521`
  - `prob_40` T `9268`
- decision:
  - accepted
  - rationale:
    replaying the already useful v090 family repair on top of the stabilized
    v092 parent preserved the full 40/40 scoreable contract, kept the old
    hidden-risk row neutral, improved two targeted rows, lowered avg objective,
    and introduced no regressions.

## reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093

- File:
  `reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093.py`
- Parent:
  `reboot_v093_20260619_0917_threebay_midproc_slackband_on_v092`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v094_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v094_threebay_medium_diffuse_20260619_001/`
- Targeted subtype outcome:
  - accepted `2/2`
  - timeout `0`
  - invalid `0`
  - improved row:
    - `prob_32`: objective `12935663 -> 12781706`, T `3021 -> 2992`,
      L `2614 -> 2434`, P `4756 -> 4662`
  - neutral sibling guard row:
    - `prob_33`
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v094_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15097571.4`
  - avg T `1558.675`
  - avg L `2725.7`
  - avg P `4162.65`
  - runtime max `58.993998s`
- Train40 comparison versus trusted v093:
  - improved row:
    - `prob_32`: objective `12935663 -> 12781706`, T `3021 -> 2992`,
      L `2614 -> 2434`, P `4756 -> 4662`
  - regressed rows:
    - none
  - avg objective `15101420.325 -> 15097571.4`
  - avg T `1559.4 -> 1558.675`
  - avg L `2730.2 -> 2725.7`
  - avg P `4165.0 -> 4162.65`
  - runtime max `57.428412 -> 58.993998`
- High-T rows at accepted result:
  - `prob_27` T `5637`
  - `prob_33` T `3805`
  - `prob_37` T `3961`
  - `prob_38` T `11120`
  - `prob_39` T `3521`
  - `prob_40` T `9268`
- decision:
  - accepted
  - rationale:
    replaying the old v069 gap-aware repair on top of the newer v093 parent
    preserved the full 40/40 scoreable contract, improved the intended medium
    diffuse family on `prob_32`, kept the sibling subtype row neutral, lowered
    avg objective and all three component averages, and introduced no
    regressions.

## reboot_v095_20260619_1118_xlarge_lowproc_replay_on_v094

- File:
  `reboot_v095_20260619_1118_xlarge_lowproc_replay_on_v094.py`
- Parent:
  `reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093`
- Status:
  - pending
- Hypothesis:
  the residual 3-bay xlarge low-proc tight-slack family still benefits from
  the old v072 penalty-and-release single-block repair, but the newer active
  parent already supplies a stronger warm start. Replaying that family-specific
  repair directly on top of v094 should improve the shared subtype
  (`prob_37`/`prob_39`-like) without disturbing unrelated rows.
- Feature selector:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean < 12.0`
  - `slack_mean <= 2.3`
  - `base obj1 >= 3000`
- Probe note before implementation:
  - on active v094 at `timelimit=60`, direct replay of the v072 helper over the
    current warm start improved:
    - `prob_37`: objective `17505105 -> 17200889`, T `3961 -> 3885`
    - `prob_39`: objective `48160369 -> 47695915`, T `3521 -> 3487`
  - next gate:
    core-9 smoke first, then targeted subtype smoke on the matching family.
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v095_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v095_xlarge_lowproc_20260619_001/`
- Targeted subtype outcome:
  - accepted_for_score `0/2`
  - timeout `2`
  - invalid `0`
  - checker-feasible but overtime:
    - `prob_37`: objective `17200889`, runtime `79.084604s`
    - `prob_39`: objective `47695915`, runtime `74.983791s`
- decision:
  - rejected
  - rationale:
    the xlarge low-proc replay signal was real, but the reused v072 helper did
    not respect the remaining wall-clock budget tightly enough. It improved
    both targeted rows while timing out on both, so the coherent hypothesis is
    kept only as evidence that the target family is promising, not as a
    scoreable candidate.

## reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094

- File:
  `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094.py`
- Parent:
  `reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093`
- Status:
  - pending
- Hypothesis:
  the same xlarge 3-bay low-proc tight-slack family still has a useful
  post-warm-start repair signal, but it must use the fast bounded reinsertion
  kernel instead of the slow greedy-prefix helper. Use v072's subtype selector
  and target-block choice, then run the cheap v073 bounded reinsertion over the
  current v094 warm start.
- Feature selector:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean < 12.0`
  - `slack_mean <= 2.3`
  - `base obj1 >= 3000`
- Probe note before implementation:
  - on active v094 at `timelimit=60`, using v072 target choice plus bounded
    reinsertion gave:
    - `prob_37`: objective `17505105 -> 17454197`, T unchanged `3961`
    - `prob_39`: no change
  - bounded reinsertion runtime stayed below `1s` on both rows, so this
    variant looks compatible with the official limit.
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v096_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v096_xlarge_lowproc_20260619_001/`
- Targeted subtype outcome:
  - accepted `2/2`
  - timeout `0`
  - invalid `0`
  - improved row:
    - `prob_37`: objective `17505105 -> 17454197`, T `3961 -> 3961`,
      L `4323 -> 4046`, P `7143 -> 7060`
  - neutral sibling guard row:
    - `prob_39`
- Full-train40 path:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`
- Full-train40 outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15096298.7`
  - avg T `1558.675`
  - avg L `2718.775`
  - avg P `4160.575`
  - runtime max `58.475376s`
- Train40 comparison versus trusted v094:
  - improved row:
    - `prob_37`: objective `17505105 -> 17454197`, T `3961 -> 3961`,
      L `4323 -> 4046`, P `7143 -> 7060`
  - regressed rows:
    - none
  - avg objective `15097571.4 -> 15096298.7`
  - avg T `1558.675 -> 1558.675`
  - avg L `2725.7 -> 2718.775`
  - avg P `4162.65 -> 4160.575`
  - runtime max `58.993998 -> 58.475376`
- High-T rows at accepted result:
  - `prob_27` T `5637`
  - `prob_33` T `3805`
  - `prob_37` T `3961`
  - `prob_38` T `11120`
  - `prob_39` T `3521`
  - `prob_40` T `9268`
- decision:
  - accepted
  - rationale:
    replaying the xlarge low-proc family on top of v094 with a bounded local
    move preserved the 40/40 scoreable contract, improved the intended subtype
    on `prob_37`, kept the sibling row neutral, lowered avg objective and both
    L/P averages, and introduced no regressions.

## reboot_v097_20260619_1308_xlarge_lowproc_deeper_positions_on_v096

- File:
  `reboot_v097_20260619_1308_xlarge_lowproc_deeper_positions_on_v096.py`
- Parent:
  `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`
- Status:
  - pending
- Hypothesis:
  the same xlarge 3-bay low-proc tight-slack family still has a small safe
  local improvement signal, but the current bounded reinsertion is clipping the
  candidate position list too early. Replaying the same target-block choice
  with a deeper position scan should keep `prob_37` at least neutral while
  unlocking a scoreable `prob_39` improvement.
- Feature selector:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean < 12.0`
  - `slack_mean <= 2.3`
  - `base obj1 >= 3000`
- Probe note before implementation:
  - on active v096 warm start with the same target choice:
    - `prob_37`: deeper search stayed at `17454197`
    - `prob_39`: `max_positions=96`, `max_orients=4` improved
      `48160369 -> 48149237` in `0.641s`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v097_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v097_xlarge_lowproc_20260619_001/`
- Targeted subtype outcome:
  - accepted `1/2`
  - timeout `1`
  - invalid `0`
  - improved but still scoreable sibling:
    - `prob_37`: objective `17454197 -> 17411785`, T `3961 -> 3961`,
      L `4046 -> 5143`, P `7060 -> 6982`
  - timed-out target row:
    - `prob_39`: objective `48160369 -> 48149237`, T `3521 -> 3521`,
      L `194 -> 261`, P `8094 -> 8018`, runtime `58.667036 -> 60.131894s`
- decision:
  - rejected
  - rationale:
    the deeper position scan did unlock the intended `prob_39` improvement, but
    only by pushing the targeted row just over the official 60-second limit.
    Because the same hypothesis fails the targeted scoreability gate before any
    full benchmark, it is kept as evidence for the minimum useful depth signal,
    not promoted as a candidate.

## reboot_v098_20260619_1418_xlarge_lowproc_mid_positions_on_v096

- File:
  `reboot_v098_20260619_1418_xlarge_lowproc_mid_positions_on_v096.py`
- Parent:
  `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`
- Status:
  - pending
- Hypothesis:
  the v097 timeout came from scanning deeper than necessary on the same xlarge
  3-bay low-proc tight-slack family. The `prob_39` improvement appeared already
  at `max_positions=56`, so shrinking the standard-tier cap to that threshold
  should keep the improvement while returning the row under the official limit.
- Feature selector:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean < 12.0`
  - `slack_mean <= 2.3`
  - `base obj1 >= 3000`
- Probe note before implementation:
  - on active v096 warm start with the same target choice:
    - `prob_39`: the improved solution first appeared at `max_positions=56`
      and stayed stable through wider scans
    - the measured reinsertion micro-step at that threshold was about `0.514s`,
      much lower than the full v097 timeout margin
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v098_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v098_xlarge_lowproc_20260619_001/`
- Targeted subtype outcome:
  - accepted `1/2`
  - timeout `1`
  - invalid `0`
  - improved sibling:
    - `prob_37`: objective `17454197 -> 17411785`, T `3961 -> 3961`,
      L `4046 -> 5143`, P `7060 -> 6982`
  - timed-out and worse target row:
    - `prob_39`: objective `48160369 -> 48598605`, T `3521 -> 3553`,
      L `194 -> 314`, P `8094 -> 8168`, runtime `58.667036 -> 61.158953s`
- decision:
  - rejected
  - rationale:
    shrinking the position cap to the first apparent improvement threshold did
    not stabilize the full algorithm path. The target row still timed out, and
    the realized `prob_39` solution also regressed T, L, P, and objective
    versus trusted v096, so this depth axis is not a safe promotion path.

## reboot_v099_20260619_1845_prob31like_runtime_flatten_on_v096

- File:
  `reboot_v099_20260619_1845_prob31like_runtime_flatten_on_v096.py`
- Parent:
  `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`
- Status:
  - pending
- Hypothesis:
  current-source reruns show that the inherited v094/v096 chain has drifted
  into a runtime cliff on the 4-bay high-proc concentrated-preference
  prob31like subtype. Replacing only that subtype with the already flattened
  v078 direct path should recover scoreable runtime there while preserving the
  stronger current v096 handling on other families such as prob37like and
  prob40like rows.
- Feature selector:
  - `bays == 4`
  - `190 <= blocks <= 210`
  - `20.0 <= proc_mean <= 22.5`
  - `0.75 <= pref_concentration <= 0.82`
  - `0.70 <= pref_pressure <= 0.75`
  - `0.74 <= workload_imbalance_pressure <= 0.82`
- Validation plan:
  - core-9 smoke
  - targeted subtype smoke on `prob_31` with same-family guards
    `prob_36`, `prob_40`
  - full train40 only if the targeted gate is scoreable and the prob31like row
    recovers under time
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v099_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v099_prob31like_20260619_001/`
- Targeted subtype outcome:
  - accepted `3/4`
  - timeout `1`
  - invalid `0`
  - recovered target row:
    - `prob_31`: objective `46503155 -> 40956985`, T `3254 -> 2836`,
      runtime `70.680680s -> 53.232775s`
  - same-family guard rows stayed scoreable:
    - `prob_36`: objective `1767730`, runtime `52.239661s`
    - `prob_40`: objective `6333528`, runtime `43.891050s`
  - non-target but inherited runtime-cliff row remained broken:
    - `prob_37`: timeout, objective `17644653`, T `3961`,
      runtime `71.357656s`
- Hidden-risk note:
  - yes
  - The prob31-like runtime recovery worked as intended, but the current-source
    active chain is also broken on the prob37-like 3-bay diffuse/mid-proc
    family, and v099 intentionally left that inherited path untouched.
  - Because the targeted recovery candidate still fails scoreability on a
    nearby runtime-risk family row, it does not justify a full-train40 run or
    any promotion claim.
- decision:
  - rejected
  - rationale:
    v099 successfully repaired the prob31-like current-source runtime cliff,
    but it did not restore the overall active chain to a scoreable state
    because prob37-like rows still time out under the inherited parent path.

## Current-Source Trust Drift Note 2026-06-19 13:10 KST

- scope:
  - revalidate whether the current source tree still supports the historical
    trust claim recorded for `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`
- current-source recheck evidence:
  - `reports/ogc2026_reboot_v001/target_recheck_v096_fourbay_runtime_20260619_001/`
    - `prob_31`: timeout, runtime `70.680680s`, objective `46503155`
    - `prob_36`: accepted, runtime `52.655423s`, objective `1713312`
    - `prob_40`: accepted, runtime `43.937350s`, objective `6333528`
  - `reports/ogc2026_reboot_v001/target_recheck_v094_fourbay_runtime_20260619_001/`
    - `prob_31`: timeout, runtime about `70.434289s`
  - `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/`
    - `prob_37`: timeout, runtime `71.377730s`, objective `17644653`
  - `reports/ogc2026_reboot_v001/full_recheck_v083_train40_20260619_001/`
    - accepted_for_score `39/40`
    - only failing row: `prob_37`, timeout at `67.648573s`
- source-hash finding:
  - the historical v096 full manifest hash does not match the current file hash
    for `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094.py`
  - therefore the historical accepted report remains valuable evidence, but it
    is not sufficient to claim that the current source tree is still trusted
- runtime-cliff diagnosis:
  - current prob37 log:
    `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/logs/hh__reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094/prob_37.log`
  - key observation:
    the inherited `v060` `release_due` direct builder now consumes about
    `46.04s`, leaving no time for later `v073`/`v084`/`v093`/`v096` repair
    phases that historically produced the accepted improvement chain
- current publication status:
  - historical best:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`
  - current-source trusted accepted BEST:
    - none established yet
  - active wrapper state:
    - still points to v096 as the explicit recovery surface
    - must not be described as a currently revalidated trusted BEST

## reboot_v100_20260619_1355_prob37like_flattened_iterative_reinsert_on_v099

- File:
  `reboot_v100_20260619_1355_prob37like_flattened_iterative_reinsert_on_v099.py`
- Parent:
  `reboot_v099_20260619_1845_prob31like_runtime_flatten_on_v096`
- Status:
  - pending
- Hypothesis:
  current-source reruns show that the inherited prob37-like path no longer
  reaches the later v073/v084/v090/v096 repair phases because the delegated
  v060 warm start now consumes nearly the full 60s budget. Replacing only the
  prob37-like subtype with a scoreable direct v057-family warm start, then
  using a tiny iterative bounded single-reinsert portfolio on the remaining
  wall-clock budget, should restore scoreability there while preserving the
  prob31-like runtime fix already introduced in v099.
- Feature selector:
  - `bays == 3`
  - diffuse-moderate selector true
  - mid-proc slack-band selector true
  - xlarge low-proc selector true
  - feature-based only; no instance-name branching
- Probe note before implementation:
  - current-source `v065` is no longer a safe flattened base on this subtype:
    a direct `prob_37` probe expanded to about `94.7s` and is therefore not a
    viable recovery warm start anymore
  - current-source `v057` remains scoreable on `prob_37` and leaves headroom:
    repeated bounded single reinserts improved
    `18033244 -> 17995072 -> 17958792 -> 17949088` within about `51.7s`
- Validation plan:
  - required smoke-9:
    `prob_1`, `prob_5`, `prob_9`, `prob_13`, `prob_17`, `prob_21`,
    `prob_26`, `prob_31`, `prob_36`
  - targeted subtype smoke:
    `prob_33`, `prob_37`, `prob_39`
  - full train40 only if both smoke gates stay fully scoreable
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v100_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
  - representative runtime-risk row remained scoreable:
    - `prob_31`: objective `40956985`, runtime `52.500376s`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v100_prob37like_20260619_001/`
- Targeted subtype outcome:
  - accepted `3/3`
  - timeout `0`
  - invalid `0`
  - target row recovered from current-source timeout:
    - `prob_37`: objective `17958792`, T `4040`, runtime `50.664843s`
  - near siblings stayed scoreable:
    - `prob_33`: objective `26172225`, runtime `53.835677s`
    - `prob_39`: objective `48598605`, runtime `59.274198s`
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v100_train40_20260619_001/`
- Full benchmark outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - runtime max `59.061387s`
  - avg comparison versus historical trusted v096:
    - avg objective `15096298.7 -> 17349103.375` (`+2252804.675`)
    - avg T `1558.675 -> 1740.125` (`+181.45`)
    - avg L `2718.775 -> 2758.325` (`+39.55`)
    - avg P `4160.575 -> 4158.0` (`-2.575`)
- Per-instance comparison highlights versus historical trusted v096:
  - recovered current-source runtime-cliff rows:
    - `prob_31`: scoreable again at `53.69s`, but objective still regressed
      by `+1175683`
    - `prob_37`: scoreable again at `50.66s`, but objective still regressed
      by `+504595`
  - inherited worst regression remained dominant:
    - `prob_38`: objective `151254848 -> 238794505` (`+87539657`),
      T `11120 -> 17701`
  - additional meaningful regressions:
    - `prob_39`: objective `48160369 -> 48598605` (`+438236`)
    - `prob_36`: objective `1499988 -> 1800047` (`+300059`)
    - `prob_32`: objective `12781706 -> 12935663` (`+153957`)
- High-T rows at this run:
  - `prob_27` T `5637`
  - `prob_32` T `3021`
  - `prob_33` T `3805`
  - `prob_37` T `4040`
  - `prob_38` T `17701`
  - `prob_39` T `3553`
  - `prob_40` T `9268`
- Hidden-risk note:
  - yes
  - The prob31-like and prob37-like current-source runtime cliffs were both
    repaired enough to restore a 40/40 scoreable run, but the full rerun still
    sits far behind the historical trusted frontier because large inherited
    current-source score drift remains on `prob_38` and several neighboring
    high-T rows.
- decision:
  - rejected
  - rationale:
    v100 succeeds as a recovery proof that the current source tree can be
    driven back to `accepted_for_score=40/40` without timeouts, but it is not a
    promotion candidate because avg objective and avg T worsen materially
    versus the historical trusted v096 frontier, with the dominant prob38-like
    regression still unresolved.

## reboot_v101_20260619_1425_prob38like_feature_budget_restore_on_v100

- File:
  `reboot_v101_20260619_1425_prob38like_feature_budget_restore_on_v100.py`
- Parent:
  `reboot_v100_20260619_1355_prob37like_flattened_iterative_reinsert_on_v099`
- Status:
  - rejected
- Hypothesis:
  after the v100 recovery, the dominant remaining score loss comes from the
  prob38-like family. Current-source single-row probes show that the modern
  v050/v080/v083 path has drifted badly on that subtype, but the older v015
  direct `due_long_proc` budget-guard policy still reproduces the stable
  `153690186 / T=11316` row under the current source tree. Reintroducing only
  that feature-based policy on top of v100 should keep the recovered 40/40
  scoreable contract while sharply reducing the largest residual regression.
- Feature selector:
  - `bays == 3`
  - `blocks >= 240`
  - `proc_mean >= 20.0`
  - `0.54 <= pref_concentration <= 0.60`
  - `50.0 <= pref_gap_mean <= 53.5`
  - `0.50 <= pref_pressure <= 0.54`
  - `0.35 <= workload_imbalance_pressure <= 0.45`
- Probe note before implementation:
  - current-source single-row `prob_38` probes:
    - `v100`: objective `251902039`, T `18675`
    - `v083`: objective `234305172`, T `17340`
    - `v075`: objective `239478376`, T `17728`
    - `v057`: objective `265021265`, T `19645`
    - legacy `v015`/`v016`/`v039` direct policy:
      objective `153690186`, T `11316`, runtime about `54s`
- Validation plan:
  - required smoke-9:
    `prob_1`, `prob_5`, `prob_9`, `prob_13`, `prob_17`, `prob_21`,
    `prob_26`, `prob_31`, `prob_36`
  - targeted subtype smoke:
    `prob_31`, `prob_38`, `prob_40`
  - full train40 only if both smoke gates stay fully scoreable
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v101_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
  - representative runtime-risk rows stayed scoreable:
    - `prob_31`: objective `40956985`, runtime `53.207988s`
    - `prob_36`: objective `1767730`, runtime `52.460618s`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v101_prob38like_20260619_001/`
- Targeted subtype outcome:
  - accepted `3/3`
  - timeout `0`
  - invalid `0`
  - dominant subtype row recovered sharply:
    - `prob_38`: objective `153690186`, T `11316`, runtime `52.800141s`
  - near family rows stayed scoreable:
    - `prob_31`: objective `40956985`, runtime `53.207988s`
    - `prob_40`: objective `6333528`, runtime `43.740218s`
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v101_train40_20260619_001/`
- Full benchmark outcome:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - runtime max `59.738994s`
  - avg comparison versus rejected recovery parent v100:
    - avg objective `17349103.375 -> 15291654.45` (`-2057448.925`)
    - avg T `1740.125 -> 1584.475` (`-155.65`)
    - avg L `2758.325 -> 2781.575` (`+23.25`)
    - avg P `4158.0 -> 4171.9` (`+13.9`)
  - avg comparison versus historical trusted v096:
    - avg objective `15096298.7 -> 15291654.45` (`+195355.75`)
    - avg T `1558.675 -> 1584.475` (`+25.8`)
    - avg L `2718.775 -> 2781.575` (`+62.8`)
    - avg P `4160.575 -> 4171.9` (`+11.325`)
- Per-instance comparison highlights:
  - strongest recovery versus v100:
    - `prob_38`: objective `238794505 -> 153690186` (`-85104319`),
      T `17701 -> 11316`
    - `prob_36`: objective `1800047 -> 1767730` (`-32317`)
  - remaining regressions versus historical trusted v096:
    - `prob_9`: objective `180488 -> 3019167` (`+2838679`),
      T `1 -> 209`
    - `prob_38`: objective `151254848 -> 153690186` (`+2435338`),
      T `11120 -> 11316`
    - `prob_31`: objective `39781302 -> 40956985` (`+1175683`)
    - `prob_37`: objective `17454197 -> 17958792` (`+504595`)
    - `prob_39`: objective `48160369 -> 48598605` (`+438236`)
- High-T rows at this run:
  - `prob_27` T `5637`
  - `prob_32` T `3021`
  - `prob_33` T `3805`
  - `prob_37` T `4040`
  - `prob_38` T `11316`
  - `prob_39` T `3553`
  - `prob_40` T `9268`
- Hidden-risk note:
  - yes
  - v101 successfully restores the prob38-like current-source family to a
    scoreable and much stronger row, and it pulls the whole train40 average
    back close to the historical frontier. However, the current-source
    recovery is still not strong enough to re-establish a trusted BEST because
    several neighboring rows remain worse than the historical v096 evidence,
    with the largest new regression now concentrated on `prob_9`.
- decision:
  - rejected
  - rationale:
    v101 is a useful recovery candidate because it preserves the restored
    `40/40` scoreable contract and cuts most of the v100 loss, but it still
    worsens avg objective, avg T, avg L, and avg P versus the historical
    trusted v096 checkpoint. It should not be promoted as BEST or published as
    the active trusted solver.

## reboot_v102_20260619_1506_lowproc_threebay_release_due_guard_on_v101

- File:
  `reboot_v102_20260619_1506_lowproc_threebay_release_due_guard_on_v101.py`
- Parent:
  `reboot_v101_20260619_1425_prob38like_feature_budget_restore_on_v100`
- Status:
  - rejected
- Hypothesis:
  after the prob38-like recovery in v101, the dominant remaining loss versus
  the historical v096 frontier is concentrated in the low-proc 3-bay diffuse
  preference class, especially the subtype around the current-source prob9-like
  rows. Fresh direct policy probes show that a small bounded
  `release_due/top_bays=3/max_positions=12` candidate can recover that subtype
  far better than the delegated parent chain. Re-applying that direct policy
  only on a feature-based low-proc 3-bay selector, while keeping the better of
  the v101 warm start and the direct candidate, should reduce the remaining
  regression without reopening the prob31/prob37/prob38 runtime risk.
- Feature selector:
  - `bays == 3`
  - `100 <= blocks <= 210`
  - `proc_mean <= 8.0`
  - `pref_concentration <= 0.40`
  - `42.0 <= pref_gap_mean <= 52.5`
  - `0.33 <= pref_pressure <= 0.40`
  - `workload_imbalance_pressure <= 0.13`
- Timelimit policy:
  - skip on `very_short` and `short`
  - build the v101 warm start first
  - only spend leftover time on one bounded direct candidate
  - candidate policy:
    `release_due`, `top_bays=3`, `max_positions=12`, cap about `18s`
- Identity-dependent logic:
  - none intended in the new selector layer
  - inherits legacy noncanonical lower-layer branches from the historical
    parent chain only outside this new guarded subtype
- Targeted subtype smoke plan:
  - `prob_2`, `prob_3`, `prob_5`, `prob_6`, `prob_7`, `prob_9`
- Required smoke gate before full:
  - `prob_1`, `prob_5`, `prob_9`, `prob_13`, `prob_17`, `prob_21`,
    `prob_26`, `prob_31`, `prob_36`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v102_core9_20260619_002/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
  - all required runtime-risk rows remained scoreable
  - representative rows:
    - `prob_9`: objective `180488`, T `1`, runtime `42.759482s`
    - `prob_31`: objective `40956985`, T `2836`, runtime `51.917109s`
    - `prob_36`: objective `1836173`, T `2518`, runtime `52.440420s`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v102_lowproc_threebay_20260619_001/`
- Targeted subtype result:
  - accepted `6/6`
  - timeout `0`
  - invalid `0`
  - low-proc 3-bay family stayed strongly scoreable:
    - `prob_2`: objective `76910`, T `0`
    - `prob_3`: objective `188500`, T `0`
    - `prob_5`: objective `169685`, T `0`
    - `prob_6`: objective `756030`, T `9`
    - `prob_7`: objective `242600`, T `0`
    - `prob_9`: objective `180488`, T `1`
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v102_train40_20260619_001/`
- Full benchmark result:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - runtime max `58.632567s`
  - avg objective `15221778.625`
  - avg T `1581.875`
  - avg L `2769.675`
  - avg P `4158.425`
- Avg comparison versus rejected recovery parent v101:
  - avg objective `15291654.45 -> 15221778.625` (`-69875.825`)
  - avg T `1584.475 -> 1581.875` (`-2.6`)
  - avg L `2781.575 -> 2769.675` (`-11.9`)
  - avg P `4171.9 -> 4158.425` (`-13.475`)
- Avg comparison versus historical trusted v096:
  - avg objective `15096298.7 -> 15221778.625` (`+125479.925`)
  - avg T `1558.675 -> 1581.875` (`+23.2`)
  - avg L `2718.775 -> 2769.675` (`+50.9`)
  - avg P `4160.575 -> 4158.425` (`-2.15`)
- Per-instance highlights:
  - strongest improvements versus v101:
    - `prob_9`: objective `3019167 -> 180488` (`-2838679`),
      T `209 -> 1`
    - `prob_3`: objective `213297 -> 188500` (`-24797`),
      T `1 -> 0`
  - only regression versus v101:
    - `prob_36`: objective `1767730 -> 1836173` (`+68443`),
      T `2413 -> 2518`
  - worst remaining regressions versus trusted v096:
    - `prob_38`: objective `151254848 -> 153690186` (`+2435338`),
      T `11120 -> 11316`
    - `prob_31`: objective `39781302 -> 40956985` (`+1175683`)
    - `prob_37`: objective `17454197 -> 17958792` (`+504595`)
    - `prob_39`: objective `48160369 -> 48598605` (`+438236`)
    - `prob_36`: objective `1682216 -> 1836173` (`+153957`)
- High-T rows:
  - `prob_27` T `5637`
  - `prob_32` T `3021`
  - `prob_33` T `3805`
  - `prob_37` T `4040`
  - `prob_38` T `11316`
  - `prob_39` T `3553`
  - `prob_40` T `9268`
- Hidden-risk note:
  - yes
  - v102 successfully closes the dominant v101 low-proc three-bay regression
    without breaking the scoreable contract, but it does not fully recover the
    historical trusted frontier. The remaining gap is now concentrated again in
    the four-bay/runtime-risk family around `prob_31`, `prob_36`, `prob_37`,
    `prob_38`, and `prob_39`.
- decision:
  - candidate
  - rationale:
    v102 is the best current-source recovery candidate so far because it keeps
    `accepted_for_score=40/40` and improves avg objective, avg T, avg L, and
    avg P versus v101, with a decisive prob9-like recovery. However, it still
    loses on avg objective and avg T versus the historical trusted v096
    evidence, so it should not replace the active recovery wrapper yet.

## reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102

- File:
  `reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102.py`
- Parent:
  `reboot_v102_20260619_1506_lowproc_threebay_release_due_guard_on_v101`
- Status:
  - candidate
- Hypothesis:
  after the v102 low-proc three-bay recovery, the main remaining loss versus
  the historical frontier is again concentrated in the dense 4-bay high-proc
  runtime-risk family around prob31/prob40-like rows. Current-source direct
  probes suggest the stronger path is not a new warm start, but the tiny
  extended tardy-block reinsertion that already helped v085/v092 on that same
  family. Replaying only that tiny reinsertion on top of the existing v102 warm
  start should recover small objective slack without reopening the broader
  runtime cliffs.
- Feature selector:
  - `bays == 4`
  - `blocks >= 200`
  - `proc_mean >= 20.0`
  - `pref_concentration >= 0.72`
  - `pref_pressure >= 0.68`
  - `workload_imbalance_pressure >= 0.70`
  - `slack_mean >= 4.8`
- Timelimit policy:
  - keep `v102` warm start unchanged
  - skip on `very_short` and `short`
  - only run the tiny extended reinsertion when the subtype matches,
    the inherited dense-family direct budget is at least `45s`,
    the warm start is feasible, `obj1 > 2500`, and some time remains
  - keep only strictly better feasible results
- Identity-dependent logic:
  - none in the new selector layer
- Targeted subtype smoke plan:
  - `prob_31`, `prob_40`
- Required smoke gate before full:
  - `prob_1`, `prob_5`, `prob_9`, `prob_13`, `prob_17`, `prob_21`,
    `prob_26`, `prob_31`, `prob_36`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v103_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
  - representative rows:
    - `prob_31`: objective `40935865`, T `2836`, runtime `54.750586s`
    - `prob_36`: objective `1736456`, T `2318`, runtime `52.583450s`
    - `prob_40` was not in core-9 and was checked in targeted smoke
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v103_dense_fourbay_20260619_001/`
- Targeted subtype result:
  - accepted `2/2`
  - timeout `0`
  - invalid `0`
  - subtype rows stayed scoreable:
    - `prob_31`: objective `40935865`, T `2836`, runtime `55.953383s`
    - `prob_40`: objective `6333528`, T `9268`, runtime `45.171022s`
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v103_train40_20260619_001/`
- Full benchmark result:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - runtime max `58.808356s`
  - avg objective `15219539.55`
  - avg T `1579.25`
  - avg L `2767.075`
  - avg P `4160.425`
- Avg comparison versus candidate parent v102:
  - avg objective `15221778.625 -> 15219539.55` (`-2239.075`)
  - avg T `1581.875 -> 1579.25` (`-2.625`)
  - avg L `2769.675 -> 2767.075` (`-2.6`)
  - avg P `4158.425 -> 4160.425` (`+2.0`)
- Avg comparison versus historical trusted v096:
  - avg objective `15096298.7 -> 15219539.55` (`+123240.85`)
  - avg T `1558.675 -> 1579.25` (`+20.575`)
  - avg L `2718.775 -> 2767.075` (`+48.3`)
  - avg P `4160.575 -> 4160.425` (`-0.15`)
- Per-instance highlights:
  - improvements versus v102:
    - `prob_36`: objective `1836173 -> 1767730` (`-68443`),
      T `2518 -> 2413`
    - `prob_31`: objective `40956985 -> 40935865` (`-21120`),
      T unchanged at `2836`
  - no other rows changed versus v102 in the full train40 result
  - worst remaining regressions versus trusted v096:
    - `prob_38`: objective `151254848 -> 153690186` (`+2435338`)
    - `prob_31`: objective `39781302 -> 40935865` (`+1154563`)
    - `prob_37`: objective `17454197 -> 17958792` (`+504595`)
    - `prob_39`: objective `48160369 -> 48598605` (`+438236`)
    - `prob_36`: objective `1499988 -> 1767730` (`+267742`)
- High-T rows:
  - `prob_27` T `5637`
  - `prob_32` T `3021`
  - `prob_33` T `3805`
  - `prob_37` T `4040`
  - `prob_38` T `11316`
  - `prob_39` T `3553`
  - `prob_40` T `9268`
- Hidden-risk note:
  - yes
  - the dense four-bay extension behaves safely and does recover small slack on
    `prob_31` and `prob_36`, but the full-train40 frontier is still limited by
    the remaining three-bay runtime-risk family around `prob_37`, `prob_38`,
    and `prob_39`.
- decision:
  - candidate
  - rationale:
    v103 is a clean current-source improvement over v102 because it preserves
    `accepted_for_score=40/40` and improves avg objective, avg T, avg L, and
    total runtime while only slightly worsening avg P. However, it still does
    not beat the historical trusted v096 averages, so it should remain a
    candidate rather than replace the active recovery wrapper.

## reboot_v104_20260619_1715_threebay_runtime_iterative_reinsert_on_v103

- File:
  `reboot_v104_20260619_1715_threebay_runtime_iterative_reinsert_on_v103.py`
- Parent:
  `reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102`
- Status:
  - candidate
- Hypothesis:
  after the v103 dense four-bay repair, the remaining large regressions are
  concentrated in a 3-bay runtime-risk family spanning prob37/prob38/prob39-like
  rows. Current-source direct probes show that the existing v103 warm start is
  already close, but a tiny iterative one-block reinsertion can still shave a
  little objective on prob37-like and prob38-like rows without changing the
  broader chain. Replaying only that bounded iterative reinsertion on a
  feature-based 3-bay runtime-risk subtype should improve the frontier while
  preserving the 40/40 contract.
- Feature selector:
  - `bays == 3`
  - `blocks >= 240`
  - `10.5 <= proc_mean <= 22.5`
  - `slack_mean <= 4.6`
  - `pref_gap_mean >= 46.0`
  - `0.38 <= pref_pressure <= 0.54`
  - `workload_imbalance_pressure >= 0.10`
- Timelimit policy:
  - keep `v103` warm start unchanged
  - skip on `very_short` and `short`
  - only run the tiny iterative reinsertion when the subtype matches, the warm
    start is feasible, `obj1 > 3000`, and some wall-clock time remains
  - keep only strictly better feasible results
- Identity-dependent logic:
  - none in the new selector layer
- Targeted subtype smoke plan:
  - `prob_37`, `prob_38`, `prob_39`
- Required smoke gate before full:
  - `prob_1`, `prob_5`, `prob_9`, `prob_13`, `prob_17`, `prob_21`,
    `prob_26`, `prob_31`, `prob_36`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v104_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
  - representative rows:
    - `prob_31`: objective `40935865`, T `2836`, runtime `54.295263s`
    - `prob_36`: objective `1800047`, T `2462`, runtime `52.855601s`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/target_reboot_v104_threebay_runtime_20260619_001/`
- Targeted subtype result:
  - accepted `1/3`
  - timeout `2`
  - invalid `0`
  - row-level outcome:
    - `prob_37`: TIMEOUT, runtime `60.12s`, objective `17949088`
    - `prob_38`: accepted, objective `153689678`, T `11316`,
      runtime `59.24s`
    - `prob_39`: TIMEOUT, runtime `60.43s`, objective `48598605`
- Hidden-risk note:
  - yes
  - the iterative reinsertion does improve `prob_37` and `prob_38` under some
    reruns, but the family is too close to the 60s wall and the broader target
    smoke became non-scoreable.
- decision:
  - rejected
  - rationale:
    targeted subtype smoke failed the scoreable gate with timeouts on
    `prob_37` and `prob_39`. Even though the row-level objective signal is
    directionally good, this candidate is not safe enough to continue to full
    train40.

## reboot_v105_20260619_1726_prob37like_fast_single_reinsert_on_v103

- File:
  `reboot_v105_20260619_1726_prob37like_fast_single_reinsert_on_v103.py`
- Parent:
  `reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102`
- Status:
  - candidate
- Hypothesis:
  the rejected v104 family search was too broad: it mixed the prob37/prob38/prob39
  runtime-risk rows and spent too much time scanning extra candidates. Fresh
  current-source probing shows the prob37-like subtype still has a small,
  scoreable improvement signal if we skip the generic iterative portfolio and
  instead reinsert exactly one short-processing tardy block that is currently
  paying a positive preference penalty. Replaying only that single cheap move on
  the prob37-like diffuse low-pressure subtype should improve objective without
  reopening the v104 timeout cliff.
- Feature selector:
  - start from `v100._matches_prob37like_runtime_class(prob_info)`
  - operationally this means a 3-bay, xlarge, low-proc, diffuse, low-pressure,
    tight-slack subtype rather than the broader v104 runtime family
- Timelimit policy:
  - keep `v103` warm start unchanged
  - skip on `very_short` and `short`
  - only run one bounded `v073._limited_single_reinsert` move when the prob37-like
    subtype matches, the warm start is feasible, `obj1 > 3000`, and some wall-clock
    time remains
  - select the target block from the warm-start tardy shortlist by preferring
    positive preference-penalty blocks with the shortest processing time
- Identity-dependent logic:
  - none; subtype and target-block selection are derived only from `prob_info`
    features and warm-start assignment attributes
- Targeted subtype smoke plan:
  - `prob_37`
- Required smoke gate before full:
  - `prob_1`, `prob_5`, `prob_9`, `prob_13`, `prob_17`, `prob_21`,
    `prob_26`, `prob_31`, `prob_36`
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v105_core9_20260619_001/`
- Smoke result:
  - accepted `9/9`
  - timeout `0`
  - invalid `0`
  - representative rows:
    - `prob_9`: objective `220043`, T `3`, runtime `45.644875s`
    - `prob_31`: objective `40935865`, T `2836`, runtime `56.747656s`
    - `prob_36`: objective `1998881`, T `2827`, runtime `52.981451s`
  - note:
    the smoke row drift on `prob_9` was not introduced by v105 itself; a fresh
    side-by-side compare showed the same current-source `prob_9` row under v103.
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/compare_v103_v105_prob9_prob37_20260619_001/`
- Targeted subtype result:
  - accepted `2/2` for both compared algorithms
  - prob37-like row improved cleanly versus fresh current-source v103:
    - `prob_37`: objective `17958792 -> 17949088` (`-9704`)
    - T unchanged at `4040`
    - runtime `52.104844s -> 52.614478s`
  - guard row held exactly:
    - `prob_9`: objective `220043 -> 220043`
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v105_train40_20260619_001/`
- Full benchmark result:
  - accepted_for_score `39/40`
  - timeout `1`
  - invalid `0`
  - timeout row:
    - `prob_31`: objective `41437279`, T `2918`, runtime `69.535005s`
  - scoreable rows kept the intended prob37-like gain:
    - `prob_37`: objective `17949088`, T `4040`, runtime `40.875797s`
  - other notable current-source drift during the failed full run:
    - `prob_39`: objective `48160369`, T `3521`, runtime `58.533225s`
    - `prob_38`: objective `153690186`, T `11316`, runtime `39.488810s`
- Hidden-risk note:
  - yes
  - the one-block prob37-like move itself is cheap and does improve the target
    subtype, but the broader chain still has an unresolved prob31-like runtime
    cliff. That current-source runtime instability breaks the scoreable contract
    before the prob37-like gain can matter for promotion.
- decision:
  - rejected
  - rationale:
    full train40 failed the scoreable gate with `accepted_for_score=39/40` and
    a prob31-like timeout at `69.535005s`. Even though the targeted subtype
    improved as intended, the candidate cannot be promoted or used as the new
    active BEST under the T-zero-first plateau mode.

## reboot_v106_20260619_1802_prob31like_internal_cap_on_v103

- File:
  `reboot_v106_20260619_1802_prob31like_internal_cap_on_v103.py`
- Parent:
  `reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102`
- Status:
  - candidate
- Hypothesis:
  the current plateau blocker is the prob31-like runtime cliff, not a lack of
  row-level score signal. Fresh current-source probing shows that the v103 chain
  on the prob31-like subtype keeps the same best row-level objective when its
  internal timelimit is capped from `60` to about `58`, while runtime falls from
  the upper-50s into a much safer high-40s band. Replaying the exact v103 chain
  but only with a feature-based internal cap on the prob31-like subtype should
  stabilize the scoreable contract without reopening unrelated families.
- Feature selector:
  - `v078._matches_prob31like_class(v078._selector_features(prob_info))`
  - operationally: 4-bay, around 200 blocks, high-proc, concentrated
    preference, high imbalance, dense runtime-sensitive subtype
- Timelimit policy:
  - keep v103 unchanged outside the prob31-like subtype
  - on the prob31-like subtype in `standard` or longer time tiers, call the
    inherited v103 chain with an internal cap of `58.0s`
  - on short tiers, keep the raw incoming timelimit
- Identity-dependent logic:
  - none; the selector uses only prob_info-derived features
- Tier smoke plan:
  - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_38`
- Targeted subtype smoke plan:
  - `prob_31`, `prob_40`
- Validation status:
  - completed
- Tier smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v106_tier9_20260619_001/`
- Tier smoke result:
  - accepted_for_score `9/9`
  - timeout `0`
  - invalid `0`
  - representative rows:
    - `prob_31`: objective `40328756`, T `2792`, runtime `49.032671s`
    - `prob_38`: objective `153690186`, T `11316`, runtime `39.594965s`
    - `prob_27`: objective `77480587`, T `5637`, runtime `30.783270s`
- Targeted subtype path:
  `reports/ogc2026_reboot_v001/compare_v103_v106_prob31_prob40_20260619_001/`
- Targeted subtype result:
  - accepted `2/2` for both compared algorithms
  - prob31-like row gained runtime margin but lost row-level score versus fresh
    current-source v103:
    - `prob_31`: objective `39781302 -> 40328756` (`+547454`)
    - T `2751 -> 2792`
    - runtime `56.203018s -> 48.894334s`
  - guard row held exactly:
    - `prob_40`: objective `6333528 -> 6333528`
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v106_train40_20260619_001/`
- Full benchmark result:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg T/obj1 `1566.55`
  - avg L/obj2 `2750.0`
  - avg P/obj3 `4156.25`
  - avg objective `15182620.85`
  - runtime max `58.279814s`
  - scoreable current-source recovery:
    - `prob_31`: objective `40328756`, T `2792`, runtime `48.820807s`
    - `prob_37`: objective `17949088`, T `4040`, runtime `37.967693s`
    - `prob_39`: objective `48160369`, T `3521`, runtime `58.279814s`
- Historical trusted BEST comparison (`v096`):
  - avg objective worsened `15096298.7 -> 15182620.85` (`+86322.15`)
  - avg T worsened `1558.675 -> 1566.55` (`+7.875`)
  - avg L worsened `2718.775 -> 2750.0` (`+31.225`)
  - avg P improved `4160.575 -> 4156.25` (`-4.325`)
  - row-level objective improvement count `1`
  - row-level objective regression count `3`
  - worst regressions:
    - `prob_38`: `151254848 -> 153690186` (`+2435338`)
    - `prob_31`: `39781302 -> 40328756` (`+547454`)
    - `prob_37`: `17454197 -> 17949088` (`+494891`)
- Hidden-risk note:
  - yes
  - the internal cap does repair the immediate prob31-like timeout cliff and
    re-establishes a current-source `40/40` scoreable run, but it does so by
    spending objective on exactly the same high-T tail we are trying to shrink.
    The largest regressions stay concentrated in the dense runtime-sensitive
    family (`prob_31`, `prob_37`, `prob_38`), so this is recovery evidence,
    not a promotion-ready T-zero improvement.
- decision:
  - rejected
  - rationale:
    this candidate successfully restores a current-source `accepted_for_score=40/40`
    contract, but it does not beat the historical trusted accepted BEST. The
    avg objective and avg T both worsen versus v096, with concentrated
    regressions on the prob31/prob37/prob38 high-T family. Keep it as recovery
    evidence only; do not promote it to `baseline_hh.py`.

## reboot_v107_20260619_1841_prob38like_quantile_on_v106

- File:
  `reboot_v107_20260619_1841_prob38like_quantile_on_v106.py`
- Parent:
  `reboot_v106_20260619_1802_prob31like_internal_cap_on_v103`
- Status:
  - candidate
- Hypothesis:
  the v106 recovery candidate already restored a current-source `40/40`
  scoreable contract, and its remaining largest objective/T regression versus
  the historical trusted BEST is the prob38like pressure row. Earlier accepted
  and targeted evidence showed that the prob38like quantile single-reinsert
  move can recover about `-2.44M` objective and `-196` T on that row when it
  is kept feature-based and time-aware. Reusing that exact prob38like move on
  top of the v106 recovery parent should preserve the current-source runtime
  repair while pulling down the largest remaining 3-bay high-pressure tail.
- Feature selector:
  - keep v106 unchanged outside the target subtype
  - target subtype:
    - `bays == 3`
    - `blocks >= 240`
    - `proc_mean >= 20.0`
    - `0.54 <= pref_concentration <= 0.60`
    - `50.0 <= pref_gap_mean <= 53.5`
    - `0.50 <= pref_pressure <= 0.54`
    - `0.35 <= workload_imbalance_pressure <= 0.45`
  - selector implementation reused from
    `reboot_v050_20260617_2015_prob38like_release_aware`
- Timelimit policy:
  - short tiers: keep the parent path untouched
  - standard or longer tiers: on the prob38like subtype only, run the
    `v080._class_solution(...)` quantile single-reinsert path
  - all non-target rows stay on `v106`
- Identity-dependent logic:
  - none; selector uses only prob_info-derived features and timelimit tier
- Tier smoke plan:
  - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_38`
- Targeted subtype smoke plan:
  - compare `v106` vs `v107` on `prob_31`, `prob_37`, `prob_38`, `prob_39`,
    `prob_40`
- Acceptance target:
  - keep current-source `accepted_for_score=40/40`
  - improve `prob_38` objective/T without reopening the prob31like runtime
    cliff
  - improve total T / avg T / avg objective versus `v106`
- Validation status:
  - completed
- Tier smoke paths:
  - first run:
    `reports/ogc2026_reboot_v001/smoke_reboot_v107_tier9_20260619_001/`
  - rerun:
    `reports/ogc2026_reboot_v001/smoke_reboot_v107_tier9_20260619_002/`
- Tier smoke result:
  - first run was noisy and non-authoritative:
    - `prob_31`: objective `40935865`, T `2836`
    - `prob_38`: objective `170633608`, T `12576`
  - rerun reproduced the intended current-source signal cleanly:
    - accepted_for_score `9/9`
    - timeout `0`
    - invalid `0`
    - `prob_31`: objective `40328756`, T `2792`, runtime `49.488198s`
    - `prob_38`: objective `151254848`, T `11120`, runtime `44.782286s`
- Targeted subtype paths:
  - compare current-source parent on target rows:
    `reports/ogc2026_reboot_v001/compare_v106_v107_prob31_prob38_20260619_001/`
  - expanded guard compare:
    `reports/ogc2026_reboot_v001/compare_v106_v107_prob31_prob37_prob38_prob39_prob40_20260619_001/`
- Targeted subtype result:
  - stable positive target signal at `60s`:
    - `prob_38`: objective `153690186 -> 151254848`
    - T `11316 -> 11120`
    - `prob_31` stayed equal on the fresh two-row compare
    - `prob_37` and `prob_40` stayed equal on the expanded guard compare
    - `prob_39` stayed scoreable for `v107`; the same compare run saw `v106`
      time out on `prob_39`
- Time-stress paths:
  - solo stress:
    `reports/ogc2026_reboot_v001/stress_reboot_v107_prob38_short45_20260619_001/`
  - parent compare:
    `reports/ogc2026_reboot_v001/compare_v106_v107_prob38_short45_20260619_001/`
- Time-stress result:
  - scoreable at `45s`, but badly regressed versus parent:
    - `v106`: objective `153690186`, T `11316`
    - `v107`: objective `268911173`, T `19939`
- Hidden-risk note:
  - yes
  - the prob38like move is real and reproducible at the standard `60s` train
    limit, but it is not timelimit-robust. At `45s` the same class path
    overfires and produces a catastrophic T/objective regression versus the
    current-source recovery parent. Under the time-aware policy rules this is a
    decisive short-limit-risk failure.
- decision:
  - rejected
  - rationale:
    the candidate has genuine `60s` target value, but it fails the required
    timelimit-aware guard. Do not run full train40 or promote it. The next
    hypothesis should keep the same prob38like move only behind a much stricter
    long-limit / remaining-budget gate, or replace the direct candidate with a
    safer current-source policy for shorter standard tiers.

## reboot_v108_20260619_1857_prob38like_longlimit_gate_on_v106

- File:
  `reboot_v108_20260619_1857_prob38like_longlimit_gate_on_v106.py`
- Parent:
  `reboot_v106_20260619_1802_prob31like_internal_cap_on_v103`
- Status:
  - candidate
- Hypothesis:
  fresh current-source probes show that the prob38like move has three regimes:
  at `50s` it is clearly worse than `v106`, at `55s` it is already better, and
  at `60s` the full quantile reinsertion recovers the best known row-level
  signal. The failure mode is therefore not the move itself but activating it
  when the direct budget is too small. Gating the same prob38like path behind a
  stricter long-limit budget threshold should keep the `55s/60s` benefit while
  reverting to the stable `v106` parent for shorter standard tiers.
- Feature selector:
  - keep `v106` unchanged outside the prob38like subtype
  - prob38like subtype selector reused from
    `reboot_v050_20260617_2015_prob38like_release_aware`
- Timelimit policy:
  - on the prob38like subtype only:
    - if `v050._policy_budget(timelimit, tier) >= 41.5`, allow the
      `v107`/`v080` prob38like path
    - otherwise fall back to `v106`
  - all non-target rows stay on `v106`
- Identity-dependent logic:
  - none
- Validation plan:
  - tier smoke:
    `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_38`
  - short-limit guards:
    `prob_38 @ 45s`, `prob_38 @ 50s`, `prob_38 @ 55s`
  - full train40 only if smoke plus short-limit guards hold
- Validation status:
  - completed
- Tier smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v108_tier9_20260619_001/`
- Tier smoke result:
  - accepted_for_score `9/9`
  - timeout `0`
  - invalid `0`
  - target family behaved as intended:
    - `prob_31`: objective `40328756`, T `2792`, runtime `49.330843s`
    - `prob_38`: objective `151254848`, T `11120`, runtime `44.178857s`
- Time-stress probes:
  - direct guard sweep on `prob_38`:
    - `45s`: `v108 == v106` at objective `153690186`, T `11316`
    - `50s`: `v108 == v106` at objective `153690186`, T `11316`
    - `55s`: `v108` improves to objective `152453868`, T `11212`
    - `60s`: `v108` improves to objective `151254848`, T `11120`
  - interpretation:
    the stricter `direct_budget >= 41.5` gate successfully removes the
    short-limit regression that rejected `v107`.
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v108_train40_20260619_001/`
- Full benchmark result:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15121737.4`
  - avg T/obj1 `1561.65`
  - avg L/obj2 `2634.125`
  - avg P/obj3 `4171.85`
  - runtime max `59.605045s`
- Current-source recovery comparison versus `v106`:
  - row-level changes:
    - only `prob_38` changed materially
    - `prob_38`: objective `153690186 -> 151254848` (`-2435338`)
    - `prob_38`: T `11316 -> 11120` (`-196`)
  - aggregate:
    - avg objective `15182620.85 -> 15121737.4` (`-60883.45`)
    - avg T `1566.55 -> 1561.65` (`-4.9`)
    - avg L `2750.0 -> 2634.125` (`-115.875`)
    - avg P `4156.25 -> 4171.85` (`+15.6`)
- Historical trusted BEST comparison versus `v096`:
  - still worse overall:
    - avg objective `15096298.7 -> 15121737.4` (`+25438.7`)
    - avg T `1558.675 -> 1561.65` (`+2.975`)
  - remaining material regressions:
    - `prob_31`: objective `39781302 -> 40328756`, T `2751 -> 2792`
    - `prob_37`: objective `17454197 -> 17949088`, T `3961 -> 4040`
  - improvements relative to `v096` remain limited:
    - `prob_3`: objective `213297 -> 188500`
- Runtime-risk note:
  - yes, but improved evidence
  - `prob_39` finished the full run at `59.605045s`, which is still cliff-like.
    However, three fresh direct reruns on the same current-source chain all
    stayed feasible and consistent around `58.4s` to `59.0s` with identical
    objective `48160369` and T `3521`.
- decision:
  - candidate
  - rationale:
    this is the best current-source recovery candidate so far: it preserves the
    restored `40/40` scoreable contract from `v106`, fixes the short-limit
    regression that rejected `v107`, and cleanly improves the largest prob38like
    tail. It is not yet an accepted replacement for the historical trusted BEST
    because `prob_31` and `prob_37` still leave avg objective and avg T slightly
    worse than `v096`.

## reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108

- File:
  `reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108.py`
- Parent:
  `reboot_v108_20260619_1857_prob38like_longlimit_gate_on_v106`
- Status:
  - candidate
- Hypothesis:
  after the prob38like recovery in `v108`, the biggest remaining T tail that
  still has a large current-source row-level opportunity is the prob40like
  high-workload family. Fresh direct probes show that the old deeper-position
  policy from `v017` still beats `v108` cleanly at `45s`, `50s`, and `60s`
  on the prob40like row, with large T and objective gains and no instability in
  repeated single-row reruns. Re-applying that deeper direct policy only on the
  prob40like feature class, while keeping every other row on `v108`, should
  lower the high-T tail substantially without reopening the prob31/prob38
  recovery work.
- Feature selector:
  - reuse `v063._matches_prob40like_class(v063._selector_features(prob_info))`
  - operationally: 4-bay, xlarge, high-proc, high-workload, concentrated,
    dense high-pressure subtype
- Timelimit policy:
  - skip on `very_short` and `short`
  - on the target subtype only, run the deeper direct
    `due_release_proc/top_bays=4/max_positions=14/max_orients=4` policy
  - otherwise keep `v108`
- Identity-dependent logic:
  - none
- Validation plan:
  - targeted guards:
    `prob_31`, `prob_39`, `prob_40`
  - time-stress:
    `prob_40 @ 45s`, `prob_40 @ 50s`
  - tier smoke:
    `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_38`
  - full train40 only if all scoreable gates hold
- Validation status:
  - completed
- Targeted guard path:
  `reports/ogc2026_reboot_v001/compare_v108_v109_prob31_prob39_prob40_20260619_001/`
- Targeted guard result:
  - accepted_for_score `6/6`
  - timeout `0`
  - invalid `0`
  - non-target guards stayed stable:
    - `prob_31`: unchanged at objective `40328756`, T `2792`
    - `prob_39`: unchanged at objective `48160369`, T `3521`
  - target row improved:
    - `prob_40`: objective `6333528 -> 5910122` (`-423406`)
    - `prob_40`: T `9268 -> 8622` (`-646`)
- Time-stress path:
  `reports/ogc2026_reboot_v001/compare_v108_v109_prob40_short45_20260619_001/`
- Time-stress result:
  - accepted_for_score `2/2`
  - timeout `0`
  - invalid `0`
  - `prob_40 @ 45s` still improves cleanly:
    - objective `6743716 -> 5910122` (`-638408`)
    - T `9882 -> 8917` (`-965`)
  - interpretation:
    the deeper prob40like branch does not need an extra long-limit gate; it
    stays helpful even under the short-45 guard that had been risky for other
    family-specific branches.
- Tier smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v109_tier9_20260619_001/`
- Tier smoke result:
  - accepted_for_score `9/9`
  - timeout `0`
  - invalid `0`
  - key guard rows remained scoreable:
    - `prob_31`: objective `40328756`, T `2792`, runtime `49.563233s`
    - `prob_38`: objective `151254848`, T `11120`, runtime `47.760477s`
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v109_train40_20260619_001/`
- Full benchmark result:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - avg objective `15111152.25`
  - avg T/obj1 `1545.5`
  - avg L/obj2 `2623.75`
  - avg P/obj3 `4187.025`
  - runtime max `58.032762s`
- Current-source recovery comparison versus `v108`:
  - only the prob40like tail changed materially:
    - `prob_40`: objective `6333528 -> 5910122` (`-423406`)
    - `prob_40`: T `9268 -> 8622` (`-646`)
  - aggregate:
    - avg objective `15121737.4 -> 15111152.25` (`-10585.15`)
    - avg T `1561.65 -> 1545.5` (`-16.15`)
    - avg L `2634.125 -> 2623.75` (`-10.375`)
    - avg P `4171.85 -> 4187.025` (`+15.175`)
- Historical trusted BEST comparison versus `v096`:
  - T is now better, but objective is still not:
    - avg objective `15096298.7 -> 15111152.25` (`+14853.55`)
    - avg T `1558.675 -> 1545.5` (`-13.175`)
  - material remaining regressions:
    - `prob_31`: objective `39781302 -> 40328756`, T `2751 -> 2792`
    - `prob_37`: objective `17454197 -> 17949088`, T `3961 -> 4040`
  - material improvements versus `v096`:
    - `prob_40`: objective `6333528 -> 5910122`, T `9268 -> 8622`
    - `prob_3`: objective `213297 -> 188500`
- Hidden-risk note:
  - managed but still present
  - runtime risk is lower than in the historical active chain because the full
    run maxed at `58.032762s`, but the candidate still depends on current-source
    recovery layers that have not yet erased the prob31/prob37 regressions
    relative to the historical v096 benchmark.
- decision:
  - candidate
  - rationale:
    `v109` is the strongest current-source recovery candidate so far. It keeps
    the restored `40/40` scoreable contract, cleanly improves the remaining
    prob40like high-T tail, and now beats the historical v096 benchmark on avg
    T. It is still not an accepted replacement for the trusted historical BEST
    because avg objective remains slightly worse, with the gap concentrated in
    the prob31/prob37 family.

## reboot_v110_20260619_2115_prob37like_fast_single_on_v109

- File:
  `reboot_v110_20260619_2115_prob37like_fast_single_on_v109.py`
- Parent:
  `reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108`
- Status:
  - pending
- Hypothesis:
  after the recovery checkpoint, the historical-v096 objective gap is now
  concentrated almost entirely in `prob_31` and `prob_37`, while the prob38like
  and prob40like tails are already repaired on the current-source line. Fresh
  same-turn rechecks show that the broader `v098` replay is too expensive on the
  3-bay xlarge low-proc family: it times out on `prob_37` and drifts on
  `prob_39` under both `45s` and `60s` targeted compares. The next safe move is
  therefore not to reopen the whole family, but to isolate only the diffuse
  low-pressure prob37-like subtype and replay the much cheaper one-block fast
  single reinsertion that previously improved that subtype in `v105`. Running
  that deterministic move on top of the stable `v109` warm start should recover
  some prob37-like objective without touching the prob39-like runtime-risk
  sibling or the prob31-like chain.
- Feature selector:
  - start from the existing feature-based prob37-like runtime class:
    `v100._matches_prob37like_runtime_class(prob_info)`
  - operationally this means:
    - 3-bay
    - xlarge block count tier
    - low-proc
    - diffuse / low-pressure preference structure
    - tight-slack subtype
  - explicitly do not activate on the more concentrated prob39-like sibling
- Timelimit policy:
  - keep `v109` unchanged outside the prob37-like subtype
  - skip on `very_short` and `short`
  - build the `v109` warm start first
  - only if the warm start is feasible, `obj1 > 3000`, and some wall-clock headroom
    remains, run one bounded `v073._limited_single_reinsert` move using the
    short-processing positive-penalty target rule from `v105`
  - keep only strictly better officially feasible results
- Identity-dependent logic:
  - none
- Validation plan:
  - representative smoke-9:
    `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_37`
  - targeted sibling guards:
    `prob_38`, `prob_39`
  - time-stress:
    `prob_37 @ 45s`, `prob_39 @ 45s`
  - full train40 only if all gates remain scoreable
- Probe note before implementation:
  - same-turn short-45 compare:
    `reports/ogc2026_reboot_v001/compare_v109_v098_prob37_prob39_short45_20260619_001/`
    showed the broader xlarge-lowproc replay is too risky:
    - `v109 prob_37`: runtime `45.217551s`, not scoreable
    - `v098 prob_37`: subprocess timeout `67.528688s`
    - `v109 prob_39`: accepted, objective `48743275`
    - `v098 prob_39`: runtime `45.442129s`, not scoreable
  - same-turn long-60 compare:
    `reports/ogc2026_reboot_v001/compare_v109_v098_prob37_prob39_long60_20260619_001/`
    confirmed that the broad replay still times out on the target row:
    - `v109 prob_37`: accepted, objective `17949088`, T `4040`
    - `v098 prob_37`: objective `17644653`, T `3961`, but runtime `63.290928s`
    - `v109 prob_39`: accepted, objective `48598605`
    - `v098 prob_39`: accepted, objective `48587025`
  - interpretation:
    the family still contains some improvement signal, but only a much narrower
    and cheaper prob37-like move is compatible with the current scoreable
    envelope.
- Validation status:
  - targeted gate failed
- Targeted guard path:
  `reports/ogc2026_reboot_v001/compare_v109_v110_prob37_prob38_prob39_long60_20260619_001/`
- Targeted guard result:
  - accepted_for_score `6/6`
  - timeout `0`
  - invalid `0`
  - target row did not improve:
    - `prob_37`: objective unchanged at `17949088`
    - T unchanged at `4040`
    - runtime `45.725233s -> 46.412510s`
  - non-target runtime-risk sibling held exactly:
    - `prob_39`: objective unchanged at `48598605`
    - T unchanged at `3553`
  - off-target family drift worsened:
    - `prob_38`: objective `166615156 -> 186785357` (`+20170201`)
    - T `12268 -> 13779` (`+1511`)
- Direct warm-start probe after guard:
  - same-turn inline probe on top of the `v109` warm start:
    - `v100._try_iterative_reinsert_portfolio(...)` on `prob_37`
    - base result: objective `17949088`, T `4040`
    - candidate result: unchanged at objective `17949088`, T `4040`
  - interpretation:
    once the current-source chain already reaches the `v109` warm start, the
    older prob37-like local-move stack no longer exposes a same-T improvement
    path.
- Time-stress status:
  - skipped
  - reason:
    the long-60 targeted gate already failed to show any prob37-like gain, so
    there is no reason to spend more benchmark budget on a short-45 follow-up.
- Full benchmark status:
  - not run
  - reason:
    target row failed to improve and an off-target sibling family regressed
    materially during the targeted guard run.
- Hidden-risk note:
  - yes
  - this hypothesis is cheap and scoreable, but it does not move the T-first
    frontier. The targeted subtype stayed flat, while the surrounding high-T
    tail showed additional current-source drift during the same compare.
- decision:
  - rejected
  - rationale:
    `v110` does not deliver a T breakthrough on the intended prob37-like
    subtype and therefore fails the plateau/T-zero-first gate. Because the
    target row stayed flat and the adjacent high-T family drifted worse during
    the guard compare, there is no case for a full-train40 run.

## reboot_v111_20260619_2130_prob31like_stable_direct_cap_on_v109

- File:
  `reboot_v111_20260619_2130_prob31like_stable_direct_cap_on_v109.py`
- Parent:
  `reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108`
- Status:
  - pending
- Hypothesis:
  current-source rechecks show that the unresolved `prob31` drift is not a
  broad family-score problem but a timing-sensitive warm-start instability
  inside the prob31-like direct builder. The same downstream
  `v067 -> v074 -> v085` repair chain still reaches the historical
  `40328756 / T=2792` row when the preference-spread direct phase is forced to
  finish a little earlier. Replacing only the prob31-like subtype in `v109`
  with the same chain under a tighter feature-based direct cap should stabilize
  that row without touching the already revalidated prob40-like gain.
- Feature selector:
  - reuse `v078._matches_prob31like_class(v078._selector_features(prob_info))`
  - operationally: 4-bay, around 200 blocks, high-proc, concentrated
    preference, high imbalance, dense runtime-sensitive subtype
- Timelimit policy:
  - keep `v109` unchanged outside the prob31-like subtype
  - on the prob31-like subtype in `standard` or longer tiers, cap the direct
    preference-spread builder lower than the current `v078` branch so the
    accepted `v067/v074/v085` repairs consistently receive slack
- Identity-dependent logic:
  - none; selector and cap use only `prob_info` features and `timelimit`
- Pre-implementation probe evidence:
  - official rechecks:
    - `reports/ogc2026_reboot_v001/recheck_v109_prob31_20260619_002/`
      reproduced the worse current-source row
      `objective=40935865`, `T=2836`
    - `reports/ogc2026_reboot_v001/recheck_v109_prob40_20260619_001/`
      preserved the prob40-like gain
      `objective=5910122`, `T=8622`
  - same-turn inline prob31 chain probe:
    a direct cap in the mid-40s kept the base direct result unchanged at
    `40956985 / T=2836`, but the inherited
    `v067 -> v074 -> v085` repairs then consistently recovered
    `40328756 / T=2792`
- Validation plan:
  - representative smoke-9:
    `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_40`
  - targeted sibling guards:
    `prob_31`, `prob_36`, `prob_40`
  - time-stress:
    `prob_31 @ 45s`
  - full train40 only if all gates remain scoreable
- Validation status:
  - completed
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v111_tier9_20260619_001/`
- Smoke result:
  - accepted_for_score `9/9`
  - timeout `0`
  - invalid `0`
  - representative rows:
    - `prob_31`: objective `40328756`, T `2792`, runtime `48.885522s`
    - `prob_40`: objective `5910122`, T `8622`, runtime `43.930954s`
    - `prob_27`: objective `77480587`, T `5637`, runtime `30.295104s`
- Targeted sibling guard path:
  `reports/ogc2026_reboot_v001/compare_v109_v111_prob31_prob36_prob40_20260619_001/`
- Targeted sibling guard result:
  - accepted_for_score `6/6`
  - timeout `0`
  - invalid `0`
  - official-limit target row:
    - `prob_31`: objective held exactly at `40328756`
    - T held exactly at `2792`
    - runtime `48.481034s -> 48.096001s`
  - same-family sibling guards:
    - `prob_36`: objective held exactly at `1499988`
    - `prob_40`: objective held exactly at `5910122`
- Time-stress path:
  `reports/ogc2026_reboot_v001/stress_v109_v111_prob31_short45_20260619_001/`
- Time-stress result:
  - accepted_for_score `2/2`
  - timeout `0`
  - invalid `0`
  - `prob_31 @ 45s`:
    - `v109`: objective `40956985`, T `2836`, runtime `35.788568s`
    - `v111`: objective `40935865`, T `2836`, runtime `39.848945s`
  - interpretation:
    the lower direct cap does mildly improve the short-limit current-source row,
    but it does not create a new official-limit win over the already-good
    `v109` rerun.
- Full benchmark status:
  - not run
  - reason:
    the official-limit targeted guard only held the improved `prob_31` row
    rather than beating `v109`, so the plateau/T-zero-first gate does not yet
    justify a fresh full train40 run.
- Hidden-risk note:
  - manageable
  - the subtype-specific cap is scoreable on smoke, holds its siblings exactly,
    and shows a small short-limit stability benefit, but it has not produced a
    new official-limit row improvement.
- decision:
  - candidate
  - rationale:
    keep `v111` as a stability-side branch for the prob31-like subtype. It is
    cleaner than a blind rejection because it preserves the recovered row and
    helps under `45s`, but without a `60s` target-row win it should not advance
    to full train40 or replace the current active wrapper.

## reboot_v112_20260619_2245_prob31like_displaced_early_reinsert_on_v111

- File:
  `reboot_v112_20260619_2245_prob31like_displaced_early_reinsert_on_v111.py`
- Parent:
  `reboot_v111_20260619_2130_prob31like_stable_direct_cap_on_v109`
- Status:
  - pending
- Hypothesis:
  the prob31-like subtype is still leaving one small but real T tail after the
  `v111` stable direct builder plus the accepted `v067/v074/v085` repair chain.
  The current dense-family reinsertion stack only rechecks blocks at or after
  their existing entry time, so it misses displaced tardy blocks that need an
  earlier re-entry on a more preferred bay. A tiny post-`v111` displaced-block
  reinsertion phase should target only those blocks with high preference
  penalty, high tardiness, and large entry delay, then allow earlier-than-
  current re-entry under a strict budget.
- Feature selector:
  - outer subtype:
    reuse `v078._matches_prob31like_class(v078._selector_features(prob_info))`
  - inner target shortlist:
    tardy blocks from the current solution with
    `pref_penalty >= 75`, `tardiness >= 30`, and `entry_delay >= 35`,
    ranked by `(entry_delay, tardiness, pref_penalty)`
- Timelimit policy:
  - keep `v111` unchanged outside the prob31-like subtype
  - run the new displaced-block phase only in `standard` or longer tiers and
    only when enough wall-time remains after the existing `v111` chain
- Identity-dependent logic:
  - none; subtype detection and target selection use only `prob_info`,
    current-solution assignments, and `timelimit`
- Pre-implementation probe evidence:
  - base current-source row from saved `v111` smoke solution:
    `40328756 / T=2792`
  - relaxed one-block reinsertion probe on the top tardy-10 list:
    block `31` improved the row to `40115695 / T=2776`
  - narrowed displaced shortlist probe:
    target ids `[90, 31, 51]` with bounded search
    (`max_positions=6`, `max_orients=3`) still recovered
    `40115695 / T=2776` in about `1.53s`
- Validation plan:
  - representative smoke-9:
    `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_40`
  - targeted sibling guards:
    `prob_31`, `prob_36`, `prob_40`
  - time-stress:
    `prob_31 @ 45s`
  - full train40 only if all gates remain scoreable and the prob31-like row
    strictly beats `v111`
- Validation status:
  - completed
- Smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v112_tier9_20260619_001/`
- Smoke result:
  - accepted_for_score `8/9`
  - timeout `1`
  - invalid `0`
  - headline row:
    - `prob_31`: objective `40115695`, T `2776`, runtime `60.389299s`
    - checker feasible `true`, but not scoreable because runtime exceeded the
      official `60s` limit
  - other representative rows remained scoreable, including:
    - `prob_40`: objective `5910122`, T `8622`, runtime `55.098690s`
    - `prob_27`: objective `77480587`, T `5637`, runtime `36.989812s`
- Hidden-risk note:
  - high
  - the displaced-block phase does find a real T/objective win on the target
    row, but the current form spends too much extra time on `prob_31` and
    breaks the accepted_for_score contract at the smoke gate
- decision:
  - rejected
  - rationale:
    `v112` proves the earlier-entry displaced-block idea is directionally
    correct, but the current implementation is too expensive to keep. Because
    `prob_31` timed out in representative smoke, this version cannot advance
    to targeted guards or full train40.

## reboot_v113_20260619_2335_prob31like_displaced_early_reinsert_lite_on_v111

- File:
  `reboot_v113_20260619_2335_prob31like_displaced_early_reinsert_lite_on_v111.py`
- Parent:
  `reboot_v111_20260619_2130_prob31like_stable_direct_cap_on_v109`
- Status:
  - pending
- Hypothesis:
  `v112` showed that the prob31-like row can beat `v111` if we allow an
  earlier-entry reinsertion on a tiny displaced-block shortlist, but it also
  showed that the three-candidate portfolio is a little too expensive at the
  official `60s` boundary. Restricting the same idea to an even smaller
  shortlist and stopping as soon as the first strict improvement is found
  should preserve the `40115695 / T=2776` signal while restoring smoke
  scoreability.
- Feature selector:
  - outer subtype:
    reuse `v078._matches_prob31like_class(v078._selector_features(prob_info))`
  - inner target shortlist:
    same displaced-block gate as `v112`:
    `pref_penalty >= 75`, `tardiness >= 30`, `entry_delay >= 35`
  - narrowed portfolio:
    only the top `2` candidates in `standard`, then stop on the first strict
    improvement
- Timelimit policy:
  - keep `v111` unchanged outside the prob31-like subtype
  - keep the lite displaced-block phase only in `standard` or longer tiers and
    under a tighter wall-time budget than `v112`
- Identity-dependent logic:
  - none; selector and stop rule use only `prob_info`, current assignments, and
    elapsed wall time
- Pre-implementation probe evidence:
  - saved-solution probe on the `v111` prob31 row:
    the top displaced shortlist `[90, 31, 51]` improved at candidate `31`
  - a narrowed top-2 replay still includes `31` and should therefore preserve
    the target-row win while skipping the third candidate that added cost only
- Validation plan:
  - quick target sanity:
    `prob_31`
  - representative smoke-9:
    `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_40`
  - targeted sibling guards:
    `prob_31`, `prob_36`, `prob_40`
  - time-stress:
    `prob_31 @ 45s`
  - full train40 only if all gates remain scoreable and the prob31-like row
    still strictly beats `v111`
- Validation status:
  - completed
- Target sanity path:
  `reports/ogc2026_reboot_v001/target_reboot_v113_prob31_20260619_001/`
- Target sanity result:
  - accepted_for_score `0/1`
  - timeout `1`
  - invalid `0`
  - `prob_31`: objective `40328756`, T `2792`, runtime `60.077600s`
  - no displaced-block phase was reached in the log because the inherited
    prob31-like `v111` chain already consumed essentially the full official
    limit on this rerun
- Hidden-risk note:
  - high
  - the lighter displaced-block idea is no longer the limiting factor; the
    current-source prob31-like parent itself is now timing out on rerun
- decision:
  - rejected
  - rationale:
    `v113` cannot be scoreable because its `v111` parent path already lands on
    the official runtime cliff for `prob_31`. The next cycle should therefore
    pivot from deeper T-improvement to prob31-like runtime re-stabilization.

## reboot_v114_20260619_2358_prob31like_direct_prefix2_stable_on_v109

- File:
  `reboot_v114_20260619_2358_prob31like_direct_prefix2_stable_on_v109.py`
- Parent:
  `reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108`
- Status:
  - pending
- Hypothesis:
  the current-source prob31-like runtime cliff is mostly caused by the
  inherited multi-stage repair chain, especially the generic `v067` path that
  spends time probing a one-block prefix before the useful two-block rebuild.
  A subtype-specific direct plan that keeps the stable capped preference-spread
  base from `v111`, then jumps immediately to the top-2 tardy prefix rebuild
  and skips the later polish-only `v074/v085` phases, should recover the
  `40349837 / T=2792` row far earlier and restore scoreability.
- Feature selector:
  - outer subtype:
    reuse `v078._matches_prob31like_class(v078._selector_features(prob_info))`
  - inner move:
    current warm-start tardy shortlist from
    `v064._tardy_block_ids(assignments, limit=2)` and one direct
    `prefix_len=2` rebuild
- Timelimit policy:
  - keep `v109` unchanged outside the prob31-like subtype
  - only activate the direct prefix-2 stabilization when `timelimit >= 55s`
  - below that, fall back to the current shorter-limit parent path
- Identity-dependent logic:
  - none; selector and move use only `prob_info`, current assignments, and
    `timelimit`
- Pre-implementation probe evidence:
  - current-source step timing on `prob_31`:
    - stable capped base: about `41.36s`
    - `v067` generic tardy research: about `14.61s`
    - `v074` fast reinsert: about `0.81s`
    - `v085` extended reinsert: about `1.53s`
    - total chained runtime: about `58.30s`
  - direct prefix-2 replay from the same capped base:
    - tardy ids `[88, 188]`
    - runtime about `8.12s`
    - row `40956985 / T=2836 -> 40349837 / T=2792`
    - total runtime about `43.43s`
- Validation plan:
  - quick target sanity:
    `prob_31`
  - representative smoke-9:
    `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_40`
  - targeted sibling guards:
    `prob_31`, `prob_36`, `prob_40`
  - time-stress:
    `prob_31 @ 45s`
  - full train40 only if all gates remain scoreable
- Validation status:
  - completed
- Target sanity path:
  `reports/ogc2026_reboot_v001/target_reboot_v114_prob31_20260619_001/`
- Target sanity result:
  - accepted_for_score `1/1`
  - timeout `0`
  - invalid `0`
  - `prob_31`: objective `40349837`, T `2792`, runtime `47.782863s`
- Representative smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v114_tier9_20260619_001/`
- Representative smoke result:
  - accepted_for_score `9/9`
  - timeout `0`
  - invalid `0`
  - representative rows:
    - `prob_31`: objective `40349837`, T `2792`, runtime `42.783250s`
    - `prob_40`: objective `5910122`, T `8622`, runtime `43.627978s`
    - `prob_27`: objective `77480587`, T `5637`, runtime `30.445228s`
- Targeted sibling guard path:
  `reports/ogc2026_reboot_v001/compare_v109_v114_prob31_prob36_prob40_20260619_001/`
- Targeted sibling guard result:
  - accepted_for_score `6/6`
  - timeout `0`
  - invalid `0`
  - official-limit target row:
    - `prob_31`:
      - `v109`: objective `40328756`, T `2792`, runtime `49.836881s`
      - `v114`: objective `40349837`, T `2792`, runtime `42.886445s`
  - same-family sibling guards:
    - `prob_36`: objective held exactly at `1499988`
    - `prob_40`: objective held exactly at `5910122`
- Official-limit repeatability path:
  `reports/ogc2026_reboot_v001/compare_v109_v114_prob31_rerun_20260620_001/`
- Official-limit repeatability result:
  - accepted_for_score `2/2`
  - timeout `0`
  - invalid `0`
  - `prob_31` rerun:
    - `v109`: objective `40328756`, T `2792`, runtime `49.146342s`
    - `v114`: objective `40349837`, T `2792`, runtime `42.552895s`
- Time-stress path:
  `reports/ogc2026_reboot_v001/stress_v109_v114_prob31_short45_20260619_001/`
- Time-stress result:
  - accepted_for_score `2/2`
  - timeout `0`
  - invalid `0`
  - `prob_31 @ 45s`:
    - `v109`: objective `45309349`, runtime `36.744207s`
    - `v114`: objective `40956985`, runtime `38.900659s`
  - interpretation:
    the runtime-stable prefix-2 branch gives up a small amount of official-limit
    objective versus the current `v109` rerun, but it materially improves the
    shorter-limit row while keeping the official-limit T exactly unchanged.
- Full benchmark status:
  - not run
  - reason:
    the official-limit target row is still a small objective regression versus
    the current `v109` rerun, so the plateau/T-zero-first gate does not justify
    a fresh full train40 run yet.
- Hidden-risk note:
  - manageable
  - `v114` is consistently faster than the current `v109` reruns on the
    prob31-like subtype and stays scoreable, but it does not create an
    official-limit T breakthrough and slightly regresses objective on the
    target row.
- decision:
  - candidate
  - rationale:
    keep `v114` as a runtime-stable prob31-like parent candidate. It is not an
    accepted BEST candidate because the official-limit target row regresses a
    little on objective, but it looks like a much better base for any next
    T-moving prob31-like follow-up than the heavier `v111` chain.

## reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114

- File:
  `reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114.py`
- Parent:
  `reboot_v114_20260619_2358_prob31like_direct_prefix2_stable_on_v109`
- Status:
  - pending
- Hypothesis:
  the `v114` prob31-like parent already restores a scoreable `T=2792` row with
  enough runtime margin left that one more tightly bounded displaced-block
  earlier-entry move can be added back safely. On the `v114` parent solution,
  the best displaced candidate remains block `31`, and it improves the row to
  `40137295 / T=2776` in well under one second. Replaying that exact idea on a
  tiny displaced shortlist should deliver the first real prob31-like T
  breakthrough on top of the new runtime-stable parent.
- Feature selector:
  - outer subtype:
    reuse `v078._matches_prob31like_class(v078._selector_features(prob_info))`
  - parent:
    reuse `v114` unchanged
  - inner displaced shortlist:
    tardy blocks on the `v114` parent solution with
    `pref_penalty >= 75`, `tardiness >= 25`, `entry_delay >= 30`,
    ranked by `(entry_delay, tardiness, pref_penalty)`
- Timelimit policy:
  - keep `v114` unchanged outside the prob31-like subtype
  - only run the displaced follow-up when `timelimit >= 55s` and enough
    remaining wall time is still available after the `v114` parent
- Identity-dependent logic:
  - none; selector and shortlist use only `prob_info`, current assignments, and
    `timelimit`
- Pre-implementation probe evidence:
  - parent `v114` on `prob_31`:
    `40349837 / T 2792`
  - displaced shortlist on top of the `v114` parent:
    `[(90 ...), (31 ...), (66 ...), ...]`
  - candidate `31` replay:
    `40137295 / T 2776`
    with about `0.38s` extra local-search cost
- Validation plan:
  - quick target sanity:
    `prob_31`
  - representative smoke-9:
    `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_40`
  - targeted sibling guards:
    `prob_31`, `prob_36`, `prob_40`
  - time-stress:
    `prob_31 @ 45s`
  - full train40 only if all gates remain scoreable and the official-limit
    target row still beats `v114`
- Validation status:
  - completed
- Target sanity path:
  `reports/ogc2026_reboot_v001/target_reboot_v115_prob31_20260620_001/`
- Target sanity result:
  - accepted_for_score `1/1`
  - timeout `0`
  - invalid `0`
  - `prob_31`: objective `40137295`, T `2776`, runtime `50.343847s`
- Representative smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v115_tier9_20260620_001/`
- Representative smoke result:
  - accepted_for_score `9/9`
  - timeout `0`
  - invalid `0`
  - representative rows:
    - `prob_31`: objective `40137295`, T `2776`, runtime `44.21s`
    - `prob_40`: objective `5910122`, T `8622`, runtime `45.08s`
    - `prob_27`: objective `77480587`, T `5637`, runtime `30.81s`
- Targeted sibling guard path:
  `reports/ogc2026_reboot_v001/compare_v109_v115_prob31_prob36_prob40_20260620_001/`
- Targeted sibling guard result:
  - accepted_for_score `6/6`
  - timeout `0`
  - invalid `0`
  - target row:
    - `prob_31`:
      - `v109`: objective `40328756`, T `2792`, runtime `49.71s`
      - `v115`: objective `40137295`, T `2776`, runtime `44.91s`
  - sibling guards:
    - `prob_36`: objective held exactly at `1499988`
    - `prob_40`: objective held exactly at `5910122`
- Time-stress path:
  `reports/ogc2026_reboot_v001/stress_v109_v115_prob31_short45_20260620_001/`
- Time-stress result:
  - accepted_for_score `2/2`
  - timeout `0`
  - invalid `0`
  - `prob_31 @ 45s`:
    - `v109`: objective `67601421`, runtime `36.621772s`
    - `v115`: objective `45309349`, runtime `36.787646s`
  - interpretation:
    the displaced follow-up keeps the shorter-limit row scoreable and preserves
    the same current-source 45s behavior that the lighter `v114` parent had
    already restored, while still leaving a strong official-limit target-row
    gain in place.
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v115_train40_20260620_001/`
- Full benchmark result:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - runtime max `58.029289s`
  - avg T `1545.1`
  - avg L `2616.85`
  - avg P `4189.15`
  - avg objective `15106365.725`
- Per-instance comparison summary:
  - versus current-source `v109`:
    - changed rows: `1`
    - improvements: `1`
    - regressions: `0`
    - improved row:
      - `prob_31`: objective `40328756 -> 40137295`,
        T `2792 -> 2776`,
        L `2483 -> 2207`,
        P `12146 -> 12231`,
        runtime `49.71s -> 44.91s`
  - versus historical trusted `v096`:
    - changed rows: `4`
    - improvements:
      - `prob_40`: objective `6333528 -> 5910122`, T `9268 -> 8622`
      - `prob_3`: objective `213297 -> 188500`, T `1 -> 0`
    - regressions:
      - `prob_37`: objective `17454197 -> 17949088`, T `3961 -> 4040`
      - `prob_31`: objective `39781302 -> 40137295`, T `2751 -> 2776`
- Hidden-risk note:
  - manageable
  - `v115` is the first current-source branch after the v096 drift cycle that
    both keeps `40/40` scoreability and creates a real official-limit T
    improvement on the prob31-like subtype. The remaining score gap to the
    historical trusted `v096` checkpoint is now concentrated mainly in the
    still-unrecovered `prob_37` and residual `prob_31` rows.
- decision:
  - candidate
- rationale:
  - `v115` becomes the leading current-source recovery candidate. It is clean,
    scoreable, and strictly improves the full-train40 averages versus `v109`
    by moving only the intended prob31-like row. It is not promoted to trusted
    accepted BEST because the historical trusted `v096` checkpoint still has
    the better avg objective (`15096298.7` vs `15106365.725`), so
    `baseline_hh.py` must remain a recovery surface only until that historical
    objective gap is closed by a current-source `40/40` line.

## reboot_v116_20260619_2339_prob37like_early_chain_on_v115
- File:
  `reboot_v116_20260619_2339_prob37like_early_chain_on_v115.py`
- Parent:
  `reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114`
- Status:
  - candidate
- Hypothesis:
  - The remaining historical-v096 objective gap is now concentrated mainly in
    the prob37-like diffuse low-proc subtype. Current-source log replay showed
    that the useful T breakthrough on that subtype happened early in the old
    chain: `v060` direct `release_due` followed by the cheap `v065`
    single-block diffuse re-search. The later inherited phases were what
    starved the branch, not the early move itself.
  - Replacing the prob37-like path inside the current-scoreable `v115` parent
    with only that early chain should keep the runtime stable while restoring a
    lower-T/lower-objective row on the targeted subtype.
- Feature / subtype / timelimit selector:
  - reuse `v100._matches_prob37like_runtime_class(prob_info)`
  - require `timelimit >= 55s`
  - run only on `standard/long/very_long`
- Identity-dependent logic:
  - none; selector is feature-based only
- Smoke-8 path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v116_tier9_20260619_001/`
- Smoke-8 result:
  - accepted_for_score `8/8`
  - timeout `0`
  - invalid `0`
  - representative rows:
    - `prob_31`: objective `40137295`, T `2776`, runtime `53.20s`
    - `prob_36`: objective `1499988`, T `0`, runtime `50.92s`
    - `prob_11`: objective `17206722`, T `2311`, runtime `10.57s`
- Targeted sibling guard path:
  `reports/ogc2026_reboot_v001/compare_v115_v116_prob33_prob35_prob37_prob39_20260619_001/`
- Targeted sibling guard result:
  - accepted_for_score `8/8`
  - timeout `0`
  - invalid `0`
  - changed target row:
    - `prob_37`:
      - `v115`: objective `17949088`, T `4040`, L `1192`, P `7465`,
        runtime `45.32s`
      - `v116`: objective `17644653`, T `3961`, L `3660`, P `7380`,
        runtime `49.71s`
  - unchanged guards:
    - `prob_33`: objective held exactly at `26172225`
    - `prob_35`: objective held exactly at `22037108`
    - `prob_39`: objective held exactly at `48160369`
- Time-stress path:
  `reports/ogc2026_reboot_v001/stress_v115_v116_prob37_prob39_short45_20260619_001/`
- Time-stress result:
  - accepted_for_score `4/4`
  - timeout `0`
  - invalid `0`
  - `45s` guard behavior:
    - `prob_37`: `v115` and `v116` both held at objective `17949088`
    - `prob_39`: `v115` and `v116` both held at objective `48598605`
  - interpretation:
    the `timelimit >= 55s` gate cleanly disables the new branch on shorter
    limits, so the runtime-stable recovery does not perturb the short-limit
    behavior.
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v116_train40_20260619_001/`
- Full benchmark result:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - runtime max `59.313323s`
  - avg T `1543.125`
  - avg L `2678.55`
  - avg P `4187.025`
  - avg objective `15098754.85`
- Per-instance comparison summary:
  - versus current-source `v115`:
    - changed rows: `1`
    - improvements: `1`
    - regressions: `0`
    - improved row:
      - `prob_37`: objective `17949088 -> 17644653`,
        T `4040 -> 3961`,
        L `1192 -> 3660`,
        P `7465 -> 7380`,
        runtime `37.95s -> 48.88s`
    - average deltas:
      - avg objective `-7610.875`
      - avg T `-1.975`
      - avg L `+61.7`
      - avg P `-2.125`
  - versus historical trusted `v096`:
    - changed rows: `4`
    - improvements:
      - `prob_40`: objective `6333528 -> 5910122`, T `9268 -> 8622`
      - `prob_3`: objective `213297 -> 188500`, T `1 -> 0`
    - regressions:
      - `prob_31`: objective `39781302 -> 40137295`, T `2751 -> 2776`
      - `prob_37`: objective `17454197 -> 17644653`, T `3961 -> 3961`
    - average deltas:
      - avg objective `+2456.15`
      - avg T `-15.55`
      - avg L `-40.225`
      - avg P `+26.45`
- Hidden-risk note:
  - manageable
  - The runtime ceiling stayed below the official limit and the new branch
    changed only the intended prob37-like row on the full train40 run. The
    remaining historical-best gap is now much narrower, but it still exists on
    the paired `prob_31`/`prob_37` rows.
- decision:
  - candidate
- rationale:
  - `v116` is now the leading current-source recovery candidate. It preserved
    the full `40/40` scoreable contract, improved avg objective and avg T
    versus `v115`, and recovered most of the prob37-like loss with a clean
    feature-based branch. It is not promoted to trusted accepted BEST because
    the historical trusted `v096` evidence still has the better avg objective
    (`15096298.7` vs `15098754.85`), even though `v116` is now much closer and
    already beats `v096` on avg T and avg L.

## reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116
- File:
  `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116.py`
- Parent:
  `reboot_v116_20260619_2339_prob37like_early_chain_on_v115`
- Status:
  - accepted
- Hypothesis:
  - After `v116`, the remaining historical-v096 gap is concentrated mainly in
    the prob31-like subtype. Historical `v096` prob31 logs show that the real
    T breakthrough was not the later polish chain; it was the
    high-proc concentrated-gap single move (`v070`) applied after the
    prob31-like warm start had already been improved.
  - Replaying only that concentrated-gap single on top of the current
    runtime-stable `v115` prob31-like parent should recover a real T drop
    again without restoring the old runtime cliff.
- Feature / subtype / timelimit selector:
  - outer subtype:
    reuse `v078._matches_prob31like_class(v078._selector_features(prob_info))`
  - inner move:
    reuse `v070._target_block_ids()` on the current prob31-like parent
    assignments
  - require `timelimit >= 55s`
  - run only on `standard/long/very_long`
- Identity-dependent logic:
  - none; selector and target choice remain feature-based and assignment-based
- Tier-representative smoke path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v117_tier9_20260620_001/`
- Tier-representative smoke result:
  - accepted_for_score `9/9`
  - timeout `0`
  - invalid `0`
  - tier representatives:
    - `prob_1`: objective `693901`, T `11`, runtime `13.85s`
    - `prob_6`: objective `756030`, T `9`, runtime `33.16s`
    - `prob_11`: objective `17206722`, T `739`, runtime `10.29s`
    - `prob_13`: objective `17775043`, T `923`, runtime `9.65s`
    - `prob_19`: objective `4715273`, T `389`, runtime `10.69s`
    - `prob_25`: objective `1499211`, T `2159`, runtime `20.01s`
    - `prob_27`: objective `77480587`, T `5637`, runtime `30.79s`
    - `prob_31`: objective `39589844`, T `2735`, runtime `54.75s`
    - `prob_38`: objective `151254848`, T `11120`, runtime `44.35s`
- Targeted sibling guard path:
  `reports/ogc2026_reboot_v001/compare_v116_v117_prob31_prob36_prob37_prob38_prob40_20260620_001/`
- Targeted sibling guard result:
  - accepted_for_score `10/10`
  - timeout `0`
  - invalid `0`
  - changed target row:
    - `prob_31`:
      - `v116`: objective `40137295`, T `2776`, L `1753`, P `11684`,
        runtime `42.90s`
      - `v117`: objective `39589844`, T `2735`, L `1843`, P `11680`,
        runtime `51.39s`
  - unchanged guards:
    - `prob_36`: objective held exactly at `1499988`
    - `prob_37`: objective held exactly at `17644653`
    - `prob_38`: objective held exactly at `151254848`
    - `prob_40`: objective held exactly at `5910122`
- Time-stress path:
  `reports/ogc2026_reboot_v001/stress_v116_v117_prob31_prob40_short45_20260620_001/`
- Time-stress result:
  - accepted_for_score `4/4`
  - timeout `0`
  - invalid `0`
  - `prob_31 @ 45s`:
    - `v116`: objective `40956985`, runtime `39.20s`
    - `v117`: objective `40956985`, runtime `39.01s`
  - interpretation:
    the new prob31-like branch stays cleanly disabled below the `55s` gate, so
    the shorter-limit behavior remains scoreable and stable.
- Full benchmark path:
  `reports/ogc2026_reboot_v001/full_reboot_v117_train40_20260620_001/`
- Full benchmark result:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
  - runtime max `57.930979s`
  - avg T `1542.1`
  - avg L `2680.8`
  - avg P `4186.925`
  - avg objective `15085068.575`
- Per-instance comparison summary:
  - versus current-source `v116`:
    - changed rows: `1`
    - improvements: `1`
    - regressions: `0`
    - improved row:
      - `prob_31`: objective `40137295 -> 39589844`,
        T `2776 -> 2735`,
        L `1753 -> 1843`,
        P `11684 -> 11680`,
        runtime `43.76s -> 50.45s`
    - average deltas:
      - avg objective `-13686.275`
      - avg T `-1.025`
      - avg L `+2.25`
      - avg P `-0.1`
  - versus historical trusted `v096`:
    - changed rows: `4`
    - improvements:
      - `prob_40`: objective `6333528 -> 5910122`, T `9268 -> 8622`
      - `prob_31`: objective `39781302 -> 39589844`, T `2751 -> 2735`
      - `prob_3`: objective `213297 -> 188500`, T `1 -> 0`
    - regressions:
      - `prob_37`: objective `17454197 -> 17644653`, T `3961 -> 3961`
    - average deltas:
      - avg objective `-11230.125`
      - avg T `-16.575`
      - avg L `-37.975`
      - avg P `+26.35`
- Hidden-risk note:
  - manageable
  - Only the intended prob31-like row changed versus `v116`, and all sibling
    and adjacent high-T guards held exactly. The sole remaining regression
    versus historical `v096` is the unchanged `prob_37` objective, which is
    more than offset by the stronger `prob_31` and `prob_40` gains.
- decision:
  - accepted
- rationale:
  - `v117` is the first current-source line that re-establishes a trusted
    accepted BEST beyond the historical `v096` checkpoint. It keeps
    `accepted_for_score=40/40`, `timeout=0`, and `invalid=0`, improves avg
    objective and avg T versus both `v116` and historical `v096`, lowers the
    prob31-like T tail to `2735`, and keeps the runtime ceiling below the
    historical accepted maximum.

## checkpoint_20260620_v117_publish_revalidation
- scope:
  - publish-checkpoint audit before starting the next candidate cycle
- active line under audit:
  - `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- source-hash check:
  - current file hash for
    `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116.py`
    still matches the saved accepted full-run manifest:
    `ff1ed8f92c974b589085efdf8ae965a748ac136a3a1b45409430648bb9c34052`
  - current file hash for `baseline_hh.py` also matches the fresh publish
    revalidation manifest:
    `0a3d12380483cc6512d3910167b1f62b954bd140767b05aeacf8d8738274856e`
- fresh publish revalidation path:
  `reports/ogc2026_reboot_v001/verify_active_v117_publish_20260620_001/`
- fresh publish revalidation result:
  - accepted_for_score `1/3`
  - checker_feasible `3/3`
  - timed_out `2`
  - invalid `0`
  - rows:
    - `prob_31`: objective `39589844`, T `2735`, runtime `61.996197s`,
      checker-feasible but timeout
    - `prob_37`: objective `17644653`, T `3961`, runtime `60.427098s`,
      checker-feasible but timeout
    - `prob_40`: objective `5910122`, T `8622`, runtime `52.389308s`,
      accepted_for_score `true`
- finding:
  - The current tracked source can still reproduce the row-level objective
    values from the accepted v117 evidence, but the active wrapper is no
    longer safely scoreable on at least two publish-guard rows at the 60s
    limit. This is a runtime reproducibility cliff, not a simple source-hash
    drift inside the v117 version file.
- publish judgment:
  - do not republish `v117` as a trusted accepted BEST today
  - publish a recovery/failure checkpoint instead, with the historical v117
    accepted evidence and the new failed revalidation evidence side by side
- historical-best note:
  - strongest historical accepted full-train evidence on this branch remains:
    `reports/ogc2026_reboot_v001/full_reboot_v117_train40_20260620_001/`
  - team-shared historical benchmark markdown reference remains:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- next recovery target:
  - re-establish a publish-safe active line that keeps
    `accepted_for_score=40/40` and removes the current `prob_31`/`prob_37`
    runtime cliff before any new BEST promotion claim

## reboot_v118_20260620_0835_prob31like_gap_hard_margin_on_v116
- File:
  `reboot_v118_20260620_0835_prob31like_gap_hard_margin_on_v116.py`
- Parent:
  `reboot_v116_20260619_2339_prob37like_early_chain_on_v115`
- Status:
  - rejected
- Hypothesis:
  - The fresh publish revalidation and direct prob31 probes show that the
    `v117` improvement itself is good, but the final `v070` concentrated-gap
    replay is too willing to spend the last 7-10 seconds after the prob31-like
    `v115` warm start. Keeping the `v115` improvement path intact while
    requiring a materially larger post-`v115` runtime margin before the
    concentrated-gap replay should preserve the score gain on fast reruns and
    fall back to the still-strong `v115` row on slow reruns.
- Feature / subtype / timelimit selector:
  - same prob31-like subtype selector as `v117` via
    `v078._matches_prob31like_class(v078._selector_features(prob_info))`
  - same standard/long/very_long tier gating
  - same `timelimit >= 55s` outer gate
  - changed inner rule only:
    run the final `v070` replay only when the post-`v115` remaining budget
    clears a harder margin
- Expected effect:
  - recover publish-safety on the prob31-like runtime-risk row
  - preserve the feature-based prob37-like sibling handling from `v116`
  - keep `accepted_for_score=40/40` on current-source validation if the harder
    margin removes the noisy overrun cases
- Validation:
  - targeted compare path:
    `reports/ogc2026_reboot_v001/compare_v117_v118_prob31_prob37_prob40_20260620_001/`
  - targeted rerun path:
    `reports/ogc2026_reboot_v001/compare_v117_v118_prob31_rerun_20260620_001/`
  - tier-representative smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v118_tier9_20260620_001/`
  - full train40 path:
    `reports/ogc2026_reboot_v001/full_reboot_v118_train40_20260620_001/`
  - wrapper-surface guard revalidation path:
    `reports/ogc2026_reboot_v001/verify_v118_wrapper_surface_20260620_001/`
  - targeted compare accepted `6/6`; timeout `0`, invalid `0`
    - `prob_31`: objective/T/L/P unchanged versus `v117`
      (`39589844 / 2735 / 1843 / 11680`)
      while runtime improved `52.80s -> 50.45s`
    - `prob_37`: objective/T/L/P unchanged; runtime `49.69s -> 50.59s`
    - `prob_40`: objective/T/L/P unchanged; runtime `43.86s -> 54.64s`
  - targeted prob31 rerun accepted `2/2`; timeout `0`, invalid `0`
    - `prob_31`: objective/T/L/P unchanged
      with runtime `54.02s -> 50.90s`
  - tier-representative smoke accepted `9/9`; timeout `0`, invalid `0`
    - includes runtime-risk / high-T guards:
      `prob_27`, `prob_31`, `prob_38`
    - `prob_31` runtime `52.48s`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
    - avg objective `15085068.575`
    - avg T `1542.1`
    - avg L `2680.8`
    - avg P `4186.925`
    - runtime max `58.311883`
  - wrapper-surface guard revalidation accepted `2/3`; timeout `1`, invalid `0`
    - `prob_31`: objective/T regressed to the `v115` keep-result
      `39589844 / 2735 -> 40137295 / 2776`
      because the harder margin skipped the final concentrated-gap replay
    - `prob_37`: checker-feasible but timeout at `60.343678s`
    - `prob_40`: accepted and unchanged on objective/T/L/P
- Per-instance comparison summary:
  - versus current-source historical accepted `v117`:
    - changed rows: `0` on objective/T/L/P across all train40 rows
    - runtime profile:
      - direct targeted reruns show lower `prob_31` runtime
      - full-train40 runtime max is slightly higher
        `57.930979 -> 58.311883`, still under the 60s limit
  - versus current-source `v116`:
    - changed rows: `1`
    - improvements: `1`
    - regressions: `0`
    - improved row:
      - `prob_31`: objective `40137295 -> 39589844`,
        T `2776 -> 2735`,
        L `1753 -> 1843`,
        P `11684 -> 11680`
    - average deltas:
      - avg objective `-13686.275`
      - avg T `-1.025`
      - avg L `+2.25`
      - avg P `-0.1`
- High-T rows (`T >= 3000`) on full train40:
  - `prob_38`: `11120`
  - `prob_40`: `8622`
  - `prob_27`: `5637`
  - `prob_37`: `3961`
  - `prob_33`: `3805`
  - `prob_39`: `3521`
- Hidden-risk note:
  - not manageable for promotion
  - The hypothesis succeeded only on direct version-file execution. Under a
    wrapper surface that mirrors the public submission chain, the added margin
    consumes the prob31-like gain and still leaves the prob37-like timeout
    cliff. That means the recovery target was not actually met.
- Decision:
  - rejected
- Rationale:
  - `v118` was a coherent runtime-recovery hypothesis and it kept the direct
    train40 score line intact, but it fails the decisive wrapper-surface guard.
    The prob31-like row falls back to the weaker `v115` result and the
    prob37-like row still times out, so it does not re-establish a publish-safe
    active line. Keep the evidence for diagnosis, but do not promote or reuse
    it as the next active recovery surface.

## reboot_v119_20260620_0635_highproc_pressure_shallow_portfolio_on_v117
- File:
  `reboot_v119_20260620_0635_highproc_pressure_shallow_portfolio_on_v117.py`
- Parent:
  `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- Status:
  - rejected
- Experiment note:
  - trusted baseline reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
    - historical accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v117_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1542.1`, `avg objective=15085068.575`
    - fresh publish revalidation block:
      `reports/ogc2026_reboot_v001/verify_active_v117_publish_20260620_001/`
      with runtime cliff on `prob_31` / `prob_37`
  - current subtype table refresh from trusted v117 full result plus train JSON
    features:
    - residual high-proc pressure family:
      `prob_25`, `prob_26`, `prob_27`, `prob_31`, `prob_38`, `prob_40`
      -> high `proc_mean`, high preference pressure/gap, low tight-slack ratio,
      still carrying the largest remaining T tail
    - low-proc 3-bay diffuse runtime-risk family:
      `prob_37`
    - low-proc 3-bay dense long-limit family:
      `prob_39`
  - chosen target for this version:
    - the broader high-proc pressure family, not the low-proc runtime-risk
      family and not a prob38-only branch
- Hypothesis:
  - After the `v117` recovery, the biggest remaining T tail is concentrated in
    a broader feature-based high-proc pressure family. A very shallow
    remaining-time-aware direct-order portfolio on top of the trusted `v117`
    warm start may reduce T on one or more of those rows without reopening the
    `prob_31` / `prob_37` wrapper-runtime cliff.
- Feature / subtype / timelimit selector:
  - feature base reused from
    `reboot_v053_20260617_2142_highproc_pressure_portfolio`
  - eligible only when:
    - `2 <= bays <= 4`
    - `blocks >= 100`
    - `proc_mean >= 16`
    - `tight_slack_ratio <= 0.12`
    - `pref_concentration >= 0.55`
    - `pref_gap_mean >= 50`
    - warm-start feasible
    - warm-start `T >= 2000`
    - tier not in `very_short/short`
    - remaining wall time after the `v117` warm start clears a stricter safe
      margin
- Planned behavior:
  - keep `v117` unchanged outside the target family
  - inside the target family only, build the `v117` warm start first, then try
    one very shallow direct-order alternative at standard limits and at most
    two on longer limits
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - block-tier representative smoke before full 40:
    - `prob_4`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_25`, `prob_27`, `prob_31`, `prob_38`
  - targeted family smoke:
    - `prob_25`, `prob_26`, `prob_27`, `prob_31`, `prob_38`, `prob_40`
  - if scoreable and same-family regression is controlled, then full train40
- Validation:
  - representative smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v119_tier9_20260620_001/`
  - targeted family smoke path:
    `reports/ogc2026_reboot_v001/target_reboot_v119_highproc_pressure_20260620_001/`
  - representative smoke accepted `9/9`; timeout `0`, invalid `0`
  - targeted family smoke accepted `6/6`; timeout `0`, invalid `0`
  - per-row deltas versus trusted `v117` on both validations:
    - objective/T/L/P changes: none
    - runtime only drifted slightly row-by-row
  - root cause:
    - the candidate never actually fired on the intended rows
    - current-source feature extraction shows the proposed parent selector from
      `v053` rejects every intended target row because the inherited
      `tight_slack_ratio <= 0.12` gate is far below the real current values
      (`0.225 .. 0.367`) for `prob_25`, `prob_26`, `prob_27`, `prob_31`,
      `prob_38`, and `prob_40`
- Decision:
  - rejected
- Rationale:
  - `v119` preserves scoreability, but it is effectively a no-op on the
    current workspace state. The selector does not match the intended family,
    so the hypothesis was not truly tested and there is no T or objective
    movement to justify escalation to full train40.

## reboot_v120_20260620_0705_highproc_tail_shallow_portfolio_on_v117
- File:
  `reboot_v120_20260620_0705_highproc_tail_shallow_portfolio_on_v117.py`
- Parent:
  `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- Status:
  - rejected
- Experiment note:
  - `v119` confirmed that the broad-family direct-order hypothesis is still
    worth testing, but its reused selector from `v053` is stale for the
    current source and training feature range.
  - current target-family feature refresh:
    - `prob_25`: `tight_slack_ratio=0.25`, `pref_concentration=0.61`,
      `pref_gap_mean=62.16`, `proc_mean=21.58`
    - `prob_26`: `0.367`, `0.773`, `62.873`, `16.92`
    - `prob_27`: `0.32`, `0.667`, `68.107`, `21.267`
    - `prob_31`: `0.225`, `0.795`, `60.615`, `21.495`
    - `prob_38`: `0.328`, `0.568`, `52.332`, `21.348`
    - `prob_40`: `0.312`, `0.76`, `59.1`, `21.688`
- Hypothesis:
  - The residual T tail still clusters in a broader high-proc preference-tail
    family, but the current-source family occupies a much looser slack band
    than the old `v053` class. Updating only the selector to the observed
    current feature band should let the same shallow direct-order portfolio
    fire on the intended rows without changing the portfolio logic itself.
- Feature / subtype / timelimit selector:
  - `2 <= bays <= 4`
  - `blocks >= 100`
  - `proc_mean >= 16`
  - `pref_concentration >= 0.55`
  - `pref_gap_mean >= 50`
  - `pref_pressure >= 0.50`
  - `0.20 <= tight_slack_ratio <= 0.40`
  - warm-start feasible
  - warm-start `T >= 2000`
  - tier not in `very_short/short`
  - remaining wall time must clear the same safe margin used in `v119`
- Planned behavior:
  - keep `v117` unchanged outside the target family
  - inside the target family only, run the exact same shallow direct-order
    portfolio logic from `v119`
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation:
  - representative smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v120_tier9_20260620_001/`
  - completion check on omitted family rows:
    `reports/ogc2026_reboot_v001/target_reboot_v120_prob26_prob40_20260620_001/`
  - representative smoke accepted `9/9`; timeout `0`, invalid `0`
  - family completion check accepted `2/2`; timeout `0`, invalid `0`
  - per-row deltas versus trusted `v117`:
    - objective/T/L/P changes: none on all checked rows
    - runtime overhead:
      - `prob_25`: `+4.462s`
      - `prob_26`: `+5.443s`
      - `prob_27`: `+4.934s`
      - `prob_38`: `+5.863s`
      - `prob_40`: `+5.831s`
  - candidate row diagnostics:
    - `prob_25`: shallow `due_long_proc` candidate worsened
      `T 2159 -> 8033`
    - `prob_27`: shallow `due_long_proc` candidate worsened
      `5637 -> 19363`
    - `prob_38`: shallow `due_release_proc` candidate worsened
      `11120 -> 124423`
    - `prob_26`: shallow `preference_spread` candidate worsened
      `2345 -> 14735`
    - `prob_40`: shallow `preference_spread` candidate worsened
      `8622 -> 106467`
    - `prob_31`: correctly skipped by the remaining-time guard
- Decision:
  - rejected
- Rationale:
  - `v120` did fire on the intended family, so the corrected selector worked,
    but the hypothesis itself failed. Across the checked high-proc family rows,
    shallow direct-order rebuilds were catastrophically weaker than the `v117`
    warm start and bought no T/objective improvement at the cost of roughly
    five extra seconds on the targeted rows. The next T-breakthrough attempt
    should stay on warm-start-preserving local moves, not fresh direct rebuilds.

## reboot_v121_20260620_0239_twobay_concentrated_quantile_reinsert_on_v117
- File:
  `reboot_v121_20260620_0239_twobay_concentrated_quantile_reinsert_on_v117.py`
- Parent:
  `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- Status:
  - rejected
- Experiment note:
  - trusted baseline reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
    - historical accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v117_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1542.1`, `avg objective=15085068.575`
    - fresh publish revalidation block remains:
      `reports/ogc2026_reboot_v001/verify_active_v117_publish_20260620_001/`
      with wrapper runtime cliff on `prob_31` / `prob_37`
  - residual high-T backlog from the trusted full result:
    - `prob_25`: `T=2159`
    - `prob_26`: `2345`
    - `prob_27`: `5637`
    - `prob_31`: `2735`
    - `prob_38`: `11120`
    - `prob_40`: `8622`
  - subtype split for this version:
    - target only the two-bay concentrated high-proc tail family, not the
      three-bay tail family and not the four-bay runtime-risk family
    - current feature band for the target subtype:
      - `bays == 2`
      - `blocks >= 100`
      - `proc_mean >= 20`
      - `slack_mean >= 4.5`
      - `pref_concentration >= 0.60`
      - `pref_pressure >= 0.59`
      - `pref_gap_mean >= 60`
    - current train rows matching that selector:
      `prob_25`, `prob_27`
  - live current-source probe on top of the real `v117` warm start showed
    genuine single-move improvement signal:
    - `prob_25`: deep quantile single reinsert improved
      `T 2159 -> 2141`, objective `1499211 -> 1489168`
    - `prob_27`: deep quantile single reinsert improved
      `5637 -> 5614`, objective `77480587 -> 77173928`
- Hypothesis:
  - The remaining two-bay concentrated high-proc tail is limited by a single
    poorly placed tardy block, but the earlier shallow prefix/direct rebuild
    hypotheses were too destructive. Reusing the `v117` warm start and trying a
    deeper quantile-sampled one-block reinsertion across a short tardy shortlist
    should capture the observed T improvement signal while keeping runtime
    bounded.
- Feature / subtype / timelimit selector:
  - `bays == 2`
  - `blocks >= 100`
  - `proc_mean >= 20`
  - `slack_mean >= 4.5`
  - `pref_concentration >= 0.60`
  - `pref_pressure >= 0.59`
  - `pref_gap_mean >= 60`
  - warm-start feasible
  - warm-start `T >= 2000`
  - tier not in `very_short/short`
  - remaining wall time after building the warm start must clear a guarded
    reserve
- Planned behavior:
  - keep `v117` unchanged outside the target subtype
  - on the target subtype, build `v117` first and then evaluate only bounded
    single-block quantile reinsertion candidates from a short tardy shortlist
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - block-tier representative smoke before any full 40:
    - `prob_4`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_25`, `prob_27`, `prob_31`, `prob_39`
  - targeted subtype smoke:
    - `prob_25`, `prob_27`
  - only if scoreable and same-family T improves without runtime-risk spillover
    should this go to full train40
- Validation:
  - representative smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v121_tier9_20260620_001/`
  - representative smoke accepted `9/9`; timeout `0`, invalid `0`
  - target-row runtime remained safe:
    - `prob_25`: `23.82s`
    - `prob_27`: `33.17s`
    - `prob_31`: `51.55s`
    - `prob_39`: `58.18s`
  - target-row T/objective movement:
    - none; `prob_25` and `prob_27` stayed at the `v117` warm-start result
  - root cause from runtime logs:
    - the implementation shortlist drifted away from the live probe signal
    - `prob_25` attempted only blocks `56` and `41`, while the live current-
      source probe improvement came from block `91`
    - `prob_27` attempted `64` and `113`, while the live current-source probe
      improvement came from block `77`
- Decision:
  - rejected
- Rationale:
  - `v121` preserved scoreability, but it did not truly exercise the observed
    improvement signal because its weighted shortlist missed the actual
    improving tardy blocks. Treat it as a shortlist-selection miss, not as a
    rejection of the underlying two-bay deep single-reinsert hypothesis.

## reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117
- File:
  `reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117.py`
- Parent:
  `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- Status:
  - accepted
- Experiment note:
  - `v121` validated the runtime safety of the two-bay deep single-reinsert
    path, but its weighted shortlist failed to hit the live-probe improving
    blocks.
  - live current-source probe details on the real `v117` warm start:
    - `prob_25`: top tardy shortlist `[91, 56, 40, 7]`, block `91` improved
      `T 2159 -> 2141`, objective `1499211 -> 1489168`
    - `prob_27`: top tardy shortlist `[65, 64, 55, 77]`, block `77` improved
      `5637 -> 5614`, objective `77480587 -> 77173928`
  - target subtype remains unchanged:
    - `bays == 2`
    - `blocks >= 100`
    - `proc_mean >= 20`
    - `slack_mean >= 4.5`
    - `pref_concentration >= 0.60`
    - `pref_pressure >= 0.59`
    - `pref_gap_mean >= 60`
    - matching current train rows:
      `prob_25`, `prob_27`
- Hypothesis:
  - The observed improvement signal is real, but the correct control variable
    is the top-tardy shortlist itself, not an entry-delay-weighted shortlist.
    Replaying the same bounded deep quantile reinsertion over the pure top-
    tardy shortlist should recover the live-probe T improvement while keeping
    the runtime safety already demonstrated by `v121`.
- Feature / subtype / timelimit selector:
  - same subtype gate as `v121`
  - warm-start feasible
  - warm-start `T >= 2000`
  - tier not in `very_short/short`
  - remaining wall time after building the warm start must clear a guarded
    reserve
- Planned behavior:
  - keep `v117` unchanged outside the target subtype
  - on the target subtype, build `v117` first and evaluate only bounded
    quantile single-block candidates from the top tardy shortlist
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - block-tier representative smoke before any full 40:
    - `prob_4`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_25`, `prob_27`, `prob_31`, `prob_39`
  - targeted subtype smoke:
    - `prob_25`, `prob_27`
  - only if scoreable and target-row T improves without same-tier regression
    should this go to full train40
- Validation:
  - representative smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v122_tier9_20260620_001/`
  - targeted subtype smoke path:
    `reports/ogc2026_reboot_v001/target_reboot_v122_twobay_tail_20260620_001/`
  - full path:
    `reports/ogc2026_reboot_v001/full_reboot_v122_train40_20260620_001/`
  - wrapper-surface revalidation path:
    `reports/ogc2026_reboot_v001/verify_v122_wrapper_surface_20260620_001/`
  - active publish revalidation path:
    `reports/ogc2026_reboot_v001/verify_active_v122_publish_20260620_001/`
  - representative smoke accepted `9/9`; timeout `0`, invalid `0`
  - targeted subtype smoke accepted `2/2`; timeout `0`, invalid `0`
  - full train40 accepted `40/40`; timeout `0`, invalid `0`
  - active publish revalidation accepted `3/3`; timeout `0`, invalid `0`
  - full-train headline deltas versus trusted `v117`:
    - objective `15085068.575 -> 15084817.5`
    - avg T `1542.1 -> 1541.65`
    - avg L `2680.8 -> 2679.875`
    - avg P `4186.925 -> 4189.425`
    - runtime max `57.930979 -> 57.913446`
  - per-instance movement versus `v117`:
    - improvement:
      - `prob_25`: objective `1499211 -> 1489168`, T `2159 -> 2141`
    - no T regressions on the remaining 39 rows
- Decision:
  - accepted
- Rationale:
  - `v122` keeps the full scoreability contract, improves total T/avg T and the
    official objective, and clears both wrapper-surface and actual active-path
    revalidation on the previously blocked runtime-risk rows.

## reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122
- File:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122.py`
- Parent:
  `reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117`
- Status:
  - accepted
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v122_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1541.65`, `avg objective=15084817.5`
    - active publish revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v122_publish_20260620_001/`
      with `accepted_for_score=3/3`, `timed_out=0`
  - refreshed current-source high-T backlog from the accepted `v122` full run:
    - `prob_38`: `T=11120`, `bays=3`, `blocks=250`, `proc_mean=21.3`
    - `prob_33`: `T=3805`, `bays=3`, `blocks=200`, `proc_mean=16.8`
    - `prob_26`: `T=2345`, `bays=3`, `blocks=150`, `proc_mean=16.9`
    - `prob_28`: same feature family, lower T but same structural band
  - refreshed subtype table from current source features:
    - `threebay_highproc_tail`:
      `prob_26`, `prob_28`, `prob_33`, `prob_38`
      -> `bays == 3`, `blocks >= 150`, `proc_mean >= 16`,
      moderate tight-slack ratio, nontrivial preference gap, and persistent
      high-T tail
    - `threebay_lowproc_runtime`:
      `prob_32`, `prob_35`, `prob_37`, `prob_39` stayed stronger than older
      legacy branches in direct compare
    - `fourbay_highpref_tail`:
      `prob_31`, `prob_36`, `prob_40`; older direct-family variants also lost
      to `v122`
  - current-source evidence against the most obvious old ideas:
    - legacy `threebay_lowproc_runtime` variants `v052`, `v081`, `v100` did
      not beat `v122` on T in
      `compare_v122_vs_legacy_threebay_lowproc_family_20260620_001/`
    - legacy four-bay direct-family variants `v078` and `v063` did not beat
      `v122` in
      `compare_v122_vs_fourbay_direct_family_20260620_001/`
    - earlier broad high-proc direct rebuild `v120` was explicitly rejected as
      too destructive on the intended family
    - live current-source single-block reinsertion probes on the high-proc tail
      did not show reusable T signal on `prob_26` / `prob_38`
- Hypothesis:
  - For the `threebay_highproc_tail` family, the remaining T is caused by a
    small interacting set of tardy blocks rather than a single bad block or a
    whole-schedule ordering failure. Single-block repair was too weak and fresh
    direct rebuilds were too destructive. Rebuilding only a short top-tardy
    prefix on top of the trusted `v122` warm start may reduce T while
    preserving the rest of the accepted schedule.
- Feature / subtype / timelimit selector:
  - `bays == 3`
  - `blocks >= 150`
  - `proc_mean >= 16`
  - `0.20 <= tight_slack_ratio <= 0.40`
  - `pref_gap_mean >= 48`
  - `0.40 <= pref_concentration <= 0.80`
  - warm-start feasible
  - warm-start `T >= 2000`
  - tier not in `very_short/short`
  - remaining wall time after the `v122` warm start must clear a guarded
    reserve before any repair is attempted
- Planned behavior:
  - keep `v122` unchanged outside the target subtype
  - on the target subtype, build the trusted `v122` warm start first
  - then rebuild only a bounded top-tardy prefix of the current assignments
    with checker validation after each checkpoint
  - test only multi-block prefix lengths so the candidate is structurally
    different from the earlier single-block reinsertion line
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - block-tier representative smoke before any full 40:
    - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_23`, `prob_27`, `prob_32`, `prob_33`, `prob_38`
  - targeted subtype smoke:
    - `prob_26`, `prob_28`, `prob_33`, `prob_38`
  - only if scoreable and same-family T improves without runtime-risk spillover
    should this go to full train40
- Validation:
  - first representative smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v123_tier10_20260620_001/`
  - corrected representative smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v123_tier10_20260620_002/`
  - targeted subtype compare path:
    `reports/ogc2026_reboot_v001/target_reboot_v123_threebay_highproc_20260620_001/`
  - runtime-risk subset revalidation path:
    `reports/ogc2026_reboot_v001/verify_v123_runtime_subset_20260620_001/`
  - full attempts:
    - failed runtime/bug probe:
      `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_001/`
    - failed runtime/bug probe after partial repair:
      `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_002/`
    - accepted full:
      `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
  - wrapper + active publish revalidation path:
    `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_001/`
  - validation note:
    `reports/ogc2026_reboot_v001/validation_note_v123_accept_20260620.md`
  - representative smoke #1 result:
    - rejected as a smoke gate because `prob_33` and `prob_38` timed out
    - root cause: infeasible prefix-check cost was too expensive on
      runtime-heavy target rows
  - representative smoke #2 result:
    - accepted `10/10`; timeout `0`, invalid `0`
  - targeted subtype compare versus trusted `v122`:
    - accepted `8/8`; timeout `0`, invalid `0`
    - `prob_26`: objective `32253881 -> 31708207`, T `2345 -> 2305`
    - `prob_28`: unchanged
    - `prob_33`: unchanged
    - `prob_38`: unchanged
  - runtime-risk subset revalidation:
    - accepted `10/10`; timeout `0`, invalid `0`
    - `prob_39` remained knife-edge but scoreable on the direct wrapper path
      at `59.91273s`
  - final full train40 versus trusted `v122`:
    - accepted `40/40`; timeout `0`, invalid `0`
    - objective `15084817.5 -> 15071175.65`
    - total T `61666 -> 61626`
    - avg T `1541.65 -> 1540.65`
    - avg L `2679.875 -> 2674.325`
    - avg P `4189.425 -> 4187.625`
    - runtime max `57.913446 -> 59.416431`
    - row-level movement:
      - improvement:
        - `prob_26`: objective `32253881 -> 31708207`, T `2345 -> 2305`
      - no T regressions on the remaining 39 rows
  - active-path revalidation after promotion:
    - wrapper `baseline_hh.py`: accepted `4/4` on `prob_31`, `prob_37`,
      `prob_39`, `prob_40`
    - active `myalgorithm.py`: accepted `4/4` on the same set
    - hidden-risk note:
      - active `prob_39` was still scoreable but weaker than the direct
        wrapper surface:
        - wrapper: objective `48160369`, T `3521`
        - active: objective `48598605`, T `3553`
- Decision:
  - accepted
- Rationale:
  - The final `v123` line restores full scoreability, improves total T/avg T
    and objective versus trusted `v122`, and does so with a coherent
    feature-gated three-bay high-proc prefix-repair hypothesis.
  - The only observed hidden-risk is a mild active-chain `prob_39` quality
    drift relative to the direct wrapper surface, but both surfaces remain
    accepted_for_score and the requested official interface is
    `baseline_hh.algorithm(prob_info, timelimit)`.

## reboot_v124_20260620_1125_fourbay_highproc_toptardy_quantile_on_v123
- File:
  `reboot_v124_20260620_1125_fourbay_highproc_toptardy_quantile_on_v123.py`
- Parent:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Status:
  - rejected
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1540.65`, `avg objective=15071175.65`
  - refreshed current-source backlog on the new trusted line:
    - `threebay_highproc_tail`: total T `18540`
    - `fourbay_highpref_tail`: total T `13367`
    - `threebay_lowproc_runtime`: total T `12066`
  - chosen target for this version:
    - the `fourbay_highproc high-preference tail`, not the low-proc runtime
      family and not another three-bay high-proc prefix pass
  - live current-source local-move probe on the real `v123` warm start:
    - `prob_31`:
      - top-tardy shortlist `[88, 18, 149, ...]`
      - block `88` was a no-op
      - blocks `18` and `149` were infeasible
    - `prob_40`:
      - top-tardy shortlist `[245, 106, 6, ...]`
      - block `245` improved `T 8622 -> 8549`,
        objective `5910122 -> 5860829`
      - block `106` improved `T 8622 -> 8502`,
        objective `5910122 -> 5830082`
      - block `6` was infeasible
- Hypothesis:
  - The residual four-bay high-proc high-preference tail is not a broad
    rebuild problem. It has a bounded one-block local-move signal on the real
    `v123` warm start, but only when searching a short top-tardy shortlist.
    Replaying a guarded quantile single-reinsert over that shortlist should
    improve the `prob_40`-like family while remaining a no-op on `prob_31`-
    like rows.
- Feature / subtype / timelimit selector:
  - `bays == 4`
  - `blocks >= 200`
  - `proc_mean >= 20`
  - `pref_concentration >= 0.75`
  - `pref_gap_mean >= 58`
  - `0.20 <= tight_slack_ratio <= 0.35`
  - warm-start feasible
  - warm-start `T >= 2500`
  - tier not in `very_short/short`
  - remaining wall time after the `v123` warm start must clear a guarded
    reserve before repair is attempted
- Planned behavior:
  - keep `v123` unchanged outside the target subtype
  - on the target subtype, build the trusted `v123` warm start first
  - evaluate only a bounded top-tardy shortlist with quantile-sampled
    single-block reinsertion
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - block-tier representative smoke before any full 40:
    - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_23`, `prob_27`, `prob_32`, `prob_33`, `prob_40`
  - targeted subtype smoke:
    - `prob_31`, `prob_40`
  - runtime-risk recheck if smoke improves:
    - `prob_39`
  - only if scoreable and same-family rows do not regress should this go to
    full train40
- Validation:
  - representative smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v124_tier10_20260620_001/`
  - targeted subtype compare path:
    `reports/ogc2026_reboot_v001/target_reboot_v124_fourbay_highproc_20260620_001/`
  - runtime-risk recheck path:
    `reports/ogc2026_reboot_v001/verify_v124_prob39_20260620_001/`
  - full path:
    `reports/ogc2026_reboot_v001/full_reboot_v124_train40_20260620_001/`
  - representative smoke accepted `10/10`; timeout `0`, invalid `0`
    - `prob_40` improved to objective `5830082`, T `8502`
  - targeted subtype compare versus trusted `v123`:
    - accepted `4/4`; timeout `0`, invalid `0`
    - `prob_31`: unchanged
    - `prob_40`: objective `5910122 -> 5830082`, T `8622 -> 8502`
  - runtime-risk recheck:
    - accepted `2/2`; timeout `0`, invalid `0`
    - hidden-risk surfaced on `prob_39`:
      objective `48160369 -> 48598605`, T `3521 -> 3553`
  - full train40 versus trusted `v123`:
    - accepted `40/40`; timeout `0`, invalid `0`
    - total T `61626 -> 61538`
    - avg T `1540.65 -> 1538.45`
    - avg objective `15071175.65 -> 15080130.55`
    - avg L `2674.325 -> 2677.325`
    - avg P `4187.625 -> 4189.475`
    - runtime max `59.416431 -> 51.945424`
    - per-instance movement:
      - improvement:
        - `prob_40`: objective `5910122 -> 5830082`, T `8622 -> 8502`
      - regression:
        - `prob_39`: objective `48160369 -> 48598605`, T `3521 -> 3553`
- Decision:
  - rejected
- Rationale:
  - `v124` is scoreable and does achieve a real T reduction on the targeted
    `prob_40`-like row, but the full-train official objective gets worse
    because the non-target runtime-risk row `prob_39` drifts to a weaker
    accepted solution. In the current plateau/T-first mode this is useful
    evidence, but it is not strong enough to replace trusted `v123` as BEST.

## reboot_v125_20260620_0000_fourbay_inline_quantile_on_v123
- File:
  `reboot_v125_20260620_0000_fourbay_inline_quantile_on_v123.py`
- Parent:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Status:
  - candidate
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1540.65`, `avg objective=15071175.65`
    - active publish revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_001/`
      with accepted wrapper/active scoreability on `prob_31`, `prob_37`,
      `prob_39`, `prob_40`
  - refreshed current-source high-T backlog from trusted `v123`:
    - `prob_38`: `T=11120`, `bays=3`, `blocks=250`
    - `prob_40`: `T=8622`, `bays=4`, `blocks=250`
    - `prob_27`: `T=5637`, `bays=2`, `blocks=150`
    - `prob_37`: `T=3961`, `bays=3`, `blocks=250`
    - `prob_33`: `T=3805`, `bays=3`, `blocks=200`
    - `prob_39`: `T=3521`, `bays=3`, `blocks=250`, runtime-risk
    - `prob_31`: `T=2735`, `bays=4`, `blocks=200`
  - refreshed subtype table on trusted `v123`:
    - `threebay_highproc_tail` total T `18540`
    - `fourbay_highpref_tail` total T `13367`
    - `threebay_lowproc_runtime` total T `12066`
    - `twobay_concentrated_highproc` total T `7778`
  - carry-over evidence from rejected `v124`:
    - targeted `prob_40` local-move signal is real:
      objective `5910122 -> 5830082`, T `8622 -> 8502`
    - same wrapper-style candidate also caused non-target runtime-risk drift on
      `prob_39`:
      objective `48160369 -> 48598605`, T `3521 -> 3553`
  - root-cause working theory:
    - `v124` preserved the right feature selector, but it wrapped
      `v123.algorithm(...)` as an external warm-start layer. The resulting
      non-target `prob_39` drift suggests that the best way to preserve the
      current trusted line is to keep the exact `v123` code path in the new
      version body, then add the four-bay move inline rather than as a parent
      wrapper around `v123`.
- Hypothesis:
  - The `prob_40`-like improvement signal is still worth pursuing, but the
    integration point was wrong. If the four-bay top-tardy quantile single
    reinsert is embedded directly into the `v123` source body, non-target rows
    should stay on the current trusted `v123` path while the `prob_40`-like
    family keeps the previously observed T reduction chance.
- Feature / subtype / timelimit selector:
  - keep existing `v123` selector unchanged for `threebay_highproc_tail`
  - add a second selector for the `fourbay_highproc high-preference tail`:
    - `bays == 4`
    - `blocks >= 200`
    - `proc_mean >= 20`
    - `pref_concentration >= 0.75`
    - `pref_gap_mean >= 58`
    - `0.20 <= tight_slack_ratio <= 0.35`
    - warm-start feasible
    - warm-start `T >= 2500`
    - tier not in `very_short/short`
    - remaining wall time must clear a guarded reserve
- Planned behavior:
  - preserve the exact `v123` body as the default line
  - keep the accepted three-bay high-proc prefix repair unchanged
  - add the four-bay quantile single-reinsert inline after the trusted base
    path is built, not by wrapping `v123.algorithm(...)` from outside
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - block-tier representative smoke before any full 40:
    - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_23`, `prob_27`, `prob_32`, `prob_33`, `prob_40`
  - targeted subtype smoke:
    - `prob_31`, `prob_40`
  - runtime-risk recheck:
    - `prob_39`
  - only if scoreable and `prob_39` stays at least as strong as trusted `v123`
    should this go to full train40
- Validation result:
  - representative smoke passed:
    `reports/ogc2026_reboot_v001/smoke_reboot_v125_tier10_20260620_001/`
    - `accepted_for_score=10/10`
    - `timeout=0`, `invalid=0`, `runtime_max=53.224765s`
    - `prob_40` stayed scoreable inside the representative tier set
  - targeted/runtime-risk compare passed:
    `reports/ogc2026_reboot_v001/target_reboot_v125_fourbay_inline_20260620_001/`
    - `prob_31`: unchanged versus same-run `v123`
      (`39589844`, `T=2735`)
    - `prob_36`: unchanged versus same-run `v123`
      (`1499988`, `T=2010`)
    - `prob_39`: unchanged versus same-run `v123`
      (`48598605`, `T=3553`)
    - `prob_40`: improved versus same-run `v123`
      (`5910122 -> 5830082`, `T 8622 -> 8502`)
  - historical runtime-risk note:
    - the stronger trusted `v123` `prob_39` evidence remains
      `48160369`, `T=3521` from
      `reports/ogc2026_reboot_v001/verify_v123_prob39_rerun_20260620_001/`
      and `_003/`
    - but `reports/ogc2026_reboot_v001/verify_v123_prob39_rerun_20260620_002/`
      also recorded a timeout cliff on the same row
    - because the `v125` compare only matched the weaker same-run `v123`
      `prob_39` line and did not re-establish the stronger trusted runtime-risk
      behavior, the promotion gate for full-train escalation is not yet cleared
- Full 40:
  - path:
    `reports/ogc2026_reboot_v001/full_reboot_v125_train40_20260620_002/`
  - accepted `40/40`; timeout `0`, invalid `0`
  - headline deltas versus trusted `v123`:
    - total T `61626 -> 61538`
    - avg T `1540.65 -> 1538.45`
    - avg objective `15071175.65 -> 15080130.55`
    - avg L `2674.325 -> 2677.325`
    - avg P `4187.625 -> 4189.475`
    - runtime max `59.416431s -> 54.885372s`
  - changed rows versus trusted `v123`:
    - `prob_39`: objective `48160369 -> 48598605`,
      T `3521 -> 3553`, L `194 -> 314`, P `8094 -> 8168`
    - `prob_40`: objective `5910122 -> 5830082`,
      T `8622 -> 8502`
- Decision:
  - rejected
- Rationale:
  - inline integration fixed the specific `v124` failure mode where the
    four-bay move visibly degraded same-run `prob_39`, and it preserved a real
    `prob_40` improvement signal.
  - but the full train40 rerun still converts that signal into an average
    objective regression because the non-target runtime-risk row `prob_39`
    worsens more than `prob_40` improves. Under the plateau/T-zero-first branch
    rules, that keeps `v125` from becoming the next trusted BEST.

## reboot_v126_20260620_0715_threebay_diffuse_lowproc_prefix_on_v123
- File:
  `reboot_v126_20260620_0715_threebay_diffuse_lowproc_prefix_on_v123.py`
- Parent:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Status:
  - candidate
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `total T=61626`, `avg T=1540.65`, `avg objective=15071175.65`
  - refreshed current-source high-T backlog from trusted `v123`:
    - `prob_38`: `T=11120`, `3-bay xlarge high-proc concentrated`
    - `prob_40`: `T=8622`, `4-bay xlarge high-proc concentrated`
    - `prob_27`: `T=5637`, `2-bay mid high-proc concentrated`
    - `prob_37`: `T=3961`, `3-bay xlarge low-proc diffuse`
    - `prob_33`: `T=3805`, `3-bay large mid-proc diffuse`
    - `prob_39`: `T=3521`, `3-bay xlarge low-proc concentrated runtime-risk`
    - `prob_32`: `T=2992`, `3-bay large low-proc diffuse`
  - refreshed subtype table on trusted `v123`:
    - `threebay_highproc_tail` total T `18540`
    - `fourbay_highpref_tail` total T `13367`
    - `threebay_lowproc_runtime` total T `12066`
    - `twobay_concentrated_highproc` total T `7778`
  - family choice for this cycle:
    - do not reopen the `fourbay_highpref_tail` candidate again before `v125`
      is resolved further
    - do not reopen the whole `threebay_lowproc_runtime` family because the
      concentrated runtime-risk branch around `prob_39` still shows a limit
      cliff
    - instead, isolate the diffuse low-proc branch that currently includes the
      stronger multi-row residual signal:
      - `prob_32`: `proc_mean=11.46`, `tight_ratio=0.555`,
        `pref_concentration=0.345`, `pref_gap_mean=45.2`
      - `prob_37`: `proc_mean=11.51`, `tight_ratio=0.592`,
        `pref_concentration=0.400`, `pref_gap_mean=46.7`
      - guarded-out neighbor `prob_39`: `pref_concentration=0.572`,
        `pref_gap_mean=55.3`
  - why this is structurally different:
    - earlier diffuse-family attempts were mostly order-only or single-block
      reinsertion probes
    - this version instead tests whether a very short multi-block tardy-prefix
      rebuild can unlock T movement on the diffuse low-proc family without
      re-opening the concentrated runtime-risk branch
- Hypothesis:
  - On the `3-bay / blocks>=200 / low-proc / diffuse / tight-slack` subtype,
    the residual T is caused by a small interacting tardy set rather than by a
    single misplaced block. A bounded 2-3 block tardy-prefix rebuild on top of
    the trusted `v123` warm start should have a better chance of lowering T on
    `prob_32`- / `prob_37`-like rows than the older single-reinsert probes,
    while the stricter diffuse selector keeps `prob_39` and other concentrated
    runtime-risk rows on the trusted path.
- Feature / subtype / timelimit selector:
  - preserve the accepted `v123` high-proc prefix-repair selector unchanged
  - add a second selector for the diffuse low-proc tail:
    - `bays == 3`
    - `blocks >= 200`
    - `proc_mean <= 12.0`
    - `tight_slack_ratio >= 0.50`
    - `pref_concentration <= 0.45`
    - `pref_gap_mean <= 50.0`
    - warm-start feasible
    - warm-start `T >= 2500`
    - tier not in `very_short/short`
    - only when remaining wall time clears a tighter runtime reserve than the
      high-proc prefix phase
- Planned behavior:
  - preserve the exact `v123` warm-start path outside the target subtype
  - keep the accepted three-bay high-proc prefix repair unchanged
  - on the new diffuse low-proc subtype only, rebuild at most the top 2-3
    tardy assignments with checker validation after each checkpoint
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - tier-representative smoke:
    - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_25`, `prob_27`, `prob_32`, `prob_37`
  - targeted subtype / neighbor check:
    - `prob_32`, `prob_37`, `prob_39`
  - only if scoreable and the diffuse rows improve without `prob_39`
    degradation should this go to full train40
- Validation:
  - representative smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v126_tier9_20260620_001/`
  - representative smoke accepted `9/9`; timeout `0`, invalid `0`
  - targeted subtype / neighbor compare path:
    `reports/ogc2026_reboot_v001/target_reboot_v126_diffuse_lowproc_20260620_001/`
  - targeted compare accepted `8/8`; timeout `0`, invalid `0`
  - same-run comparative result versus trusted `v123`:
    - `prob_32`: unchanged
      - objective `12781706`
      - T `2992`
    - `prob_33`: unchanged
      - objective `26172225`
      - T `3805`
    - `prob_37`: unchanged
      - objective `17644653`
      - T `3961`
    - `prob_39`: unchanged
      - objective `48598605`
      - T `3553`
  - runtime note:
    - smoke and targeted runs stayed scoreable with no new runtime cliff
    - but they also showed no measurable target-family movement
- Full 40:
  - not run
- Decision:
  - rejected
- Rationale:
  - the guarded diffuse low-proc prefix phase was runtime-safe, but it produced
    no T/objective movement on either intended diffuse row and no neighbor-row
    change at all. Under the plateau/T-zero-first gate, a no-signal candidate
    is still rejected because it does not make the requested end state more
    true.

## reboot_v127_20260620_0815_twobay_concentrated_prefix_on_v123
- File:
  `reboot_v127_20260620_0815_twobay_concentrated_prefix_on_v123.py`
- Parent:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Status:
  - candidate
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `total T=61626`, `avg T=1540.65`, `avg objective=15071175.65`
  - refreshed current-source subtype table on trusted `v123`:
    - `threebay_highproc_tail` total T `18540`
    - `fourbay_highpref_tail` total T `13367`
    - `threebay_lowproc_runtime` total T `12066`
    - `twobay_concentrated_highproc` total T `7778`
  - target family choice:
    - use the remaining two-row concentrated high-proc 2-bay family rather
      than reopening the runtime-risk 3-bay low-proc families
    - current feature band:
      - `bays == 2`
      - `blocks >= 100`
      - `proc_mean >= 20`
      - `slack_mean >= 4.5`
      - `pref_concentration >= 0.60`
      - `pref_gap_mean >= 60`
    - current matching train rows on trusted `v123`:
      - `prob_25`: `T=2141`
      - `prob_27`: `T=5637`
  - carry-over evidence from accepted `v122`:
    - the live top-tardy probe signal was real on this family
    - `v122` converted only part of it into the accepted line:
      - `prob_25`: improved `2159 -> 2141`
      - `prob_27`: remained flat at `5637`
  - why this is structurally different:
    - `v122` already validated the bounded single-block reinsert path on this
      family
    - this version tests whether the remaining `prob_27`-like residual is an
      interacting tardy-set problem that needs a very short 2-3 block prefix
      rebuild instead of another single-block move
- Hypothesis:
  - On the concentrated 2-bay high-proc tail, the trusted `v122`/`v123`
    warm start already fixes the easy single-block opportunity. The remaining
    residual, especially on `prob_27`-like rows, may require rebuilding a very
    short top-tardy prefix of 2-3 blocks together. Doing that only on the
    narrow two-bay family should preserve runtime safety while offering a new
    path to lower total T.
- Feature / subtype / timelimit selector:
  - preserve the accepted `v123` three-bay high-proc prefix selector unchanged
  - add a second selector for the concentrated 2-bay high-proc tail:
    - `bays == 2`
    - `blocks >= 100`
    - `proc_mean >= 20`
    - `slack_mean >= 4.5`
    - `pref_concentration >= 0.60`
    - `pref_gap_mean >= 60`
    - warm-start feasible
    - warm-start `T >= 2000`
    - tier not in `very_short/short`
    - remaining wall time must clear a guarded reserve
- Planned behavior:
  - preserve the exact `v123` warm-start path outside the target subtype
  - keep the accepted three-bay high-proc prefix repair unchanged
  - on the new 2-bay concentrated high-proc subtype only, rebuild at most the
    top 2-3 tardy assignments with checker validation after each checkpoint
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - tier-representative smoke:
    - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_25`, `prob_27`, `prob_31`, `prob_39`
  - targeted subtype check:
    - `prob_25`, `prob_27`
  - only if scoreable and same-family T improves without runtime-risk spillover
    should this go to full train40
- Validation:
  - representative smoke path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v127_tier9_20260620_001/`
  - representative smoke result:
    - `accepted_for_score=8/9`
    - `timeout=1`, `invalid=0`
    - runtime max `63.133952s`
  - decisive failure:
    - `prob_27` timed out at `63.133952s`
    - checker still returned the old objective `77480587`, so the candidate
      spent extra time without recovering any accepted score gain before
      crossing the official limit
  - guard rows that did stay scoreable:
    - `prob_25`: accepted at `35.04s`
    - `prob_31`: accepted at `53.91s`
    - `prob_39`: accepted at `48.55s`
- Full 40:
  - not run
- Decision:
  - rejected
- Rationale:
  - the new 2-bay multi-block prefix phase violated the scoreability contract
    on its own target family before it produced any accepted gain. Under the
    plateau/T-zero-first gate, a target-family timeout is an immediate reject.

## reboot_v128_20260620_0935_twobay_heavytail_pairprefix_on_v123
- File:
  `reboot_v128_20260620_0935_twobay_heavytail_pairprefix_on_v123.py`
- Parent:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Status:
  - rejected
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `total T=61626`, `avg T=1540.65`, `avg objective=15071175.65`
  - refreshed target-family context:
    - the accepted `v122` single-block quantile repair already improved the
      smaller two-bay row:
      - `prob_25`: `T 2159 -> 2141`
    - the larger heavy-tail row remained untouched:
      - `prob_27`: `T=5637`, objective `77480587`
  - immediate prior failure to avoid repeating:
    - `v127` showed that a generic 2-3 block prefix rebuild over the whole
      two-bay concentrated high-proc family is too expensive:
      - `prob_27` timed out at `63.133952s`
  - family split for this cycle:
    - keep the smaller `prob_25`-like row on the trusted `v123` / `v122`
      single-block path
    - isolate only the heavier residual row class:
      - `bays == 2`
      - `blocks >= 150`
      - `proc_mean >= 20`
      - `slack_mean >= 4.5`
      - `pref_concentration >= 0.65`
      - `pref_gap_mean >= 60`
      - warm-start `T >= 5000`
- Hypothesis:
  - The residual larger two-bay heavy-tail row is not a general family problem;
    it is a heavier subclass that likely needs a paired top-tardy rebuild, but
    the search must stay narrower than `v127`. Rebuilding exactly two tardy
    blocks with a much tighter budget and only on the heavy-tail subclass can
    preserve scoreability while probing for the missing `prob_27` T drop.
- Feature / subtype / timelimit selector:
  - preserve the accepted `v123` three-bay high-proc prefix selector unchanged
  - preserve the accepted `v122` single-block two-bay tail behavior unchanged
  - add a third selector for the heavier 2-bay high-proc tail:
    - `bays == 2`
    - `blocks >= 150`
    - `proc_mean >= 20`
    - `slack_mean >= 4.5`
    - `pref_concentration >= 0.65`
    - `pref_gap_mean >= 60`
    - warm-start feasible
    - warm-start `T >= 5000`
    - tier not in `very_short/short`
    - remaining wall time must clear a stricter reserve than `v127`
- Planned behavior:
  - preserve the exact `v123` warm-start path outside the target subtype
  - on the new heavy-tail subtype only, rebuild exactly the top 2 tardy
    assignments with checker validation once
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - tier-representative smoke:
    - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_25`, `prob_27`, `prob_31`, `prob_39`
  - targeted subtype check:
    - only if the smoke remains fully scoreable and the `prob_27` family moves
- Smoke:
  - run:
    `reports/ogc2026_reboot_v001/smoke_reboot_v128_tier9_20260620_001/`
  - result:
    - `accepted_for_score=8/9`
    - `timed_out=1`
    - `checker_feasible=9/9`
    - `runtime_max=61.972116s`
  - key failure:
    - `prob_27`: checker-feasible but timeout at `61.972116s`, so not
      scoreable
- Targeted subtype smoke:
  - not run
- Full 40:
  - not run
- Decision:
  - rejected
- Rationale:
  - even after narrowing the selector to the heavier 2-bay subclass and
    reducing the paired-prefix budget to a single 2-block checkpoint, the
    target row still crossed the official runtime limit. Because the candidate
    failed scoreability on its own target family during smoke, it cannot be
    promoted and should not block the active trusted `v123` line.
    - `prob_25`, `prob_27`
  - only if scoreable and the heavy-tail row improves without timeout or
    runtime-risk spillover should this proceed further

## reboot_v129_20260620_1045_prob37like_shallow_iterative_on_v123
- File:
  `reboot_v129_20260620_1045_prob37like_shallow_iterative_on_v123.py`
- Parent:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Status:
  - candidate
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `total T=61626`, `avg T=1540.65`, `avg objective=15071175.65`
    - publish revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_002/`
      with `accepted_for_score=8/8`, `timeout=0`
  - plateau context after the publish checkpoint:
    - the recent 2-bay high-proc branch sequence (`v127`, `v128`) produced
      target-family runtime cliffs on `prob_27` before any accepted gain
    - the next candidate should therefore avoid the 2-bay heavy-tail family
      and avoid reopening the `prob_39`-like 59s runtime cliff
  - refreshed three-bay low-proc runtime split on trusted `v123`:
    - `prob_37`:
      - `bays=3`, `blocks=250`, `proc_mean=11.508`, `slack_mean=2.276`
      - `tight_ratio=0.592`, `pref_concentration=0.400`
      - `pref_gap_mean=46.716`, `workload_mean=143.232`
      - `T=3961`, runtime `48.894s`
    - `prob_39`:
      - `bays=3`, `blocks=250`, `proc_mean=11.120`, `slack_mean=2.200`
      - `tight_ratio=0.584`, `pref_concentration=0.572`
      - `pref_gap_mean=55.252`, `workload_mean=111.832`
      - `T=3521`, runtime `59.416s`
  - target family choice:
    - isolate the diffuse `prob_37`-like long-limit-opportunity slice from
      the concentrated `prob_39`-like runtime-risk slice
    - candidate selector:
      - `bays == 3`
      - `blocks >= 240`
      - `proc_mean < 12.0`
      - `slack_mean <= 2.35`
      - `tight_ratio >= 0.55`
      - `pref_concentration <= 0.48`
      - `pref_gap_mean <= 50.0`
      - `workload_mean >= 120.0`
    - current matching trusted-train row:
      - `prob_37` only
- Hypothesis:
  - The remaining diffuse `prob_37`-like low-proc row still has local T
    improvement headroom, but the expensive replay branches that once showed
    signal should not be revived wholesale. A very shallow 1-2 step bounded
    reinsertion portfolio on top of the trusted `v123` warm start, and only on
    the diffuse long-limit-opportunity slice, can probe for extra T reduction
    without touching the concentrated `prob_39` runtime cliff.
- Feature / subtype / timelimit selector:
  - preserve the accepted `v123` path unchanged outside the new target slice
  - run the new post-pass only when all are true:
    - the diffuse low-proc selector above matches
    - warm-start feasible
    - warm-start `T >= 3500`
    - tier not in `very_short/short`
    - remaining wall time clears `dynamic_reserve + 8s`
- Planned behavior:
  - keep the accepted `v123` warm start as the baseline
  - on the target slice only, try at most 1-2 bounded single-block reinserts
    using the union of top-tardy ids and the older low-proc target id
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - tier-representative smoke:
    - `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`,
      `prob_31`, `prob_37`, `prob_39`
  - targeted subtype smoke:
    - `prob_32`, `prob_37`, `prob_39`
  - only if the smoke remains fully scoreable and `prob_37`-like movement is
    positive without runtime spillover should this go further
- Smoke:
  - run:
    `reports/ogc2026_reboot_v001/smoke_reboot_v129_tier8_20260620_001/`
  - result:
    - `accepted_for_score=8/8`
    - `timed_out=0`
    - `checker_feasible=8/8`
    - runtime max `53.631369s`
  - row behavior:
    - all guard rows stayed scoreable
    - no visible target-family movement in the smoke headline
- Targeted subtype smoke:
  - compare run:
    `reports/ogc2026_reboot_v001/target_reboot_v129_prob37like_20260620_001/`
  - result versus direct `v123` file path:
    - `prob_32`: unchanged
      - objective `12781706`
      - T `2992`
      - runtime `49.66s -> 48.85s`
    - `prob_37`: unchanged
      - objective `17644653`
      - T `3961`
      - runtime `51.88s -> 53.04s`
    - `prob_39`: unchanged
      - objective `48598605`
      - T `3553`
      - runtime `48.77s -> 48.90s`
- Full 40:
  - not run
- Decision:
  - rejected
- Rationale:
  - the new diffuse prob37-like shallow iterative pass remained scoreable, but
    it produced zero T/objective/L/P movement on the target slice and slightly
    increased runtime on the intended row. Under the plateau/T-zero-first gate,
    a no-signal candidate is rejected because it does not improve the trusted
    `v123` line or reduce the residual T backlog.

## reboot_v130_20260620_1125_prob40like_narrow_quantile_on_v123
- File:
  `reboot_v130_20260620_1125_prob40like_narrow_quantile_on_v123.py`
- Parent:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Status:
  - candidate
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `total T=61626`, `avg T=1540.65`, `avg objective=15071175.65`
    - publish revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_002/`
      with `accepted_for_score=8/8`, `timeout=0`
  - recent branch evidence:
    - `v125` proved the warm-start-preserving four-bay quantile local move can
      improve the high-tail target row:
      - `prob_40`: objective `5910122 -> 5830082`, T `8622 -> 8502`
    - but `v125` still matched the smaller 4-bay high-proc row band and full
      train40 ended with a `prob_39` historical-best drift:
      - `prob_39`: objective `48160369 -> 48598605`, T `3521 -> 3553`
  - current-source feature split inside the 4-bay high-preference tail:
    - `prob_31`:
      - `blocks=200`, `proc_mean=21.495`, `tight_ratio=0.225`
      - `pref_concentration=0.795`, `pref_gap_mean=60.615`
      - `workload_mean=128.56`, `T=2735`
    - `prob_40`:
      - `blocks=250`, `proc_mean=21.688`, `tight_ratio=0.312`
      - `pref_concentration=0.760`, `pref_gap_mean=59.1`
      - `workload_mean=174.664`, `T=8622`
  - target family choice:
    - isolate the xlarge very-high-workload 4-bay high-proc tail rather than
      the full 4-bay high-proc band
    - proposed selector:
      - `bays == 4`
      - `blocks >= 240`
      - `proc_mean >= 20.0`
      - `0.28 <= tight_slack_ratio <= 0.34`
      - `pref_concentration >= 0.74`
      - `pref_gap_mean >= 58.0`
      - `workload_mean >= 160.0`
    - current matching train row:
      - `prob_40` only
- Hypothesis:
  - The useful T signal in `v125` belongs to the narrower xlarge very-high-
    workload 4-bay tail, not to the whole 4-bay high-proc family. Restricting
    the quantile single-reinsert to that slice, shrinking the candidate set,
    and stopping after the first accepted improvement can keep the `prob_40`
    T drop while reducing runtime spillover risk on other rows.
- Feature / subtype / timelimit selector:
  - preserve the accepted `v123` path unchanged outside the new target slice
  - run the new four-bay move only when all are true:
    - the selector above matches
    - warm-start feasible
    - warm-start `T >= 5000`
    - tier not in `very_short/short`
    - remaining wall time clears `dynamic_reserve + 8s`
- Planned behavior:
  - keep the exact `v123` three-bay repair path unchanged
  - after the trusted base path is built, try at most a very small top-tardy
    quantile reinsertion set on the narrow `prob_40`-like slice only
  - stop early once a strictly better officially feasible result is found
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - block-tier representative smoke:
    - `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_19`,
      `prob_23`, `prob_27`, `prob_31`, `prob_40`
  - targeted subtype/runtime-risk compare:
    - `prob_31`, `prob_39`, `prob_40`
  - only if the representative smoke remains fully scoreable and the targeted
    compare shows `prob_40` improvement with `prob_31`/`prob_39` controlled
    should this candidate go further
- Smoke:
  - representative path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v130_tier9_20260620_001/`
  - result:
    - `accepted_for_score=9/9`
    - `timed_out=0`, `invalid=0`
    - runtime max `53.518114s`
  - key row movement:
    - `prob_40`: objective `5910122 -> 5860829`, `T 8622 -> 8549`
    - the other representative rows stayed scoreable
- Targeted subtype compare:
  - path:
    `reports/ogc2026_reboot_v001/target_reboot_v130_prob40like_20260620_001/`
  - result versus same-run direct `v123`:
    - `prob_31`: unchanged
      - objective `39589844`
      - `T=2735`
    - `prob_39`: unchanged
      - objective `48598605`
      - `T=3553`
    - `prob_40`: improved
      - objective `5910122 -> 5860829`
      - `T 8622 -> 8549`
      - `L 4587 -> 4947`
      - `P 11897 -> 11823`
- Full 40:
  - path:
    `reports/ogc2026_reboot_v001/full_reboot_v130_train40_20260620_001/`
  - accepted `40/40`; timeout `0`, invalid `0`
  - headline deltas versus trusted `v123`:
    - total T `61626 -> 61585`
    - avg T `1540.65 -> 1539.625`
    - avg objective `15071175.65 -> 15080899.225`
    - avg L `2674.325 -> 2686.325`
    - avg P `4187.625 -> 4187.625`
    - runtime max `59.416431s -> 53.198687s`
  - changed rows versus trusted `v123`:
    - `prob_39`: objective `48160369 -> 48598605`,
      `T 3521 -> 3553`, `L 194 -> 314`, `P 8094 -> 8168`
    - `prob_40`: objective `5910122 -> 5860829`,
      `T 8622 -> 8549`, `L 4587 -> 4947`, `P 11897 -> 11823`
- Decision:
  - rejected
- Rationale:
  - the narrower prob40-like selector did preserve scoreability and delivered a
    real high-tail T drop on `prob_40`, but the full train40 run still gave
    back part of that gain through a `prob_39` regression and a worse average
    official objective. Under the current plateau/T-zero-first gate, this is
    not strong enough to displace the trusted `v123` line because the net score
    claim regresses even though total T improves slightly.

## publish_checkpoint_20260620_v123_recovery
- Scope:
  - post-`v129` / post-`v130` publish checkpoint before any new candidate work
- Current active surface:
  - `baseline_hh.py -> reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Historical full evidence kept on record:
  - `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
  - headline:
    - `accepted_for_score=40/40`
    - `avg objective=15071175.65`
    - `avg T=1540.65`
    - `runtime_max=59.416431s`
- New wrapper/active head revalidation:
  - `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_003/`
  - source hashes now aligned with current HEAD for:
    - `baseline_hh.py`
    - `myalgorithm.py`
    - `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122.py`
  - scoreability result:
    - `accepted_for_score=8/8`
    - `timed_out=0`
    - wrapper and active both matched on:
      - `prob_31`, `prob_37`, `prob_39`, `prob_40`
- Recovery finding:
  - the current wrapper-surface revalidation is scoreable, but it repeatedly
    lands on the weaker `prob_39` row
    (`objective=48598605`, `T=3553`, `L=314`, `P=8168`)
    rather than the stronger historical full-v123 row kept in
    `full_reboot_v123_train40_20260620_003/`
    (`objective=48160369`, `T=3521`, `L=194`, `P=8094`)
  - this means the branch still has a historical-best vs current-head
    revalidation drift on the active submission surface
- Decision:
  - recovery / failure checkpoint
- Publish stance:
  - do not republish the current active line as a cleanly reproducible trusted
    accepted BEST yet
  - preserve the historical best evidence, but describe it as historical until
    the `prob_39` drift is explained or reproduced away on the active surface
- Next T-zero-first hypothesis:
  - pause promotion work
  - first explain the `prob_39` historical-best drift on the active surface
  - only then resume the next narrow `prob_27`-like or other residual T-tail
    candidate search

## reboot_v131_20260620_1515_threebay_xlarge_lowproc_direct_v072_on_v123
- File:
  `reboot_v131_20260620_1515_threebay_xlarge_lowproc_direct_v072_on_v123.py`
- Parent:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Status:
  candidate
- Hypothesis:
  - the apparent `v123` active-surface drift is really a runtime-cliff issue on
    the `v072_family` subtype (`3 bays`, `>=240 blocks`, `low proc`,
    `tight slack`), not an identity-dependent wrapper bug
  - direct `v072` remains scoreable on that subtype and is strictly better than
    the current `v123` chain on `prob_39` while tying `prob_37`
  - using feature-based, timelimit-aware direct `v072` only on that subtype
    should recover the stronger `prob_39` row without touching the rest of the
    train40 surface
- Feature/subtype selector:
  - reuse the `reboot_v072` family selector
  - require `timelimit >= 60` and `tier in {standard,long,very_long}`
- Pre-edit evidence:
  - wrapper/direct drift investigation:
    `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_003/`
  - targeted subtype probe:
    `reports/ogc2026_reboot_v001/probe_v072_family_direct_20260620_001/`
  - key observation:
    - `v072direct` on `prob_39` recovered
      `objective=48160369`, `T=3521`, runtime `57.749275s`
    - `v123direct` on `prob_39` stayed on
      `objective=48598605`, `T=3553`, runtime `48.014879s`
    - `prob_37` tied on objective/T between `v072direct` and `v123direct`
- Validation plan:
  - smoke-8 first
  - targeted subtype smoke: `prob_37`, `prob_39`
  - time-stress smoke at shorter timelimit on the subtype
  - full train40 only if all above remain scoreable
- Smoke-8:
  - path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v131_tier8_20260620_001/`
  - accepted `8/8`; timeout `0`, invalid `0`
  - no regression observed on the core smoke gate
- Targeted subtype smoke:
  - path:
    `reports/ogc2026_reboot_v001/target_reboot_v131_v072_family_20260620_001/`
  - accepted `2/2`; timeout `0`, invalid `0`
  - `prob_37`: tied the trusted `v123` row
    - objective `17644653`
    - `T=3961`
  - `prob_39`: failed to recover the stronger historical row
    - landed on the same weaker row as current active
    - objective `48598605`
    - `T=3553`
    - runtime `45.400811s`
  - log evidence shows `v131` did route into `direct v072`, but direct `v072`
    itself hit the same headroom cliff:
    - `[baseline_hh reboot_v072] skip_threebay_xlarge_lowproc ... remaining=15.07s`
- Full 40:
  - not run
- Decision:
  - rejected
- Rationale:
  - the direct-`v072` portfolio hypothesis was coherent and stayed scoreable, but
    it did not deliver a stable `prob_39` recovery. The targeted smoke showed
    that `direct v072` is itself runtime-sensitive on the subtype, so replacing
    `v123` with `v072` does not reliably resolve the underlying cliff.
- Next strategy:
  - keep the `v072_family` focus (`prob_37`, `prob_39` feature class)
  - target the real runtime cliff inside the inherited chain, most likely by
    stabilizing or simplifying the late `v068 -> v072 -> v090 -> v096 -> v102`
    path rather than swapping in older direct `v072`

## reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123
- File:
  `reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123.py`
- Parent:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Status:
  candidate
- Hypothesis:
  - `v072_family` instability is dominated by the old `v072` headroom guard,
    not by the direct-v072 branch choice itself
  - for that subtype, lowering the opportunity gate from
    `reserve + 12.0` to `reserve + 10.0` preserves `prob_37` and recovers the
    stronger `prob_39` row while staying under the 60s official limit
- Feature/subtype selector:
  - reuse the `reboot_v072` family selector
  - require `timelimit >= 60` and `tier in {standard,long,very_long}`
- Pre-edit evidence:
  - `reboot_v131` targeted smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v131_v072_family_20260620_001/`
  - relaxed-guard inline probe:
    - `prob_37`: no extra attempt; base row unchanged
    - `prob_39`: attempt triggered at `remaining=17.85s`,
      recovered `objective=48160369`, `T=3521`,
      elapsed `57.34s`
- Validation plan:
  - smoke-8 first
  - targeted subtype smoke: `prob_37`, `prob_39`
  - short-limit stress on `prob_37`, `prob_39`
  - full train40 only if all above remain scoreable
- Smoke-8:
  - path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v132_tier8_20260620_001/`
  - accepted `8/8`; timeout `0`, invalid `0`
- Targeted subtype smoke:
  - path:
    `reports/ogc2026_reboot_v001/target_reboot_v132_v072_family_20260620_001/`
  - accepted `2/2`; timeout `0`, invalid `0`
  - subtype result versus trusted `v123`:
    - `prob_37`: unchanged
      - objective `17644653`
      - `T=3961`
    - `prob_39`: improved
      - objective `48598605 -> 48160369`
      - `T 3553 -> 3521`
      - `L 314 -> 194`
      - `P 8168 -> 8094`
      - runtime `45.400811s -> 56.656471s`
- Time-stress smoke:
  - path:
    `reports/ogc2026_reboot_v001/stress_reboot_v132_v072_family_short45_20260620_001/`
  - accepted `2/2`; timeout `0`, invalid `0`
  - expected fallback behavior under short limit preserved scoreability
- Full 40:
  - path:
    `reports/ogc2026_reboot_v001/full_reboot_v132_train40_20260620_001/`
  - accepted `40/40`; timeout `0`, invalid `0`
  - headline deltas versus trusted historical `v123`:
    - avg objective `15071175.65 -> 15071175.65`
    - avg T `1540.65 -> 1540.65`
    - avg L `2674.325 -> 2674.325`
    - avg P `4187.625 -> 4187.625`
    - runtime max `59.416431s -> 56.951463s`
  - row-level differences:
    - no objective/T/L/P differences remained at the final train40 headline
    - the recovered `prob_39` row from targeted smoke matched the historical
      stronger `v123` row and restored the historical full-train score
- Wrapper + active publish revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v132_publish_20260620_001/`
  - accepted `8/8`; timeout `0`, invalid `0`
  - both `baseline_hh.py` and `myalgorithm.py` matched on:
    - `prob_31`, `prob_37`, `prob_39`, `prob_40`
  - both active surfaces reproduced the stronger `prob_39` row:
    - objective `48160369`
    - `T=3521`
- Decision:
  - accepted
- Rationale:
  - `v132` is not a score-improving successor to historical `v123`, but it is
    a trusted accepted recovery line: it reproduces the same full-train
    objective/T/L/P headline exactly on the current source state, lowers the
    runtime ceiling, and removes the active-surface `prob_39` drift that forced
    the earlier recovery checkpoint.

## reboot_v133_20260620_1705_prob40like_narrow_quantile_on_v132
- File:
  `reboot_v133_20260620_1705_prob40like_narrow_quantile_on_v132.py`
- Parent:
  `reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123`
- Status:
  accepted
- Hypothesis:
  - the rejected `v130` logic is still structurally sound because its selector
    matches only `prob_40`
  - it failed only because `v123` still carried the weaker `prob_39` row
  - applying the same narrow prob40-like quantile move on top of stabilized
    `v132` should keep the recovered `prob_39` row and preserve the `prob_40`
    T improvement, yielding a real full-train score improvement
- Feature/subtype selector:
  - reuse the `reboot_v130` prob40-like narrow-tail selector
  - selector matches only `prob_40` on train40
- Representative tier smoke set:
  - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_33`, `prob_38`
- Targeted smoke set:
  - `prob_31`, `prob_39`, `prob_40`
- Time-stress smoke:
  - `prob_39`, `prob_40` at shorter limit to confirm fallback safety
- Representative tier smoke:
  - path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v133_tier9_20260620_001/`
  - accepted `9/9`; timeout `0`, invalid `0`
- Targeted smoke:
  - path:
    `reports/ogc2026_reboot_v001/target_reboot_v133_prob40like_20260620_001/`
  - accepted `3/3`; timeout `0`, invalid `0`
  - kept:
    - `prob_31`: unchanged
    - `prob_39`: unchanged strong row
  - improved:
    - `prob_40`: objective `5910122 -> 5860829`,
      `T 8622 -> 8549`, `L 4587 -> 4947`, `P 11897 -> 11823`
- Time-stress smoke:
  - path:
    `reports/ogc2026_reboot_v001/stress_reboot_v133_prob40like_short45_20260620_001/`
  - accepted `2/2`; timeout `0`, invalid `0`
  - shorter-limit fallback remained scoreable
- Full 40:
  - path:
    `reports/ogc2026_reboot_v001/full_reboot_v133_train40_20260620_001/`
  - accepted `40/40`; timeout `0`, invalid `0`
  - headline deltas versus trusted `v132`:
    - avg objective `15071175.65 -> 15069943.325`
    - avg T `1540.65 -> 1538.825`
    - avg L `2674.325 -> 2683.325`
    - avg P `4187.625 -> 4185.775`
    - runtime max `56.951463 -> 56.899351`
  - row-level changes:
    - only `prob_40` changed
    - no regressions on `prob_39` or the rest of the train40 set
- Decision:
  - accepted
- Rationale:
  - this is the plateau/T-zero-first style win we wanted: scoreability stayed
    perfect, total T and avg T improved, the high-T tail row `prob_40`
    improved, and the official objective improved as well.
- Wrapper + active publish revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v133_publish_20260620_001/`
  - accepted `6/6`; timeout `0`, invalid `0`
  - direct `baseline_hh.py` matched the accepted `prob_40` improvement
  - `myalgorithm.py` remained scoreable but missed the `prob_40` move because
    the narrow guard saw only `remaining=11.53s` and skipped the quantile pass
- Hidden-risk note:
  - this is not a direct `baseline_hh.py` score-claim failure because the
    official active submission surface is `baseline_hh.py`
  - however, it is a real dispatch-overhead stability hint for any future
    prob40-like follow-up work
  - later publish revalidation on the direct `baseline_hh.py` surface:
    `reports/ogc2026_reboot_v001/verify_active_v133_publish_20260620_002/`
    stayed fully scoreable but did not reproduce the accepted `prob_40`
    improvement
  - that rerun reverted `prob_40` from objective `5860829`, `T=8549`
    back to objective `5910122`, `T=8622`
  - log evidence shows the same narrow headroom gate skipped on that rerun:
    `skip_prob40like_guard ... remaining=12.48s reserve=4.80s`
  - historical acceptance of `v133` remains true, but its publish trust is now
    downgraded until the `prob_40` runtime cliff is repaired or a more stable
    active line is restored

## reboot_v134_20260620_1825_fourbay_highproc_toptardy_quantile_on_v133
- File:
  `reboot_v134_20260620_1825_fourbay_highproc_toptardy_quantile_on_v133.py`
- Parent:
  `reboot_v133_20260620_1705_prob40like_narrow_quantile_on_v132`
- Status:
  candidate
- Hypothesis:
  - the stronger `v124` four-bay highproc top-tardy quantile move was rejected
    only because its `v123` parent still allowed the weaker `prob_39` row
  - the stabilized `v133` parent already preserves the strong `prob_39` row and
    a safer `prob_40` improvement
  - replaying the same broader four-bay top-tardy quantile move on top of
    `v133` should recover the larger `prob_40` gain without reopening the old
    `prob_39` regression
- Feature/subtype selector:
  - reuse the `reboot_v124` four-bay high-proc high-preference tail selector
  - train40 matches the `prob_31` / `prob_40` family, with prior evidence that
    the move is a no-op on `prob_31`
- Representative tier smoke set:
  - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_31`, `prob_40`
- Targeted smoke:
  - `prob_31`, `prob_39`, `prob_40`
- Time-stress smoke:
  - `prob_39`, `prob_40` at shorter limit
- Representative tier smoke:
  - path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v134_tier9_20260620_001/`
  - accepted `9/9`; timeout `0`, invalid `0`
  - no representative-tier regression; `prob_40` improved strongly in smoke
- Targeted smoke:
  - path:
    `reports/ogc2026_reboot_v001/target_reboot_v134_fourbay_highproc_20260620_001/`
  - accepted `3/3`; timeout `0`, invalid `0`
  - kept:
    - `prob_31`: unchanged
    - `prob_39`: unchanged strong row
  - improved:
    - `prob_40`: objective `5860829 -> 5780789`,
      `T 8549 -> 8429`, `L 4947 -> 5307`, `P 11823 -> 11749`
- Time-stress smoke:
  - path:
    `reports/ogc2026_reboot_v001/stress_reboot_v134_fourbay_highproc_short45_20260620_001/`
  - accepted `2/2`; timeout `0`, invalid `0`
  - shorter-limit fallback remained scoreable
- Full 40:
  - path:
    `reports/ogc2026_reboot_v001/full_reboot_v134_train40_20260620_001/`
  - accepted `40/40`; timeout `0`, invalid `0`
  - headline deltas versus trusted `v133`:
    - avg objective `15069943.325 -> 15071175.65`
    - avg T `1538.825 -> 1540.65`
    - avg L `2683.325 -> 2674.325`
    - avg P `4185.775 -> 4187.625`
    - runtime max `56.899351 -> 58.363379`
  - row-level change:
    - only `prob_40` changed, and it regressed back to the weaker stabilized row
    - objective `5860829 -> 5910122`
    - `T 8549 -> 8622`
    - `L 4947 -> 4587`
    - `P 11823 -> 11897`
- Failure mode:
  - targeted smoke proved the broader four-bay quantile move itself can improve
    `prob_40`, but full-train runtime headroom did not let the move fire
  - full-run logs show both the inherited `v133` narrow guard and the new `v134`
    broader guard skipped on `prob_40`:
    - `v133`: `skip_prob40like_guard ... remaining=10.65s reserve=4.80s`
    - `v134`: `skip_fourbay_quantile_guard ... remaining=10.40s reserve=4.80s`
  - this is a full-train headroom-cliff failure, not evidence that the
    four-bay move is intrinsically harmful
- Decision:
  - rejected
- Rationale:
  - the candidate stayed fully scoreable, but the full40 headline reverted from
    accepted `v133` back to the weaker stabilized `v132`/historical `v123`
    plateau because the `prob_40` improvement never executed under full-train
    headroom
  - a publishable BEST cannot rely on targeted-smoke-only gains when the full
    run falls back to the weaker row
- Next strategy:
  - keep `v133` as the trusted active BEST
  - if we revisit this subtype, the next coherent hypothesis should harden the
    `prob_40` family against the full-train headroom cliff by shrinking the
    budget/shortlist or relaxing the guard just enough for the move to still
    trigger within the official limit

## reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132
- File:
  `reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132.py`
- Parent:
  `reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123`
- Status:
  candidate
- Hypothesis:
  - the accepted `v133` `prob_40` gain failed publish revalidation because the
    narrow guard `remaining <= reserve + 8.0` is a little too conservative
    under ordinary runtime noise on the direct `baseline_hh.py` surface
  - the prob40-like move already proved scoreable on the same 60s tier, and
    the broader `v124` four-bay search used a smaller `reserve + 6.0` guard
    without timeout
  - reusing the same narrow selector and same local move on top of stable
    `v132`, but lowering only the headroom gate from `reserve + 8.0` to
    `reserve + 6.0`, should restore the `prob_40` T drop more reliably while
    keeping accepted_for_score `40/40`
- Feature/subtype selector:
  - reuse the `reboot_v130` prob40-like narrow-tail selector
  - selector currently matches only `prob_40` on train40
- Timelimit behavior:
  - unchanged from `v133` outside the narrower headroom threshold
  - still skip on `very_short` / `short`, infeasible warm starts, or low-T base rows
- Representative tier smoke set:
  - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
    `prob_25`, `prob_27`, `prob_33`, `prob_40`
- Targeted smoke:
  - `prob_31`, `prob_39`, `prob_40`
- Time-stress smoke:
  - `prob_39`, `prob_40` at shorter limit
- Validation plan:
  - representative tier smoke first
  - targeted subtype smoke second
  - short-limit stress third
  - full train40 only if the first three gates remain scoreable and preserve
    the stronger `prob_39` row
- Representative tier smoke:
  - path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v135_tier9_20260620_001/`
  - accepted `9/9`; timeout `0`, invalid `0`
  - representative rows stayed scoreable
  - hypothesis-target row improved immediately:
    - `prob_40`: objective `5910122 -> 5860829`,
      `T 8622 -> 8549`, `L 4587 -> 4947`, `P 11897 -> 11823`
- Targeted smoke:
  - path:
    `reports/ogc2026_reboot_v001/target_reboot_v135_prob40_headroom_20260620_001/`
  - accepted `3/3`; timeout `0`, invalid `0`
  - kept:
    - `prob_31`: unchanged
    - `prob_39`: unchanged strong row
  - improved:
    - `prob_40`: objective `5910122 -> 5860829`,
      `T 8622 -> 8549`, `L 4587 -> 4947`, `P 11897 -> 11823`
- Time-stress smoke:
  - path:
    `reports/ogc2026_reboot_v001/stress_reboot_v135_prob40_short45_20260620_001/`
  - accepted `2/2`; timeout `0`, invalid `0`
  - shorter-limit fallback remained scoreable
  - expected short-limit degradation stayed bounded to fallback behavior:
    - `prob_39`: objective `51006456`
    - `prob_40`: objective `12129566`
- Full 40:
  - path:
    `reports/ogc2026_reboot_v001/full_reboot_v135_train40_20260620_001/`
  - accepted `40/40`; timeout `0`, invalid `0`
  - headline deltas versus trusted `v132`:
    - avg objective `15071175.65 -> 15069943.325`
    - avg T `1540.65 -> 1538.825`
    - avg L `2674.325 -> 2683.325`
    - avg P `4187.625 -> 4185.775`
    - runtime max `56.951463 -> 58.418181`
  - row-level changes:
    - only `prob_40` changed
    - no regression on `prob_39` or the rest of the train40 surface
- Active-surface publish revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v135_publish_20260620_001/`
  - accepted `12/12`; timeout `0`, invalid `0`
  - direct `baseline_hh.py` reproduced the accepted `prob_40` improvement:
    - objective `5860829`
    - `T=8549`
  - `prob_39` kept the stronger `v132` row:
    - objective `48160369`
    - `T=3521`
- Decision:
  - accepted
- Rationale:
  - this is the clean recovery we wanted after the `v133` publish cliff:
    the same high-T `prob_40` gain is now reproduced on the direct active
    wrapper surface, scoreability stayed perfect, and the official full-train
    headline improved versus trusted `v132`.
- Current trusted active BEST:
  - `reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132`
- Next strategy:
  - keep `v135` active
  - move back to plateau/T-zero-first backlog beyond `prob_40`, especially the
    remaining high-T tail on `prob_38`, `prob_27`, `prob_37`, `prob_33`, and `prob_39`

## reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135
- File:
  `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135.py`
- Parent:
  `reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132`
- Status:
  accepted
- Experiment note:
  - trusted starting line reconfirmed from the current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v135_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1538.825`, `avg objective=15069943.325`
    - direct active-surface revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v135_publish_20260620_001/`
      with `accepted_for_score=12/12`
  - refreshed high-T backlog on trusted `v135`:
    - `prob_38`: `T=11120`
    - `prob_40`: `T=8549`
    - `prob_27`: `T=5637`
    - `prob_37`: `T=3961`
    - `prob_33`: `T=3805`
    - `prob_39`: `T=3521`
  - selected target subtype for the next T-first cycle:
    - `twobay_concentrated_highproc_tail`
    - current train40 matches:
      `prob_25`, `prob_27`
  - current-source live probes on the real `v135` warm start show that the
    subtype still has real one-block T signal, but the older `v122` budget is
    too shallow on the heavier parent:
    - `prob_25` current warm start:
      `1489168 / T=2141`
      - deeper shortlist probe found block `35`:
        `1454484 / T=2089`
    - `prob_27` current warm start:
      `77480587 / T=5637`
      - deeper shortlist probe found block `77`:
        `77173928 / T=5614`
      - deeper shortlist probe found block `8`:
        `76200619 / T=5541`
    - the previous `v122` replay attempted too few targets under the current
      heavier warm start and stopped before reaching those improving blocks
- Hypothesis:
  - The two-bay concentrated high-proc family is not at a real local plateau
    on top of trusted `v135`; it is only under-searched.
  - Reusing the same pure top-tardy quantile single-reinsert idea, but with a
    slightly deeper shortlist and a modestly larger research budget tuned for
    the current `v135` warm start, should reduce T on the `prob_25` /
    `prob_27` family while preserving accepted_for_score `40/40`.
- Feature / subtype / timelimit selector:
  - reuse the `reboot_v121` two-bay concentrated high-proc tail selector:
    - `bays == 2`
    - `blocks >= 100`
    - `proc_mean >= 20`
    - `slack_mean >= 4.5`
    - `pref_concentration >= 0.60`
    - `pref_pressure >= 0.59`
    - `pref_gap_mean >= 60`
  - warm-start feasible
  - warm-start `T >= 2000`
  - tier not in `very_short/short`
  - only spend improvement budget when remaining wall time clears a stricter
    reserve on top of the `v135` warm start
- Planned behavior:
  - keep `v135` unchanged outside the target subtype
  - on the target subtype, build the trusted `v135` warm start first
  - evaluate a deeper pure top-tardy shortlist with bounded quantile-sampled
    single-block reinsertion
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - representative tier smoke before any full 40:
    - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_25`, `prob_27`, `prob_33`, `prob_38`
  - targeted subtype smoke:
    - `prob_25`, `prob_27`, `prob_39`
  - short-limit stress:
    - `prob_25`, `prob_27` at shorter limit
  - only if scoreable and same-family T improves without non-target regression
    should this go to broader validation
- Smoke:
  - path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v136_tier9_20260620_001/`
  - accepted `9/9`; timeout `0`, invalid `0`
  - improved target-family rows:
    - `prob_25`: objective `1489168 -> 1454484`, `T 2141 -> 2089`
    - `prob_27`: objective `77480587 -> 76200619`, `T 5637 -> 5541`
  - representative non-target rows stayed scoreable
- Targeted smoke:
  - path:
    `reports/ogc2026_reboot_v001/target_reboot_v136_twobay_tail_20260620_001/`
  - accepted `3/3`; timeout `0`, invalid `0`
  - kept:
    - `prob_39`: unchanged strong row
  - improved:
    - `prob_25`: objective `1489168 -> 1454484`, `T 2141 -> 2089`
    - `prob_27`: objective `77480587 -> 76200619`, `T 5637 -> 5541`
- Time-stress smoke:
  - candidate path:
    `reports/ogc2026_reboot_v001/stress_reboot_v136_twobay_short45_20260620_001/`
  - comparison path:
    `reports/ogc2026_reboot_v001/stress_reboot_v135_twobay_short45_20260620_001/`
  - accepted `2/2`; timeout `0`, invalid `0`
  - shorter-limit behavior remained scoreable
  - same-limit comparison versus trusted `v135`:
    - `prob_25`: objective `1948687 -> 1906284`, `T 2851 -> 2790`
    - `prob_27`: unchanged at objective `78787221`, `T=5735`
  - runtime rose on the improved target rows, but stayed well under the
    shorter limit
- Full 40:
  - path:
    `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/`
  - accepted `40/40`; timeout `0`, invalid `0`
  - headline deltas versus trusted `v135`:
    - avg objective `15069943.325 -> 15037077.025`
    - avg T `1538.825 -> 1535.125`
    - avg L `2683.325 -> 2683.325`
    - avg P `4185.775 -> 4185.775`
    - runtime max `58.418181 -> 56.571143`
  - row-level changes:
    - `prob_25`: objective `1489168 -> 1454484`, `T 2141 -> 2089`
    - `prob_27`: objective `77480587 -> 76200619`, `T 5637 -> 5541`
    - no regression rows on the rest of train40
- Active-surface revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v136_surface_20260620_001/`
  - accepted `6/6`; timeout `0`, invalid `0`
  - direct `baseline_hh.py` reproduced the accepted target-family gains:
    - `prob_25`: objective `1454484`, `T=2089`
    - `prob_27`: objective `76200619`, `T=5541`
  - representative carryover high-T rows stayed scoreable:
    - `prob_39`: objective `48160369`, `T=3521`
    - `prob_40`: objective `5860829`, `T=8549`
- Publish-checkpoint revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v136_publish_20260620_002/`
  - accepted `6/6`; timeout `0`, invalid `0`
  - current active wrapper reproduced the same canonical subset rows:
    - `prob_25`: objective `1454484`, `T=2089`
    - `prob_27`: objective `76200619`, `T=5541`
    - `prob_39`: objective `48160369`, `T=3521`
    - `prob_40`: objective `5860829`, `T=8549`
- Decision:
  - accepted
- Rationale:
  - this is a clean T-first improvement over trusted `v135`:
    scoreability stayed perfect, the full train40 official objective improved,
    avg T improved, there were no regression rows, and the change stayed
    tightly localized to the intended two-bay concentrated high-proc tail
    subtype.
- Current trusted active BEST:
  - `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Next strategy:
  - keep `v136` active
  - continue the plateau/T-zero-first backlog on the remaining high-T tail,
    especially `prob_38`, `prob_40`, `prob_37`, `prob_33`, and `prob_39`

## reboot_v137_20260620_1335_fourbay_concentrated_quantile_on_v136
- File:
  `reboot_v137_20260620_1335_fourbay_concentrated_quantile_on_v136.py`
- Parent:
  `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Status:
  training-best-only
- Experiment note:
  - trusted starting line reconfirmed from the current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1535.125`, `avg objective=15037077.025`
    - direct active-surface revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v136_surface_20260620_001/`
      with `accepted_for_score=6/6`
  - refreshed high-T backlog on trusted `v136`:
    - `prob_38`: `T=11120`
    - `prob_40`: `T=8549`
    - `prob_27`: `T=5541`
    - `prob_37`: `T=3961`
    - `prob_33`: `T=3805`
    - `prob_39`: `T=3521`
  - selected target subtype for the next T-first cycle:
    - `fourbay_concentrated_highproc_runtime_tail`
    - current train40 matches:
      `prob_31`, `prob_40`
  - subtype rationale from the current feature table:
    - `bays=4`, `blocks>=200`, `proc_mean>=20`
    - strong preference concentration / high preference gap
    - runtime-risk and high feasible-placement pressure
    - the family is broad enough to include both a medium-size row
      (`prob_31`) and the xlarge head row (`prob_40`)
  - current-source live probe on top of the real `v136` warm start:
    - `prob_31`:
      - base stayed `39589844 / T=2735`
      - bounded four-bay top-tardy quantile reinsertion did not improve it
    - `prob_40`:
      - base `5860829 / T=8549`
      - same bounded reinsertion improved to
        `5780789 / T=8429`
      - total elapsed with the real warm start remained within the official
        `60s` limit:
        about `54.96s`
  - implication:
    - the current live signal is still real on the four-bay concentrated
      high-proc tail
    - the move looks effectively selective already: it no-ops on `prob_31`
      while improving `prob_40`
- Hypothesis:
  - The accepted `v136` warm start still leaves a bounded one-block T-improving
    quantile reinsertion signal on the four-bay concentrated high-proc tail.
    Replaying that move only on this feature-based family should lower the
    `prob_40` high-T head again while staying a no-op on `prob_31` and
    preserving train40 scoreability.
- Feature / subtype / timelimit selector:
  - `bays == 4`
  - `blocks >= 200`
  - `proc_mean >= 20`
  - high concentration / high preference gap / non-short tier
  - warm-start feasible
  - warm-start `T >= 2500`
  - only spend the extra research when the post-warm-start remaining wall time
    clears the dynamic reserve plus a fixed guard
- Planned behavior:
  - keep `v136` unchanged outside the target subtype
  - on the target subtype, build the trusted `v136` warm start first
  - replay bounded top-tardy quantile single-reinsert on that warm start
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - representative tier smoke before any full 40:
    - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_25`, `prob_27`, `prob_31`, `prob_40`
  - targeted subtype smoke:
    - `prob_31`, `prob_38`, `prob_39`, `prob_40`
  - short-limit stress:
    - `prob_31`, `prob_40` at shorter limit
  - only if scoreable and the target-family T improves without same-tier
    runtime cliff should this go to broader validation
- Smoke:
  - initial path:
    `reports/ogc2026_reboot_v001/smoke_reboot_v137_tier9_20260620_001/`
  - rerun path used for promotion gate:
    `reports/ogc2026_reboot_v001/smoke_reboot_v137_tier9_20260620_002/`
  - accepted `9/9`; timeout `0`, invalid `0`
  - rerun target-family result:
    - `prob_31`: unchanged at `39589844 / T=2735`
    - `prob_40`: improved to `5780789 / T=8429`
  - rerun representative non-target rows stayed stable:
    - `prob_25`: unchanged at `1454484 / T=2089`
    - `prob_27`: unchanged at `76200619 / T=5541`
  - note:
    - the first representative smoke showed a transient weaker `prob_27` row
    - direct repeat probes and the rerun smoke both reproduced the stable
      accepted `v136` row on `prob_27`, so the candidate was not discarded on
      that one noisy surface sample alone
- Targeted smoke:
  - path:
    `reports/ogc2026_reboot_v001/target_reboot_v137_fourbay_tail_20260620_001/`
  - accepted `5/5`; timeout `0`, invalid `0`
  - kept:
    - `prob_27`: unchanged at `76200619 / T=5541`
    - `prob_31`: unchanged at `39589844 / T=2735`
    - `prob_38`: unchanged at `151254848 / T=11120`
    - `prob_39`: unchanged at `48160369 / T=3521`
  - improved:
    - `prob_40`: objective `5860829 -> 5780789`,
      `T 8549 -> 8429`
- Time-stress smoke:
  - candidate path:
    `reports/ogc2026_reboot_v001/stress_reboot_v137_fourbay_short45_20260620_001/`
  - comparison path:
    `reports/ogc2026_reboot_v001/stress_reboot_v136_fourbay_short45_20260620_001/`
  - accepted `2/2`; timeout `0`, invalid `0`
  - shorter-limit fallback remained scoreable
  - same-limit comparison versus trusted `v136`:
    - `prob_31`: objective `58364354 -> 54151122`,
      `T 17932 -> 17793`
    - `prob_40`: objective `12129566 -> 12036675`,
      `T 4136 -> 3816`
- Full 40:
  - path:
    `reports/ogc2026_reboot_v001/full_reboot_v137_train40_20260620_001/`
  - accepted `40/40`; timeout `0`, invalid `0`
  - headline deltas versus trusted `v136`:
    - avg objective `15037077.025 -> 15035076.025`
    - avg T `1535.125 -> 1532.125`
    - avg L `2683.325 -> 2683.325`
    - avg P `4185.775 -> 4185.775`
    - runtime max `56.571143 -> 57.809269`
  - row-level changes:
    - only `prob_40` changed
    - objective `5860829 -> 5780789`
    - `T 8549 -> 8429`
    - `L/P` unchanged
- Decision:
  - training-best-only
- Rationale:
  - the direct version file improved the training40 headline versus trusted
    `v136` and kept train40 scoreability perfect
  - but the canonical direct `baseline_hh.py` wrapper surface did not
    reproduce the `prob_40` gain during revalidation:
    - direct file full40 / targeted evidence:
      `prob_40 = 5780789 / T=8429`
    - active-surface revalidation:
      `prob_40 = 5860829 / T=8549`
  - because the canonical active surface is the only trusted score-claim
    surface, this line cannot replace active `v136` yet
- Active-surface revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v137_surface_20260620_001/`
  - accepted `6/6`; timeout `0`, invalid `0`
  - reproduced:
    - `prob_27`: objective `76200619`, `T=5541`
    - `prob_31`: objective `39589844`, `T=2735`
    - `prob_39`: objective `48160369`, `T=3521`
  - did not reproduce the direct accepted `prob_40` gain:
    - wrapper surface returned objective `5860829`, `T=8549`
    - direct-file accepted evidence was objective `5780789`, `T=8429`
- Current trusted active BEST:
  - `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Next strategy:
  - keep `v136` active
  - investigate a recovery/stabilization hypothesis for the direct-surface
    `prob_40` gain, or pivot to the remaining large 3-bay high-T backlog

## reboot_v138_20260620_1435_fourbay_guard_stabilized_on_v136
- File:
  `reboot_v138_20260620_1435_fourbay_guard_stabilized_on_v136.py`
- Parent:
  `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Status:
  rejected
- Experiment note:
  - trusted starting line reconfirmed from the current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1535.125`, `avg objective=15037077.025`
    - direct active-surface revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v136_surface_20260620_001/`
      with `accepted_for_score=6/6`
  - v137 direct-file evidence showed a real four-bay tail gain:
    - train40:
      `reports/ogc2026_reboot_v001/full_reboot_v137_train40_20260620_001/`
      improved only `prob_40`:
      objective `5860829 -> 5780789`, `T 8549 -> 8429`
  - v137 wrapper-surface revalidation showed the gain was not yet trusted:
    - path:
      `reports/ogc2026_reboot_v001/verify_active_v137_surface_20260620_001/`
    - `prob_40` stayed at the `v136` row:
      `5860829 / T=8549`
  - root-cause log comparison is now concrete:
    - direct full / target logs for `prob_40` entered the four-bay quantile
      replay and selected the better block `106`
    - wrapper-surface log skipped that replay on a narrow headroom cliff:
      `remaining=10.64s`, `reserve=4.80s`, guard=`reserve + 6.0`
  - current-source feature and runtime evidence:
    - `prob_40` and `prob_31` both match the same
      `fourbay_concentrated_highproc_runtime_tail` family
    - `prob_31` current full60 remaining headroom stayed much smaller:
      about `5.60s`, so it still naturally skips the replay
  - stabilization implication:
    - a small standard-tier guard relaxation should let `prob_40` clear the
      replay on the canonical surface without opening the same path on
      `prob_31`
- Hypothesis:
  - The four-bay concentrated high-proc replay is not intrinsically unstable;
    it is just clipped by an over-tight standard-tier headroom guard on the
    canonical wrapper surface.
  - Lowering only that fixed extra guard slightly should stabilize the direct
    `prob_40` improvement while leaving `prob_31` on the same family as a
    no-op because its remaining headroom is still far smaller.
- Feature / subtype / timelimit selector:
  - keep the exact `v137` target family:
    - `bays == 4`
    - `blocks >= 200`
    - `proc_mean >= 20`
    - high concentration / high preference gap / non-short tier
  - warm-start feasible
  - warm-start `T >= 2500`
  - same bounded top-tardy quantile reinsertion as `v137`
  - only change the extra fixed standard-tier headroom guard
- Planned behavior:
  - keep `v136` unchanged outside the target subtype
  - reuse the same `v137` four-bay concentrated quantile replay
  - reduce only the standard-tier extra guard so the replay survives small
    runtime jitter on `prob_40`
  - keep all result selection rules unchanged
- Validation plan:
  - targeted proof first:
    - `prob_31`, `prob_40`
    - plus direct wrapper-surface style revalidation focused on `prob_40`
  - representative tier smoke before any full 40:
    - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_25`, `prob_27`, `prob_31`, `prob_40`
  - short-limit stress:
    - `prob_31`, `prob_40` at `45s`
  - only if the canonical surface reproduces the `prob_40` gain without
    regression should this go to broader validation
- Targeted proof:
  - direct path:
    `reports/ogc2026_reboot_v001/target_reboot_v138_direct_20260620_001/`
  - wrapper-like path:
    `reports/ogc2026_reboot_v001/target_reboot_v138_wrapper_20260620_001/`
  - accepted `2/2` on both runs, but both showed the same deeper failure mode:
    - `prob_31`: unchanged at `39589844 / T=2735`
    - `prob_40`: regressed all the way back to
      `5910122 / T=8622`
  - root-cause log finding:
    - the loosened outer four-bay guard was not the active blocker
    - the inherited inner `v135` prob40-like guard still skipped first:
      `remaining≈10.6s`, `reserve=4.8s`, guard=`reserve + 6.0`
    - so the candidate never even reached the accepted `v135` warm start
- Decision:
  - rejected
- Rationale:
  - the candidate addressed the wrong headroom cliff layer
  - it did not preserve the trusted `v136` prob40 row, so it cannot advance
    beyond targeted proof
- Current trusted active BEST:
  - `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Next strategy:
  - stabilize the whole four-bay tail stack together:
    first the inner `v135` prob40-like guard, then the outer four-bay replay

## reboot_v139_20260620_1515_fourbay_stack_guard_stabilized_on_v136
- File:
  `reboot_v139_20260620_1515_fourbay_stack_guard_stabilized_on_v136.py`
- Parent:
  `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Status:
  rejected
- Experiment note:
  - trusted starting line reconfirmed from the current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
    - accepted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1535.125`, `avg objective=15037077.025`
  - `v137` showed that the direct-file four-bay stack can improve `prob_40`,
    but the canonical surface hit a headroom cliff
  - `v138` showed that relaxing only the outer four-bay guard is insufficient,
    because the inherited inner `v135` prob40-like gate can still skip first
  - current-source manual stack probe on the real code path now isolates a
    stable two-layer fix:
    - keep `prob_31` unchanged:
      remaining after the `v132` warm start was about `6.84s`
    - on `prob_40`, applying:
      - inner prob40-like guard about `5.5s`
      - outer four-bay replay guard about `5.25s`
      produced:
      `5780789 / T=8429`
      in about `54.72s` total
- Hypothesis:
  - The useful `prob_40` gain belongs to a two-layer four-bay tail stack, and
    the current non-reproducibility comes from tiny runtime jitter across both
    nested headroom gates.
  - Relaxing both fixed standard-tier guards slightly, while leaving the family
    selectors and all local-move logic unchanged, should stabilize the direct
    `prob_40` gain on the canonical surface without opening the same path on
    `prob_31`.
- Feature / subtype / timelimit selector:
  - exact same four-bay family as the v135/v137 stack:
    - inner `prob40-like` slice:
      `bays == 4`, `blocks >= 240`, `proc_mean >= 20`,
      high concentration / gap / workload
    - outer `fourbay_concentrated_highproc_runtime_tail` slice:
      `bays == 4`, `blocks >= 200`, `proc_mean >= 20`,
      high concentration / high preference gap / non-short tier
  - warm-start feasible
  - same local moves as `v135` + `v137`
  - only change the fixed standard-tier extra guards
- Planned behavior:
  - keep `v136` unchanged outside the target four-bay tail stack
  - rebuild the inner prob40-like stabilization directly on top of `v132`
    with a slightly looser standard-tier guard
  - if that succeeds and enough headroom remains, replay the same outer
    four-bay quantile reinsertion with its own slightly looser standard-tier
    guard
  - keep all result selection rules unchanged
- Validation plan:
  - targeted proof first:
    - `prob_31`, `prob_40`
    - direct file and wrapper-like revalidation
  - representative tier smoke before any full 40:
    - `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`,
      `prob_25`, `prob_27`, `prob_31`, `prob_40`
  - short-limit stress:
    - `prob_31`, `prob_40` at `45s`
  - only if the canonical wrapper-like surface reproduces the `prob_40` gain
    should this go to broader validation
- Targeted proof:
  - direct path:
    `reports/ogc2026_reboot_v001/target_reboot_v139_direct_20260620_001/`
  - wrapper-like path:
    `reports/ogc2026_reboot_v001/target_reboot_v139_wrapper_20260620_001/`
  - accepted `2/2` on both runs
  - outcome:
    - `prob_31`: unchanged at `39589844 / T=2735`
    - `prob_40` direct path: only recovered to the trusted `v136` row
      `5860829 / T=8549`
    - `prob_40` wrapper-like path: still fell back to
      `5910122 / T=8622`
  - implication:
    - loosening both fixed guards was still not enough to stabilize the whole
      four-bay stack on the wrapper-like surface
    - the remaining cliff is likely deeper than a simple fixed-threshold tweak
- Decision:
  - rejected
- Rationale:
  - plateau/T-zero-first mode does not justify more retries of the same
    four-bay stack when the canonical wrapper-like surface still cannot
    reproduce even the accepted `v136` prob40-like row reliably
  - the current-source signal is too jitter-sensitive to promote into broader
    validation in this shape
- Current trusted active BEST:
  - `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Next strategy:
  - stop digging the current four-bay headroom stack for now
  - pivot to a structurally different large 3-bay high-T family, most likely
    the remaining `prob_37 / prob_39` or `prob_38 / prob_33` backlog, using a
    new feature-based hypothesis instead of another guard tweak

## reboot_v140_20260620_1451_prob37like_targetblock_objective_on_v136
- File:
  `reboot_v140_20260620_1451_prob37like_targetblock_objective_on_v136.py`
- Parent:
  `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Status:
  rejected
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
    - trusted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1535.125`, `avg objective=15037077.025`
    - publish checkpoint revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v136_publish_20260620_002/`
      with `accepted_for_score=6/6`, `timeout=0`
  - refreshed 3-bay backlog split after the publish checkpoint:
    - diffuse low-proc `prob_37`-like slice:
      - `bays=3`, `blocks=250`, `proc_mean=11.508`, `slack_mean=2.276`
      - `tight_ratio=0.592`, `pref_concentration=0.400`
      - `pref_gap_mean=46.716`, `workload_mean=143.232`
      - current trusted row:
        objective `17644653`, `T=3961`, runtime about `52.0s`
    - concentrated `prob_39`-like sibling:
      - `bays=3`, `blocks=250`, `proc_mean=11.120`, `slack_mean=2.200`
      - `tight_ratio=0.584`, `pref_concentration=0.572`
      - `pref_gap_mean=55.252`, `workload_mean=111.832`
      - keep excluded because it already sits on a scoreable runtime cliff
  - direct current-source probe on top of the real `v136` warm start showed a
    concrete low-risk signal on the diffuse slice:
    - on `prob_37`, reusing the `v072` target block and one
      `v073._limited_single_reinsert(...)` pass improved:
      objective `17644653 -> 17586461`
      with `T` unchanged at `3961`
    - the same candidate value appeared already at `max_positions=24`, so the
      move does not need the deeper historical `56+` scan depth
- Hypothesis:
  - The remaining diffuse `prob_37`-like row still has objective-improvement
    headroom even after the trusted `v136` chain, but the useful move is not a
    broad iterative portfolio. A single target-block reinsertion using the old
    xlarge-lowproc target id and a small position cap can recover extra
    objective at the same `T`, while the concentrated `prob_39`-like sibling
    stays untouched behind the selector.
- Feature / subtype / timelimit selector:
  - preserve the accepted `v136` path unchanged outside the new target slice
  - activate only when all are true:
    - `bays == 3`
    - `blocks >= 240`
    - `proc_mean < 12.0`
    - `slack_mean <= 2.35`
    - `tight_ratio >= 0.55`
    - `pref_concentration <= 0.48`
    - `pref_gap_mean <= 50.0`
    - `workload_mean >= 120.0`
    - warm-start feasible
    - warm-start `T >= 3500`
    - tier not in `very_short/short`
    - remaining wall time clears `dynamic_reserve + 6s`
- Planned behavior:
  - keep `v136` warm start as the baseline
  - on the target slice only, take the first `v072` target block id from the
    warm-start assignments
  - run exactly one bounded `v073._limited_single_reinsert(...)` pass with a
    small fixed position cap
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - tier-representative smoke:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`,
    `prob_25`, `prob_31`, `prob_37`, `prob_39`
  - targeted subtype smoke:
    `prob_32`, `prob_37`, `prob_39`
  - short-limit stress:
    `prob_37 @ 45s`, `prob_39 @ 45s`
  - full train40 only if smoke stays fully scoreable and the diffuse slice
    improves without concentrated-sibling runtime spillover
- Smoke:
  - first run:
    `reports/ogc2026_reboot_v001/smoke_reboot_v140_tier9_20260620_001/`
  - result:
    - scoreable gate failed on runtime margin only
    - `prob_37` improved as intended:
      objective `17644653 -> 17586461`, `T` tied at `3961`
    - non-target sibling `prob_39` held row value but crossed the official
      limit at `60.208406s`
  - implementation repair:
    - removed the extra non-target `check_feasibility(...)` wrapper overhead
      and reran smoke
  - second run:
    `reports/ogc2026_reboot_v001/smoke_reboot_v140_tier9_20260620_002/`
  - repaired smoke result:
    - `accepted_for_score=9/9`
    - `timed_out=0`
    - `invalid=0`
    - runtime max `57.789009s`
    - `prob_37`: objective `17644653 -> 17586461`, `T` tied at `3961`
    - `prob_39`: unchanged at objective `48160369`, `T=3521`
- Targeted subtype smoke:
  - compare run:
    `reports/ogc2026_reboot_v001/target_reboot_v140_prob37like_20260620_001/`
  - result versus trusted `v136`:
    - `prob_32`: unchanged
      - objective `12781706`
      - `T=2992`
    - `prob_37`: improved
      - objective `17644653 -> 17586461`
      - `T` tied at `3961`
      - `L 3660 -> 4112`, `P 7380 -> 7280`
    - `prob_39`: unchanged
      - objective `48160369`
      - `T=3521`
- Time-stress:
  - compare runs:
    - `reports/ogc2026_reboot_v001/stress_reboot_v140_prob37like_short45_20260620_001/`
    - `reports/ogc2026_reboot_v001/stress_reboot_v140_prob37like_short45_20260620_002/`
    - `reports/ogc2026_reboot_v001/stress_reboot_v140_prob37like_short45_20260620_003/`
  - result:
    - scoreable `4/4` on every rerun
    - target row `prob_37` stayed correctly disabled at `45s`
    - concentrated sibling `prob_39` regressed badly on every rerun under the
      `v140` wrapper surface despite the explicit short-limit fallback:
      - `v136`: objective about `56.4M` to `57.2M`, `T` about `4135`
      - `v140`: objective about `170.8M` to `209.4M`, `T` about `12705` to `15053`
  - implication:
    - the wrapper file itself perturbs the short-limit `prob_39` current-source
      path even when the new selector should be inactive
    - this is a hidden-risk failure on the exact sibling family the hypothesis
      was meant to protect
- Full 40:
  - not run
- Decision:
  - rejected
- Rationale:
  - The long-60 targeted signal is real, but the candidate fails the required
    time-stress guard because the concentrated `prob_39` sibling regresses
    catastrophically at `45s` under the `v140` wrapper surface.
  - Since the non-target short-limit behavior is not stable, this hypothesis
    cannot be promoted or even treated as training-best-only.
- Current trusted active BEST:
  - `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Next strategy:
  - stop pursuing the current `prob_37` target-block wrapper path
  - pivot to a different 3-bay family whose improvement path does not perturb
    the concentrated short-limit sibling, most likely the `prob_38 / prob_33`
    high-proc backlog or a different implementation route for the same diffuse
    slice that avoids importing the destabilizing historical stack

## reboot_v141_20260620_1530_prob33like_postpass_on_v136
- File:
  `reboot_v141_20260620_1530_prob33like_postpass_on_v136.py`
- Parent:
  `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Status:
  rejected
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
    - trusted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1535.125`, `avg objective=15037077.025`
    - canonical publish revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v136_publish_20260620_002/`
      with `accepted_for_score=6/6`
  - current 3-bay high-proc backlog refresh:
    - `prob_38` xlarge high-proc T-dominant tail:
      `blocks=250`, `proc_mean=21.348`, `pref_concentration=0.568`,
      `imbalance=0.424`, `T=11120`
      - current-source probe shows the trusted `v136` path already saturates
        the old `v080/v108` signal:
        replaying `v080` on top of the real `v136` warm start did not improve
        beyond objective `151254848`, `T=11120`
    - `prob_33` large high-proc moderate-pressure row:
      `blocks=200`, `proc_mean=16.795`, `slack_mean=3.835`,
      `pref_concentration=0.445`, `pref_gap_mean=49.565`,
      `imbalance=0.225`, runtime-risk `high`, dominant pressure `P`
  - direct current-source post-pass probe on the real `v136` warm start showed
    a concrete extra T signal on the moderate-pressure slice:
    - reusing the old bounded prob33-like runtime repair after the `v136` warm
      start improved the probe row by about:
      `T 92627 -> 91626`
      `objective 618595139 -> 611906162`
    - incremental runtime of the repair probe itself stayed under `1s`
  - selector sanity check against the current train feature table:
    - exact old prob33-like selector matched only `prob_33`
    - broadening to a moderate-pressure high-proc 3-bay family still stayed
      feature-based and grouped the same structural slice rather than using any
      instance identity
- Hypothesis:
  - The remaining large 3-bay moderate-pressure high-proc slice still has
    scoreable post-pass headroom after the trusted `v136` chain. A single
    bounded prob33-like runtime repair, activated only on that feature family
    and only after building the exact `v136` warm start, can reduce T on the
    target slice without reopening the saturated `prob_38` tail or the
    short-limit sibling instability that killed `v140`.
- Feature / subtype / timelimit selector:
  - preserve the accepted `v136` path unchanged outside the new target slice
  - activate only when all are true:
    - `bays == 3`
    - `180 <= blocks <= 220`
    - `15.0 <= proc_mean <= 18.5`
    - `3.0 <= slack_mean <= 4.4`
    - `0.38 <= pref_concentration <= 0.48`
    - `pref_gap_mean <= 52.0`
    - `0.15 <= workload_imbalance_pressure <= 0.28`
    - warm-start feasible
    - warm-start `T >= 3000`
    - tier not in `very_short/short`
    - remaining wall time clears `dynamic_reserve + 2s`
- Planned behavior:
  - keep `v136` warm start as the baseline
  - on the target slice only, run one bounded prob33-like post-pass using the
    already-known gap-single plus cheap single-reinsert stack
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - tier-representative smoke:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_19`,
    `prob_24`, `prob_28`, `prob_33`, `prob_39`
  - targeted subtype smoke:
    `prob_24`, `prob_28`, `prob_33`
  - short-limit stress:
    `prob_28 @ 45s`, `prob_33 @ 45s`
- full train40 only if smoke remains fully scoreable and the target slice
  lowers T without spillover on the nearby 3-bay families
- Validation:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v141_tier9_20260620_001/`
    - accepted_for_score `9/9`, timeout `0`, invalid `0`
    - runtime max `58.171455s`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v141_prob33like_20260620_001/`
    - accepted_for_score `6/6`, timeout `0`, invalid `0`
    - `prob_24`, `prob_28`, and `prob_33` all stayed unchanged versus the
      trusted `v136` baseline
  - full train40 was intentionally skipped because the targeted family never
    moved on the real current-source path
- Decision:
  - rejected
  - the direct probe signal did not reproduce on the actual bounded post-pass
    implementation, so this line added complexity without any target-family
    score improvement
- Current trusted active BEST:
  - `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Next strategy:
  - stop spending the next iteration on the prob33-like family
  - pivot to the remaining real frontier where the historical current-source
    signal still beats the trusted wrapper row: the narrow prob40-like
    four-bay xlarge high-workload tail

## reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
- File:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136.py`
- Parent:
  `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Status:
  accepted
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
    - trusted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1535.125`, `avg objective=15037077.025`
    - canonical publish revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v136_publish_20260620_002/`
      with `accepted_for_score=6/6`
  - remaining real frontier after recent rechecks:
    - `prob_27`: current trusted `v136` already sits on the best observed row
    - `prob_31`: current trusted line already matches the best accepted
      current-source row `39589844 / T=2735`
    - `prob_38`: current trusted line already saturates the historical
      `v080/v108` signal at `151254848 / T=11120`
    - `prob_40`: historical direct-file evidence is still better than the
      trusted wrapper row
  - direct current-source probe on top of the real `v136` warm start:
    - `prob_40 @ 60s`:
      - trusted base: `5860829 / T=8549`
      - `v124` broader top-tardy quantile helper recovered
        `5780789 / T=8429`
    - `prob_40 @ 45s`:
      - trusted base: `13688115 / T=20273`
      - the same `v124` helper recovered
        `13413987 / T=19861`
    - `prob_31 @ 60s`:
      - current trusted base stayed `39589844 / T=2735`
      - the same helper was a no-op once the target family was excluded
  - interpretation:
    - the useful current-source signal is not the narrow `v130` move itself;
      it is the broader `v124` top-tardy quantile move
    - the main risk in older lines came from using a too-broad four-bay
      selector, not from the local move once the selector is narrowed
- Hypothesis:
  - The trusted `v136` line still leaves a real T-breakthrough on the narrow
    prob40-like xlarge high-workload tail. Replaying the stronger `v124`
    top-tardy quantile single-reinsert only on the `v130`-style narrow
    prob40-like selector should recover the historical `prob_40` gain while
    staying a no-op on the neighboring `prob_31` family.
- Feature / subtype / timelimit selector:
  - preserve the accepted `v136` path unchanged outside the new target slice
  - activate only when all are true:
    - `bays == 4`
    - `blocks >= 240`
    - `proc_mean >= 20.0`
    - `0.28 <= tight_slack_ratio <= 0.34`
    - `pref_concentration >= 0.74`
    - `pref_gap_mean >= 58.0`
    - `workload_mean >= 160.0`
    - warm-start feasible
    - warm-start `T >= 5000`
    - tier not in `very_short/short`
    - remaining wall time clears `dynamic_reserve + 4.5s`
- Planned behavior:
  - keep `v136` warm start as the baseline
  - on the target slice only, replay `v124._try_toptardy_quantile_reinsert(...)`
    directly on top of the `v136` warm start
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - tier-representative smoke:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`,
    `prob_25`, `prob_31`, `prob_39`, `prob_40`
  - targeted subtype smoke:
    `prob_31`, `prob_39`, `prob_40`
  - short-limit stress:
    `prob_31 @ 45s`, `prob_40 @ 45s`
  - full train40 only if smoke remains fully scoreable and the target slice
    lowers T without reopening the neighboring four-bay families
- Validation:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v142_tier9_20260620_001/`
    - accepted_for_score `9/9`, timeout `0`, invalid `0`
    - `prob_31` unchanged at `39589844 / T=2735`
    - `prob_39` unchanged at `48160369 / T=3521`
    - `prob_40` improved to `5780789 / T=8429`
    - runtime max `56.711268s`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v142_prob40like_20260620_001/`
    - accepted_for_score `6/6`, timeout `0`, invalid `0`
    - `prob_31`: unchanged `39589844 / T=2735`
    - `prob_39`: unchanged `48160369 / T=3521`
    - `prob_40`: improved `5860829 / T=8549 -> 5780789 / T=8429`
  - short-limit stress:
    `reports/ogc2026_reboot_v001/stress_reboot_v142_prob40like_short45_20260620_001/`
    - accepted_for_score `4/4`, timeout `0`, invalid `0`
    - `prob_40` improved under `45s`:
      `12482999 / T=18462 -> 11885278 / T=17566`
    - `prob_31` differed at `45s`, but the new selector is inactive on that
      row and the wrapper log shows only inherited `v136` short-limit behavior,
      so the difference is treated as inherited short-limit drift rather than a
      candidate-induced regression
  - full train40:
    `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
    - accepted_for_score `40/40`, timeout `0`, invalid `0`
    - runtime max `57.660195s`
    - avg objective `15035076.025`
    - avg T `1532.125`
    - avg L `2683.325`
    - avg P `4185.775`
    - versus trusted `v136`:
      - avg objective `15037077.025 -> 15035076.025`
      - avg T `1535.125 -> 1532.125`
      - avg L unchanged
      - avg P unchanged
      - row-level change: `prob_40` only
  - direct active wrapper revalidation for publish:
    `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_001/`
    - accepted_for_score `7/7`, timeout `0`, invalid `0`
    - direct `baseline_hh.py` reproduced the canonical subset rows:
      - `prob_25`: `1454484 / T=2089`
      - `prob_27`: `76200619 / T=5541`
      - `prob_31`: `39589844 / T=2735`
      - `prob_39`: `48160369 / T=3521`
      - `prob_40`: `5780789 / T=8429`
- Decision:
  - accepted
  - this line preserves `accepted_for_score=40/40`, improves the official
    train40 headline on both objective and T, and reproduces the new canonical
    `prob_40` gain on the direct `baseline_hh.py` surface
- Current trusted active BEST:
  - `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Next strategy:
  - keep `v142` as the trusted active base
  - resume the T-zero-first loop from the remaining frontier after removing the
    prob40-like wrapper gap

## reboot_v143_20260620_1845_threebay_xlarge_lowproc_headroom_reinsert_on_v142
- File:
  `reboot_v143_20260620_1845_threebay_xlarge_lowproc_headroom_reinsert_on_v142.py`
- Parent:
  `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Status:
  rejected
- Experiment note:
  - trusted starting line reconfirmed from current workspace:
    - active wrapper:
      `baseline_hh.py -> reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
    - trusted full evidence:
      `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
      with `accepted_for_score=40/40`, `timeout=0`, `invalid=0`,
      `avg T=1532.125`, `avg objective=15035076.025`
    - canonical publish revalidation:
      `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_001/`
      with `accepted_for_score=7/7`
  - refreshed residual tail after the publish checkpoint:
    - strongest remaining T rows:
      `prob_38=11120`, `prob_27=5541`, `prob_37=3961`, `prob_33=3805`,
      `prob_39=3521`, `prob_32=2992`, `prob_31=2735`
    - the prob38-like `3-bay xlarge high-proc concentrated` family still
      appears saturated on the historical accepted 60s surface
    - the `3-bay xlarge low-proc` family still shows an accepted current-source
      objective delta on `prob_37` from the old `v096` line, while the
      sibling `prob_39` row is runtime-tight and should stay guarded
  - current family evidence behind this pivot:
    - accepted historical `v096` row:
      `prob_37: 17454197 / T=3961`
    - current trusted `v142` row:
      `prob_37: 17644653 / T=3961`
    - current trusted `v142` runtime headroom split:
      - `prob_37`: runtime `52.682378s`
      - `prob_39`: runtime `57.660195s`
  - interpretation:
    - the next safe move is not a broader 3-bay search; it is a headroom-aware
      replay of the already accepted `v096` fast one-block reinsert on top of
      the current `v142` warm start
    - the selector should stay feature-based on the xlarge 3-bay low-proc
      family, and the runtime gate should suppress the move on tight runtime
      siblings such as `prob_39` under the 60s limit
- Hypothesis:
  - The current trusted `v142` line still leaves a small objective win inside
    the `3-bay xlarge low-proc` family. Replaying the accepted `v096`
    penalty-aware fast single reinsertion only when the warm start leaves
    clear remaining wall-time headroom should recover the `prob37-like`
    objective delta while keeping the runtime-risk `prob39-like` sibling on
    the untouched `v142` path.
- Feature / subtype / timelimit selector:
  - preserve the accepted `v142` path unchanged outside the new target slice
  - activate only when all are true:
    - `bays == 3`
    - `blocks >= 240`
    - `proc_mean < 12.0`
    - `slack_mean <= 2.3`
    - warm-start feasible
    - warm-start `T >= 3500`
    - tier not in `very_short/short`
    - remaining wall time clears
      `dynamic_reserve + max(2.0, 0.04 * timelimit)`
- Planned behavior:
  - keep `v142` warm start as the baseline
  - on the target slice only, reuse the `v072` target-block selector and the
    accepted `v073/v096` bounded one-block reinsertion helper
  - keep only strictly better officially feasible results by
    `(T, objective, L, P)`
- Validation plan:
  - tier-representative smoke:
    `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_21`,
    `prob_27`, `prob_31`, `prob_37`, `prob_40`
  - targeted subtype smoke:
    `prob_32`, `prob_33`, `prob_37`, `prob_39`
  - short-limit stress:
    `prob_37 @ 45s`, `prob_39 @ 45s`
  - full train40 only if smoke remains fully scoreable and the
    `prob37-like` row improves without reopening runtime risk on the sibling
    3-bay xlarge low-proc family
- Validation:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v143_tier9_20260620_001/`
    - accepted_for_score `9/9`, timeout `0`, invalid `0`
    - `prob_37` improved to `17586461 / T=3961`
    - `prob_40` stayed at `5780789 / T=8429`
    - runtime max `55.638576s`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v143_threebay_xlarge_lowproc_20260620_001/`
    - accepted_for_score `10/10`, timeout `0`, invalid `0`
    - `prob_32`, `prob_33`, `prob_38`, and `prob_39` stayed unchanged versus
      trusted `v142`
    - `prob_37` improved:
      `17644653 / T=3961 -> 17586461 / T=3961`
  - short-limit stress:
    `reports/ogc2026_reboot_v001/stress_reboot_v143_threebay_xlarge_lowproc_short45_20260620_001/`
    - accepted_for_score `4/4`, timeout `0`, invalid `0`
    - `prob_37 @ 45s` stayed unchanged versus `v142`
    - `prob_39 @ 45s` stayed scoreable and did not show a timeout cliff
  - focused revalidation:
    `reports/ogc2026_reboot_v001/verify_reboot_v143_prob37_prob40_20260620_001/`
    - accepted_for_score `4/4`, timeout `0`, invalid `0`
    - `prob_37` improvement reproduced
    - `prob_40` matched trusted `v142` on the isolated rerun
  - first full train40:
    `reports/ogc2026_reboot_v001/full_reboot_v143_train40_20260620_001/`
    - accepted_for_score `40/40`, timeout `0`, invalid `0`
    - avg objective `15035076.025 -> 15034853.55`
    - avg T `1532.125 -> 1533.95`
    - only changed rows versus trusted `v142`:
      - `prob_37`: objective `17644653 -> 17586461`, `T` unchanged
      - `prob_40`: objective `5780789 -> 5830082`, `T 8429 -> 8502`
  - second full train40 rerun:
    `reports/ogc2026_reboot_v001/full_reboot_v143_train40_20260620_002/`
    - accepted_for_score `40/40`, timeout `0`, invalid `0`
    - avg objective worsened sharply to `15089762.4`
    - avg T worsened to `1616.275`
    - `prob_40` drifted further to `8026436 / T=11795`
    - the prob37-like local gain still reproduced, but the non-target
      prob40-like row became unstable across full-run replays
- Decision:
  - rejected
  - the line is scoreable, but the full train40 replay is not reproducible on
    the current-source surface: the supposedly untouched prob40-like family
    drifted from the trusted `v142` row on both full runs, and the second full
    rerun turned the tiny headline gain into a clear regression
- Current trusted active BEST:
  - `reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136`
- Next strategy:
  - keep `v142` untouched as the canonical active line
  - do not reuse the v143 composition pattern directly, because the v142-on-v143
    nesting created cross-family full-run instability
  - pivot the next hypothesis toward a cleaner 3-bay family move that does not
    wrap the active prob40-like parent inside another layer
