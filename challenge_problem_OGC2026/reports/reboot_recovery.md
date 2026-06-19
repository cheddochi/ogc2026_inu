# OGC2026 Reboot Recovery

Generated: 2026-06-16

## Scope

This recovery pass keeps the current branch and working tree intact. No prior
benchmark outputs, algorithm versions, or CSV/HTML reports are deleted or
rewritten. Historical artifacts are retained only as forensic records until
they are rerun under the reboot validation contract.

## Git Snapshot

- Branch: `hh_algorithm_loop`
- HEAD: `48056deebcf014905e0057d00eae1aeef55c880f`
- Required policy: no branch creation, branch switching, reset, rewrite, commit,
  or push during this reboot pass.

## Current Dirty/Untracked Areas Observed

- `ogc2026/baseline/alg_versions/README.md`
- `ogc2026/baseline/alg_versions/baseline_hh_v007_limited_concurrent.py`
- `ogc2026/batchrunner/README.md`
- `ogc2026/batchrunner/benchmark.py`
- `reports/ogc2026_benchmark/benchmark_results.csv`
- `reports/ogc2026_benchmark/scratch_probe_results.csv`
- Multiple untracked `reports/ogc2026_benchmark/*v007*` run directories
- Existing reboot scratch area: `reports/ogc2026_reboot_v001/`

These are treated as pre-existing user/workspace state. This pass does not
revert them.

## Contamination Policy

The following are contaminated for score claims and algorithm selection:

- All historical cumulative CSV files under `reports/ogc2026_benchmark/`.
- All historical HTML/CSV/JSON benchmark reports under
  `reports/ogc2026_benchmark/`.
- Any `latest`, `best`, `active`, or `v007` claim produced before
  timeout-aware `accepted_for_score` reporting.
- HH variants `baseline_hh_v001_*` through `baseline_hh_v007_*` when used as
  trusted best claims. They may be inspected as code, but cannot be used as
  trusted baselines or winners without a clean reboot rerun.

Reference-only files:

- `ogc2026/baseline/alg_versions/baseline_hh_v000_original.py`
- `ogc2026/baseline/alg_versions/myalgorithm_v000_original.py`

## Clean Reboot Rule

Future benchmark comparisons must use:

```text
accepted_for_score =
  checker_feasible == true
  AND timed_out == false
  AND runtime_sec <= official_limit
  AND error_message empty
```

`checker_feasible` alone is not a scoring-valid feasibility count.

## Immediate Recovery Actions

- Add an explicit contaminated legacy manifest.
- Add problem and validation contract audit documents.
- Patch batch reporting so readable CSV and HTML headlines use
  `accepted_for_score`, not checker feasibility alone.
- Validate timeout classification with a controlled slow dummy algorithm before
  any full 40-instance benchmark.

## Manual Cycle 2026-06-16 16:28 KST

- Current branch was kept as `hh_algorithm_loop`.
- No legacy files were deleted.
- No benchmark was started.
- No algorithm logic was edited in this manual cycle.
- Official contract was re-anchored from README files, checker code,
  batchrunner code, and existing reboot audit notes.
- Current active HH chain is now documented as:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `reboot_v002_20260616_1547_candidate_slack_preference.algorithm`.
- Trusted reboot evidence currently includes timeout classification smoke,
  accepted reference smoke, v002 full train40, and rejected v003 subset smoke.
- Detailed cycle audit:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260616_1628_audit.md`
- Detailed cycle manifest:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260616_1628_manifest.json`

## Manual Cycle 2026-06-16 19:27 KST

- Current branch was kept as `hh_algorithm_loop`.
- No legacy files were deleted.
- No benchmark was started.
- No algorithm logic was edited in this manual cycle.
- Official problem/checker/submission/timeout/reporting/versioning contract was
  re-anchored from the local README files, checker, batchrunner, active
  entrypoint, version notes, and existing recovery notes.
- Historical `reports/ogc2026_benchmark/` outputs and prior-loop HH
  `baseline_hh_v001_*` through `baseline_hh_v007_*` claims remain
  contaminated for score claims unless reproduced under the reboot
  `accepted_for_score` contract.
- Current active HH implementation was observed as consolidated
  `baseline_hh_20260616_consolidated_v007_best`, while `ACTIVE_VERSION.md`
  still describes a thin import to `reboot_v007`; this versioning-doc mismatch
  should be fixed before the next algorithm edit.
