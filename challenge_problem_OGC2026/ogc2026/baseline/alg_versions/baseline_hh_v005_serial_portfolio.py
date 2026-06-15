"""baseline_hh_v005_serial_portfolio.py

Strategy:
    Multi-order safe-serial portfolio.

Changes from v003:
    - Keeps the empty-bay serial invariant: no two blocks overlap in the same
      bay, so crane entry/exit and spatial collisions remain structurally safe.
    - Generates several deterministic order/selection variants, ranks them by
      the official objective formula, then validates only the best few with the
      official checker.
    - Includes the official serial fallback candidate so feasibility is
      preserved even if an experimental serial variant is worse.

Expected strengths:
    May improve tardiness and workload balance over v003 without the timeout
    risk observed in v004's repaired-greedy experiment.

Expected weaknesses:
    Still cannot exploit concurrent occupancy within a bay, so it is a stable
    feasibility baseline rather than a deep packing/local-search solver.
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


def _bay_weights(bays: list[Bay]) -> list[float]:
    areas = [bay.width * bay.height for bay in bays]
    avg_area = sum(areas) / max(1, len(areas))
    return [avg_area / area for area in areas]


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


def _order_key(blocks: list[dict], name: str):
    if name == "official":
        return lambda i: (blocks[i]["due_date"], blocks[i]["processing_time"])
    if name == "edd_release":
        return lambda i: (
            blocks[i]["due_date"],
            blocks[i]["release_time"],
            blocks[i]["processing_time"],
            -max(blocks[i]["bay_preferences"]),
        )
    if name == "slack":
        return lambda i: (
            blocks[i]["due_date"] - blocks[i]["release_time"] - blocks[i]["processing_time"],
            blocks[i]["due_date"],
            blocks[i]["release_time"],
            blocks[i]["processing_time"],
        )
    if name == "release_due":
        return lambda i: (
            blocks[i]["release_time"],
            blocks[i]["due_date"],
            blocks[i]["processing_time"],
        )
    if name == "long_proc_due":
        return lambda i: (
            blocks[i]["due_date"],
            -blocks[i]["processing_time"],
            blocks[i]["release_time"],
        )
    if name == "workload_due":
        return lambda i: (
            blocks[i]["due_date"],
            -blocks[i]["workload"],
            blocks[i]["release_time"],
        )
    raise ValueError(f"unknown order: {name}")


def _candidate_key(
    selector: str,
    weighted: float,
    tardiness: float,
    pref_penalty: float,
    exit_time: int,
    imbalance: float,
    bay_load: float,
    bay_id: int,
    orient_idx: int,
) -> tuple:
    imbalance_floor = math.floor(imbalance)
    if selector == "objective":
        return (weighted, tardiness, pref_penalty, exit_time, bay_load, bay_id, orient_idx)
    if selector == "tardiness":
        return (tardiness, exit_time, weighted, pref_penalty, imbalance_floor, bay_load, bay_id, orient_idx)
    if selector == "finish":
        return (exit_time, tardiness, weighted, pref_penalty, imbalance_floor, bay_load, bay_id, orient_idx)
    if selector == "balance":
        return (imbalance_floor, weighted, tardiness, exit_time, pref_penalty, bay_load, bay_id, orient_idx)
    if selector == "preference":
        return (pref_penalty, tardiness, exit_time, weighted, imbalance_floor, bay_load, bay_id, orient_idx)
    raise ValueError(f"unknown selector: {selector}")


def _build_serial_assignments(prob_info: dict, order_name: str, selector: str) -> dict[int, dict]:
    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info["bays"])]
    blocks = prob_info["blocks"]
    weights = prob_info.get("weights", {})
    w1 = float(weights.get("w1", 1.0))
    w2 = float(weights.get("w2", 1.0))
    w3 = float(weights.get("w3", 1.0))

    bay_weights = _bay_weights(bays)
    bay_schedule: list[list[tuple[int, int]]] = [[] for _ in bays]
    bay_loads = [0.0 for _ in bays]
    assignments: dict[int, dict] = {}

    for block_id in sorted(range(len(blocks)), key=_order_key(blocks, order_name)):
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
                weighted = w1 * tardiness + w2 * math.floor(imbalance) + w3 * pref_penalty
                key = _candidate_key(
                    selector,
                    weighted,
                    tardiness,
                    pref_penalty,
                    exit_time,
                    imbalance,
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

    return assignments


def _objective_from_assignments(prob_info: dict, assignments: dict[int, dict]) -> tuple[float, float, float, float]:
    blocks = prob_info["blocks"]
    bays = prob_info["bays"]
    weights = prob_info.get("weights", {})
    w1 = float(weights.get("w1", 1.0))
    w2 = float(weights.get("w2", 1.0))
    w3 = float(weights.get("w3", 1.0))

    obj1 = 0.0
    bay_loads = [0.0 for _ in bays]
    obj3 = 0.0
    for assignment in assignments.values():
        block = blocks[assignment["block_id"]]
        bay_id = assignment["bay_id"]
        obj1 += max(0.0, assignment["exit_time"] - block["due_date"])
        bay_loads[bay_id] += block["workload"]
        obj3 += max(block["bay_preferences"]) - block["bay_preferences"][bay_id]

    areas = [bay["width"] * bay["height"] for bay in bays]
    avg_area = sum(areas) / max(1, len(areas))
    normalized = [avg_area / area for area in areas]
    if len(bays) >= 2:
        obj2 = math.floor(
            max(
                abs(normalized[i] * bay_loads[i] - normalized[j] * bay_loads[j])
                for i in range(len(bays))
                for j in range(len(bays))
                if i != j
            )
        )
    else:
        obj2 = 0.0

    return w1 * obj1 + w2 * obj2 + w3 * obj3, obj1, obj2, obj3


def _solution_from_assignments(assignments: dict[int, dict]) -> dict:
    return {"operations": baseline_greedy._build_operations(list(assignments.values()))}


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result["objective"]),
        float(result["obj1"]),
        float(result["obj2"]),
        float(result["obj3"]),
    )


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    started = time.time()
    print(
        f"[baseline_hh v005] instance={prob_info.get('name', '?')} "
        f"blocks={len(prob_info.get('blocks', []))} bays={len(prob_info.get('bays', []))} "
        f"timelimit={timelimit:.1f}s"
    )

    specs = [
        ("official_serial", "official", "preference"),
        ("v002_objective", "edd_release", "objective"),
        ("slack_tardiness", "slack", "tardiness"),
        ("release_finish", "release_due", "finish"),
        ("due_balance", "edd_release", "balance"),
        ("long_proc_tardiness", "long_proc_due", "tardiness"),
        ("workload_objective", "workload_due", "objective"),
    ]

    ranked: list[tuple[float, str, dict[int, dict], tuple[float, float, float, float]]] = []
    seen_signatures: set[tuple] = set()
    for label, order_name, selector in specs:
        assignments = _build_serial_assignments(prob_info, order_name, selector)
        signature = tuple(
            (a["block_id"], a["bay_id"], a["orient_idx"], a["entry_time"], a["exit_time"])
            for a in sorted(assignments.values(), key=lambda item: item["block_id"])
        )
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        estimate = _objective_from_assignments(prob_info, assignments)
        ranked.append((estimate[0], label, assignments, estimate))
        print(
            f"[baseline_hh v005] candidate={label} estimated_obj={estimate[0]:.2f} "
            f"obj1={estimate[1]:.1f} obj2={estimate[2]} obj3={estimate[3]:.1f}"
        )

    ranked.sort(key=lambda item: item[3])
    labels_to_validate = {item[1] for item in ranked[:5]}
    labels_to_validate.add("official_serial")

    best_solution: dict | None = None
    best_result: dict | None = None
    for _, label, assignments, estimate in ranked:
        if label not in labels_to_validate:
            continue
        solution = _solution_from_assignments(assignments)
        result = check_feasibility(prob_info, solution)
        print(
            f"[baseline_hh v005] validate={label} feasible={result['feasible']} "
            f"actual_obj={result.get('objective')} estimated_obj={estimate[0]:.2f}"
        )
        if result.get("feasible") and (best_result is None or _result_key(result) < _result_key(best_result)):
            best_solution = solution
            best_result = result

    if best_solution is not None and best_result is not None:
        print(
            f"[baseline_hh v005] selected obj={best_result['objective']:.2f} "
            f"elapsed={time.time() - started:.2f}s"
        )
        return best_solution

    print("[baseline_hh v005] no validated feasible candidate; returning official serial fallback")
    official = next(item for item in ranked if item[1] == "official_serial")
    return _solution_from_assignments(official[2])
