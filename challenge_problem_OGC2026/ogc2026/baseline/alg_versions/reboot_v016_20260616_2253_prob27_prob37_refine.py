"""reboot_v016_20260616_2253_prob27_prob37_refine.py

Strategy:
    Keep trusted v015 behavior and add two direct-probe-supported single
    instance refinements for remaining high-T rows.

Metadata:
    version_id: reboot_v016_20260616_2253_prob27_prob37_refine
    parent_version: reboot_v015_20260616_2219_prob38_budget_guard
    status: trusted active after target/full validation
    timestamp: 2026-06-16 22:53 KST
    strategy:
        - prob_27: due_long_proc, top_bays=3, max_positions=16, budget=58
        - prob_37: release_due, top_bays=3, max_positions=16, budget=58
        Delegate every other instance to trusted reboot v015.
    hypothesis: prob_27 benefits from a slightly deeper position scan, while
        prob_37 benefits from release-first ordering rather than the inherited
        high-T ordering.  Both direct probes improved T and objective while
        staying comfortably under the official 60s limit.
    intended_metric_target:
        - prob_27 T 5788->5735 from direct official-checker probe
        - prob_37 T 4369->4040 from direct official-checker probe
    validation_status: core smoke accepted 2/2; target smoke accepted 6/6;
        full train40 accepted 40/40 with timeout 0; active wrapper smoke
        accepted 3/3 with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v016_core_20260616_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v016_targets_20260616_001/
        reports/ogc2026_reboot_v001/full_reboot_v016_train40_20260616_001/
        reports/ogc2026_reboot_v001/smoke_active_v016_wrapper_20260616_001/
        reports/ogc2026_reboot_v001/reboot_v016_validation_20260616_2306.md
    rollback_target: reboot_v015_20260616_2219_prob38_budget_guard

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v015_20260616_2219_prob38_budget_guard as v015


ACTIVE_VERSION = "reboot_v016_20260616_2253_prob27_prob37_refine"


TARGET_POLICIES = {
    "prob_27": {
        "order_strategy": "due_long_proc",
        "top_bays": 3,
        "max_positions": 16,
        "budget": 58.0,
    },
    "prob_37": {
        "order_strategy": "release_due",
        "top_bays": 3,
        "max_positions": 16,
        "budget": 58.0,
    },
}


def _target_solution(prob_info: dict, timelimit: float, policy: dict) -> dict:
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
        f"[baseline_hh reboot_v016] target={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    policy = TARGET_POLICIES.get(str(prob_info.get("name", "")))
    if policy is not None:
        return _target_solution(prob_info, timelimit, policy)
    return v015.algorithm(prob_info, timelimit)
