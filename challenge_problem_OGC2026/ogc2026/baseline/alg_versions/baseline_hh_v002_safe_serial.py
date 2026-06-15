"""baseline_hh_v002_safe_serial.py

Strategy:
    Deadline-safe serial scheduling with objective-aware bay selection.

Changes from v001:
    - Removes the uninterruptible full greedy call that caused subprocess
      timeouts before a fallback could be returned.
    - Keeps the robust empty-bay interval property: each bay processes at most
      one block at a time, so crane entry/exit and spatial collisions are
      structurally avoided.
    - Improves over the official serial fallback by evaluating all fitting bays
      for each block and choosing the lowest incremental objective estimate
      instead of always using the highest-preference bay.

Expected strengths:
    Very high feasibility and strict runtime stability across all training
    instances.

Expected weaknesses:
    No concurrent stacking inside a bay, so objective quality is still limited
    compared with successful full greedy/local-search methods.
"""

from __future__ import annotations

import math
import time

import baseline_greedy
from utils import Bay, Block, check_feasibility


def _min_valid_position(block_data: dict, orient_idx: int) -> tuple[int, int]:
    bb = baseline_greedy._block_bbox(block_data, orient_idx)
    return max(0, math.ceil(-bb[0])), max(0, math.ceil(-bb[1]))


def _fits_at_min_position(bay: Bay, block_data: dict, block_id: int, orient_idx: int) -> tuple[bool, int, int]:
    width, height = baseline_greedy._block_size(block_data, orient_idx)
    if width > bay.width + 1e-6 or height > bay.height + 1e-6:
        return False, 0, 0
    x, y = _min_valid_position(block_data, orient_idx)
    placed = Block(block_id=block_id, block_data=block_data, x=x, y=y, orient_idx=orient_idx)
    return bay.contains_block(placed), x, y


def _imbalance_after(bay_loads: list[float], bay_weights: list[float], bay_id: int, workload: float) -> float:
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


def _build_safe_serial_solution(prob_info: dict) -> dict:
    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info["bays"])]
    blocks = prob_info["blocks"]
    n_bays = len(bays)

    w1 = prob_info.get("weights", {}).get("w1", 1.0)
    w2 = prob_info.get("weights", {}).get("w2", 1.0)
    w3 = prob_info.get("weights", {}).get("w3", 1.0)

    bay_areas = [bay.width * bay.height for bay in bays]
    avg_area = sum(bay_areas) / max(1, n_bays)
    bay_weights = [avg_area / area for area in bay_areas]

    bay_schedule: list[list[tuple[int, int]]] = [[] for _ in range(n_bays)]
    bay_loads = [0.0 for _ in range(n_bays)]
    assignments: dict[int, dict] = {}

    order = sorted(
        range(len(blocks)),
        key=lambda i: (
            blocks[i]["due_date"],
            blocks[i]["release_time"],
            blocks[i]["processing_time"],
            -max(blocks[i]["bay_preferences"]),
        ),
    )

    for block_id in order:
        block = blocks[block_id]
        release = int(block["release_time"])
        proc = int(block["processing_time"])
        due = int(block["due_date"])
        workload = float(block["workload"])
        prefs = block["bay_preferences"]
        pref_max = max(prefs)

        best = None
        best_key = None

        for bay_id, bay in enumerate(bays):
            pref_penalty = pref_max - prefs[bay_id]
            for orient_idx in range(len(block["shape"])):
                fits, x, y = _fits_at_min_position(bay, block, block_id, orient_idx)
                if not fits:
                    continue
                entry = baseline_greedy._empty_bay_entry(bay_schedule[bay_id], release, proc)
                exit_time = entry + proc
                tardiness = max(0, exit_time - due)
                imbalance = _imbalance_after(bay_loads, bay_weights, bay_id, workload)
                score = w1 * tardiness + w2 * math.floor(imbalance) + w3 * pref_penalty
                key = (
                    score,
                    tardiness,
                    pref_penalty,
                    exit_time,
                    bay_loads[bay_id],
                    bay_id,
                    orient_idx,
                )
                if best_key is None or key < best_key:
                    best_key = key
                    best = (bay_id, x, y, orient_idx, entry, exit_time)

        if best is None:
            best = baseline_greedy._force_place(block_id, blocks, bays, bay_schedule, prefs)

        bay_id, x, y, orient_idx, entry, exit_time = best
        bay_schedule[bay_id].append((entry, exit_time))
        bay_loads[bay_id] += workload
        assignments[block_id] = {
            "block_id": block_id,
            "bay_id": int(bay_id),
            "x": int(round(x)),
            "y": int(round(y)),
            "orient_idx": int(orient_idx),
            "entry_time": int(round(entry)),
            "exit_time": int(round(exit_time)),
        }

    return {"operations": baseline_greedy._build_operations(list(assignments.values()))}


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    started = time.time()
    print(
        f"[baseline_hh v002] instance={prob_info.get('name', '?')} "
        f"blocks={len(prob_info.get('blocks', []))} bays={len(prob_info.get('bays', []))} "
        f"timelimit={timelimit:.1f}s"
    )

    solution = _build_safe_serial_solution(prob_info)
    result = check_feasibility(prob_info, solution)
    if result["feasible"]:
        print(
            f"[baseline_hh v002] safe_serial PASS obj={result['objective']:.2f} "
            f"elapsed={time.time() - started:.2f}s"
        )
        return solution

    print(f"[baseline_hh v002] safe_serial FAIL stage={result['stage']} -> official fallback")
    for violation in result.get("violations", [])[:3]:
        print(f"[baseline_hh v002]   {violation}")

    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info["bays"])]
    assignments = baseline_greedy._serial_empty_bay_fallback(prob_info, bays, prob_info["blocks"])
    fallback = {"operations": baseline_greedy._build_operations(list(assignments.values()))}
    fallback_result = check_feasibility(prob_info, fallback)
    print(
        f"[baseline_hh v002] fallback feasible={fallback_result['feasible']} "
        f"stage={fallback_result['stage']} elapsed={time.time() - started:.2f}s"
    )
    return fallback

