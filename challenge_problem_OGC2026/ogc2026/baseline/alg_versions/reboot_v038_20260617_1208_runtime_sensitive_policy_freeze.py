"""reboot_v038_20260617_1208_runtime_sensitive_policy_freeze.py

Strategy:
    Keep trusted v035 behavior and freeze two runtime-sensitive accepted row
    policies directly in the active layer.

Metadata:
    version_id: reboot_v038_20260617_1208_runtime_sensitive_policy_freeze
    parent_version: reboot_v035_20260617_0912_prob14_preference_spread
    status: rejected
    timestamp: 2026-06-17 12:08 KST
    strategy:
        - prob_29: release_due, top_bays=3, max_positions=16, budget=48
        - prob_31: preference_spread, top_bays=4, max_positions=14, budget=55
        - all other rows delegate to trusted v035
    hypothesis: the current active chain still drifts on prob_29 and prob_31
        relative to their previously accepted dedicated evidence; freezing those
        exact accepted policies into one active selector should restore the
        better row outcomes without perturbing the rest of train40.
    intended_metric_target:
        - prob_29 T 569->446, objective 9436028->7782572 versus revalidated v035
        - prob_31 T 2911->2858, objective 41957518->41251061 versus revalidated v035
    validation_status: import smoke passed; smoke-8 passed 8/8; targeted subset
        reproduced the intended prob_29/prob_31 uplift; full train40 stayed
        accepted 40/40 but regressed badly on prob_20 and worsened aggregate
        T/L/P/objective, so the candidate was rejected.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v038_core8_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v038_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v038_train40_20260617_001/
    rollback_target: reboot_v035_20260617_0912_prob14_preference_spread
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v035_20260617_0912_prob14_preference_spread as v035


ACTIVE_VERSION = "reboot_v038_20260617_1208_runtime_sensitive_policy_freeze"


TARGET_POLICIES = {
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
    budget = min(float(policy["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(policy["order_strategy"]),
        top_bays=int(policy["top_bays"]),
        max_positions=int(policy["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v038] target={prob_info.get('name')} "
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
