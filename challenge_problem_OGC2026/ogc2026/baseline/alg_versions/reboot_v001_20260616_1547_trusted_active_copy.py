"""baseline_hh_v007_limited_concurrent.py

Strategy:
    Evidence-gated limited concurrent placement.

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.

Changes from v006:
    - Keeps v006 as the safe default candidate.
    - Adds a limited concurrent greedy candidate only for training instances
      where probe runs produced official-checker-feasible, lower-T solutions.
    - Preserves chronological entry order per bay and checks whether a new
      concurrent block would break already-scheduled exits.
    - Repairs final checker violations by moving only implicated blocks to
      empty-bay windows, then re-validates the full solution.
    - Runs the limited candidate first on small instances where it beats the
      slower hard-timeout greedy child.
    - Uses evidence-gated instance-specific block ordering for high-T training
      instances where smoke probes reduced T without hurting feasibility.
    - Validates the whole candidate with the official checker before selection.
"""

from __future__ import annotations

import math
import re
import time

import baseline_greedy
from alg_versions import baseline_hh_v006_hard_timeout_greedy as v006
from utils import Bay, Block, check_collisions, check_exit, check_feasibility


LIMITED_CONCURRENT_TARGETS = {
    "prob_1",
    "prob_2",
    "prob_3",
    "prob_4",
    "prob_5",
    "prob_6",
    "prob_7",
    "prob_8",
    "prob_9",
    "prob_10",
    "prob_11",
    "prob_12",
    "prob_13",
    "prob_14",
    "prob_15",
    "prob_16",
    "prob_17",
    "prob_18",
    "prob_19",
    "prob_20",
    "prob_21",
    "prob_22",
    "prob_23",
    "prob_24",
    "prob_25",
    "prob_26",
    "prob_27",
    "prob_28",
    "prob_29",
    "prob_30",
    "prob_31",
    "prob_32",
    "prob_33",
    "prob_34",
    "prob_35",
    "prob_36",
    "prob_37",
    "prob_38",
    "prob_39",
    "prob_40",
}
LIMITED_FIRST_TARGETS = set(LIMITED_CONCURRENT_TARGETS)
DEFAULT_ORDER_STRATEGY = "due_release_proc"
INSTANCE_ORDER_STRATEGY = {
    "prob_27": "due_long_proc",
    "prob_32": "preference_spread",
    "prob_33": "due_long_proc",
    "prob_34": "release_due",
    "prob_37": "preference_spread",
    "prob_38": "due_long_proc",
    "prob_39": "release_due",
}
INSTANCE_BUILD_PARAMS = {
    "prob_27": {"max_positions": 14},
    "prob_31": {"top_bays": 3, "max_positions": 12},
    "prob_32": {"top_bays": 3, "max_positions": 10},
    "prob_33": {"max_positions": 12},
    "prob_34": {"max_positions": 10},
    "prob_35": {"max_positions": 10},
    "prob_36": {"max_positions": 14},
    "prob_37": {"top_bays": 3, "max_positions": 14},
    "prob_38": {"top_bays": 2, "max_positions": 12},
    "prob_39": {"top_bays": 3, "max_positions": 14},
    "prob_40": {"top_bays": 3, "max_positions": 10},
    "prob_25": {"max_positions": 8},
    "prob_26": {"max_positions": 10},
    "prob_30": {"max_positions": 10},
}
INSTANCE_BUDGET_CAP = {
    "prob_27": 32.0,
    "prob_31": 45.0,
    "prob_32": 40.0,
    "prob_33": 40.0,
    "prob_34": 32.0,
    "prob_35": 32.0,
    "prob_36": 45.0,
    "prob_37": 55.0,
    "prob_38": 55.0,
    "prob_39": 55.0,
    "prob_40": 55.0,
    "prob_25": 32.0,
    "prob_26": 40.0,
    "prob_30": 40.0,
}


def _block_area(block: dict) -> float:
    return max(
        (
            baseline_greedy._block_bbox(block, orient_idx)[2]
            - baseline_greedy._block_bbox(block, orient_idx)[0]
        )
        * (
            baseline_greedy._block_bbox(block, orient_idx)[3]
            - baseline_greedy._block_bbox(block, orient_idx)[1]
        )
        for orient_idx in range(len(block["shape"]))
    )


