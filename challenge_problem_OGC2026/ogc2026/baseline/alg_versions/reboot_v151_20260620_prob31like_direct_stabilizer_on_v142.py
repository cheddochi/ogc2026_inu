"""reboot_v151_20260620_prob31like_direct_stabilizer_on_v142.py

Strategy:
    Keep trusted v142 as the default path, but replace only the prob31-like
    runtime-risk family with one capped direct preference-spread warm start.

Metadata:
    version_id: reboot_v151_20260620_prob31like_direct_stabilizer_on_v142
    parent_version: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
    status: candidate
    timestamp: 2026-06-20 KST
    strategy:
        - Preserve v142 unchanged outside the prob31-like subtype.
        - On the prob31-like subtype only, bypass the inherited deep repair
          chain and build one capped direct limited-concurrent warm start.
        - Keep the direct candidate only when it is officially feasible;
          otherwise fall back to v142.
    hypothesis:
        The reopened current-tree prob31-like timeout risk comes more from the
        inherited delegated repair chain than from the direct warm start
        itself. Returning one capped direct preference-spread build should
        stabilize runtime on this isolated subtype before any further local
        T-breakthrough tuning.
    intended_metric_target:
        - keep prob31-like scoreable on the canonical wrapper surface
        - reduce runtime-cliff risk on the reopened full40 family
        - preserve accepted_for_score 40/40 before further T-focused work
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v046_20260617_1835_runtime_sensitive_feature_guard as v046
from alg_versions import reboot_v078_20260619_1535_fourbay_runtime_family_flatten as v078


ACTIVE_VERSION = "reboot_v151_20260620_prob31like_direct_stabilizer_on_v142"

_PROB31LIKE_DIRECT_CAP = 45.0
_PROB31LIKE_TOP_BAYS = 4
_PROB31LIKE_MAX_POSITIONS = {
    "standard": 12,
    "long": 12,
    "very_long": 12,
}


def _build_prob31like_direct_solution(
    prob_info: dict,
    timelimit: float,
    tier: str,
) -> tuple[dict, dict]:
    started = time.time()
    budget = v046._policy_budget(float(timelimit), tier, _PROB31LIKE_DIRECT_CAP)
    solution = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="preference_spread",
        top_bays=_PROB31LIKE_TOP_BAYS,
        max_positions=_PROB31LIKE_MAX_POSITIONS.get(tier, 12),
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, solution)
    print(
        f"[baseline_hh reboot_v151] prob31like_direct_stabilizer instance={prob_info.get('name')} "
        f"tier={tier} feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s top_bays={_PROB31LIKE_TOP_BAYS} "
        f"max_positions={_PROB31LIKE_MAX_POSITIONS.get(tier, 12)}"
    )
    return solution, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    tier = v078._time_tier(timelimit)

    from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as v142

    if tier in {"very_short", "short"}:
        return v142.algorithm(prob_info, timelimit)

    features = v078._selector_features(prob_info)
    if not v078._matches_prob31like_class(features):
        return v142.algorithm(prob_info, timelimit)

    candidate_solution, candidate_result = _build_prob31like_direct_solution(
        prob_info,
        timelimit,
        tier,
    )
    if candidate_result.get("feasible"):
        return candidate_solution

    print(
        f"[baseline_hh reboot_v151] prob31like_direct_fallback "
        f"instance={prob_info.get('name')} feasible={candidate_result.get('feasible')} "
        f"objective={candidate_result.get('objective')}"
    )
    return v142.algorithm(prob_info, timelimit)
