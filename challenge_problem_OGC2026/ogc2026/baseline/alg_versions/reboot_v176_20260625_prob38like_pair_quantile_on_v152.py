"""reboot_v176_20260625_prob38like_pair_quantile_on_v152.py

Strategy:
    Keep the current-tree recovery-safe parent v152 as the exact warm start,
    then spend only a small residual budget on a bounded two-block quantile
    reinsert for the prob38-like Family B high-T tail.

Metadata:
    version_id: reboot_v176_20260625_prob38like_pair_quantile_on_v152
    parent_version: reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151
    status: candidate
    timestamp: 2026-06-25 KST
    strategy:
        - Preserve v152 unchanged outside the prob38-like subtype.
        - Build the exact v152 base solution first.
        - On the prob38-like slice only, remove the top tardy block together
          with one same-bay blocker and reinsert them sequentially with the
          existing quantile kernel under a strict shared deadline.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The largest remaining current-tree T tail is now a local interaction on
        top of a scoreable parent surface, not a whole-branch builder problem.
        A tiny pair-quantile postpass should recover some T on prob38-like
        rows without reopening the runtime-risk guard rows that direct
        specialist paths disturbed.
    intended_metric_target:
        - reduce the prob38-like T tail on top of v152
        - preserve accepted_for_score on the current-tree recovery surface
        - avoid reopening Family B guard regressions
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151 as v152


ACTIVE_VERSION = "reboot_v176_20260625_prob38like_pair_quantile_on_v152"

_PAIR_BUDGET_CAP = 2.8
_PAIR_MIN_HEADROOM = 1.0


def _pair_target_block_ids(prob_info: dict, assignments: dict[int, dict]) -> list[int]:
    top_tardy_ids = v064._tardy_block_ids(prob_info, assignments, 1)
    if not top_tardy_ids:
        return []

    target_block_id = top_tardy_ids[0]
    target_assignment = assignments[target_block_id]
    target_bay_id = int(target_assignment["bay_id"])
    target_entry = int(target_assignment["entry_time"])
    target_exit = int(target_assignment["exit_time"])
    blocks = prob_info["blocks"]

    blocker_rank = []
    for block_id, assignment in assignments.items():
        if int(block_id) == int(target_block_id):
            continue
        if int(assignment["bay_id"]) != target_bay_id:
            continue

        entry = int(assignment["entry_time"])
        exit_time = int(assignment["exit_time"])
        overlap = max(0, min(target_exit, exit_time) - max(target_entry, entry))
        exit_distance = abs(exit_time - target_entry)
        due = int(blocks[int(block_id)]["due_date"])
        tardiness = max(0, exit_time - due)
        prefs = list(blocks[int(block_id)]["bay_preferences"])
        pref_penalty = max(prefs) - prefs[target_bay_id]
        blocker_rank.append(
            (
                0 if overlap > 0 else 1,
                -overlap,
                exit_distance,
                -tardiness,
                -pref_penalty,
                int(block_id),
            )
        )

    if not blocker_rank:
        return [target_block_id]

    blocker_block_id = min(blocker_rank)[-1]
    return [target_block_id, blocker_block_id]


def _pair_orders(prob_info: dict, pair_ids: list[int]) -> list[list[int]]:
    if len(pair_ids) < 2:
        return [pair_ids]

    blocks = prob_info["blocks"]
    due_first = sorted(
        pair_ids,
        key=lambda block_id: (
            int(blocks[block_id]["due_date"]),
            int(blocks[block_id]["processing_time"]),
            int(block_id),
        ),
    )
    target_first = pair_ids[:]

    orders: list[list[int]] = []
    for order in (target_first, due_first):
        if order not in orders:
            orders.append(order)
    return orders


def _pair_budget(remaining: float) -> float:
    return min(_PAIR_BUDGET_CAP, max(0.0, remaining - 0.25))


def _pair_max_positions(tier: str) -> int:
    return {
        "standard": 10,
        "long": 12,
        "very_long": 14,
    }.get(tier, 10)


def _try_prob38like_pair_quantile(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    pair_ids = _pair_target_block_ids(
        prob_info,
        v064._solution_to_assignments(base_solution),
    )
    if len(pair_ids) < 2:
        return base_solution, base_result

    budget = _pair_budget(remaining)
    if budget < _PAIR_MIN_HEADROOM:
        return base_solution, base_result
    deadline = time.time() + budget

    base_assignments = v064._solution_to_assignments(base_solution)
    best_solution = base_solution
    best_result = base_result
    max_positions = _pair_max_positions(tier)

    for ordered_pair_ids in _pair_orders(prob_info, pair_ids):
        if time.time() >= deadline:
            break

        working_assignments = dict(base_assignments)
        for block_id in ordered_pair_ids:
            working_assignments.pop(block_id, None)

        success = True
        for block_id in ordered_pair_ids:
            candidate_assignments = v080._quantile_single_reinsert(
                prob_info,
                working_assignments,
                block_id,
                max_positions=max_positions,
                deadline=deadline,
            )
            if candidate_assignments is None:
                success = False
                print(
                    f"[baseline_hh reboot_v176] prob38like_pair_quantile order={ordered_pair_ids} "
                    f"block={block_id} candidate=none"
                )
                break
            working_assignments = candidate_assignments

        if not success:
            continue

        candidate_solution = v001._solution_from_assignments(working_assignments)
        candidate_result = v001.check_feasibility(prob_info, candidate_solution)
        print(
            f"[baseline_hh reboot_v176] prob38like_pair_quantile instance={prob_info.get('name')} "
            f"pair={pair_ids} order={ordered_pair_ids} feasible={candidate_result.get('feasible')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')} "
            f"budget={budget:.2f}s"
        )
        if v064._result_key(candidate_result) < v064._result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result

    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    overall_started = time.time()
    timelimit = float(timelimit)
    tier = v050._time_tier(timelimit)
    if tier in {"very_short", "short"}:
        return v152.algorithm(prob_info, timelimit)

    features = v050._selector_features(prob_info)
    if not v050._matches_prob38like_class(features):
        return v152.algorithm(prob_info, timelimit)

    base_solution = v152.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or float(base_result.get("obj1") or 0.0) < 9000.0
    ):
        return base_solution

    reserve = v050._dynamic_reserve(timelimit)
    remaining = max(0.0, timelimit - (time.time() - overall_started) - reserve)
    if remaining < _PAIR_MIN_HEADROOM + 0.25:
        print(
            f"[baseline_hh reboot_v176] skip_prob38like_pair_quantile "
            f"instance={prob_info.get('name')} tier={tier} remaining={remaining:.2f}s "
            f"reserve={reserve:.2f}s base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result = _try_prob38like_pair_quantile(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if v064._result_key(best_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v176] selected_prob38like_pair_quantile "
            f"instance={prob_info.get('name')} base_T={base_result.get('obj1')} "
            f"best_T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v176] keep_v152_base instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={best_result.get('obj1')}"
    )
    return base_solution
