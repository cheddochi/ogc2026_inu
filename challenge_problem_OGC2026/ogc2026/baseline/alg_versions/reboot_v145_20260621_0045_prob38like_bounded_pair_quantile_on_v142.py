"""reboot_v145_20260621_0045_prob38like_bounded_pair_quantile_on_v142.py

Strategy:
    Keep trusted v142 as the default path, then run a bounded sequential
    two-block quantile repair only on the prob38-like tail family.

Metadata:
    version_id: reboot_v145_20260621_0045_prob38like_bounded_pair_quantile_on_v142
    parent_version: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
    status: candidate
    timestamp: 2026-06-21 00:45 KST
    strategy:
        - Preserve v142 unchanged outside the target subtype.
        - Build the exact v142 warm start first.
        - On the prob38-like family only, remove the top tardy block together
          with one same-bay blocker and reinsert them sequentially.
        - Reuse the existing quantile one-block kernel with a shared deadline,
          tighter position cap, and only two deterministic block orders.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The residual prob38-like T tail is still a two-block interaction, but
        the expensive full pair rebuild in v144 was the wrong kernel. A bounded
        sequential quantile repair can keep the pair hypothesis while staying
        on the 60s scoreable surface.
    intended_metric_target:
        - improve prob38-like T
        - preserve accepted_for_score 40/40
        - reduce total T / avg T / high-T tail before polish-only work
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080


ACTIVE_VERSION = "reboot_v145_20260621_0045_prob38like_bounded_pair_quantile_on_v142"


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


def _try_prob38like_bounded_pair_quantile(
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

    budget = min(4.0, max(0.0, remaining - 0.5))
    if budget <= 0.0:
        return base_solution, base_result
    deadline = time.time() + budget

    base_assignments = v064._solution_to_assignments(base_solution)
    best_solution = base_solution
    best_result = base_result

    max_positions = {
        "standard": 16,
        "long": 20,
        "very_long": 24,
    }.get(tier, 16)

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
                    f"[baseline_hh reboot_v145] prob38like_bounded_pair order={ordered_pair_ids} "
                    f"block={block_id} candidate=none"
                )
                break
            working_assignments = candidate_assignments

        if not success:
            continue

        candidate_solution = v001._solution_from_assignments(working_assignments)
        candidate_result = v001.check_feasibility(prob_info, candidate_solution)
        print(
            f"[baseline_hh reboot_v145] prob38like_bounded_pair instance={prob_info.get('name')} "
            f"pair={pair_ids} order={ordered_pair_ids} feasible={candidate_result.get('feasible')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        if v064._result_key(candidate_result) < v064._result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result

    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    overall_started = time.time()
    tier = v050._time_tier(timelimit)
    features = v050._selector_features(prob_info)

    from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as v142

    base_solution = v142.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)

    if (
        tier in {"very_short", "short"}
        or not base_result.get("feasible")
        or not v050._matches_prob38like_class(features)
        or float(base_result.get("obj1") or 0.0) < 9000.0
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - overall_started))
    reserve = v050._dynamic_reserve(timelimit)
    if remaining <= reserve + 6.0:
        print(
            f"[baseline_hh reboot_v145] skip_prob38like_bounded_pair instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result = _try_prob38like_bounded_pair_quantile(
        prob_info,
        base_solution,
        base_result,
        remaining - reserve,
        tier,
    )
    if v064._result_key(best_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v145] selected_prob38like_bounded_pair instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v145] keep_v142_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={best_result.get('obj1')}"
    )
    return base_solution