- Detailed cycle audit:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260616_1927_audit.md`
- Detailed cycle manifest:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260616_1927_manifest.json`
- Contaminated manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260616_1927.json`

## Manual Progress 2026-06-16 19:50 KST

- A v008 candidate was tested on target instances only:
  `reports/ogc2026_reboot_v001/smoke_reboot_v008_targets_20260616_001/`.
- The smoke accepted 4/4 with timeout 0, but T regressed on `prob_31`,
  `prob_37`, and `prob_40`; full train40 was skipped.
- Active HH was restored to trusted
  `reboot_v007_20260616_1835_midT_param_pack`.
- Restore smoke passed 2/2:
  `reports/ogc2026_reboot_v001/smoke_active_v007_restore_20260616_001/`.
- Rejection note:
  `reports/ogc2026_reboot_v001/reboot_v008_rejection_20260616_1950.md`

## Manual Progress 2026-06-16 20:15 KST

- v009 isolated the `prob_33` improvement and passed smoke, but exposed current
  v007 runtime variability on `prob_40`; it was superseded before full train40.
- v010 combined `prob_33` with a `prob_40` runtime guard and completed full
  train40:
  `reports/ogc2026_reboot_v001/full_reboot_v010_train40_20260616_001/`.
- v010 accepted 40/40 with timeout 0, but avg T regressed from trusted v007
  `2215.325` to `2217.65`; active HH was restored to trusted v007.
- Rejection note:
  `reports/ogc2026_reboot_v001/reboot_v010_rejection_20260616_2015.md`

## Manual Progress 2026-06-16 20:30 KST

- v011 combined the `prob_33` improvement with larger internal builder budgets
  for high-runtime `prob_36` and `prob_40`.
- v011 target smoke passed 4/4:
  `reports/ogc2026_reboot_v001/smoke_reboot_v011_targets_20260616_001/`.
- v011 full train40 passed with `accepted_for_score=40/40`, timeout 0:
  `reports/ogc2026_reboot_v001/full_reboot_v011_train40_20260616_001/`.
- Avg T improved from trusted v007 `2215.325` to `2191.55`; only `prob_33`
  changed versus v007, T `5187 -> 4236`.
- v011 is now trusted active.
- Validation note:
  `reports/ogc2026_reboot_v001/reboot_v011_validation_20260616_2030.md`

## Manual Recovery Cycle 2026-06-16 20:30 KST

- Current branch was kept as `hh_algorithm_loop`.
- No legacy files were deleted.
- No benchmark was started.
- No algorithm logic was edited in this manual cycle.
- Official problem/checker/submission/timeout/reporting/versioning contract was
  re-anchored from the local README files, checker, batchrunner, active
  entrypoint, version notes, recovery notes, and v011 full-run manifest.
- Historical `reports/ogc2026_benchmark/` outputs, scratch probe CSVs, nested
  accidental output roots, and prior-loop HH `baseline_hh_v001_*` through
  `baseline_hh_v007_*` claims remain contaminated for score claims unless
  reproduced under the reboot `accepted_for_score` contract.
- Current active HH implementation was observed as a thin wrapper to
  `reboot_v011_20260616_2025_prob33_guarded_high_runtime`.
- v011 clean full train40 evidence remains trusted:
  `accepted_for_score=40/40`, timeout 0, avg T/obj1 `2191.55`.
- The v011 version-file header still says candidate/pending; this is stale
  metadata to clean up before the next algorithm edit, not an algorithm change
  made in this cycle.
- Detailed cycle audit:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260616_2030_audit.md`
- Detailed cycle manifest:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260616_2030_manifest.json`
- Contaminated manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260616_2030.json`

## Manual Progress 2026-06-16 20:55 KST

- v011 header metadata was synchronized with its already-validated active
  state; no algorithm logic changed in v011.
- A direct official-checker probe found a better `prob_38` policy:
  `due_long_proc`, `top_bays=3`, `max_positions=16`, `budget=52`.
- v012 was added as a versioned candidate and then promoted to active after
  target/full validation:
  `ogc2026/baseline/alg_versions/reboot_v012_20260616_2040_prob38_deeper_positions.py`
- Active wrapper now points to v012:
  `ogc2026/baseline/baseline_hh.py`
