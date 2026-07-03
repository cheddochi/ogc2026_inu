"""reboot_v446_20260703_trackA_prob11_shifted_bayassign_localsearch_on_v317.py

Strategy:
    Keep the accepted v317 surface as the default route. On the exact
    prob11like Family A residual subtype only, preserve the improved shifted
    bay-assignment seed from v445 and replace the unstable replay tail with
    bounded same-bay pair/group local search plus latest-feasible pull-back.
"""

from __future__ import annotations

import time

from alg_versions import (
    reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186,
)
from alg_versions import (
    reboot_v216_20260627_trackA_inline_latest_feasible_slice_on_v212 as v216,
)
from alg_versions import (
    reboot_v238_20260627_trackA_prob11like_constructive_seed_portfolio_on_v218 as v238,
)
from alg_versions import (
    reboot_v298_20260629_trackA_prob11_rescue_with_familyB_tail_freeze_on_v290 as v298,
)
from alg_versions import (
    reboot_v317_20260630_trackA_prob13_only_window_multiblock_on_v314 as v317,
)
from alg_versions import (
    reboot_v357_20260701_trackA_prob20_exact3_companion_groupmove_on_v317 as v357,
)
from alg_versions import (
    reboot_v394_20260702_trackA_prob11_front_bayassign_on_v317 as v394,
)
from alg_versions import (
    reboot_v395_20260702_trackA_prob11_front_grasp_on_v317 as v395,
)
from alg_versions import (
    reboot_v405_20260702_trackA_prob11_rescue_pocket_grasp_on_v317 as v405,
)
from alg_versions import (
    reboot_v416_20260702_trackA_prob11_protected_pairswap_groupreorder_on_v317 as v416,
)
from alg_versions import (
    reboot_v420_20260702_trackA_prob11_predecessor_regret_on_v317 as v420,
)
from alg_versions import (
    reboot_v423_20260702_trackA_prob11_predecessor_bayassign_on_v317 as v423,
)
from alg_versions import (
    reboot_v437_20260703_trackA_prob11_shifted_backward_latest_on_v317 as v437,
)


ACTIVE_VERSION = "reboot_v446_20260703_trackA_prob11_shifted_bayassign_localsearch_on_v317"
PARENT_VERSION = "reboot_v317_20260630_trackA_prob13_only_window_multiblock_on_v314"


def _score_key(result: dict) -> tuple[float, float, float, float]:
    return v186.v064._result_key(result)


def _append_attempt(attempted: list[tuple[str, float, float]], label: str, result: dict) -> None:
    attempted.append(
        (
            label,
            float(result.get("obj1") or 0.0),
            float(result.get("objective") or 0.0),
        )
    )


def _search_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    return min(
        {
            "standard": 5.0,
            "long": 6.0,
            "very_long": 7.0,
        }[tier],
        remaining,
    )


def _protected_warm_limit(timelimit: float, reserve: float, phase_budget: float) -> float:
    return max(18.0, timelimit - reserve - phase_budget)


def _seeded_focus(assignments: dict[int, dict], fallback_focus: list[int]) -> list[int]:
    preferred = [81, 105, 3, 118, 153, 193, 39, 154]
    if all(int(block_id) in assignments for block_id in preferred):
        return [int(block_id) for block_id in preferred]
    return [int(block_id) for block_id in fallback_focus]


