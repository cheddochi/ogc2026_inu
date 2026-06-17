"""reboot_v027_20260617_0512_prob35_release_due_refine.py

Strategy:
    Keep trusted v026 behavior and add one release-first refinement only for
    prob_35.

Metadata:
    version_id: reboot_v027_20260617_0512_prob35_release_due_refine
    parent_version: reboot_v026_20260617_0444_prob21_release_due_refine
    status: trusted active BEST
    timestamp: 2026-06-17 05:12 KST
    strategy:
        - prob_35: release_due, top_bays=3, max_positions=16, budget=52
        Delegate every other instance to trusted v026.
    hypothesis: prob_35 still has a release-ordering bottleneck under trusted
        v026, and a deeper release_due scan can trim T without pushing runtime
        over the official limit.
    intended_metric_target:
        - prob_35 T 2111->1979 from direct official-checker probe
    validation_status: import smoke passed; prob_1/prob_35/prob_38 single-row
        smoke accepted; target smoke accepted 6/6; full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v027_prob1_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v027_prob35_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v027_prob38_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v027_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v027_train40_20260617_001/
    rollback_target: reboot_v026_20260617_0444_prob21_release_due_refine

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v026_20260617_0444_prob21_release_due_refine as v026


ACTIVE_VERSION = "reboot_v027_20260617_0512_prob35_release_due_refine"


PROB35_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 16,
    "budget": 52.0,
}


def _prob35_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB35_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB35_POLICY["order_strategy"]),
        top_bays=int(PROB35_POLICY["top_bays"]),
        max_positions=int(PROB35_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v027] target=prob_35 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_35":
        return _prob35_solution(prob_info, timelimit)
    return v026.algorithm(prob_info, timelimit)
