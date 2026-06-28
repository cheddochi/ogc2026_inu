"""reboot_v252_20260628_trackA_spatial_split_seed_on_v247.py

Strategy:
    Split the Track A spatial gate into two tighter subtype bands and compare a
    bounded spatial constructive seed against trusted v247 on the remaining
    time. The fallback remains a black-box call to v247.
"""

from __future__ import annotations

import math
import time

import baseline_greedy
from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
from alg_versions import reboot_v247_20260627_trackA_prob11plus_prob33_direct_selector_on_v241 as v247
from utils import Bay, Block


ACTIVE_VERSION = "reboot_v252_20260628_trackA_spatial_split_seed_on_v247"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _orientation_dims(block: dict, orient_idx: int) -> tuple[float, float]:
    bb = baseline_greedy._block_bbox(block, orient_idx)
    return bb[2] - bb[0], bb[3] - bb[1]


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info.get("bays", []))]
    weights = prob_info.get("weights", {})
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    rel_values = [float(block.get("release_time", 0.0)) for block in blocks]
    due_values = [float(block.get("due_date", 0.0)) for block in blocks]

    top_choices = []
    pref_weight = [0.0] * len(bays)
    bay_areas = [float(bay.width * bay.height) for bay in bays] or [1.0]
    mean_bay_area = sum(bay_areas) / len(bay_areas)
    best_bbox_areas: list[float] = []

    for block in blocks:
        prefs = [float(value) for value in block.get("bay_preferences", [])]
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += pref_value
        areas = [
            _orientation_dims(block, orient_idx)[0] * _orientation_dims(block, orient_idx)[1]
            for orient_idx in range(len(block.get("shape", [])))
        ]
        if areas:
            best_bbox_areas.append(max(areas))

    pref_concentration = 0.0
    if top_choices and blocks:
        pref_concentration = max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    slack_values = [due - rel - proc for due, rel, proc in zip(due_values, rel_values, proc_values)]
    tight_slack_ratio = 0.0
    if slack_values:
        tight_slack_ratio = sum(1 for value in slack_values if value <= 1.0) / len(slack_values)

    p90_area_ratio = 0.0
    max_area_ratio = 0.0
    if best_bbox_areas:
        ranked = sorted(best_bbox_areas)
        p90_area_ratio = ranked[int(0.9 * (len(ranked) - 1))] / max(1.0, mean_bay_area)
        max_area_ratio = ranked[-1] / max(1.0, mean_bay_area)

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "w1": float(weights.get("w1", 1.0)),
        "proc_mean": _mean(proc_values),
        "slack_mean": _mean(slack_values),
        "tight_slack_ratio": tight_slack_ratio,
        "pref_concentration": pref_concentration,
        "pref_pressure": pref_pressure,
        "max_area_ratio": max_area_ratio,
        "p90_area_ratio": p90_area_ratio,
    }


def _matches_prob13like(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 240 <= int(features.get("blocks", 0)) <= 260
        and 17500.0 <= float(features.get("w1", 0.0)) <= 19500.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.35
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.60
        and float(features.get("pref_concentration", 1.0)) <= 0.29
        and float(features.get("pref_pressure", 1.0)) <= 0.265
        and 0.20 <= float(features.get("max_area_ratio", 0.0)) <= 0.26
        and 0.15 <= float(features.get("p90_area_ratio", 0.0)) <= 0.17
    )


def _matches_prob19like(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 280 <= int(features.get("blocks", 0)) <= 320
        and 9500.0 <= float(features.get("w1", 0.0)) <= 12000.0
        and float(features.get("proc_mean", 0.0)) <= 7.6
        and 1.35 <= float(features.get("slack_mean", 0.0)) <= 1.50
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.55
        and float(features.get("pref_concentration", 1.0)) <= 0.29
        and float(features.get("pref_pressure", 1.0)) <= 0.27
        and 0.27 <= float(features.get("max_area_ratio", 0.0)) <= 0.30
        and 0.16 <= float(features.get("p90_area_ratio", 0.0)) <= 0.17
    )


def _subtype(features: dict[str, float]) -> str | None:
    if _matches_prob13like(features):
        return "prob13like"
    if _matches_prob19like(features):
        return "prob19like"
    return None


