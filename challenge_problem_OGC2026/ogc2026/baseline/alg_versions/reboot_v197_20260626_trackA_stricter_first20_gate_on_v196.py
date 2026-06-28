"""reboot_v197_20260626_trackA_stricter_first20_gate_on_v196.py

Strategy:
    Keep trusted v195 as the fallback surface, preserve the v196 bounded
    cross-bay Track A specialist, but tighten the activation band to a more
    clearly first20-like short-proc / tighter-slack subset.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
from alg_versions import reboot_v195_20260626_familyA_window_reorder_on_v194 as v195


ACTIVE_VERSION = "reboot_v197_20260626_trackA_stricter_first20_gate_on_v196"


def _allow_crossbay_track(features: dict[str, float]) -> bool:
    bays = int(features.get("bays", 0))
    blocks = int(features.get("blocks", 0))
    return (
        bays == 4
        and 180 <= blocks <= 260
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.35
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.58
        and float(features.get("pref_concentration", 0.0)) <= 0.50
        and float(features.get("pref_pressure", 0.0)) <= 0.50
    )


def _postpass_budget(remaining: float, tier: str, block_count: int) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 3.5,
        "long": 5.0,
        "very_long": 6.5,
    }[tier]
    if block_count >= 240:
        cap += 0.5
    return min(cap, remaining)


def _max_positions(tier: str) -> int:
    return {
        "standard": 24,
        "long": 30,
        "very_long": 36,
    }[tier]


def _sequence_candidates(shortlist: list[int], tier: str) -> list[list[int]]:
    seqs: list[list[int]] = [[block_id] for block_id in shortlist]
    if len(shortlist) >= 2:
        seqs.append(shortlist[:2])
        seqs.append(list(reversed(shortlist[:2])))
    if len(shortlist) >= 3 and tier in {"long", "very_long"}:
        seqs.append([shortlist[0], shortlist[2]])
        seqs.append([shortlist[1], shortlist[0]])

    unique: list[list[int]] = []
    seen = set()
    for seq in seqs:
        key = tuple(seq)
        if key not in seen:
            unique.append(seq)
            seen.add(key)
    return unique


def _crossbay_single_reinsert(
    prob_info: dict,
    assignments: dict[int, dict],
    block_id: int,
    *,
    max_positions: int,
    deadline: float,
) -> tuple[dict[int, dict] | None, tuple[int, int] | None]:
    previous = assignments.get(block_id)
    if previous is None:
        return None, None
    previous_bay = int(previous["bay_id"])
    candidate = v080._quantile_single_reinsert(
        prob_info,
        assignments,
        block_id,
        max_positions=max_positions,
        deadline=deadline,
    )
    if candidate is None:
        return None, None
    moved = candidate.get(block_id)
    if moved is None:
        return None, None
    new_bay = int(moved["bay_id"])
    if new_bay == previous_bay:
        return None, None
    return candidate, (previous_bay, new_bay)


def _apply_crossbay_sequence(
    prob_info: dict,
    start_assignments: dict[int, dict],
    sequence: list[int],
    *,
    max_positions: int,
    deadline: float,
) -> tuple[dict[int, dict] | None, list[tuple[int, int, int]]]:
    current = dict(start_assignments)
    moved: list[tuple[int, int, int]] = []
    for block_id in sequence:
        if time.time() >= deadline:
            return None, moved
        candidate, bay_move = _crossbay_single_reinsert(
            prob_info,
            current,
            block_id,
            max_positions=max_positions,
            deadline=deadline,
        )
        if candidate is None or bay_move is None:
            return None, moved
        current = candidate
        moved.append((block_id, bay_move[0], bay_move[1]))
    return current, moved


def _try_crossbay_postpass(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict, list[tuple[list[int], list[tuple[int, int, int]], float, float]]]:
    budget = _postpass_budget(remaining, tier, len(prob_info.get("blocks", [])))
    if budget <= 0.0:
        return base_solution, base_result, []

    deadline = time.time() + budget
    base_assignments = v186.v064._solution_to_assignments(base_solution)
    shortlist = v186._family_a_tardy_shortlist(prob_info, base_assignments, 3)
    sequences = _sequence_candidates(shortlist, tier)

    best_solution = base_solution
    best_result = base_result
    attempted: list[tuple[list[int], list[tuple[int, int, int]], float, float]] = []

    for sequence in sequences:
        if time.time() >= deadline:
            break
        candidate_assignments, moved = _apply_crossbay_sequence(
            prob_info,
            base_assignments,
            sequence,
            max_positions=_max_positions(tier),
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

    base_solution = v195.algorithm(prob_info, timelimit)
    base_result = v186.v001.check_feasibility(prob_info, base_solution)
    features = v186._selector_features(prob_info)
    tier = v186.v169._time_tier(timelimit)

    if (
        not base_result.get("feasible")
        or not v186._matches_family_a_tightslack(features)
        or not _allow_crossbay_track(features)
        or float(base_result.get("obj1") or 0.0) <= 0.0
        or tier in {"very_short", "short"}
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    reserve = v186._dynamic_reserve(timelimit)
    spendable = remaining - reserve
    if spendable <= 1.0:
        print(
            f"[baseline_hh reboot_v197] skip_trackA_crossbay instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result, attempted = _try_crossbay_postpass(
        prob_info,
        base_solution,
        base_result,
        spendable,
        tier,
    )
    print(
        f"[baseline_hh reboot_v197] trackA_crossbay instance={prob_info.get('name')} "
        f"tier={tier} base_T={base_result.get('obj1')} best_T={best_result.get('obj1')} "
        f"attempted={attempted}"
    )
    if v186.v064._result_key(best_result) < v186.v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v197] selected_trackA_crossbay instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution
    return base_solution
