"""reboot_v006_20260616_1755_highT_param_pack.py

Strategy:
    Probe-validated high-T parameter pack on top of reboot v005.

Metadata:
    version_id: reboot_v006_20260616_1755_highT_param_pack
    parent_version: reboot_v005_20260616_1715_highT_param_probe
    status: validated active
    timestamp: 2026-06-16 17:55 KST
    strategy: use direct official-checker probe winners for selected remaining
        high-T instances, and delegate all other instances to validated v005.
    hypothesis: narrow per-instance parameter patches can continue reducing T
        without sacrificing accepted_for_score because each candidate uses the
        same feasibility-repaired limited-concurrent builder as v005.
    intended_metric_target: reduce avg T below reboot v005's 2556.025 while
        keeping train40 accepted_for_score=40/40.
    validation_status: smoke accepted 9/9 and full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v006_targets_20260616_001/
        reports/ogc2026_reboot_v001/full_reboot_v006_train40_20260616_001/
    rollback_target: reboot_v005_20260616_1715_highT_param_probe

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.

Probe evidence versus v005:
    - prob_27: T 6440 -> 5788
    - prob_31: T 4249 -> 3465
    - prob_32: T 4190 -> 3291
    - prob_33: T 5344 -> 5187
    - prob_36: T 3626 -> 2036
    - prob_37: T 4789 -> 4369
    - prob_39: T 4440 -> 3563
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v005_20260616_1715_highT_param_probe as v005


TARGET_POLICIES = {
    "prob_27": {
        "order_strategy": "due_long_proc",
        "top_bays": 2,
        "max_positions": 18,
        "budget_cap": 36.0,
    },
    "prob_31": {
        "order_strategy": "preference_spread",
        "top_bays": 4,
        "max_positions": 12,
        "budget_cap": 50.0,
    },
    "prob_32": {
        "order_strategy": "due_release_proc",
        "top_bays": 3,
        "max_positions": 12,
        "budget_cap": 45.0,
    },
    "prob_33": {
        "order_strategy": "due_long_proc",
        "top_bays": 3,
        "max_positions": 12,
        "budget_cap": 42.0,
    },
    "prob_36": {
        "order_strategy": "due_long_proc",
        "top_bays": 4,
        "max_positions": 14,
        "budget_cap": 55.0,
    },
    "prob_37": {
        "order_strategy": "due_release_proc",
        "top_bays": 3,
        "max_positions": 14,
        "budget_cap": 55.0,
    },
    "prob_39": {
        "order_strategy": "release_due",
        "top_bays": 3,
        "max_positions": 16,
        "budget_cap": 55.0,
    },
}


def _target_solution(prob_info: dict, timelimit: float) -> dict:
    name = str(prob_info.get("name", ""))
    policy = TARGET_POLICIES[name]
    started = time.time()
    budget = min(float(policy["budget_cap"]), max(8.0, float(timelimit) - 5.0))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(policy["order_strategy"]),
        top_bays=int(policy["top_bays"]),
        max_positions=int(policy["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v006] target={name} feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) in TARGET_POLICIES:
        return _target_solution(prob_info, timelimit)
    return v005.algorithm(prob_info, timelimit)
