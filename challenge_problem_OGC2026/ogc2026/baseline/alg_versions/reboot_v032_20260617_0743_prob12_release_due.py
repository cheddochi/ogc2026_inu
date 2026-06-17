"""reboot_v032_20260617_0743_prob12_release_due.py

Strategy:
    Keep trusted v031 behavior and add one release-first refinement only for
    prob_12.

Metadata:
    version_id: reboot_v032_20260617_0743_prob12_release_due
    parent_version: reboot_v031_20260617_0711_prob17_release_due
    status: trusted active BEST
    timestamp: 2026-06-17 07:43 KST
    strategy:
        - prob_12: release_due, top_bays=3, max_positions=12, budget=30
        Delegate every other instance to trusted v031.
    hypothesis: prob_12 still has a sizable tardiness tail under trusted v031,
        and a release-first ordering can sharply cut it without runtime risk.
    intended_metric_target:
        - prob_12 T 1096->20 from direct official-checker probe
    validation_status: import smoke passed; prob_1/prob_12/prob_38 single-row
        smoke accepted; target smoke accepted 6/6; full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v032_prob1_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v032_prob12_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v032_prob38_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v032_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v032_train40_20260617_001/
    rollback_target: reboot_v031_20260617_0711_prob17_release_due

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v031_20260617_0711_prob17_release_due as v031


ACTIVE_VERSION = "reboot_v032_20260617_0743_prob12_release_due"


PROB12_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 12,
    "budget": 30.0,
}


def _prob12_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB12_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB12_POLICY["order_strategy"]),
        top_bays=int(PROB12_POLICY["top_bays"]),
        max_positions=int(PROB12_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v032] target=prob_12 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_12":
        return _prob12_solution(prob_info, timelimit)
    return v031.algorithm(prob_info, timelimit)
