"""reboot_v202_20260626_trackA_portfolio_plus_multiblock_sequence_repair.py

Strategy:
    Keep v200 as the trusted warm-start portfolio, then add a stronger Track A
    repair candidate on top of that selected solution: bounded cross-bay
    multiblock sequence repair. Return the best officially feasible result by
    T-first ordering.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
from alg_versions import reboot_v196_20260626_trackA_crossbay_tardy_migration_on_v195 as v196
from alg_versions import reboot_v200_20260626_trackA_stricter_first20_with_stable_prob38_guard as v200


ACTIVE_VERSION = "reboot_v202_20260626_trackA_portfolio_plus_multiblock_sequence_repair"


def _allow_post_multiblock_repair(features: dict[str, float]) -> bool:
    bays = int(features.get("bays", 0))
    blocks = int(features.get("blocks", 0))
    return (
        4 <= bays <= 5
        and 180 <= blocks <= 320
        and float(features.get("proc_mean", 0.0)) <= 7.9
        and float(features.get("slack_mean", 0.0)) <= 1.7
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.50
        and float(features.get("pref_concentration", 0.0)) <= 0.33
        and float(features.get("pref_pressure", 0.0)) <= 0.30
    )


def _post_budget(remaining: float, tier: str, bays: int) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 5.0,
        "long": 7.0,
        "very_long": 9.0,
    }[tier]
    if bays >= 5:
        cap += 1.0
    return min(cap, remaining)


def _post_positions(tier: str) -> int:
    return {
        "standard": 26,
        "long": 34,
        "very_long": 42,
    }[tier]


def _sequence_candidates(shortlist: list[int], tier: str) -> list[list[int]]:
    seqs: list[list[int]] = [[block_id] for block_id in shortlist]
    if len(shortlist) >= 2:
        seqs.append(shortlist[:2])
        seqs.append(list(reversed(shortlist[:2])))
    if len(shortlist) >= 3:
        seqs.append([shortlist[0], shortlist[2]])
        seqs.append([shortlist[1], shortlist[0]])
    if len(shortlist) >= 3 and tier in {"standard", "long", "very_long"}:
        seqs.append(shortlist[:3])
        seqs.append([shortlist[1], shortlist[0], shortlist[2]])
    if len(shortlist) >= 4 and tier in {"long", "very_long"}:
        seqs.append([shortlist[0], shortlist[2], shortlist[3]])

    unique: list[list[int]] = []
    seen = set()
    for seq in seqs:
        key = tuple(seq)
        if key not in seen:
            unique.append(seq)
            seen.add(key)
    return unique


def _try_post_multiblock_repair(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
    features: dict[str, float],
) -> tuple[dict, dict, list[tuple[list[int], list[tuple[int, int, int]], float, float]]]:
    budget = _post_budget(remaining, tier, int(features.get("bays", 0)))
    if budget <= 0.0:
        return base_solution, base_result, []

    deadline = time.time() + budget
    base_assignments = v186.v064._solution_to_assignments(base_solution)
    shortlist_limit = 5 if int(features.get("blocks", 0)) <= 260 else 4
    shortlist = v186._family_a_tardy_shortlist(prob_info, base_assignments, shortlist_limit)
    sequences = _sequence_candidates(shortlist, tier)

    best_solution = base_solution
    best_result = base_result
    attempted: list[tuple[list[int], list[tuple[int, int, int]], float, float]] = []

    for sequence in sequences:
        if time.time() >= deadline:
            break
        candidate_assignments, moved = v196._apply_crossbay_sequence(
            prob_info,
            base_assignments,
            sequence,
            max_positions=_post_positions(tier),
            deadline=deadline,
        )
        if candidate_assignments is None:
            attempted.append((sequence, moved, float("inf"), float("inf")))
            continue

        candidate_solution = v186.v001._solution_from_assignments(candidate_assignments)
        candidate_result = v186.v001.check_feasibility(prob_info, candidate_solution)
        if not candidate_result.get("feasible"):
            repaired_assignments, repaired_result, _ = v186.v001._repair_with_empty_windows(
                prob_info,
                candidate_assignments,
                max_rounds=4,
            )
            if repaired_result.get("feasible"):
                candidate_solution = v186.v001._solution_from_assignments(repaired_assignments)
                candidate_result = repaired_result

        attempted.append(
            (
                sequence,
                moved,
                float(candidate_result.get("obj1") or float("inf")),
                float(candidate_result.get("objective") or float("inf")),
            )
        )
        if v186.v064._result_key(candidate_result) < v186.v064._result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result

    return best_solution, best_result, attempted


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    started = time.time()
    tier = v186.v169._time_tier(timelimit)
    reserve = v186._dynamic_reserve(timelimit)

    portfolio_solution = v200.algorithm(prob_info, timelimit)
    portfolio_result = v186.v001.check_feasibility(prob_info, portfolio_solution)
    features = v186._selector_features(prob_info)

    if (
        not portfolio_result.get("feasible")
        or not v186._matches_family_a_tightslack(features)
        or not _allow_post_multiblock_repair(features)
        or float(portfolio_result.get("obj1") or 0.0) < 20.0
        or tier in {"very_short", "short"}
    ):
        print(
            f"[baseline_hh reboot_v202] return_portfolio instance={prob_info.get('name')} "
            f"tier={tier} T={portfolio_result.get('obj1')} "
            f"objective={portfolio_result.get('objective')}"
        )
        return portfolio_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    spendable = remaining - reserve
    if spendable <= 1.0:
        print(
            f"[baseline_hh reboot_v202] skip_post_multiblock_repair instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"T={portfolio_result.get('obj1')} objective={portfolio_result.get('objective')}"
        )
        return portfolio_solution

    repaired_solution, repaired_result, attempted = _try_post_multiblock_repair(
        prob_info,
        portfolio_solution,
        portfolio_result,
        spendable,
        tier,
        features,
    )
    print(
        f"[baseline_hh reboot_v202] post_multiblock_repair instance={prob_info.get('name')} "
        f"tier={tier} base_T={portfolio_result.get('obj1')} best_T={repaired_result.get('obj1')} "
        f"attempted={attempted}"
    )
    if v186.v064._result_key(repaired_result) < v186.v064._result_key(portfolio_result):
        print(
            f"[baseline_hh reboot_v202] selected_post_multiblock_repair instance={prob_info.get('name')} "
            f"T={repaired_result.get('obj1')} objective={repaired_result.get('objective')}"
        )
        return repaired_solution
    return portfolio_solution
