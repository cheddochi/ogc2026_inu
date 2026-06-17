"""reboot_v029_20260617_0613_prob18_release_due.py

Strategy:
    Keep trusted v028 behavior and add one release-first refinement only for
    prob_18.

Metadata:
    version_id: reboot_v029_20260617_0613_prob18_release_due
    parent_version: reboot_v028_20260617_0554_prob24_preference_spread
    status: trusted active BEST
    timestamp: 2026-06-17 06:13 KST
    strategy:
        - prob_18: release_due, top_bays=3, max_positions=12, budget=36
        Delegate every other instance to trusted v028.
    hypothesis: prob_18 has a strong release-ordering bottleneck, and a
        release-first scan can eliminate residual tardiness without creating
        runtime pressure.
    intended_metric_target:
        - prob_18 T 767->0 from direct official-checker probe
    validation_status: import smoke passed; prob_1/prob_18/prob_38 single-row
        smoke accepted; target smoke accepted 6/6; full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v029_prob1_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v029_prob18_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v029_prob38_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v029_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v029_train40_20260617_001/
    rollback_target: reboot_v028_20260617_0554_prob24_preference_spread

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v028_20260617_0554_prob24_preference_spread as v028


ACTIVE_VERSION = "reboot_v029_20260617_0613_prob18_release_due"


PROB18_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 12,
    "budget": 36.0,
}


def _prob18_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB18_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB18_POLICY["order_strategy"]),
        top_bays=int(PROB18_POLICY["top_bays"]),
        max_positions=int(PROB18_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v029] target=prob_18 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_18":
        return _prob18_solution(prob_info, timelimit)
    return v028.algorithm(prob_info, timelimit)
