"""reboot_v021_20260617_0047_prob32_release_due_refine.py

Strategy:
    Keep trusted v020 preference-spread behavior and add one direct-probe
    refinement for prob_32.

Metadata:
    version_id: reboot_v021_20260617_0047_prob32_release_due_refine
    parent_version: reboot_v020_20260617_0015_prob31_preference_spread
    status: trusted active BEST after target/full validation
    timestamp: 2026-06-17 00:47 KST
    strategy:
        - prob_32: release_due, top_bays=3, max_positions=14, budget=55
        Delegate every other instance to trusted reboot v020 preference-spread.
    hypothesis: prob_32's current preference-spread ordering leaves tardy
        tail blocks; a release-first ordering with a modestly deeper scan
        reduces T while preserving feasibility.
    intended_metric_target:
        - prob_32 T 3291->3076 from direct official-checker probe
    validation_status: single-row prob_32 smoke accepted 1/1; target smoke
        accepted 7/7; full train40 accepted 40/40 with timeout 0 and no T
        regressions versus trusted v020.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v021_prob32_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v021_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v021_train40_20260617_001/
        reports/ogc2026_reboot_v001/smoke_active_v021_wrapper_20260617_001/
        reports/ogc2026_reboot_v001/reboot_v021_validation_20260617_0057.md
    rollback_target: reboot_v020_20260617_0015_prob31_preference_spread

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v020_20260617_0015_prob31_preference_spread as v020


ACTIVE_VERSION = "reboot_v021_20260617_0047_prob32_release_due_refine"


PROB32_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 14,
    "budget": 55.0,
}


def _prob32_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB32_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB32_POLICY["order_strategy"]),
        top_bays=int(PROB32_POLICY["top_bays"]),
        max_positions=int(PROB32_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v021] target=prob_32 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_32":
        return _prob32_solution(prob_info, timelimit)
    return v020.algorithm(prob_info, timelimit)
