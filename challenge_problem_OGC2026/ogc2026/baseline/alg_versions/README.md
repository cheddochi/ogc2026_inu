# OGC2026 Algorithm Versions

This folder keeps versioned algorithm snapshots used by benchmark runs.

- `myalgorithm_v000_original.py`: exact backup of the original active entrypoint before the `hh` activation work.
- `baseline_hh_v000_original.py`: documented reference wrapper for the official greedy baseline because no pre-existing `baseline_hh.py` file was present in this clone.
- `baseline_hh_v001_portfolio.py`: feasibility-first portfolio entry used by `baseline_hh.py`.
- `baseline_hh_v002_safe_serial.py`: deadline-safe serial scheduler with objective-aware bay selection.
- `baseline_hh_v003_hybrid_serial.py`: validates official serial and v002 serial, then returns the better feasible objective.
- `baseline_hh_v004_guarded_greedy.py`: inactive experiment; tried guarded repaired greedy on small/medium instances but smoke timed out on `prob_7`.
- `baseline_hh_v005_serial_portfolio.py`: active experiment; tries multiple safe serial order/selection variants and validates the best candidates.
- `baseline_hh_v006_hard_timeout_greedy.py`: active experiment; keeps v005 fallback and hard-timeout repaired greedy for evidence-backed low-T instances.
- `baseline_hh_v007_limited_concurrent.py`: active experiment; keeps v006 fallback and adds checker-validated limited concurrent candidates, empty-window repair, evidence-backed instance-specific ordering, and targeted per-instance search-width/bay-count parameters for high-T instances.

The public submission interface remains:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```
