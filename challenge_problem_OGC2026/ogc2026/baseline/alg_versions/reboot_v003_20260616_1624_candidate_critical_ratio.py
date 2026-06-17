"""reboot_v003_20260616_1624_candidate_critical_ratio.py

Strategy:
    Long-job critical-ratio ordering on top of reboot v002.

Metadata:
    version_id: reboot_v003_20260616_1624_candidate_critical_ratio
    parent_version: reboot_v002_20260616_1547_candidate_slack_preference
    status: rejected
    timestamp: 2026-06-16 16:24 KST
    strategy: use critical-ratio ordering for long-processing, non
        preference-dominated instances.
    hypothesis: high-T long-job instances such as prob_38 have enough average
        slack that pure due/long-proc ordering can leave some long operations
        late; ordering by slack per processing time should reduce the tardy
        tail without increasing search width.
    intended_metric_target: reduce T and objective on long-job high-T cases
        while preserving accepted_for_score and timeout safety.
    validation_status: rejected after subset smoke; accepted_for_score passed
        but high-T target prob_38 regressed versus reboot_v002.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v003_subset_20260616_162542/
    rollback_target: reboot_v002_20260616_1547_candidate_slack_preference

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.

Changes from reboot_v002:
    - For long-processing instances that are not preference-dominated, use
      `critical_ratio` block ordering instead of `due_long_proc`.
    - No search-width, repair, fallback, or checker contract changes.
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
DEFAULT_POLICY = {
    "order_strategy": DEFAULT_ORDER_STRATEGY,
    "top_bays": 2,
    "max_positions": 6,
    "max_orients": 4,
    "budget_cap": 24.0,
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


def _instance_features(prob_info: dict) -> dict[str, float]:
    blocks = prob_info.get("blocks", [])
    bays = prob_info.get("bays", [])
    if not blocks:
        return {
            "n_blocks": 0.0,
            "n_bays": float(len(bays)),
            "avg_slack": 0.0,
            "tight_ratio": 0.0,
            "avg_proc": 0.0,
            "avg_pref_spread": 0.0,
            "pref_concentration": 0.0,
        }

    slacks = [
        float(block["due_date"] - block["release_time"] - block["processing_time"])
        for block in blocks
    ]
    procs = [float(block["processing_time"]) for block in blocks]
    pref_spreads = [
        float(max(block["bay_preferences"]) - min(block["bay_preferences"]))
        for block in blocks
    ]
    pref_counts = []
    for bay_id in range(len(bays)):
        pref_counts.append(
            sum(
                1
                for block in blocks
                if block["bay_preferences"][bay_id] == max(block["bay_preferences"])
            )
        )

    return {
        "n_blocks": float(len(blocks)),
        "n_bays": float(len(bays)),
        "avg_slack": sum(slacks) / len(slacks),
        "tight_ratio": sum(1 for slack in slacks if slack <= 0.0) / len(slacks),
        "avg_proc": sum(procs) / len(procs),
        "avg_pref_spread": sum(pref_spreads) / len(pref_spreads),
        "pref_concentration": (max(pref_counts) / len(blocks)) if pref_counts else 0.0,
    }


def _policy_for(prob_info: dict) -> dict:
    features = _instance_features(prob_info)
    policy = dict(DEFAULT_POLICY)

    tight_slack = features["avg_slack"] <= 1.4 or features["tight_ratio"] >= 0.32
    preference_pressure = (
        features["pref_concentration"] >= 0.70
        or features["avg_pref_spread"] >= 74.0
    )
    long_jobs = features["avg_proc"] >= 16.0
    runtime_risk = features["n_blocks"] >= 250.0

    if tight_slack:
        policy.update(
            order_strategy="slack_workload",
            max_positions=10,
            budget_cap=30.0,
        )
    elif long_jobs:
        policy.update(
            order_strategy="critical_ratio",
            max_positions=8,
            budget_cap=28.0,
        )

    if preference_pressure:
        policy.update(
            order_strategy="preference_critical" if tight_slack else "preference_spread",
            top_bays=2,
            max_positions=max(int(policy["max_positions"]), 8),
            budget_cap=max(float(policy["budget_cap"]), 30.0),
        )

    if runtime_risk:
        policy.update(
            max_positions=min(int(policy["max_positions"]), 8),
            budget_cap=min(float(policy["budget_cap"]), 28.0),
        )

    policy["features"] = features
    return policy


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
    if strategy == "preference_critical":
        return (slack, due, -pref_spread, -workload, release, block_id)
    if strategy == "critical_ratio":
        return (slack / max(1, proc), due, release, -proc, block_id)
    return (due, release, proc, block_id)


def _ordered_block_ids(blocks: list[dict], strategy: str) -> list[int]:
    return sorted(
        range(len(blocks)),
        key=lambda block_id: _block_order_key(blocks, strategy, block_id),
    )


def _order_strategy_for(prob_info: dict) -> str:
    return str(_policy_for(prob_info)["order_strategy"])


def _limited_budget_for(prob_info: dict, available: float) -> float:
    cap = float(_policy_for(prob_info)["budget_cap"])
    return min(cap, max(8.0, available - 2.0))


def _build_params_for(prob_info: dict) -> dict[str, int]:
    policy = _policy_for(prob_info)
    return {
        "top_bays": int(policy["top_bays"]),
        "max_positions": int(policy["max_positions"]),
        "max_orients": int(policy["max_orients"]),
    }


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
    features = _instance_features(prob_info)
    tight_pressure = features["avg_slack"] <= 1.4 or features["tight_ratio"] >= 0.32
    preference_pressure = (
        features["pref_concentration"] >= 0.70
        or features["avg_pref_spread"] >= 74.0
    )
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
                        if preference_pressure and not tight_pressure:
                            key = (
                                tardiness,
                                pref_penalty,
                                weighted,
                                exit_at,
                                imbalance,
                                y + bb[3],
                                bay_loads[bay_id],
                                bay_id,
                                orient_idx,
                            )
                        else:
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
            f"[baseline_hh reboot_v003] empty-window repair feasible={repaired_result.get('feasible')} "
            f"stage={repaired_result.get('stage')} rounds={rounds} "
            f"T={repaired_result.get('obj1')} objective={repaired_result.get('objective')}"
        )
        if repaired_result.get("feasible"):
            solution = _solution_from_assignments(repaired)

    print(
        f"[baseline_hh reboot_v003] limited_concurrent built forced={forced} "
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
    policy = _policy_for(prob_info)
    features = policy["features"]
    print(
        f"[baseline_hh reboot_v003] instance={name or '?'} "
        f"blocks={len(prob_info.get('blocks', []))} bays={len(prob_info.get('bays', []))} "
        f"timelimit={timelimit:.1f}s"
    )
    print(
        f"[baseline_hh reboot_v003] policy order={policy['order_strategy']} "
        f"top_bays={policy['top_bays']} max_positions={policy['max_positions']} "
        f"budget_cap={policy['budget_cap']} avg_slack={features['avg_slack']:.2f} "
        f"tight_ratio={features['tight_ratio']:.2f} pref_conc={features['pref_concentration']:.2f}"
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
            f"[baseline_hh reboot_v003] limited_first feasible={result.get('feasible')} "
            f"order={order_strategy} T={result.get('obj1')} objective={result.get('objective')}"
        )
        if result.get("feasible"):
            return candidate
        print("[baseline_hh reboot_v003] limited_first failed; using v006 fallback")

    fallback = v006.algorithm(prob_info, timelimit)
    fallback_result = check_feasibility(prob_info, fallback)
    best_solution = fallback
    best_result = fallback_result
    print(
        f"[baseline_hh reboot_v003] v006 fallback feasible={fallback_result.get('feasible')} "
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
            f"[baseline_hh reboot_v003] limited_concurrent feasible={result.get('feasible')} "
            f"order={order_strategy} T={result.get('obj1')} objective={result.get('objective')}"
        )
        if _result_key(result) < _result_key(best_result):
            best_solution = candidate
            best_result = result
            print(
                f"[baseline_hh reboot_v003] selected limited_concurrent "
                f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
            )
        else:
            print("[baseline_hh reboot_v003] keep v006 fallback")
    else:
        print(
            f"[baseline_hh reboot_v003] skip limited_concurrent "
            f"remaining={remaining:.2f}s name={name or '?'}"
        )

    return best_solution
