"""reboot_v018_20260616_2333_prob40_conservative_deeper_positions.py

Strategy:
    Keep trusted v016 behavior and add a conservative prob_40 position-scan
    refinement.  This is intentionally narrower than rejected v017.

Metadata:
    version_id: reboot_v018_20260616_2333_prob40_conservative_deeper_positions
    parent_version: reboot_v016_20260616_2253_prob27_prob37_refine
    status: rejected after single-row smoke
    timestamp: 2026-06-16 23:33 KST
    strategy:
        - prob_40: due_release_proc, top_bays=4, max_positions=12,
          max_orients=4, budget=58
        Delegate every other instance to trusted reboot v016.
    hypothesis: v017's max_positions=14 probe can be excellent when it
        completes, but it is timing-sensitive and regressed badly in target
        smoke.  max_positions=12 gives a smaller T gain with more runtime
        headroom.
    intended_metric_target:
        - prob_40 T 9542->9446 from direct official-checker probe
    validation_status: single-row smoke regressed prob_40; target/full skipped.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v018_prob40_20260616_001/
        reports/ogc2026_reboot_v001/reboot_v017_v018_rejection_20260616_2336.md
    rollback_target: reboot_v016_20260616_2253_prob27_prob37_refine

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v016_20260616_2253_prob27_prob37_refine as v016


ACTIVE_VERSION = "reboot_v018_20260616_2333_prob40_conservative_deeper_positions"


PROB40_POLICY = {
    "order_strategy": "due_release_proc",
    "top_bays": 4,
    "max_positions": 12,
    "max_orients": 4,
    "budget": 58.0,
}


def _prob40_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB40_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB40_POLICY["order_strategy"]),
        top_bays=int(PROB40_POLICY["top_bays"]),
        max_positions=int(PROB40_POLICY["max_positions"]),
        max_orients=int(PROB40_POLICY["max_orients"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v018] target=prob_40 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_40":
        return _prob40_solution(prob_info, timelimit)
    return v016.algorithm(prob_info, timelimit)
