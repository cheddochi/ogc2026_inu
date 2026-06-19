# OGC2026 Validation Audit

Generated: 2026-06-16

## Main Finding

The existing benchmark/reporting path can overstate validity because it uses
checker feasibility as the headline feasibility signal and best-row filter.
Rows that exceed the requested official limit can still be checker-feasible if
the subprocess returns before the external watchdog kills it.

## Current Batchrunner Behavior

`ogc2026/batchrunner/benchmark.py` currently:

- Runs each algorithm in a subprocess.
- Passes requested `timelimit` to `algorithm`.
- Uses external watchdog:

```text
timeout = max(timelimit + timeout_grace, timelimit * 1.5)
```

- Calls official `check_feasibility` after a solution is returned.
- Stores `feasible = bool(result.get("feasible"))`.
- Uses `is_feasible_row(row)` for summary counts, best-by-instance, HTML
  headline, infeasible lists, comparison tables, and compact CSV status.

This means a row can be:

- `checker_feasible=true`
- `runtime_sec > requested_timelimit`
- not killed by watchdog because grace allowed it
- counted as feasible/best by current reports

That row must be `accepted_for_score=false`.

## Required Row Semantics

Definitions:

- `checker_feasible`: official checker result only.
- `timed_out`: true when the subprocess watchdog expires, or the measured row
  runtime exceeds the official requested limit.
- `valid_under_time_limit`: true when `runtime_sec <= official_limit` and no
  timeout marker exists.
- `accepted_for_score`: true only when all acceptance conditions hold.

Acceptance formula:

```text
accepted_for_score =
  checker_feasible == true
  AND timed_out == false
  AND runtime_sec <= official_limit
  AND error_message empty
```

## Required Readable CSV Order

`readable_results.csv` must use this fixed human-facing schema:

```text
instance,
blocks,
bays,
objective,
T,
L,
P,
runtime_sec,
checker_feasible,
timed_out,
valid_under_time_limit,
accepted_for_score,
error_message,
algorithm_version,
report_path,
solution_file
```

Debug and provenance columns belong in raw CSV/JSON, not the readable CSV.

## Required HTML Behavior

HTML headline `Feasible X/Y` must mean accepted-for-score rows, not checker
PASS rows.

Best comparisons must exclude rows where:

- `accepted_for_score=false`
- `timed_out=true`
- `runtime_sec > official_limit`
- `error_message` is non-empty

Rows with checker PASS but timeout invalidity must be displayed as timeout or
invalid under time limit, not as scoring-valid feasible rows.

## Contaminated Legacy Outputs

All prior reports under `reports/ogc2026_benchmark/` are classified as
contaminated for score claims. They may be inspected only as forensic records.

The active HH entrypoint currently resolves to v007, so any previous `v007`,
`latest`, or `best` report must not be used as a warm-start benchmark claim.

## Required Smoke Test

Before any full 40-instance run:

1. Run a controlled slow dummy algorithm that returns a checker-feasible
   solution after exceeding a small official timelimit but before watchdog
   expiry.
2. Confirm the row is:
   - `checker_feasible=true`
   - `timed_out=true`
   - `valid_under_time_limit=false`
   - `accepted_for_score=false`
3. Run a normal tiny smoke test and confirm accepted rows still pass.

## Smoke Evidence

Controlled timeout smoke:

- Run directory:
  `reports/ogc2026_reboot_v001/smoke_timeout_classification_20260616_153812/`
- `readable_results.csv` row:
  - `checker_feasible=true`
  - `timed_out=true`
  - `valid_under_time_limit=false`
  - `accepted_for_score=false`
  - `error_message=runtime exceeded official_limit 1.000000s`
- HTML headline:
  - `Feasible (accepted) 0/1`
  - `Checker PASS 1/1`
  - `Timed Out 1`

Accepted reference smoke:

- Run directory:
  `reports/ogc2026_reboot_v001/smoke_accepted_reference_20260616_153830/`
- `readable_results.csv` row:
  - `checker_feasible=true`
  - `timed_out=false`
  - `valid_under_time_limit=true`
  - `accepted_for_score=true`
- HTML headline:
  - `Feasible (accepted) 1/1`
  - `Checker PASS 1/1`
  - `Timed Out 0`

The controlled timeout command exits with code 1 because no row is accepted
for score. That is expected and confirms the reboot acceptance rule.

## Recovery Validation Addendum 2026-06-19 13:10 KST

The acceptance contract itself is still valid, but the currently wired active
source no longer reproduces the historical acceptance checkpoint that its
metadata advertises.

### Historical vs current-source split

- Historical accepted checkpoint:
  `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`
  - `accepted_for_score=40/40`
  - timeout `0`
  - avg objective `15096298.7`
- Current-source rechecks:
  - `reports/ogc2026_reboot_v001/target_recheck_v096_fourbay_runtime_20260619_001/`
    - `prob_31`: `accepted_for_score=false`, timeout `true`,
      runtime `70.680680s`
  - `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/`
    - `prob_37`: `accepted_for_score=false`, timeout `true`,
      runtime `71.377730s`
  - `reports/ogc2026_reboot_v001/full_recheck_v083_train40_20260619_001/`
    - only `39/40` accepted for score

### Validation consequence

- The historical v096 benchmark remains a valid archived result.
- It is not valid evidence that the current worktree still has a trusted
  `40/40` active BEST.
- Recovery work must therefore publish as a recovery/failure checkpoint, not as
  a trusted-best promotion, until a current-source full revalidation succeeds.