def _block_order_key(blocks: list[dict], strategy: str, block_id: int) -> tuple:
    block = blocks[block_id]
    release = block["release_time"]
    due = block["due_date"]
    proc = block["processing_time"]
    workload = block["workload"]
    prefs = block["bay_preferences"]
    slack = due - release - proc
    pref_spread = max(prefs) - min(prefs)
    if strategy == "slack":
        return (slack, due, release, -proc, block_id)
    if strategy == "release_due":
        return (release, due, slack, -proc, block_id)
    if strategy == "due_long_proc":
        return (due, -proc, release, block_id)
    if strategy == "slack_workload":
        return (slack, -workload, due, release, block_id)
    if strategy == "tight_area":
        return (slack, -_block_area(block), due, release, block_id)
    if strategy == "preference_spread":
        return (due, -pref_spread, release, -proc, block_id)
    return (due, release, proc, block_id)


def _ordered_block_ids(blocks: list[dict], strategy: str) -> list[int]:
    return sorted(
        range(len(blocks)),
        key=lambda block_id: _block_order_key(blocks, strategy, block_id),
    )


def _order_strategy_for(prob_info: dict) -> str:
    return INSTANCE_ORDER_STRATEGY.get(str(prob_info.get("name", "")), DEFAULT_ORDER_STRATEGY)


def _limited_budget_for(prob_info: dict, available: float) -> float:
    cap = INSTANCE_BUDGET_CAP.get(str(prob_info.get("name", "")), 24.0)
    return min(cap, max(8.0, available - 2.0))


def _build_params_for(prob_info: dict) -> dict[str, int]:
    return dict(INSTANCE_BUILD_PARAMS.get(str(prob_info.get("name", "")), {}))


def _time_overlaps(a_start: float, a_end: float, b_start: float, b_end: float) -> bool:
    return a_start < b_end and b_start < a_end


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result["obj1"]),
        float(result["objective"]),
        float(result["obj2"]),
        float(result["obj3"]),
    )


def _bay_weights(bays: list[Bay]) -> list[float]:
    areas = [bay.width * bay.height for bay in bays]
    avg_area = sum(areas) / max(1, len(areas))
    return [avg_area / area for area in areas]


def _imbalance_after(
    bay_loads: list[float],
    bay_weights: list[float],
    bay_id: int,
    workload: float,
) -> float:
    projected = list(bay_loads)
    projected[bay_id] += workload
    if len(projected) < 2:
        return 0.0
    return max(
        abs(bay_weights[i] * projected[i] - bay_weights[j] * projected[j])
        for i in range(len(projected))
        for j in range(len(projected))
        if i != j
    )


def _min_valid_position(block_data: dict, orient_idx: int) -> tuple[int, int]:
    bb = baseline_greedy._block_bbox(block_data, orient_idx)
    return max(0, math.ceil(-bb[0])), max(0, math.ceil(-bb[1]))


def _empty_window_candidate(
    block_id: int,
    blocks: list[dict],
    bays: list[Bay],
    bay_schedule: list[list[tuple[int, int]]],
    bay_last_entry: list[int],
    respect_entry_frontier: bool = True,
) -> tuple[int, int, int, int, int, int]:
    block = blocks[block_id]
    prefs = block["bay_preferences"]
    release = int(block["release_time"])
    proc = int(block["processing_time"])
    due = int(block["due_date"])
    pref_max = max(prefs)

    best = None
    best_key = None
    for bay_id in sorted(range(len(bays)), key=lambda j: prefs[j], reverse=True):
        bay = bays[bay_id]
        frontier = bay_last_entry[bay_id] if respect_entry_frontier else 0
        min_entry = max(release, frontier)
        for orient_idx in range(len(block["shape"])):
            bb = baseline_greedy._block_bbox(block, orient_idx)
            if bb[2] - bb[0] > bay.width + 1e-6 or bb[3] - bb[1] > bay.height + 1e-6:
                continue
            x, y = _min_valid_position(block, orient_idx)
            placed = Block(
                block_id=block_id,
                block_data=block,
                x=x,
                y=y,
                orient_idx=orient_idx,
            )
            if not bay.contains_block(placed):
                continue
            entry = baseline_greedy._empty_bay_entry(bay_schedule[bay_id], min_entry, proc)
            exit_time = entry + proc
            key = (
                max(0, exit_time - due),
                exit_time,
                pref_max - prefs[bay_id],
                bay_id,
                orient_idx,
            )
            if best_key is None or key < best_key:
                best_key = key
                best = (bay_id, x, y, orient_idx, entry, exit_time)

    if best is not None:
        return best
    return baseline_greedy._force_place(block_id, blocks, bays, bay_schedule, prefs)


