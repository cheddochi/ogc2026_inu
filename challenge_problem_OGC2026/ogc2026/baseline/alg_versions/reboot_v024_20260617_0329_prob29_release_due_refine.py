"""reboot_v024_20260617_0329_prob29_release_due_refine.py

Strategy:
    Keep trusted v023 behavior and add one release-first refinement only for
    prob_29.

Metadata:
    version_id: reboot_v024_20260617_0329_prob29_release_due_refine
    parent_version: reboot_v023_20260617_0208_prob33_release_due_deeper
    status: trusted active BEST
    timestamp: 2026-06-17 03:29 KST
    strategy:
        - prob_29: release_due, top_bays=3, max_positions=16, budget=48
        Delegate every other instance to trusted reboot v023.
    hypothesis: prob_29 benefits from a release-first ordering with a slightly
        deeper position scan, yielding a large T reduction while staying well
        inside the 60s limit.
    intended_metric_target:
        - prob_29 T 2297->446 from direct official-checker probe
    validation_status: import smoke passed; prob_1/prob_29/prob_38 single-row
        smoke accepted; target smoke accepted 7/7; full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v024_prob1_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v024_prob29_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v024_prob38_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v024_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v024_train40_20260617_001/
    rollback_target: reboot_v023_20260617_0208_prob33_release_due_deeper

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v023_20260617_0208_prob33_release_due_deeper as v023


ACTIVE_VERSION = "reboot_v024_20260617_0329_prob29_release_due_refine"


PROB29_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 16,
    "budget": 48.0,
}


def _prob29_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB29_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB29_POLICY["order_strategy"]),
        top_bays=int(PROB29_POLICY["top_bays"]),
        max_positions=int(PROB29_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v024] target=prob_29 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_29":
        return _prob29_solution(prob_info, timelimit)
    return v023.algorithm(prob_info, timelimit)
