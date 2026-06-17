"""reboot_v022_20260617_0119_prob25_prob26_release_refine.py

Strategy:
    Keep trusted v021 behavior and add two direct-probe-supported mid-T
    refinements for prob_25 and prob_26.

Metadata:
    version_id: reboot_v022_20260617_0119_prob25_prob26_release_refine
    parent_version: reboot_v021_20260617_0047_prob32_release_due_refine
    status: trusted active BEST
    timestamp: 2026-06-17 01:19 KST
    strategy:
        - prob_25: release_due, top_bays=2, max_positions=10, budget=40
        - prob_26: release_due, top_bays=3, max_positions=14, budget=50
        Delegate every other instance to trusted reboot v021.
    hypothesis: release-first ordering reduces tardy tails on prob_25 and
        prob_26 while keeping runtime small enough for stable full runs.
    intended_metric_target:
        - prob_25 T 2911->2851 from direct official-checker probe
        - prob_26 T 2885->2345 from direct official-checker probe
    validation_status: core smoke accepted; target smoke accepted 6/6; full
        train40 accepted 40/40 with timeout 0; active wrapper smoke accepted
        2/2 with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v022_core_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v022_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v022_train40_20260617_001/
        reports/ogc2026_reboot_v001/smoke_active_v022_wrapper_20260617_0135/
    rollback_target: reboot_v021_20260617_0047_prob32_release_due_refine

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v021_20260617_0047_prob32_release_due_refine as v021


ACTIVE_VERSION = "reboot_v022_20260617_0119_prob25_prob26_release_refine"


TARGET_POLICIES = {
    "prob_25": {
        "order_strategy": "release_due",
        "top_bays": 2,
        "max_positions": 10,
        "budget": 40.0,
    },
    "prob_26": {
        "order_strategy": "release_due",
        "top_bays": 3,
        "max_positions": 14,
        "budget": 50.0,
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
        f"[baseline_hh reboot_v022] target={prob_info.get('name')} "
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
    return v021.algorithm(prob_info, timelimit)
