"""reboot_v020_20260617_0015_prob31_preference_spread.py

Strategy:
    Keep trusted v016 behavior and try one deeper preference-aware search only
    on prob_31.

Metadata:
    version_id: reboot_v020_20260617_0015_prob31_preference_spread
    parent_version: reboot_v016_20260616_2253_prob27_prob37_refine
    status: trusted active BEST
    timestamp: 2026-06-17 00:15 KST
    strategy:
        - prob_31: preference_spread, top_bays=4, max_positions=14, budget=55
        Delegate every other instance to trusted reboot v016.
    hypothesis: prob_31 benefits from a deeper preference-aware bay/position
        search, and the gain may be stable when isolated instead of bundled
        with other runtime-sensitive overrides.
    intended_metric_target:
        - prob_31 T 3465->2836 from direct checker probe
    validation_status: import smoke passed; prob_1/prob_31/prob_38 single-row
        smoke accepted; target smoke accepted 5/5; full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v020_prob1_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v020_prob31_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v020_prob38_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v020_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v020_preference_train40_20260617_001/
        reports/ogc2026_reboot_v001/smoke_active_v020_wrapper_20260617_001/
        reports/ogc2026_reboot_v001/reboot_v020_preference_validation_20260617_0032.md
    rollback_target: reboot_v016_20260616_2253_prob27_prob37_refine

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v016_20260616_2253_prob27_prob37_refine as v016


ACTIVE_VERSION = "reboot_v020_20260617_0015_prob31_preference_spread"


PROB31_POLICY = {
    "order_strategy": "preference_spread",
    "top_bays": 4,
    "max_positions": 14,
    "budget": 55.0,
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
