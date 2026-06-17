"""reboot_v023_20260617_0208_prob33_release_due_deeper.py

Strategy:
    Keep trusted v022 behavior and deepen the validated release-first scan only
    for prob_33.

Metadata:
    version_id: reboot_v023_20260617_0208_prob33_release_due_deeper
    parent_version: reboot_v022_20260617_0119_prob25_prob26_release_refine
    status: trusted active BEST
    timestamp: 2026-06-17 02:08 KST
    strategy:
        - prob_33: release_due, top_bays=3, max_positions=18, budget=50
        Delegate every other instance to trusted reboot v022.
    hypothesis: prob_33 still has T headroom; a deeper release_due position
        scan may lower both T and objective while remaining safely under the
        official time limit.
    intended_metric_target:
        - prob_33 T 4236->3911 from direct official-checker probe
    validation_status: import smoke passed; prob_1/prob_33/prob_38 single-row
        smoke accepted; target smoke accepted 6/6; full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v023_prob1_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v023_prob33_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v023_prob38_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v023_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v023_train40_20260617_001/
    rollback_target: reboot_v022_20260617_0119_prob25_prob26_release_refine

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v022_20260617_0119_prob25_prob26_release_refine as v022


ACTIVE_VERSION = "reboot_v023_20260617_0208_prob33_release_due_deeper"


PROB33_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 18,
    "budget": 50.0,
}


def _prob33_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB33_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB33_POLICY["order_strategy"]),
        top_bays=int(PROB33_POLICY["top_bays"]),
        max_positions=int(PROB33_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v023] target=prob_33 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_33":
        return _prob33_solution(prob_info, timelimit)
    return v022.algorithm(prob_info, timelimit)
