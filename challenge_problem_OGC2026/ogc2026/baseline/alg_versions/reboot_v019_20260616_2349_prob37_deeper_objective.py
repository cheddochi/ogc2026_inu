"""reboot_v019_20260616_2349_prob37_deeper_objective.py

Strategy:
    Keep trusted v016 behavior and try one deeper, still-bounded scan only on
    prob_37.

Metadata:
    version_id: reboot_v019_20260616_2349_prob37_deeper_objective
    parent_version: reboot_v016_20260616_2253_prob27_prob37_refine
    status: rejected after full train40 under T-first rule
    timestamp: 2026-06-16 23:49 KST
    strategy:
        - prob_37: release_due, top_bays=3, max_positions=18, budget=58
        Delegate every other instance to trusted reboot v016.
    hypothesis: prob_37's v016 release_due ordering looks stable; a slightly
        deeper position scan may improve checker objective with only a very
        small T tradeoff while staying within the 60s limit.
    intended_metric_target:
        - prob_37 objective 18033244->18007304 from direct checker probe
    validation_status: import smoke passed; prob_1/prob_37/prob_38 single-row
        smoke accepted; target smoke accepted 5/5; full train40 accepted 40/40
        with timeout 0, but avg T regressed 2031.1 -> 2031.4 and prob_37 T
        regressed 4040 -> 4052. Kept as rejected candidate evidence only.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v019_prob1_20260616_002/
        reports/ogc2026_reboot_v001/smoke_reboot_v019_prob37_20260616_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v019_prob38_20260616_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v019_targets_20260616_001/
        reports/ogc2026_reboot_v001/full_reboot_v019_train40_20260616_001/
    rollback_target: reboot_v016_20260616_2253_prob27_prob37_refine

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v016_20260616_2253_prob27_prob37_refine as v016


ACTIVE_VERSION = "reboot_v019_20260616_2349_prob37_deeper_objective"


PROB37_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 18,
    "budget": 58.0,
}


def _prob37_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB37_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB37_POLICY["order_strategy"]),
        top_bays=int(PROB37_POLICY["top_bays"]),
        max_positions=int(PROB37_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v019] target=prob_37 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_37":
        return _prob37_solution(prob_info, timelimit)
    return v016.algorithm(prob_info, timelimit)