- v012 target smoke passed with `accepted_for_score=4/4`, timeout 0:
  `reports/ogc2026_reboot_v001/smoke_reboot_v012_targets_20260616_001/`.
- v012 full train40 passed with `accepted_for_score=40/40`, timeout 0:
  `reports/ogc2026_reboot_v001/full_reboot_v012_train40_20260616_001/`.
- Avg T improved from trusted v011 `2191.55` to `2121.55`.
- Only `prob_38` changed versus v011: T `14157 -> 11357`; no T regressions,
  no infeasible rows.
- Validation note:
  `reports/ogc2026_reboot_v001/reboot_v012_validation_20260616_2055.md`

## Recovery Checkpoint 2026-06-19 13:10 KST

- Branch was kept as `hh_algorithm_loop`; no reset, rewrite, or branch switch
  was used.
- Current active wrapper still points at historical checkpoint
  `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`, but that
  claim is no longer treated as current-source trusted.
- Why it is not publishable as a trusted BEST:
  - `reports/ogc2026_reboot_v001/target_recheck_v096_fourbay_runtime_20260619_001/`
    reproduces a prob31-like timeout:
    - `prob_31`: runtime `70.680680s`, objective `46503155`
  - `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/`
    reproduces a prob37-like timeout:
    - `prob_37`: runtime `71.377730s`, objective `17644653`
  - fallback recovery candidate
    `reports/ogc2026_reboot_v001/full_recheck_v083_train40_20260619_001/`
    only reached `accepted_for_score=39/40`
- Historical best evidence is still preserved:
  - `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`
  - `benchmark_report.md` in that directory remains the team-readable record of
    the historical accepted train40 result.
- Current recovery conclusion:
  - historical best: v096
  - current-source trusted accepted BEST: none established
  - next repair focus: flatten or cap the inherited prob37-like
    `v060 release_due` warm-start path so later cheap reinsertion phases are
    no longer starved of time.
- Current contaminated manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260616_2055.json`

## Manual Recovery Cycle 2026-06-16 21:55 KST

- Current branch was kept as `hh_algorithm_loop`.
- No legacy files were deleted.
- No benchmark was started.
- No algorithm logic was edited in this manual cycle.
- Official problem/checker/submission/timeout/reporting/versioning contract was
  re-anchored from local README files, checker code, batchrunner code, active
  entrypoint, version notes, and v013 full-run manifest.
- Current active HH implementation was observed as a thin wrapper to
  `reboot_v013_20260616_2130_prob20_wider_bay_scan`.
- v013 clean full train40 evidence remains trusted:
  `accepted_for_score=40/40`, timeout 0, avg T/obj1 `2102.475`, avg objective
  `23248614.45`.
- Historical `reports/ogc2026_benchmark/` outputs, scratch probe CSVs, nested
  accidental output roots, prior-loop HH `baseline_hh_v001_*` through
  `baseline_hh_v007_*` claims, and non-manifested outputs remain contaminated
  for score claims unless reproduced under the reboot `accepted_for_score`
  contract.
- v014 current state is not trusted for score claims: target smoke exists, but
  `full_reboot_v014_train40_20260616_001/` is incomplete with 35 raw/solution
  files and no summary/readable/report outputs.
- Detailed cycle audit:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260616_2155_audit.md`
- Detailed cycle manifest:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260616_2155_manifest.json`
- Contaminated manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260616_2155.json`

## Manual Progress 2026-06-16 22:33 KST

- v015 keeps trusted v013 behavior and only changes the `prob_38` override
  budget from `52` to `59` for the existing `due_long_proc`, `top_bays=3`,
  `max_positions=16` limited-concurrent search.
- Rationale: direct probes and previous smoke showed `prob_38` quality was
  sensitive to wall-clock cutoff; increasing the internal builder budget avoids
  premature forced empty-window placements while staying inside the official
  60s runtime gate.
- v015 single-row smoke passed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v015_prob38_20260616_001/`
  with `accepted_for_score=1/1`, timeout 0, `prob_38` T `11316`.
- v015 target smoke passed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v015_targets_20260616_001/`
  with `accepted_for_score=6/6`, timeout 0.
- v015 full train40 passed:
  `reports/ogc2026_reboot_v001/full_reboot_v015_train40_20260616_001/`
  with `accepted_for_score=40/40`, timeout 0.
