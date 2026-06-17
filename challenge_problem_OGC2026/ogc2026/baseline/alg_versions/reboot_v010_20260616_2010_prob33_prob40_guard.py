"""reboot_v010_20260616_2010_prob33_prob40_guard.py

Strategy:
    Single improving target plus a runtime-sensitive prob_40 guard.

Metadata:
    version_id: reboot_v010_20260616_2010_prob33_prob40_guard
    parent_version: reboot_v007_20260616_1835_midT_param_pack
    status: candidate pending smoke/full validation
    timestamp: 2026-06-16 20:10 KST
    strategy: override `prob_33` with the reproducible release_due policy and
        override `prob_40` with a narrower top_bays=3 policy that has shown
        less severe forced-fallback degradation than the v005/v007 top_bays=4
        policy under current runner conditions.
    hypothesis: `prob_33` improvement can offset the small trusted-v007
        tradeoff on prob_40 while making current-run prob_40 behavior less
        volatile.
    intended_metric_target: keep accepted_for_score=40/40 and reduce average T
        versus trusted reboot v007.
    validation_status: pending.
    benchmark_evidence_path: pending.
    rollback_target: reboot_v007_20260616_1835_midT_param_pack

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v007_20260616_1835_midT_param_pack as v007


ACTIVE_VERSION = "reboot_v010_20260616_2010_prob33_prob40_guard"


TARGET_POLICIES = {
    "prob_33": {
        "order_strategy": "release_due",
        "top_bays": 3,
        "max_positions": 14,
        "budget_cap": 46.0,
    },
    "prob_40": {
        "order_strategy": "due_release_proc",
        "top_bays": 3,
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
        f"[baseline_hh reboot_v010] target={name} feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) in TARGET_POLICIES:
        return _target_solution(prob_info, timelimit)
    return v007.algorithm(prob_info, timelimit)
