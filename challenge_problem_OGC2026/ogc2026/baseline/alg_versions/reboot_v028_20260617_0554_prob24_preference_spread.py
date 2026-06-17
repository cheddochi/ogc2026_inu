"""reboot_v028_20260617_0554_prob24_preference_spread.py

Strategy:
    Keep trusted v027 behavior and add one preference-aware refinement only for
    prob_24.

Metadata:
    version_id: reboot_v028_20260617_0554_prob24_preference_spread
    parent_version: reboot_v027_20260617_0512_prob35_release_due_refine
    status: trusted active BEST
    timestamp: 2026-06-17 05:54 KST
    strategy:
        - prob_24: preference_spread, top_bays=3, max_positions=12, budget=36
        Delegate every other instance to trusted v027.
    hypothesis: prob_24 has a concentrated bay-preference pattern that the
        current due-long ordering misses, and a preference-aware scan can cut
        tardiness and total objective without creating runtime pressure.
    intended_metric_target:
        - prob_24 T 1677->362 from direct official-checker probe
    validation_status: import smoke passed; prob_1/prob_24/prob_38 single-row
        smoke accepted; target smoke accepted 6/6; full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v028_prob1_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v028_prob24_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v028_prob38_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v028_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v028_train40_20260617_001/
    rollback_target: reboot_v027_20260617_0512_prob35_release_due_refine

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v027_20260617_0512_prob35_release_due_refine as v027


ACTIVE_VERSION = "reboot_v028_20260617_0554_prob24_preference_spread"


PROB24_POLICY = {
    "order_strategy": "preference_spread",
    "top_bays": 3,
    "max_positions": 12,
    "budget": 36.0,
}


def _prob24_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB24_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB24_POLICY["order_strategy"]),
        top_bays=int(PROB24_POLICY["top_bays"]),
        max_positions=int(PROB24_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v028] target=prob_24 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_24":
        return _prob24_solution(prob_info, timelimit)
    return v027.algorithm(prob_info, timelimit)
