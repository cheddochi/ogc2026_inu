"""reboot_v013_20260616_2130_prob20_wider_bay_scan.py

Strategy:
    Add one direct-probe-supported prob_20 policy on top of trusted v012.

Metadata:
    version_id: reboot_v013_20260616_2130_prob20_wider_bay_scan
    parent_version: reboot_v012_20260616_2040_prob38_deeper_positions
    status: trusted active
    timestamp: 2026-06-16 21:30 KST
    strategy: override only prob_20 with the v001 limited-concurrent builder
        using due_release_proc ordering, top_bays=4, max_positions=12, and
        budget=48.  Delegate every other instance to trusted reboot v012.
    hypothesis: prob_20 was still using a narrow default search; widening bay
        and position consideration substantially reduces T while staying inside
        the 60s official timelimit.
    intended_metric_target: prob_20 T 3478->660 from official runner smoke,
        with no change to the other 39 instances.
    validation_status: single-row smoke accepted 1/1, gate smoke accepted 4/4,
        and full train40 accepted 40/40 with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v013_prob20_20260616_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v013_prob20_targets_20260616_001/
        reports/ogc2026_reboot_v001/full_reboot_v013_prob20_train40_20260616_001/
    rollback_target: reboot_v012_20260616_2040_prob38_deeper_positions

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v012_20260616_2040_prob38_deeper_positions as v012


ACTIVE_VERSION = "reboot_v013_20260616_2130_prob20_wider_bay_scan"


PROB20_POLICY = {
    "order_strategy": "due_release_proc",
    "top_bays": 4,
    "max_positions": 12,
    "budget": 48.0,
}


def _prob20_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB20_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB20_POLICY["order_strategy"]),
        top_bays=int(PROB20_POLICY["top_bays"]),
        max_positions=int(PROB20_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v013] target=prob_20 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_20":
        return _prob20_solution(prob_info, timelimit)
    return v012.algorithm(prob_info, timelimit)
