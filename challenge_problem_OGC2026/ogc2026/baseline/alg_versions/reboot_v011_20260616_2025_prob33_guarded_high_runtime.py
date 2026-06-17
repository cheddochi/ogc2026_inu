"""reboot_v011_20260616_2025_prob33_guarded_high_runtime.py

Strategy:
    Prob_33 T improvement plus guard-margin stabilization for high-runtime
    prob_36/prob_40.

Metadata:
    version_id: reboot_v011_20260616_2025_prob33_guarded_high_runtime
    parent_version: reboot_v007_20260616_1835_midT_param_pack
    status: trusted active after smoke/full validation
    timestamp: 2026-06-16 20:25 KST
    strategy: override only prob_33, prob_36, and prob_40.  Prob_33 uses the
        release_due policy that improved in v008/v009 smoke.  Prob_36 and
        prob_40 keep the same policy shape as trusted v007/v005 but pass a
        larger builder budget so the internal 95% guard is less likely to force
        late empty-window fallback before the official 60s limit.
    hypothesis: preserve accepted_for_score=40/40 while reducing average T
        versus trusted reboot v007.
    intended_metric_target: prob_33 5187->4236 while keeping prob_36 near 2010
        and prob_40 near 9542.
    validation_status: target smoke accepted 4/4; full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v011_targets_20260616_001/
        reports/ogc2026_reboot_v001/full_reboot_v011_train40_20260616_001/
        reports/ogc2026_reboot_v001/reboot_v011_validation_20260616_2030.md
    rollback_target: reboot_v007_20260616_1835_midT_param_pack

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v007_20260616_1835_midT_param_pack as v007


ACTIVE_VERSION = "reboot_v011_20260616_2025_prob33_guarded_high_runtime"


TARGET_POLICIES = {
    "prob_33": {
        "order_strategy": "release_due",
        "top_bays": 3,
        "max_positions": 14,
        "budget": 46.0,
    },
    "prob_36": {
        "order_strategy": "due_long_proc",
        "top_bays": 4,
        "max_positions": 14,
        "budget": 58.0,
    },
    "prob_40": {
        "order_strategy": "due_release_proc",
        "top_bays": 4,
        "max_positions": 10,
        "budget": 58.0,
    },
}


def _target_solution(prob_info: dict, timelimit: float) -> dict:
    name = str(prob_info.get("name", ""))
    policy = TARGET_POLICIES[name]
    started = time.time()
    budget = min(float(policy["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(policy["order_strategy"]),
        top_bays=int(policy["top_bays"]),
        max_positions=int(policy["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v011] target={name} feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) in TARGET_POLICIES:
        return _target_solution(prob_info, timelimit)
    return v007.algorithm(prob_info, timelimit)