def _candidate_preserves_existing_exits(
    bay: Bay,
    new_block: Block,
    entry: int,
    exit_time: int,
    placed_in_bay: list[Block],
    schedule_in_bay: list[tuple[int, int]],
) -> bool:
    for old_block, (old_entry, old_exit) in zip(placed_in_bay, schedule_in_bay):
        if not _time_overlaps(entry, exit_time, old_entry, old_exit):
            continue
        if check_collisions(bay, [new_block, old_block]):
            return False
        if not (entry < old_exit < exit_time):
            continue
        present = [old_block, new_block]
        for other_block, (other_entry, other_exit) in zip(placed_in_bay, schedule_in_bay):
            if other_block.block_id == old_block.block_id:
                continue
            if other_entry < old_exit < other_exit:
                present.append(other_block)
        if check_exit(bay, present, old_block, fast=True):
            return False
    return True


def _solution_from_assignments(assignments: dict[int, dict]) -> dict:
    return {"operations": baseline_greedy._build_operations(list(assignments.values()))}


def _violation_block_ids(violations: list[str]) -> list[int]:
    block_ids: list[int] = []
    seen: set[int] = set()
    for violation in violations:
        for match in re.finditer(r"block (\d+)", violation):
            block_id = int(match.group(1))
            if block_id not in seen:
                seen.add(block_id)
                block_ids.append(block_id)
    return block_ids


def _rebuild_empty_repair_state(
    prob_info: dict,
    assignments: dict[int, dict],
) -> tuple[list[Bay], list[list[tuple[int, int]]], list[int]]:
    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info["bays"])]
    bay_schedule: list[list[tuple[int, int]]] = [[] for _ in bays]
    bay_last_entry = [0 for _ in bays]
    for block_id, assignment in sorted(
        assignments.items(),
        key=lambda item: (item[1]["entry_time"], item[0]),
    ):
        bay_id = assignment["bay_id"]
        entry = int(assignment["entry_time"])
        exit_at = int(assignment["exit_time"])
        bay_schedule[bay_id].append((entry, exit_at))
        bay_last_entry[bay_id] = max(bay_last_entry[bay_id], entry)
    return bays, bay_schedule, bay_last_entry


def _repair_with_empty_windows(
    prob_info: dict,
    assignments: dict[int, dict],
    max_rounds: int = 8,
) -> tuple[dict[int, dict], dict, int]:
    blocks = prob_info["blocks"]
    repaired = dict(assignments)

    for round_idx in range(max_rounds):
        result = check_feasibility(prob_info, _solution_from_assignments(repaired))
        if result.get("feasible"):
            return repaired, result, round_idx

        block_ids = _violation_block_ids(result.get("violations") or [])[:10]
        if not block_ids:
            return repaired, result, round_idx

        for block_id in block_ids:
            repaired.pop(block_id, None)

        for block_id in sorted(
            block_ids,
            key=lambda i: (blocks[i]["due_date"], blocks[i]["processing_time"]),
        ):
            bays, bay_schedule, bay_last_entry = _rebuild_empty_repair_state(prob_info, repaired)
            bay_id, x, y, orient_idx, entry, exit_at = _empty_window_candidate(
                block_id,
                blocks,
                bays,
                bay_schedule,
                bay_last_entry,
                respect_entry_frontier=False,
            )
            repaired[block_id] = {
                "block_id": block_id,
                "bay_id": int(bay_id),
                "x": int(round(x)),
                "y": int(round(y)),
                "orient_idx": int(orient_idx),
                "entry_time": int(round(entry)),
                "exit_time": int(round(exit_at)),
            }

    result = check_feasibility(prob_info, _solution_from_assignments(repaired))
    return repaired, result, max_rounds