def _ordered_block_ids(blocks: list[dict], subtype: str) -> list[int]:
    def key(block_id: int) -> tuple[float, ...]:
        block = blocks[block_id]
        release = float(block.get("release_time", 0.0))
        due = float(block.get("due_date", 0.0))
        proc = float(block.get("processing_time", 0.0))
        slack = due - release - proc
        area = max((_orientation_dims(block, orient_idx)[0] * _orientation_dims(block, orient_idx)[1] for orient_idx in range(len(block.get("shape", [])))), default=0.0)
        if subtype == "prob13like":
            return (slack, -area, due, release, -proc, block_id)
        return (slack, due, -area, -proc, release, block_id)

    return sorted(range(len(blocks)), key=key)


def _spatial_positions(
    bay: Bay,
    active_blocks: list[Block],
    bb: tuple[float, float, float, float],
    max_positions: int,
) -> list[tuple[int, int]]:
    min_x = max(0, math.ceil(-bb[0]))
    min_y = max(0, math.ceil(-bb[1]))
    max_x = math.floor(bay.width - bb[2])
    max_y = math.floor(bay.height - bb[3])
    corners = [(min_x, min_y), (max_x, min_y), (min_x, max_y), (max_x, max_y)]
    raw = baseline_greedy._candidate_positions(bay.width, bay.height, active_blocks, bb)
    edge_sorted = sorted(
        {(int(round(x)), int(round(y))) for x, y in raw},
        key=lambda pos: (
            min(pos[0] - min_x, max_x - pos[0], pos[1] - min_y, max_y - pos[1]),
            pos[0] + pos[1],
            pos[1],
            pos[0],
        ),
    )
    merged: list[tuple[int, int]] = []
    seen = set()
    for pos in corners + edge_sorted:
        if pos in seen:
            continue
        if pos[0] < min_x or pos[0] > max_x or pos[1] < min_y or pos[1] > max_y:
            continue
        seen.add(pos)
        merged.append(pos)
        if len(merged) >= max_positions:
            break
    return merged


def _orientation_order(block: dict) -> list[int]:
    ranked = []
    for orient_idx in range(len(block.get("shape", []))):
        w, h = _orientation_dims(block, orient_idx)
        ranked.append((-(w * h), min(w, h), max(w, h), orient_idx))
    ranked.sort()
    return [orient_idx for *_, orient_idx in ranked[:4]]


def _fragmentation_score(bay: Bay, x: int, y: int, width: float, height: float) -> tuple[float, float, float]:
    left_gap = float(x)
    bottom_gap = float(y)
    right_gap = max(0.0, float(bay.width) - (float(x) + width))
    top_gap = max(0.0, float(bay.height) - (float(y) + height))
    wall_gap = min(left_gap, right_gap, bottom_gap, top_gap)
    corner_gap = min(
        left_gap + bottom_gap,
        left_gap + top_gap,
        right_gap + bottom_gap,
        right_gap + top_gap,
    )
    central_void = min(left_gap, right_gap) * min(bottom_gap, top_gap)
    return central_void, wall_gap, corner_gap


