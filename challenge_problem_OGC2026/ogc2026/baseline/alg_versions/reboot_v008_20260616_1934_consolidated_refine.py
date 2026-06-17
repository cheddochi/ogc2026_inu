"""reboot_v008_20260616_1934_consolidated_refine.py

Strategy:
    Targeted refinement on top of validated reboot v007.

Metadata:
    version_id: reboot_v008_20260616_1934_consolidated_refine
    parent_version: reboot_v007_20260616_1835_midT_param_pack
    status: rejected after target smoke
    timestamp: 2026-06-16 19:34 KST
    strategy: override only four runtime/T-sensitive instances and delegate all
        other instances to validated reboot v007.
    hypothesis: direct probes found lower-T policies for prob_31, prob_33, and
        prob_37.  prob_40 is moved to a slightly lower-T-than-v004 but faster
        top_bays=3 policy because the v007/v005 top_bays=4 policy is close to
        the 60s boundary and can degrade sharply when the builder starts
        forced fallback late in the run.
    intended_metric_target: keep accepted_for_score=40/40 while improving
        average T versus reboot v007 under current machine/runtime conditions.
    validation_status: rejected; target smoke accepted 4/4 but regressed T on
        prob_31, prob_37, and prob_40 versus trusted reboot v007.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v008_targets_20260616_001/
    rollback_target: reboot_v007_20260616_1835_midT_param_pack

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.

Probe evidence versus reboot v007/full evidence:
    - prob_31: T 3465 -> 2836 with preference_spread, top_bays=4,
      max_positions=14, budget=55.
    - prob_33: T 5187 -> 4236 with release_due, top_bays=3,
      max_positions=14, budget=46.
    - prob_37: T 4369 -> 4040 with release_due, top_bays=3,
      max_positions=16, budget=55.
    - prob_40: validated v007-best T 9542 is kept as historical best, but a
      current consolidated smoke produced T 21470 when the top_bays=4 policy
      crossed the builder guard.  A current direct probe of top_bays=3,
      max_positions=10, budget=55 produced accepted T 10439 in 45.9s.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v007_20260616_1835_midT_param_pack as v007


ACTIVE_VERSION = "reboot_v008_20260616_1934_consolidated_refine"


TARGET_POLICIES = {
    "prob_31": {
        "order_strategy": "preference_spread",
        "top_bays": 4,
        "max_positions": 14,
        "budget_cap": 55.0,
    },
    "prob_33": {
        "order_strategy": "release_due",
        "top_bays": 3,
        "max_positions": 14,
        "budget_cap": 46.0,
    },
    "prob_37": {
        "order_strategy": "release_due",
        "top_bays": 3,
        "max_positions": 16,
        "budget_cap": 55.0,
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
        f"[baseline_hh reboot_v008] target={name} feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) in TARGET_POLICIES:
        return _target_solution(prob_info, timelimit)
    return v007.algorithm(prob_info, timelimit)