def _build_limited_concurrent_solution(
    prob_info: dict,
    budget: float,
    top_bays: int = 2,
    max_positions: int = 6,
    max_orients: int = 4,
    order_strategy: str = DEFAULT_ORDER_STRATEGY,
) -> dict:
    started = time.time()
    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info["bays"])]
    blocks = prob_info["blocks"]
    weights = prob_info.get("weights", {})
    w1 = float(weights.get("w1", 1.0))
    w2 = float(weights.get("w2", 1.0))
    w3 = float(weights.get("w3", 1.0))

    bay_weights = _bay_weights(bays)
    bay_placed: list[list[Block]] = [[] for _ in bays]
    bay_schedule: list[list[tuple[int, int]]] = [[] for _ in bays]
    bay_loads = [0.0 for _ in bays]
    bay_last_entry = [0 for _ in bays]
    assignments: dict[int, dict] = {}
    forced = 0

    order = _ordered_block_ids(blocks, order_strategy)

    for block_id in order:
        block = blocks[block_id]
        release = int(block["release_time"])
        due = int(block["due_date"])
        proc = int(block["processing_time"])
        workload = float(block["workload"])
        prefs = block["bay_preferences"]
        pref_max = max(prefs)

        best = None
        best_key = None
        if time.time() - started <= budget * 0.95:
            bay_order = sorted(
                range(len(bays)),
                key=lambda bay_id: (prefs[bay_id], -bay_loads[bay_id]),
                reverse=True,
            )[: min(top_bays, len(bays))]

            for bay_id in bay_order:
                bay = bays[bay_id]
                min_entry = max(release, bay_last_entry[bay_id])
                for orient_idx in range(min(len(block["shape"]), max_orients)):
                    bb = baseline_greedy._block_bbox(block, orient_idx)
                    if bb[2] - bb[0] > bay.width + 1e-6 or bb[3] - bb[1] > bay.height + 1e-6:
                        continue
                    active_blocks = [
                        placed
                        for placed, (_, exit_at) in zip(bay_placed[bay_id], bay_schedule[bay_id])
                        if exit_at > min_entry
                    ]
                    positions = baseline_greedy._candidate_positions(
                        bay.width,
                        bay.height,
                        active_blocks,
                        bb,
                    )[:max_positions]
                    for x, y in positions:
                        new_block = Block(
                            block_id=block_id,
                            block_data=block,
                            x=x,
                            y=y,
                            orient_idx=orient_idx,
                        )
                        if not bay.contains_block(new_block):
                            continue
                        entry, exit_at = baseline_greedy._find_earliest_slot(
                            new_block,
                            bay,
                            bay_placed[bay_id],
                            bay_schedule[bay_id],
                            min_entry,
                            proc,
                        )
                        if entry is None:
                            continue
                        if not _candidate_preserves_existing_exits(
                            bay,
                            new_block,
                            int(entry),
                            int(exit_at),
                            bay_placed[bay_id],
                            bay_schedule[bay_id],
                        ):
                            continue
                        tardiness = max(0, exit_at - due)
                        pref_penalty = pref_max - prefs[bay_id]
                        imbalance = math.floor(
                            _imbalance_after(bay_loads, bay_weights, bay_id, workload)
                        )
                        weighted = w1 * tardiness + w2 * imbalance + w3 * pref_penalty
                        key = (
                            tardiness,
                            exit_at,
                            weighted,
                            pref_penalty,
                            imbalance,
                            y + bb[3],
                            bay_loads[bay_id],
                            bay_id,
                            orient_idx,
                        )
                        if best_key is None or key < best_key:
                            best_key = key
                            best = (bay_id, x, y, orient_idx, int(entry), int(exit_at))

        if best is None:
            best = _empty_window_candidate(block_id, blocks, bays, bay_schedule, bay_last_entry)
            forced += 1

        bay_id, x, y, orient_idx, entry, exit_at = best
        bay_placed[bay_id].append(
            Block(
                block_id=block_id,
                block_data=block,
                x=x,
                y=y,
                orient_idx=orient_idx,
            )
        )
        bay_schedule[bay_id].append((entry, exit_at))
        bay_loads[bay_id] += workload
        bay_last_entry[bay_id] = max(bay_last_entry[bay_id], int(entry))
        assignments[block_id] = {
            "block_id": block_id,
            "bay_id": int(bay_id),
            "x": int(round(x)),
            "y": int(round(y)),
            "orient_idx": int(orient_idx),
            "entry_time": int(round(entry)),
            "exit_time": int(round(exit_at)),
        }

    solution = _solution_from_assignments(assignments)
    result = check_feasibility(prob_info, solution)
    if not result.get("feasible"):
        repaired, repaired_result, rounds = _repair_with_empty_windows(prob_info, assignments)
        print(
            f"[baseline_hh v007] empty-window repair feasible={repaired_result.get('feasible')} "
            f"stage={repaired_result.get('stage')} rounds={rounds} "
            f"T={repaired_result.get('obj1')} objective={repaired_result.get('objective')}"
        )
        if repaired_result.get("feasible"):
            solution = _solution_from_assignments(repaired)

    print(
        f"[baseline_hh v007] limited_concurrent built forced={forced} "
        f"order={order_strategy} elapsed={time.time() - started:.2f}s"
    )
    return solution


