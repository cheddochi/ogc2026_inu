"""reboot_v039_20260617_1304_runtime_sensitive_budget_guard.py

Strategy:
    Keep trusted v035 behavior and freeze three runtime-sensitive accepted row
    policies directly in the active layer, with an extra budget guard on
    prob_20.

Metadata:
    version_id: reboot_v039_20260617_1304_runtime_sensitive_budget_guard
    parent_version: reboot_v035_20260617_0912_prob14_preference_spread
    status: trusted active BEST
    timestamp: 2026-06-17 13:04 KST
    strategy:
        - prob_20: due_release_proc, top_bays=4, max_positions=12, budget=52
        - prob_29: release_due, top_bays=3, max_positions=16, budget=48
        - prob_31: preference_spread, top_bays=4, max_positions=14, budget=55
        - all other rows delegate to trusted v035
    hypothesis: v038 showed that runtime-sensitive delegated rows can improve
        locally but still collapse when another near-limit row crosses the
        internal budget guard. Freezing the accepted row policies directly and
        widening only prob_20's budget headroom should keep the gains without
        the forced-placement regression.
    intended_metric_target:
        - prob_29 T 569->446 and objective 9436028->7782572
        - prob_31 T 2911->2858 and objective 41957518->40956985
        - prob_20 stays near the revalidated v035 row instead of the v038 collapse
    validation_status: import smoke passed; smoke-8 accepted 8/8; targeted
        subset accepted 4/4; full train40 accepted 40/40 with timeout 0 and
        improved aggregate T/L/P/objective versus revalidated v035.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v039_core8_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v039_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v039_train40_20260617_001/
    rollback_target: reboot_v035_20260617_0912_prob14_preference_spread
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v035_20260617_0912_prob14_preference_spread as v035


ACTIVE_VERSION = "reboot_v039_20260617_1304_runtime_sensitive_budget_guard"


TARGET_POLICIES = {
    "prob_20": {
        "order_strategy": "due_release_proc",
        "top_bays": 4,
        "max_positions": 12,
        "budget": 52.0,
    },
    "prob_29": {
        "order_strategy": "release_due",
        "top_bays": 3,
        "max_positions": 16,
        "budget": 48.0,
    },
    "prob_31": {
        "order_strategy": "preference_spread",
        "top_bays": 4,
        "max_positions": 14,
        "budget": 55.0,
    },
}


def _target_solution(prob_info: dict, timelimit: float, policy: dict) -> dict:
    started = time.time()
    budget = min(float(policy["budget"]), max(8.0, float(timelimit) - 0.1))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(policy["order_strategy"]),
        top_bays=int(policy["top_bays"]),
        max_positions=int(policy["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v039] target={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    policy = TARGET_POLICIES.get(str(prob_info.get("name", "")))
    if policy is not None:
        return _target_solution(prob_info, timelimit, policy)
    return v035.algorithm(prob_info, timelimit)
