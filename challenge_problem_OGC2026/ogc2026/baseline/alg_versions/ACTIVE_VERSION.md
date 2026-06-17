# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v039_20260617_1304_runtime_sensitive_budget_guard`
- Status: trusted active BEST
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v039_20260617_1304_runtime_sensitive_budget_guard.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Trusted evidence:
  - smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v039_core8_20260617_001/`
    `reports/ogc2026_reboot_v001/smoke_reboot_v039_targets_20260617_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v039_train40_20260617_001/`
  - previous trusted smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v035_prob1_20260617_001/`
    `reports/ogc2026_reboot_v001/smoke_reboot_v035_prob14_20260617_001/`
    `reports/ogc2026_reboot_v001/smoke_reboot_v035_prob38_20260617_001/`
    `reports/ogc2026_reboot_v001/smoke_reboot_v035_targets_20260617_001/`
  - previous trusted smoke:
    `reports/ogc2026_reboot_v001/full_reboot_v034_train40_20260617_001/`
    `reports/ogc2026_reboot_v001/revalidate_reboot_v035_train40_20260617_001/`
- Current trusted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `53.781209s`
  - avg T/obj1 `1758.925`
  - avg L/obj2 `3297.0`
  - avg P/obj3 `4501.425`
  - avg objective `18572924.425`
- Improvement versus prior trusted v035 revalidation:
  - avg T/obj1 `1763.875 -> 1758.925`
  - avg L/obj2 `3297.45 -> 3297.0`
  - avg P/obj3 `4502.6 -> 4501.425`
  - avg objective `18639274.15 -> 18572924.425`
  - improved `prob_29`: T `569 -> 446`
  - improved `prob_31`: T `2911 -> 2836`
  - no timeout rows
  - no infeasible or unaccepted rows
  - no T regressions.
- Rollback target:
  `reboot_v035_20260617_0912_prob14_preference_spread`
- Canonical note:
  - noncanonical `v014` artifacts remain ignored for score claims because
    their full train40 run is incomplete.
  - `reboot_v019_20260616_2349_prob37_deeper_objective` is rejected under the
    T-first rule: full train40 accepted 40/40 but avg T regressed
    `2031.1 -> 2031.4`.
  - `reboot_v020_20260617_0009_prob31_release_due_refine` is superseded by
    this preference-spread v020; it also improved T, but only to avg
    `2025.275`.
  - `reboot_v021_20260617_0047_prob32_release_due_refine` remains valid
    rollback evidence; v022 adds `prob_25` and `prob_26` improvements on top.
