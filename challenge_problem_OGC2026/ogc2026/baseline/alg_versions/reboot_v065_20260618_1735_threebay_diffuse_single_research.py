"""reboot_v065_20260618_1735_threebay_diffuse_single_research.py

Strategy:
    Keep trusted v063 as the default path, then greedily re-search exactly one
    tardy block on a narrow 3-bay diffuse-moderate-pressure mid-proc class.

Metadata:
    version_id: reboot_v065_20260618_1735_threebay_diffuse_single_research
    parent_version: reboot_v063_20260618_1605_prob40like_direct_first_due_release
    status: accepted
    timestamp: 2026-06-18 17:35 KST
    strategy:
        - Preserve v063 unchanged outside the target subtype.
        - Build the trusted warm start first.
        - On the target subtype, remove only the single worst tardy block and
          re-place it with the full greedy kernel under a strict budget.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The subtype improvement signal survives at width 1, and width 1 avoids
        the timeout that rejected v064.
    intended_metric_target:
        - improve prob33-like and prob37-like rows
        - preserve representative smoke rows
        - improve avg objective versus trusted v063
    validation_status:
        accepted_for_score=40/40 on full train40 benchmark
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v065_train40_20260618_001
    rollback_target: reboot_v063_20260618_1605_prob40like_direct_first_due_release
"""

from __future__ import annotations

import baseline_greedy
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064


ACTIVE_VERSION = "reboot_v065_20260618_1735_threebay_diffuse_single_research"


def _move_limit(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 1,
        "long": 1,
        "very_long": 2,
    }[tier]


def _checkpoint_counts(move_limit: int, tier: str) -> list[int]:
    if move_limit <= 0:
        return []
    if tier == "very_long" and move_limit >= 2:
        return [1, 2]
    return [1]


def _try_greedy_research(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    timelimit: float,
    tier: str,
) -> tuple[dict, dict]:
    if tier in {"very_short", "short"}:
        return base_solution, base_result

    budget = v064._repair_budget(timelimit, remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    base_assignments = v064._solution_to_assignments(base_solution)
    tardy_block_ids = v064._tardy_block_ids(prob_info, base_assignments, _move_limit(tier))
    if not tardy_block_ids:
        return base_solution, base_result

    deadline = v064.time.time() + budget
    best_solution = base_solution
    best_result = base_result
    for prefix_len in _checkpoint_counts(len(tardy_block_ids), tier):
        if v064.time.time() >= deadline:
            break
        candidate_assignments = v064._greedy_research_prefix(
            prob_info,
            base_assignments,
            tardy_block_ids,
            prefix_len,
        )
        candidate_solution = v064.v001._solution_from_assignments(candidate_assignments)
        candidate_result = v064.v001.check_feasibility(prob_info, candidate_solution)
        print(
            f"[baseline_hh reboot_v065] diffuse_single_research instance={prob_info.get('name')} "
            f"tier={tier} moved={prefix_len} feasible={candidate_result.get('feasible')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        if v064._result_key(candidate_result) < v064._result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = v064.time.time()
    features = v064._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v064.v063.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not v064._matches_threebay_diffuse_moderate_class(features)
        or float(base_result.get("obj1") or 0.0) <= 3000.0
    ):
        return base_solution

    elapsed = v064.time.time() - started
    remaining = max(0.0, float(timelimit) - elapsed)
    if remaining <= v064._dynamic_reserve(float(timelimit)) + 2.0:
        print(
            f"[baseline_hh reboot_v065] skip_diffuse_single instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_greedy_research(
        prob_info,
        base_solution,
        base_result,
        remaining,
        float(timelimit),
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v065] selected_diffuse_single instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v065] keep_warm_start instance={prob_info.get('name')} "
        f"best_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