def _run_shifted_local_refine(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    local_ids: list[int],
    deadline: float,
    tier: str,
) -> tuple[dict, dict, list[tuple[str, object]]]:
    best_solution = base_solution
    best_result = base_result
    refine_log: list[tuple[str, object]] = []

    if time.time() < deadline:
        portfolio_solution, portfolio_result, portfolio_moves = v416._run_local_portfolio(
            prob_info,
            best_solution,
            best_result,
            local_ids,
            deadline,
        )
        refine_log.append(("pair_group_local", portfolio_moves))
        if _score_key(portfolio_result) < _score_key(best_result):
            best_solution = portfolio_solution
            best_result = portfolio_result

    remaining = max(0.0, deadline - time.time())
    if remaining > 0.35:
        pullback_solution, pullback_result, pullback_moves = v216._try_exact_latest_feasible_slice(
            prob_info,
            best_solution,
            best_result,
            remaining,
            tier,
        )
        refine_log.append(
            ("latest_feasible_pullback", [int(block_id) for block_id, _, _ in pullback_moves])
        )
        if _score_key(pullback_result) < _score_key(best_result):
            best_solution = pullback_solution
            best_result = pullback_result

    return best_solution, best_result, refine_log


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    features = v394._target_prob11like(prob_info, timelimit)
    if features is None:
        return v317.algorithm(prob_info, timelimit)

    started = time.time()
    tier = v186.v169._time_tier(timelimit)
    reserve = v186._dynamic_reserve(timelimit)
    phase_budget = _search_budget(max(0.0, timelimit - reserve - 18.0), tier)

    warm_limit = _protected_warm_limit(timelimit, reserve, phase_budget)
    warm_solution = v298.algorithm(prob_info, warm_limit)
    warm_result = v186.v001.check_feasibility(prob_info, warm_solution)
    if (
        not warm_result.get("feasible")
        or float(warm_result.get("obj1") or 0.0) <= 0.0
    ):
        return warm_solution

    attempted: list[tuple[str, float, float]] = []
    _append_attempt(attempted, "v298_prob11_protected_warm", warm_result)
    best_label = "v298_prob11_protected_warm"
    best_solution = warm_solution
    best_result = warm_result
    move_log: list[tuple[str, object]] = []

    for label, order_name, selector in [
        ("slack_tardiness_seed", "slack", "tardiness"),
        ("edd_release_preference_seed", "edd_release", "preference"),
    ]:
        _, seed_result = v238._build_constructive_seed(prob_info, order_name, selector)
        _append_attempt(attempted, label, seed_result)

    remaining = max(0.0, timelimit - (time.time() - started))
    budget = _search_budget(max(0.0, remaining - reserve), tier)
    if budget <= 0.0:
        print(
            f"[baseline_hh reboot_v446] keep_warm instance={prob_info.get('name')} "
            f"tier={tier} warm_limit={warm_limit:.2f}s remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"T={warm_result.get('obj1')} objective={warm_result.get('objective')}"
        )
        return warm_solution

    deadline = time.time() + budget
    assignments = v186.v064._solution_to_assignments(warm_solution)
    raw_focus_ids = v405._focus_cluster(prob_info, assignments)
    focus_ids = _seeded_focus(assignments, raw_focus_ids)
    rescue_local_ids = v405._rescue_local_ids(assignments, focus_ids)
    cluster = v420._cluster_from_focus(focus_ids)
    if len(cluster) < 3:
        print(
            f"[baseline_hh reboot_v446] no_cluster instance={prob_info.get('name')} "
            f"tier={tier} focus_ids={focus_ids} T={warm_result.get('obj1')} objective={warm_result.get('objective')}"
        )
        return warm_solution

    move_log.append(("focus_ids", list(focus_ids)))
    move_log.append(("rescue_local_ids", list(rescue_local_ids)))
    move_log.append(("cluster", list(cluster)))

    for label, cluster_plan, chooser in v420._plan_specs(prob_info, assignments, cluster):
        if time.time() >= deadline:
            break
        pocket, blockers, predecessors = v420._causal_pocket(
            prob_info,
            assignments,
            cluster,
            cluster_plan,
            focus_ids,
            rescue_local_ids,
        )
        base_variants = v420._pocket_variants(cluster, focus_ids, blockers, predecessors, pocket)
        cluster_focus_ids = next((ids for sublabel, ids in base_variants if sublabel == "cluster_focus"), list(cluster))
        variants = v437._shifted_latest_variants(
            cluster,
            cluster_focus_ids,
            blockers,
            predecessors,
            rescue_local_ids,
        )
        source_bay = int(assignments[cluster[0]]["bay_id"])
        forced_move_ids = set(blockers + predecessors)
        local_plan_all = v357._choose_local_bays(
            prob_info,
            assignments,
            list(dict.fromkeys(pocket + blockers[:3] + predecessors[:3] + rescue_local_ids[:4])),
            cluster_plan,
            mode=chooser,
            source_bay=source_bay,
            forced_move_ids=forced_move_ids,
        )

        move_log.append((f"{label}_blockers", [int(block_id) for block_id in blockers]))
        move_log.append((f"{label}_predecessors", [int(block_id) for block_id in predecessors]))
        move_log.append((f"{label}_variants", [(sublabel, [int(block_id) for block_id in ids]) for sublabel, ids in variants]))

        for variant_label, variant_ids in variants[:2]:
            if time.time() >= deadline:
                break
            variant_plan = {
                int(block_id): int(local_plan_all.get(int(block_id), assignments[int(block_id)]["bay_id"]))
                for block_id in variant_ids
            }
            local_search_ids = list(
                dict.fromkeys(variant_ids + rescue_local_ids[:4] + blockers[:2] + predecessors[:2])
            )
            for sequence_mode in ("backward_latest", "latest", "slack"):
                if time.time() >= deadline:
                    break
                candidate_assignments = v423._reinsert_on_assigned_bays(
                    prob_info,
                    assignments,
                    variant_ids,
                    variant_plan,
                    sequence_mode=sequence_mode,
                    deadline=deadline,
                )
                base_label = f"{label}_{variant_label}_{sequence_mode}"
                if candidate_assignments is None:
                    _append_attempt(attempted, base_label + "_failed", warm_result)
                    continue

                candidate_solution, candidate_result = v395._evaluate_candidate(prob_info, candidate_assignments)
                _append_attempt(attempted, base_label, candidate_result)
                if not candidate_result.get("feasible"):
                    continue

                refined_solution, refined_result, refine_log = _run_shifted_local_refine(
                    prob_info,
                    candidate_solution,
                    candidate_result,
                    local_search_ids,
                    deadline,
                    tier,
                )
                _append_attempt(attempted, base_label + "_localsearch", refined_result)
                move_log.append((base_label + "_local_ids", [int(block_id) for block_id in local_search_ids]))
                move_log.append((base_label + "_localsearch", refine_log))
                if _score_key(refined_result) < _score_key(best_result):
                    best_label = base_label + "_localsearch"
                    best_solution = refined_solution
                    best_result = refined_result
        break

    if time.time() < deadline and _score_key(best_result) < _score_key(warm_result):
        tail_remaining = max(0.0, deadline - time.time())
        repaired_solution, repaired_result, accepted_moves = v186._try_family_a_warm_repair(
            prob_info,
            best_solution,
            best_result,
            tail_remaining,
            tier,
            features,
        )
        _append_attempt(attempted, "best_shifted_bayassign_localsearch_plus_warmrepair", repaired_result)
        move_log.append(
            ("best_shifted_bayassign_localsearch_plus_warmrepair", [int(block_id) for block_id, _, _ in accepted_moves])
        )
        if repaired_result.get("feasible") and _score_key(repaired_result) < _score_key(best_result):
            best_label = "best_shifted_bayassign_localsearch_plus_warmrepair"
            best_solution = repaired_solution
            best_result = repaired_result

    print(
        f"[baseline_hh reboot_v446] prob11_shifted_bayassign_localsearch instance={prob_info.get('name')} "
        f"tier={tier} warm_limit={warm_limit:.2f}s best={best_label} attempted={attempted} move_log={move_log} "
        f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
    )
    return best_solution if _score_key(best_result) < _score_key(warm_result) else warm_solution