- Active wrapper smoke passed after promotion:
  `reports/ogc2026_reboot_v001/smoke_active_v015_wrapper_20260616_001/`
  with `accepted_for_score=2/2`, timeout 0.
- Avg T improved from trusted v013 `2102.475` to `2040.65`; avg objective
  improved from `23248614.45` to `22399390.125`.
- Changed rows versus v013:
  - `prob_20`: T `358 -> 283`
  - `prob_38`: T `13714 -> 11316`
- No infeasible rows, no timeout rows, and no T regressions were observed.
- Active HH now points to:
  `reboot_v015_20260616_2219_prob38_budget_guard`.
- Validation note:
  `reports/ogc2026_reboot_v001/reboot_v015_validation_20260616_2233.md`
- Current contaminated manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260616_2233.json`

## Manual Progress 2026-06-16 23:06 KST

- v016 keeps trusted v015 behavior and adds two single-instance refinements:
  - `prob_27`: `due_long_proc`, `top_bays=3`, `max_positions=16`, budget `58`
  - `prob_37`: `release_due`, `top_bays=3`, `max_positions=16`, budget `58`
- v016 core smoke passed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v016_core_20260616_001/`
  with `accepted_for_score=2/2`, timeout 0.
- v016 target smoke passed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v016_targets_20260616_001/`
  with `accepted_for_score=6/6`, timeout 0.
- v016 full train40 passed:
  `reports/ogc2026_reboot_v001/full_reboot_v016_train40_20260616_001/`
  with `accepted_for_score=40/40`, timeout 0.
- Active wrapper smoke passed after promotion:
  `reports/ogc2026_reboot_v001/smoke_active_v016_wrapper_20260616_001/`
  with `accepted_for_score=3/3`, timeout 0.
- Avg T improved from trusted v015 `2040.65` to `2031.1`; avg objective
  improved from `22399390.125` to `22362771.975`.
- Changed rows versus v015:
  - `prob_27`: T `5788 -> 5735`
  - `prob_37`: T `4369 -> 4040`
- No infeasible rows, no timeout rows, and no T regressions were observed.
- Active HH now points to:
  `reboot_v016_20260616_2253_prob27_prob37_refine`.
- Validation note:
  `reports/ogc2026_reboot_v001/reboot_v016_validation_20260616_2306.md`
- Current contaminated manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260616_2306.json`

## Manual Progress 2026-06-16 23:36 KST

- Explored `prob_40` deeper position scans on top of trusted v016.
- v017 single-row smoke looked promising:
  `reports/ogc2026_reboot_v001/smoke_reboot_v017_prob40_20260616_001/`
  with `prob_40` T `8622`, but target smoke rejected it:
  `reports/ogc2026_reboot_v001/smoke_reboot_v017_targets_20260616_001/`.
- v017 target smoke was checker-feasible and accepted for time, but `prob_40`
  regressed to T `24863` after the deep scan hit `forced=78`; full train40 was
  skipped.
- v018 conservative variant was also rejected by single-row smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v018_prob40_20260616_001/`
  with `prob_40` T `20836` and `forced=59`.
- Conclusion: `prob_40` deeper position scans are too timing-sensitive in the
  current runner context; active remains trusted v016.
- Rejection note:
  `reports/ogc2026_reboot_v001/reboot_v017_v018_rejection_20260616_2336.md`
- Current contaminated manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260616_2336.json`

## Manual Recovery Cycle 2026-06-16 23:54 KST

- Current branch was kept as `hh_algorithm_loop`.
- No legacy files were deleted.
- No benchmark was started by this cycle.
- No algorithm logic was edited in this cycle.
- Official problem/checker/submission/timeout/reporting/versioning contract was
  re-anchored from the local README files, checker code, batchrunner code,
  active wrapper, version notes, recovery notes, and current clean v016
  evidence.
- The local problem statement PDF exists, but this environment had no available
  PDF text extractor in the cycle; checker/README/batchrunner files remain the
  enforceable local contract.
- Current trusted active HH remains
  `reboot_v016_20260616_2253_prob27_prob37_refine`, with clean full train40
  evidence at
  `reports/ogc2026_reboot_v001/full_reboot_v016_train40_20260616_001/`.
- Trusted v016 status remains `accepted_for_score=40/40`, timeout 0, avg
  T/obj1 `2031.1`.
