"""reboot_v194_20260626_familyA_fourbay_inline_on_v186.py

Strategy:
    Keep trusted v186 as the active surface and add a narrow 4-bay inline
    tardy-order postpass inside that same surface.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186


ACTIVE_VERSION = "reboot_v194_20260626_familyA_fourbay_inline_on_v186"


def _allow_fourbay_inline(features: dict[str, float]) -> bool:
    bays = int(features.get("bays", 0))
    blocks = int(features.get("blocks", 0))
    return bays == 4 and 180 <= blocks <= 320


def _postpass_budget(remaining: float, tier: str, block_count: int) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 4.0,
        "long": 6.0,
        "very_long": 8.0,
    }[tier]
    if block_count >= 240:
        cap += 1.0
    return min(cap, remaining)


def _moves_per_round(tier: str) -> int:
    return {
        "standard": 2,
        "long": 3,
        "very_long": 4,
    }[tier]


def _group_bay_sequences(assignments: dict[int, dict]) -> dict[int, list[int]]:
    grouped: dict[int, list[tuple[int, int]]] = {}
    for block_id, assignment in assignments.items():
        bay_id = int(assignment["bay_id"])
        grouped.setdefault(bay_id, []).append((int(assignment["entry_time"]), block_id))
    return {
        bay_id: [block_id for _, block_id in sorted(items)]
        for bay_id, items in grouped.items()
    }


def _replay_with_fixed_layout(
    prob_info: dict,
    assignments: dict[int, dict],
    bay_sequences: dict[int, list[int]],
) -> dict[int, dict] | None:
    bays = [v186.v001.Bay.from_dict(data, idx) for idx, data in enumerate(prob_info["bays"])]
    blocks = prob_info["blocks"]
    rebuilt: dict[int, dict] = {}

    for bay_id, sequence in bay_sequences.items():
        placed_in_bay: list[v186.v001.Block] = []
        schedule_in_bay: list[tuple[int, int]] = []
        bay = bays[bay_id]

        for block_id in sequence:
            prev = assignments[block_id]
            block_data = blocks[block_id]
            placed = v186.v001.Block(
                block_id=block_id,
                block_data=block_data,
                x=int(prev["x"]),
                y=int(prev["y"]),
                orient_idx=int(prev["orient_idx"]),
            )
            if not bay.contains_block(placed):
                return None

            entry, exit_time = v186.v001.baseline_greedy._find_earliest_slot(
                placed,
                bay,
                placed_in_bay,
                schedule_in_bay,
                int(block_data["release_time"]),
                int(block_data["processing_time"]),
            )
            if entry is None:
                return None

            placed_in_bay.append(placed)
            schedule_in_bay.append((int(entry), int(exit_time)))
            rebuilt[block_id] = {
                "block_id": block_id,
                "bay_id": bay_id,
                "x": int(prev["x"]),
                "y": int(prev["y"]),
                "orient_idx": int(prev["orient_idx"]),
                "entry_time": int(entry),
                "exit_time": int(exit_time),
            }

    if len(rebuilt) != len(assignments):
        return None
    return rebuilt


def _candidate_sequences(
    prob_info: dict,
    assignments: dict[int, dict],
    shortlist: list[int],
) -> list[tuple[int, list[int]]]:
    sequences = _group_bay_sequences(assignments)
    candidates: list[tuple[int, list[int]]] = []
    seen: set[tuple[int, tuple[int, ...]]] = set()

    for block_id in shortlist:
        assignment = assignments.get(block_id)
        if assignment is None:
            continue
        bay_id = int(assignment["bay_id"])
        sequence = list(sequences.get(bay_id, []))
        if block_id not in sequence:
            continue
        idx = sequence.index(block_id)
        if idx <= 0:
            continue

        for jump in (1, 2):
            target_idx = max(0, idx - jump)
            if target_idx == idx:
                continue
            moved = list(sequence)
            moved.pop(idx)
            moved.insert(target_idx, block_id)
            key = (bay_id, tuple(moved))
            if key in seen:
                continue
            seen.add(key)
            candidates.append((bay_id, moved))

    return candidates


def _try_inline_postpass(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict, list[tuple[int, float, float]]]:
    budget = _postpass_budget(remaining, tier, len(prob_info.get("blocks", [])))
    if budget <= 0.0:
        return base_solution, base_result, []

    deadline = time.time() + budget
    best_solution = base_solution
    best_result = base_result
    accepted_moves: list[tuple[int, float, float]] = []

    for _ in range(_moves_per_round(tier)):
        if time.time() >= deadline:
            break

        base_assignments = v186.v064._solution_to_assignments(best_solution)
        shortlist = v186._family_a_tardy_shortlist(prob_info, base_assignments, 4)
        candidates = _candidate_sequences(prob_info, base_assignments, shortlist)
        if not candidates:
            break

        improved = False
        for bay_id, moved_sequence in candidates:
            if time.time() >= deadline:
                break
            bay_sequences = _group_bay_sequences(base_assignments)
            bay_sequences[bay_id] = moved_sequence
            candidate_assignments = _replay_with_fixed_layout(
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
                moved_block_id = moved_sequence[0]
                accepted_moves.append(
                    (
                        moved_block_id,
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

    base_solution = v186.algorithm(prob_info, timelimit)
    base_result = v186.v001.check_feasibility(prob_info, base_solution)
    features = v186._selector_features(prob_info)
    tier = v186.v169._time_tier(timelimit)

    if (
        not base_result.get("feasible")
        or not v186._matches_family_a_tightslack(features)
        or not _allow_fourbay_inline(features)
        or float(base_result.get("obj1") or 0.0) <= 0.0
        or tier in {"very_short", "short"}
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    reserve = v186._dynamic_reserve(timelimit)
    spendable = remaining - reserve
    if spendable <= 1.0:
        print(
            f"[baseline_hh reboot_v194] skip_familyA_fourbay_inline instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result, accepted_moves = _try_inline_postpass(
        prob_info,
        base_solution,
        base_result,
        spendable,
        tier,
    )
    print(
        f"[baseline_hh reboot_v194] familyA_fourbay_inline instance={prob_info.get('name')} "
        f"tier={tier} base_T={base_result.get('obj1')} best_T={best_result.get('obj1')} "
        f"accepted_moves={accepted_moves}"
    )
    if v186.v064._result_key(best_result) < v186.v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v194] selected_familyA_fourbay_inline instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution
    return base_solution
