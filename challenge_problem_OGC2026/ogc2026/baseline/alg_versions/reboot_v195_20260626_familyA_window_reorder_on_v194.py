"""reboot_v195_20260626_familyA_window_reorder_on_v194.py

Strategy:
    Keep trusted v194 as the active fallback surface and add a bounded same-bay
    tardy-window local reorder pass for 4~5 bay Family A rows.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
from alg_versions import reboot_v194_20260626_familyA_fourbay_inline_on_v186 as v194


ACTIVE_VERSION = "reboot_v195_20260626_familyA_window_reorder_on_v194"


def _allow_window_reorder(features: dict[str, float]) -> bool:
    bays = int(features.get("bays", 0))
    blocks = int(features.get("blocks", 0))
    return 4 <= bays <= 5 and 180 <= blocks <= 320


def _postpass_budget(remaining: float, tier: str, block_count: int, bays: int) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 4.5,
        "long": 6.5,
        "very_long": 8.5,
    }[tier]
    if block_count >= 240:
        cap += 1.0
    if bays >= 5:
        cap += 0.5
    return min(cap, remaining)


def _rounds_per_tier(tier: str) -> int:
    return {
        "standard": 2,
        "long": 3,
        "very_long": 4,
    }[tier]


def _block_meta(prob_info: dict, block_id: int) -> tuple[int, int, int, float]:
    block = prob_info["blocks"][block_id]
    due = int(block["due_date"])
    release = int(block["release_time"])
    proc = max(1, int(block["processing_time"]))
    slack = due - release - proc
    critical_ratio = (due - release) / proc
    return due, release, proc, float(slack), float(critical_ratio)


def _window_variants(
    prob_info: dict,
    sequence: list[int],
    target_idx: int,
) -> list[list[int]]:
    start = max(0, target_idx - 2)
    end = min(len(sequence), target_idx + 3)
    base_window = sequence[start:end]
    if len(base_window) < 2:
        return []

    variants: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()

    def add_window(window: list[int]) -> None:
        key = tuple(window)
        if key == tuple(base_window) or key in seen:
            return
        seen.add(key)
        candidate = list(sequence)
        candidate[start:end] = window
        variants.append(candidate)

    local_idx = target_idx - start
    if local_idx > 0:
        swapped = list(base_window)
        swapped[local_idx - 1], swapped[local_idx] = swapped[local_idx], swapped[local_idx - 1]
        add_window(swapped)
    if local_idx + 1 < len(base_window):
        swapped = list(base_window)
        swapped[local_idx], swapped[local_idx + 1] = swapped[local_idx + 1], swapped[local_idx]
        add_window(swapped)

    add_window(sorted(base_window, key=lambda bid: _block_meta(prob_info, bid)[0:3]))
    add_window(sorted(base_window, key=lambda bid: (_block_meta(prob_info, bid)[3],) + _block_meta(prob_info, bid)[0:3]))
    add_window(sorted(base_window, key=lambda bid: (_block_meta(prob_info, bid)[4],) + _block_meta(prob_info, bid)[0:3]))

    target_block = sequence[target_idx]
    if target_block in base_window:
        moved_front = [target_block] + [bid for bid in base_window if bid != target_block]
        add_window(moved_front)

    return variants


def _candidate_sequences(
    prob_info: dict,
    assignments: dict[int, dict],
    shortlist: list[int],
) -> list[tuple[int, list[int], int]]:
    grouped = v194._group_bay_sequences(assignments)
    candidates: list[tuple[int, list[int], int]] = []
    seen: set[tuple[int, tuple[int, ...]]] = set()

    for block_id in shortlist:
        assignment = assignments.get(block_id)
        if assignment is None:
            continue
        bay_id = int(assignment["bay_id"])
        sequence = grouped.get(bay_id, [])
        if block_id not in sequence:
            continue
        target_idx = sequence.index(block_id)
        for variant in _window_variants(prob_info, sequence, target_idx):
            key = (bay_id, tuple(variant))
            if key in seen:
                continue
            seen.add(key)
            candidates.append((bay_id, variant, block_id))
    return candidates


def _try_window_reorder(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
    features: dict[str, float],
) -> tuple[dict, dict, list[tuple[int, float, float]]]:
    budget = _postpass_budget(
        remaining,
        tier,
        int(features.get("blocks", 0)),
        int(features.get("bays", 0)),
    )
    if budget <= 0.0:
        return base_solution, base_result, []

    deadline = time.time() + budget
    best_solution = base_solution
    best_result = base_result
    accepted_moves: list[tuple[int, float, float]] = []

    for _ in range(_rounds_per_tier(tier)):
        if time.time() >= deadline:
            break

        base_assignments = v186.v064._solution_to_assignments(best_solution)
        shortlist = v186._family_a_tardy_shortlist(prob_info, base_assignments, 5)
        candidates = _candidate_sequences(prob_info, base_assignments, shortlist)
        if not candidates:
            break

        improved = False
        for bay_id, moved_sequence, focus_block_id in candidates:
            if time.time() >= deadline:
                break
            bay_sequences = v194._group_bay_sequences(base_assignments)
            bay_sequences[bay_id] = moved_sequence
            candidate_assignments = v194._replay_with_fixed_layout(
                prob_info,
                base_assignments,
                bay_sequences,
            )
            if candidate_assignments is None:
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

            if v186.v064._result_key(candidate_result) < v186.v064._result_key(best_result):
                best_solution = candidate_solution
                best_result = candidate_result
                accepted_moves.append(
                    (
                        focus_block_id,
                        float(best_result.get("obj1") or 0.0),
                        float(best_result.get("objective") or 0.0),
                    )
                )
                improved = True
                break

        if not improved:
            break

    return best_solution, best_result, accepted_moves


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    started = time.time()

    base_solution = v194.algorithm(prob_info, timelimit)
    base_result = v186.v001.check_feasibility(prob_info, base_solution)
    features = v186._selector_features(prob_info)
    tier = v186.v169._time_tier(timelimit)

    if (
        not base_result.get("feasible")
        or not v186._matches_family_a_tightslack(features)
        or not _allow_window_reorder(features)
        or float(base_result.get("obj1") or 0.0) <= 0.0
        or tier in {"very_short", "short"}
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    reserve = v186._dynamic_reserve(timelimit)
    spendable = remaining - reserve
    if spendable <= 1.0:
        print(
            f"[baseline_hh reboot_v195] skip_familyA_window_reorder instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result, accepted_moves = _try_window_reorder(
        prob_info,
        base_solution,
        base_result,
        spendable,
        tier,
        features,
    )
    print(
        f"[baseline_hh reboot_v195] familyA_window_reorder instance={prob_info.get('name')} "
        f"tier={tier} base_T={base_result.get('obj1')} best_T={best_result.get('obj1')} "
        f"accepted_moves={accepted_moves}"
    )
    if v186.v064._result_key(best_result) < v186.v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v195] selected_familyA_window_reorder instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution
    return base_solution
