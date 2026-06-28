"""reboot_v114_20260619_2358_prob31like_direct_prefix2_stable_on_v109.py

Strategy:
    Keep v109 as the default path, but replace only the prob31-like subtype
    with one runtime-stable direct prefix-2 repair plan.

Metadata:
    version_id: reboot_v114_20260619_2358_prob31like_direct_prefix2_stable_on_v109
    parent_version: reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108
    status: candidate
    timestamp: 2026-06-19 23:58 KST
    strategy:
        - Preserve v109 unchanged outside the prob31-like subtype.
        - Keep the stable capped preference-spread base from the v111 branch.
        - Replace the generic v067/v074/v085 multi-stage chain with one direct
          top-2 tardy prefix rebuild.
        - Use the subtype-specific runtime-stable branch only when
          `timelimit >= 55s`; otherwise fall back to the shorter-limit parent.
    hypothesis:
        The prob31-like current-source runtime cliff comes from paying for a
        generic multi-stage repair chain when only the two-block tardy prefix
        rebuild is actually needed to recover the stronger T row.
    intended_metric_target:
        - keep prob31-like scoreable under the official 60s limit
        - recover the stronger `40349837 / T=2792` row
        - preserve non-prob31-like families through the v109 parent
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108
"""

from __future__ import annotations

import time

from alg_versions import reboot_v046_20260617_1835_runtime_sensitive_feature_guard as v046
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v078_20260619_1535_fourbay_runtime_family_flatten as v078
from alg_versions import reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108 as v109
from alg_versions import reboot_v111_20260619_2130_prob31like_stable_direct_cap_on_v109 as v111
from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001


ACTIVE_VERSION = "reboot_v114_20260619_2358_prob31like_direct_prefix2_stable_on_v109"


def _build_prob31like_stable_base(prob_info: dict, timelimit: float, tier: str) -> tuple[dict, dict]:
    return v111._build_prob31like_stable_base(prob_info, timelimit, tier)


def _try_direct_prefix2_rebuild(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    if tier in {"very_short", "short"} or remaining <= v046._dynamic_reserve(60.0) + 2.0:
        return base_solution, base_result

    started = time.time()
    base_assignments = v064._solution_to_assignments(base_solution)
    tardy_block_ids = v064._tardy_block_ids(prob_info, base_assignments, 2)
    if len(tardy_block_ids) < 2:
        return base_solution, base_result

    candidate_assignments = v064._greedy_research_prefix(
        prob_info,
        base_assignments,
        tardy_block_ids,
        2,
    )
    candidate_solution = v001._solution_from_assignments(candidate_assignments)
    candidate_result = v001.check_feasibility(prob_info, candidate_solution)
    print(
        f"[baseline_hh reboot_v114] prob31like_direct_prefix2 instance={prob_info.get('name')} "
        f"tier={tier} tardy_ids={tardy_block_ids} elapsed={time.time() - started:.2f}s "
        f"feasible={candidate_result.get('feasible')} T={candidate_result.get('obj1')} "
        f"objective={candidate_result.get('objective')}"
    )
    if v064._result_key(candidate_result) < v064._result_key(base_result):
        return candidate_solution, candidate_result
    return base_solution, base_result


def _prob31like_runtime_stable_solution(prob_info: dict, timelimit: float, tier: str) -> tuple[dict, dict]:
    started = time.time()
    solution, result = _build_prob31like_stable_base(prob_info, timelimit, tier)
    if not result.get("feasible"):
        return solution, result

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    return _try_direct_prefix2_rebuild(
        prob_info,
        solution,
        result,
        remaining,
        tier,
    )


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v078._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    if (
        tier not in {"very_short", "short"}
        and float(timelimit) >= 55.0
        and v078._matches_prob31like_class(features)
    ):
        candidate_solution, candidate_result = _prob31like_runtime_stable_solution(
            prob_info,
            timelimit,
            tier,
        )
        if candidate_result.get("feasible"):
            return candidate_solution
        print(
            f"[baseline_hh reboot_v114] prob31like_runtime_stable_fallback "
            f"instance={prob_info.get('name')} feasible={candidate_result.get('feasible')} "
            f"objective={candidate_result.get('objective')}"
        )

    return v109.algorithm(prob_info, timelimit)
