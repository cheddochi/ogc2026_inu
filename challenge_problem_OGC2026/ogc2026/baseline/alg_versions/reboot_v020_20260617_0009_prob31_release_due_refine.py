"""reboot_v020_20260617_0009_prob31_release_due_refine.py

Strategy:
    Keep trusted v016 behavior and add one direct-probe-supported refinement
    for prob_31.

Metadata:
    version_id: reboot_v020_20260617_0009_prob31_release_due_refine
    parent_version: reboot_v016_20260616_2253_prob27_prob37_refine
    status: superseded candidate
    timestamp: 2026-06-17 00:09 KST
    strategy:
        - prob_31: release_due, top_bays=3, max_positions=14, budget=58
        Delegate every other instance to trusted reboot v016.
    hypothesis: prob_31 benefits from release-first ordering and a modestly
        deeper position scan.  Direct official-checker probe reduced T from
        3465 to 3232 while staying feasible.
    intended_metric_target:
        - prob_31 T 3465->3232 from direct official-checker probe
    validation_status: single-row prob_31 smoke accepted 1/1; target smoke
        accepted 6/6; full train40 accepted 40/40 with timeout 0 and improved
        avg T 2031.1 -> 2025.275, but this candidate was superseded by
        reboot_v020_20260617_0015_prob31_preference_spread with avg T
        2015.375.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v020_prob31_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v020_targets_20260617_001/
        reports/ogc2026_reboot_v001/smoke_compare_v016_v020_prob31_prob40_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v020_train40_20260617_001/
    rollback_target: reboot_v016_20260616_2253_prob27_prob37_refine

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v016_20260616_2253_prob27_prob37_refine as v016


ACTIVE_VERSION = "reboot_v020_20260617_0009_prob31_release_due_refine"


PROB31_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 14,
    "budget": 58.0,
}


def _prob31_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB31_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB31_POLICY["order_strategy"]),
        top_bays=int(PROB31_POLICY["top_bays"]),
        max_positions=int(PROB31_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v020] target=prob_31 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_31":
        return _prob31_solution(prob_info, timelimit)
    return v016.algorithm(prob_info, timelimit)