- An existing v019 target smoke was observed active:
  `reports/ogc2026_reboot_v001/smoke_reboot_v019_targets_20260616_001/`.
  It was not started by this cycle and is not score evidence until complete.
- v019 single-instance evidence observed:
  - `prob_37` accepted, T/obj1 `4052`, objective `18007304`, runtime
    `50.389614s`; this improves weighted objective but regresses primary T
    versus trusted v016 `prob_37` T `4040`.
  - `prob_38` accepted, T/obj1 `11316`, objective `153690186`, runtime
    `56.768275s`.
- Post-write validation observed the v019 target smoke completed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v019_targets_20260616_001/`.
  It accepted `5/5` with timeout 0, but `prob_37` remained a T regression
  (`4040 -> 4052` versus trusted v016).
- A separate v019 full train40 process was then observed active:
  `reports/ogc2026_reboot_v001/full_reboot_v019_train40_20260616_001/`.
  It was not started by this recovery cycle and is not score evidence until
  completed artifacts are inspected.
- Under the current T-first rule, v019 is not a promotion candidate from the
  available smoke evidence alone; keep v016 unless the completed full train40
  provides a clear T-first reason to override.
- Detailed cycle audit:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260616_2354_audit.md`
- Detailed cycle manifest:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260616_2354_manifest.json`
- Contaminated manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260616_2354.json`

## Manual Progress 2026-06-17 00:06 KST

- The previously observed v019 full train40 run completed:
  `reports/ogc2026_reboot_v001/full_reboot_v019_train40_20260616_001/`.
- v019 full train40 was valid evidence:
  - `accepted_for_score=40/40`
  - timeout `0`
  - runtime max `40.047726s`
  - avg objective improved `22362771.975 -> 22362123.475`
  - avg T regressed `2031.1 -> 2031.4`
  - only changed row: `prob_37` T `4040 -> 4052`, objective
    `18033244 -> 18007304`
- Decision: v019 is rejected under the current T-first rule.  The weighted
  objective gain is not enough to accept a T/obj1 regression.
- Corrected stale metadata that had marked v019 as trusted active BEST.
- Active HH restored to:
  `reboot_v016_20260616_2253_prob27_prob37_refine`.
- Restore smoke passed:
  `reports/ogc2026_reboot_v001/smoke_active_v016_restored_20260617_0006/`.
  It accepted `2/2` with timeout 0, and `prob_37` returned to T/obj1
  `4040`.
- Rejection note:
  `reports/ogc2026_reboot_v001/reboot_v019_rejection_20260617_0006.md`
- Current contaminated/rejected-output manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260617_0006.json`

## Manual Progress 2026-06-17 00:32 KST

- Validated current active preference-spread v020 on a fresh unique full-run
  path to avoid confusion with the release-due v020 run:
  `reports/ogc2026_reboot_v001/full_reboot_v020_preference_train40_20260617_001/`.
- Active wrapper:
  `reboot_v020_20260617_0015_prob31_preference_spread`.
- Full train40 result:
  - `accepted_for_score=40/40`
  - timeout `0`
  - runtime max `49.692239s`
  - avg T improved `2031.1 -> 2015.375`
  - avg objective improved `22362771.975 -> 22150076.05`
  - only changed row versus v016: `prob_31` T `3465 -> 2836`
  - no T regressions and no infeasible rows
- The earlier release-due v020 run is valid but superseded:
  `reports/ogc2026_reboot_v001/full_reboot_v020_train40_20260617_001/`.
  It improved avg T only to `2025.275`.
- Validation note:
  `reports/ogc2026_reboot_v001/reboot_v020_preference_validation_20260617_0032.md`
- Current contaminated/rejected-output manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260617_0032.json`

## Manual Progress 2026-06-17 00:57 KST

- Probed `prob_32` on top of trusted v020 preference-spread:
  - trusted v020 `prob_32`: T `3291`, objective `14514538`
  - `release_due`, `top_bays=3`, `max_positions=14`, budget `55`:
    T `3076`, objective `13118978`
- Added v021:
  `ogc2026/baseline/alg_versions/reboot_v021_20260617_0047_prob32_release_due_refine.py`.
- v021 single-row smoke passed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v021_prob32_20260617_001/`.
- v021 target smoke passed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v021_targets_20260617_001/`.
- v021 full train40 passed:
  `reports/ogc2026_reboot_v001/full_reboot_v021_train40_20260617_001/`.
