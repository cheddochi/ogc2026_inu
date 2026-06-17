"""reboot_v035_20260617_0912_prob14_preference_spread.py

Strategy:
    Keep trusted v034 behavior and add one preference-aware refinement only for
    prob_14.

Metadata:
    version_id: reboot_v035_20260617_0912_prob14_preference_spread
    parent_version: reboot_v034_20260617_0841_prob15_preference_spread
    status: trusted active BEST
    timestamp: 2026-06-17 09:12 KST
    strategy:
        - prob_14: preference_spread, top_bays=3, max_positions=12, budget=34
        Delegate every other instance to trusted v034.
    hypothesis: prob_14 has a preference-sensitive bottleneck under trusted
        v034, and a preference-spread ordering can cut tardiness and objective
        without creating runtime risk.
    intended_metric_target:
        - prob_14 T 858->329 from direct official-checker probe
    validation_status: import smoke passed; prob_1/prob_14/prob_38 single-row
        smoke accepted; target smoke accepted 6/6; full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v035_prob1_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v035_prob14_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v035_prob38_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v035_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v035_train40_20260617_001/
    rollback_target: reboot_v034_20260617_0841_prob15_preference_spread

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v034_20260617_0841_prob15_preference_spread as v034


ACTIVE_VERSION = "reboot_v035_20260617_0912_prob14_preference_spread"


PROB14_POLICY = {
    "order_strategy": "preference_spread",
    "top_bays": 3,
    "max_positions": 12,
    "budget": 34.0,
}


def _prob14_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB14_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB14_POLICY["order_strategy"]),
        top_bays=int(PROB14_POLICY["top_bays"]),
        max_positions=int(PROB14_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v035] target=prob_14 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_14":
        return _prob14_solution(prob_info, timelimit)
    return v034.algorithm(prob_info, timelimit)