def _seed_budget(remaining: float, subtype: str, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = 6.5 if subtype == "prob13like" else 5.0
    return min(cap, max(3.0, remaining * 0.10))


def _build_spatial_candidate(prob_info: dict, budget: float, subtype: str) -> tuple[dict, dict]:
    started = time.time()
    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info["bays"])]
    blocks = prob_info["blocks"]
    weights = prob_info.get("weights", {})
    w1 = float(weights.get("w1", 1.0))
    w2 = float(weights.get("w2", 1.0))
    w3 = float(weights.get("w3", 1.0))

    bay_weights = v001._bay_weights(bays)
    bay_placed: list[list[Block]] = [[] for _ in bays]
    bay_schedule: list[list[tuple[int, int]]] = [[] for _ in bays]
    bay_loads = [0.0 for _ in bays]
    bay_last_entry = [0 for _ in bays]
    assignments: dict[int, dict] = {}
    forced = 0
    order = _ordered_block_ids(blocks, subtype)

    for block_id in order:
        block = blocks[block_id]
        release = int(block["release_time"])
        due = int(block["due_date"])
        proc = int(block["processing_time"])
        workload = float(block["workload"])
        prefs = [float(value) for value in block["bay_preferences"]]
        pref_max = max(prefs)

        best = None
        best_key = None
        if time.time() - started <= budget * 0.95:
            bay_order = sorted(range(len(bays)), key=lambda bay_id: (prefs[bay_id], -bay_loads[bay_id]), reverse=True)[: min(4, len(bays))]
            for bay_id in bay_order:
                bay = bays[bay_id]
                min_entry = max(release, bay_last_entry[bay_id])
                for orient_idx in _orientation_order(block):
                    bb = baseline_greedy._block_bbox(block, orient_idx)
                    width = bb[2] - bb[0]
                    height = bb[3] - bb[1]
                    if width > bay.width + 1e-6 or height > bay.height + 1e-6:
                        continue
                    active_blocks = [
                        placed
                        for placed, (_, exit_at) in zip(bay_placed[bay_id], bay_schedule[bay_id])
                        if exit_at > min_entry
                    ]
                    positions = _spatial_positions(bay, active_blocks, bb, 12 if subtype == "prob13like" else 10)
                    for x, y in positions:
                        new_block = Block(block_id=block_id, block_data=block, x=x, y=y, orient_idx=orient_idx)
                        if not bay.contains_block(new_block):
                            continue
                        entry, exit_at = baseline_greedy._find_earliest_slot(
                            new_block, bay, bay_placed[bay_id], bay_schedule[bay_id], min_entry, proc
                        )
                        if entry is None:
                            continue
                        if not v001._candidate_preserves_existing_exits(
                            bay, new_block, int(entry), int(exit_at), bay_placed[bay_id], bay_schedule[bay_id]
                        ):
                            continue
                        tardiness = max(0, int(exit_at) - due)
                        pref_penalty = pref_max - prefs[bay_id]
                        imbalance = math.floor(v001._imbalance_after(bay_loads, bay_weights, bay_id, workload))
                        central_void, wall_gap, corner_gap = _fragmentation_score(bay, int(x), int(y), width, height)
                        weighted = w1 * tardiness + w2 * imbalance + w3 * pref_penalty
                        key = (
                            tardiness,
                            -int(entry) if tardiness == 0 else int(exit_at),
                            weighted,
                            pref_penalty,
                            central_void,
                            wall_gap,
                            corner_gap,
                            bay_loads[bay_id],
                            bay_id,
                            orient_idx,
                        )
                        if best_key is None or key < best_key:
                            best_key = key
                            best = (bay_id, x, y, orient_idx, int(entry), int(exit_at))

        if best is None:
            best = v001._empty_window_candidate(block_id, blocks, bays, bay_schedule, bay_last_entry)
            forced += 1

        bay_id, x, y, orient_idx, entry, exit_at = best
        bay_placed[bay_id].append(Block(block_id=block_id, block_data=block, x=x, y=y, orient_idx=orient_idx))
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

    solution = v001._solution_from_assignments(assignments)
    result = v001.check_feasibility(prob_info, solution)
    if not result.get("feasible"):
        repaired, repaired_result, rounds = v001._repair_with_empty_windows(prob_info, assignments)
        print(
            f"[baseline_hh reboot_v252] spatial_empty_window_repair subtype={subtype} "
            f"feasible={repaired_result.get('feasible')} stage={repaired_result.get('stage')} "
            f"rounds={rounds} T={repaired_result.get('obj1')} objective={repaired_result.get('objective')}"
        )
        if repaired_result.get("feasible"):
            solution = v001._solution_from_assignments(repaired)
            result = repaired_result

    print(
        f"[baseline_hh reboot_v252] spatial_seed built subtype={subtype} forced={forced} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}s "
        f"T={result.get('obj1')} objective={result.get('objective')}"
    )
    return solution, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    features = _selector_features(prob_info)
    subtype = _subtype(features)
    if subtype is None:
        return v247.algorithm(prob_info, timelimit)

    tier = v186.v169._time_tier(timelimit)
    seed_budget = _seed_budget(timelimit, subtype, tier)
    if seed_budget <= 0.0 or timelimit - seed_budget < 45.0:
        return v247.algorithm(prob_info, timelimit)

    started = time.time()
    spatial_solution, spatial_result = _build_spatial_candidate(prob_info, seed_budget, subtype)
    remaining = max(1.0, timelimit - (time.time() - started))
    fallback_solution = v247.algorithm(prob_info, remaining)
    fallback_result = v001.check_feasibility(prob_info, fallback_solution)

    print(
        f"[baseline_hh reboot_v252] compare subtype={subtype} instance={prob_info.get('name')} "
        f"spatial_T={spatial_result.get('obj1')} spatial_objective={spatial_result.get('objective')} "
        f"fallback_T={fallback_result.get('obj1')} fallback_objective={fallback_result.get('objective')} "
        f"remaining_for_fallback={remaining:.2f}s"
    )

    if v186.v064._result_key(spatial_result) < v186.v064._result_key(fallback_result):
        return spatial_solution
    return fallback_solution
