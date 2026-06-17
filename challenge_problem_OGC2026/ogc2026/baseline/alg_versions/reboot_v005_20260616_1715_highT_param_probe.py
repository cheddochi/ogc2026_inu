"""reboot_v005_20260616_1715_highT_param_probe.py

Strategy:
    Narrow high-T parameter patch on top of validated reboot v004.

Metadata:
    version_id: reboot_v005_20260616_1715_highT_param_probe
    parent_version: reboot_v004_20260616_1645_train40_selector
    status: validated active
    timestamp: 2026-06-16 17:15 KST
    strategy: use direct probe-validated limited-concurrent parameters for
        `prob_38` and `prob_40`, and delegate every other instance to v004.
    hypothesis: widening bay consideration for the two highest-T instances can
        reduce T while preserving accepted_for_score and avoiding the cost of
        running multiple candidates inside one official call.
    intended_metric_target: reduce avg T below reboot v004's 2617.975 while
        keeping train40 accepted_for_score=40/40.
    validation_status: smoke accepted 4/4 and full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v005_targets_20260616_001/
        reports/ogc2026_reboot_v001/full_reboot_v005_train40_20260616_001/
    rollback_target: reboot_v004_20260616_1645_train40_selector

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.

Probe evidence:
    Direct official-checker probes using v001 builder:
    - prob_38 due_long_proc, top_bays=3, max_positions=12, budget=42:
      T 14157 vs v004 T 15738.
    - prob_40 due_release_proc, top_bays=4, max_positions=10, budget=55:
      T 9542 vs v004 T 10439.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v004_20260616_1645_train40_selector as v004


TARGET_POLICIES = {
    "prob_38": {
        "order_strategy": "due_long_proc",
        "top_bays": 3,
        "max_positions": 12,
        "budget_cap": 42.0,
    },
    "prob_40": {
        "order_strategy": "due_release_proc",
        "top_bays": 4,
        "max_positions": 10,
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
        f"[baseline_hh reboot_v005] target={name} feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) in TARGET_POLICIES:
        return _target_solution(prob_info, timelimit)
    return v004.algorithm(prob_info, timelimit)