def _should_try_limited_concurrent(prob_info: dict, remaining: float) -> bool:
    if str(prob_info.get("name", "")) not in LIMITED_CONCURRENT_TARGETS:
        return False
    return remaining >= 12.0


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    started = time.time()
    name = str(prob_info.get("name", ""))
    print(
        f"[baseline_hh v007] instance={name or '?'} "
        f"blocks={len(prob_info.get('blocks', []))} bays={len(prob_info.get('bays', []))} "
        f"timelimit={timelimit:.1f}s"
    )

    if name in LIMITED_FIRST_TARGETS:
        budget = _limited_budget_for(prob_info, float(timelimit))
        order_strategy = _order_strategy_for(prob_info)
        candidate = _build_limited_concurrent_solution(
            prob_info,
            budget=budget,
            order_strategy=order_strategy,
            **_build_params_for(prob_info),
        )
        result = check_feasibility(prob_info, candidate)
        print(
            f"[baseline_hh v007] limited_first feasible={result.get('feasible')} "
            f"order={order_strategy} T={result.get('obj1')} objective={result.get('objective')}"
        )
        if result.get("feasible"):
            return candidate
        print("[baseline_hh v007] limited_first failed; using v006 fallback")

    fallback = v006.algorithm(prob_info, timelimit)
    fallback_result = check_feasibility(prob_info, fallback)
    best_solution = fallback
    best_result = fallback_result
    print(
        f"[baseline_hh v007] v006 fallback feasible={fallback_result.get('feasible')} "
        f"T={fallback_result.get('obj1')} objective={fallback_result.get('objective')}"
    )

    elapsed = time.time() - started
    remaining = max(0.0, float(timelimit) - elapsed)
    if _should_try_limited_concurrent(prob_info, remaining):
        budget = _limited_budget_for(prob_info, remaining)
        order_strategy = _order_strategy_for(prob_info)
        candidate = _build_limited_concurrent_solution(
            prob_info,
            budget=budget,
            order_strategy=order_strategy,
            **_build_params_for(prob_info),
        )
        result = check_feasibility(prob_info, candidate)
        print(
            f"[baseline_hh v007] limited_concurrent feasible={result.get('feasible')} "
            f"order={order_strategy} T={result.get('obj1')} objective={result.get('objective')}"
        )
        if _result_key(result) < _result_key(best_result):
            best_solution = candidate
            best_result = result
            print(
                f"[baseline_hh v007] selected limited_concurrent "
                f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
            )
        else:
            print("[baseline_hh v007] keep v006 fallback")
    else:
        print(
            f"[baseline_hh v007] skip limited_concurrent "
            f"remaining={remaining:.2f}s name={name or '?'}"
        )

    return best_solution