- Active wrapper smoke passed:
  `reports/ogc2026_reboot_v001/smoke_active_v021_wrapper_20260617_001/`.
  It accepted `2/2` with timeout 0, confirming `prob_31` T `2836` and
  `prob_32` T `3076` through `baseline_hh.py`.
- v021 result:
  - `accepted_for_score=40/40`
  - timeout `0`
  - runtime max `39.575383s`
  - avg T improved `2015.375 -> 2010.0`
  - avg objective improved `22150076.05 -> 22115187.05`
  - only changed row: `prob_32` T `3291 -> 3076`
  - no T regressions and no infeasible rows
- Active HH promoted to:
  `reboot_v021_20260617_0047_prob32_release_due_refine`.
- Validation note:
  `reports/ogc2026_reboot_v001/reboot_v021_validation_20260617_0057.md`
- Current contaminated/rejected-output manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260617_0057.json`

## Manual Recovery Cycle 2026-06-17 01:35 KST

- Current branch was kept as `hh_algorithm_loop`.
- No legacy files were deleted.
- No benchmark was started by this cycle.
- No algorithm logic was edited in this cycle.
- Official problem/checker/submission/timeout/reporting/versioning contract was
  re-anchored from local README files, checker code, batchrunner code, active
  wrapper, version notes, and latest clean evidence.
- Current trusted active HH remains:
  `reboot_v021_20260617_0047_prob32_release_due_refine`.
- Active v021 evidence remains:
  `reports/ogc2026_reboot_v001/full_reboot_v021_train40_20260617_001/`
  with `accepted_for_score=40/40`, timeout 0, avg T/obj1 `2010.0`.
- Existing v022 candidate evidence was inspected and classified as
  `validated_candidate_pending_promotion`:
  `reports/ogc2026_reboot_v001/full_reboot_v022_train40_20260617_001/`.
- v022 full train40 result:
  - `accepted_for_score=40/40`
  - timeout `0`
  - runtime max `39.499515s`
  - avg T improved `2010.0 -> 1995.0`
  - avg objective improved `22115187.05 -> 21934192.375`
  - changed rows: `prob_25` T `2911 -> 2851`, `prob_26` T `2885 -> 2345`
  - no unaccepted rows and no T regressions versus v021
- v022 was not promoted in this cycle because `baseline_hh.py` still points to
  v021 and the request explicitly forbade algorithm-logic edits.  The next
  implementation step is a careful v022 wrapper/metadata promotion plus active
  wrapper smoke on `prob_25` and `prob_26`.
- Detailed cycle audit:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260617_0135_audit.md`
- Detailed cycle manifest:
  `reports/ogc2026_reboot_v001/manual_recovery_cycle_20260617_0135_manifest.json`
- Current contaminated/recovery manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260617_0135.json`

## Manual Progress 2026-06-17 01:40 KST

- Promoted v022 to the active HH wrapper:
  `reboot_v022_20260617_0119_prob25_prob26_release_refine`.
- No commit or push was created.
- `py_compile` passed for:
  - `ogc2026/baseline/baseline_hh.py`
  - `ogc2026/baseline/alg_versions/reboot_v022_20260617_0119_prob25_prob26_release_refine.py`
- Active wrapper smoke passed:
  `reports/ogc2026_reboot_v001/smoke_active_v022_wrapper_20260617_0135/`
  with `accepted_for_score=2/2`, checker feasible `2/2`, timeout 0.
- Active wrapper smoke confirmed:
  - `prob_25` T `2851`, objective `1948687`
  - `prob_26` T `2345`, objective `32253881`
- v022 full train40 remains the current trusted score evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v022_train40_20260617_001/`
  with `accepted_for_score=40/40`, timeout 0, avg T/obj1 `1995.0`,
  avg objective `21934192.375`.
- Improvement versus previous trusted v021:
  - avg T/obj1 `2010.0 -> 1995.0`
  - avg objective `22115187.05 -> 21934192.375`
  - `prob_25` T `2911 -> 2851`
  - `prob_26` T `2885 -> 2345`
  - no T regressions and no infeasible/unaccepted rows
- Validation note:
  `reports/ogc2026_reboot_v001/reboot_v022_validation_20260617_0140.md`
- Current contaminated/recovery manifest:
  `reports/ogc2026_reboot_v001/contaminated_manifest_20260617_0140.json`
