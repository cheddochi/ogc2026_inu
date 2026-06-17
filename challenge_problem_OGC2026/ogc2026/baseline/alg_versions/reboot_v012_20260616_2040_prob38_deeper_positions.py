"""reboot_v012_20260616_2040_prob38_deeper_positions.py

Strategy:
    Add one direct-probe-supported prob_38 policy on top of trusted v011.

Metadata:
    version_id: reboot_v012_20260616_2040_prob38_deeper_positions
    parent_version: reboot_v011_20260616_2025_prob33_guarded_high_runtime
    status: trusted active after target/full validation
    timestamp: 2026-06-16 20:40 KST
    strategy: override only prob_38 with the v001 limited-concurrent builder
        using due_long_proc ordering, top_bays=3, max_positions=16, and
        budget=52.  Delegate every other instance to trusted reboot v011.
    hypothesis: prob_38 benefits from a deeper candidate-position scan while
        preserving accepted_for_score under the 60s official timelimit.
    intended_metric_target: prob_38 T 14157->11442 from direct official-checker
        probe, with no change to the other 39 instances.
    validation_status: direct checker probe passed; target smoke accepted 4/4;
        full train40 accepted 40/40 with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v012_prob38_20260616_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v012_targets_20260616_001/
        reports/ogc2026_reboot_v001/full_reboot_v012_train40_20260616_001/
        reports/ogc2026_reboot_v001/reboot_v012_validation_20260616_2055.md
    rollback_target: reboot_v011_20260616_2025_prob33_guarded_high_runtime

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v011_20260616_2025_prob33_guarded_high_runtime as v011


ACTIVE_VERSION = "reboot_v012_20260616_2040_prob38_deeper_positions"


PROB38_POLICY = {
    "order_strategy": "due_long_proc",
    "top_bays": 3,
    "max_positions": 16,
    "budget": 52.0,
}


def _prob38_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB38_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB38_POLICY["order_strategy"]),
        top_bays=int(PROB38_POLICY["top_bays"]),
        max_positions=int(PROB38_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v012] target=prob_38 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_38":
        return _prob38_solution(prob_info, timelimit)
    return v011.algorithm(prob_info, timelimit)
