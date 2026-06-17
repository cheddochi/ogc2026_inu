# Contaminated Legacy Algorithm Artifacts

Generated: 2026-06-16

## Policy

This directory contains pre-reboot HH experiments. They are not deleted because
they remain useful for forensic review and implementation ideas, but their
historical benchmark results are not trusted for score claims.

Trusted comparisons must start again from `reboot_v001` after the benchmark
runner separates:

- `checker_feasible`
- `timed_out`
- `valid_under_time_limit`
- `accepted_for_score`

## Reference Only

- `baseline_hh_v000_original.py`
- `myalgorithm_v000_original.py`

These are reference snapshots, not current best claims.

## Contaminated Prior-Loop Candidates

- `baseline_hh_v001_portfolio.py`
- `baseline_hh_v002_safe_serial.py`
- `baseline_hh_v003_hybrid_serial.py`
- `baseline_hh_v004_guarded_greedy.py`
- `baseline_hh_v005_serial_portfolio.py`
- `baseline_hh_v006_hard_timeout_greedy.py`
- `baseline_hh_v007_limited_concurrent.py`

Reasons:

- They were created or benchmarked before the reboot scoring contract.
- Prior reports may count checker-passing rows as feasible even when runtime
  exceeds the requested official limit.
- At the original contamination snapshot, `baseline_hh.py` imported the v007
  file.  The active HH entrypoint has since moved to a reboot version, while
  the historical v007 file and its prior benchmark claims remain contaminated.
- Any previous `best`, `latest`, or `40/40 feasible` claim tied to these files
  must be ignored unless reproduced with `accepted_for_score=true`.

## Required New Version Naming

New trusted work starts at reboot version ids such as:

- `reboot_v001_YYYYMMDD_HHMM_trusted_baseline`
- `reboot_v002_YYYYMMDD_HHMM_candidate_slack_ordering`
- `reboot_v003_YYYYMMDD_HHMM_rejected_timeout`
- `reboot_v004_YYYYMMDD_HHMM_accepted_instance_selector`

Every reboot version must include metadata:

- `version_id`
- `parent_version`
- `status`
- `timestamp`
- `strategy`
- `hypothesis`
- `intended_metric_target`
- `validation_status`
- `benchmark_evidence_path`
- `rollback_target`
