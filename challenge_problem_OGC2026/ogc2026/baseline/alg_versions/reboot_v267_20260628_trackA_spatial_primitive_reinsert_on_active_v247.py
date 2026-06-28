"""reboot_v267_20260628_trackA_spatial_primitive_reinsert_on_active_v247.py

Strategy:
    Preserve the exact trusted active `baseline_hh.py` wrapper result first.
    On a very narrow Family A subtype gate only, run a tiny spatial-aware
    primitive reinsertion on the top tardy shortlist blocks and keep only
    strictly better accepted results.
"""

from __future__ import annotations

import importlib.util
import math
import time
from pathlib import Path

import baseline_greedy
from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
from alg_versions import reboot_v216_20260627_trackA_inline_latest_feasible_slice_on_v212 as v216
from alg_versions import reboot_v252_20260628_trackA_spatial_split_seed_on_v247 as v252
from utils import Bay, Block


ACTIVE_VERSION = "reboot_v267_20260628_trackA_spatial_primitive_reinsert_on_active_v247"


def _load_trusted_wrapper_fallback_module():
    wrapper_path = Path(__file__).resolve().with_name(
        "reboot_v267_20260628_trusted_wrapper_fallback_v247.py"
    )
    spec = importlib.util.spec_from_file_location(
        "_ogc2026_v267_trusted_wrapper_fallback_v247",
        wrapper_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load trusted wrapper fallback from {wrapper_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_TRUSTED_WRAPPER_FALLBACK = _load_trusted_wrapper_fallback_module()


def _safety_margin(timelimit: float) -> float:
    return max(1.0, min(10.0, timelimit * 0.08))


def _orientation_dims(block: dict, orient_idx: int) -> tuple[float, float]:
    bb = baseline_greedy._block_bbox(block, orient_idx)
    return bb[2] - bb[0], bb[3] - bb[1]


def _orientation_order(block: dict) -> list[int]:
    ranked = []
    for orient_idx in range(len(block.get("shape", []))):
        w, h = _orientation_dims(block, orient_idx)
        ranked.append((-(w * h), max(w, h), min(w, h), orient_idx))
    ranked.sort()
    return [orient_idx for *_, orient_idx in ranked[:4]]


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
    corners = [
        (min_x, min_y),
        (max_x, min_y),
        (min_x, max_y),
        (max_x, max_y),
    ]
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


def _fragmentation_score(
    bay: Bay,
    x: int,
    y: int,
    width: float,
    height: float,
) -> tuple[float, float, float]:
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


def _repair_budget(remaining: float, timelimit: float, subtype: str, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    spendable = max(0.0, remaining - _safety_margin(timelimit))
    cap = 1.55 if subtype == "prob13like" else 1.25
    floor = 0.85 if subtype == "prob13like" else 0.65
    if spendable < floor:
        return 0.0
    return min(cap, spendable * 0.45)


def _exact_budget(remaining: float, timelimit: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    spendable = max(0.0, remaining - _safety_margin(timelimit))
    if spendable < 0.55:
        return 0.0
    return min(0.50, spendable * 0.22)


def _spatial_primitive_reinsert(
    prob_info: dict,
    assignments: dict[int, dict],
    target_block_id: int,
    *,
    max_positions: int,
    deadline: float,
) -> dict[int, dict] | None:
    previous = assignments.get(target_block_id)
    if previous is None:
        return None

    repaired = dict(assignments)
    repaired.pop(target_block_id, None)

    bays, bay_placed, bay_schedule, bay_loads = v064._rebuild_state(prob_info, repaired)
    bay_weights = v064.v001._bay_weights(bays)
    w1, w2, w3 = v064._weights(prob_info)

    block = prob_info["blocks"][target_block_id]
    prefs = [float(value) for value in block["bay_preferences"]]
    pref_max = max(prefs)
    release = int(block["release_time"])
    due = int(block["due_date"])
    proc = int(block["processing_time"])
    workload = float(block["workload"])

    best = None
    best_key = None
    bay_order = sorted(
        range(len(bays)),
        key=lambda bay_id: (prefs[bay_id], -bay_loads[bay_id]),
        reverse=True,
    )

    for bay_id in bay_order:
        if time.time() >= deadline:
            break
        bay = bays[bay_id]
        active_blocks = [
            placed
            for placed, (_, exit_at) in zip(bay_placed[bay_id], bay_schedule[bay_id])
            if exit_at > release
        ]
        for orient_idx in _orientation_order(block):
            if time.time() >= deadline:
                break
            bb = baseline_greedy._block_bbox(block, orient_idx)
            width = bb[2] - bb[0]
            height = bb[3] - bb[1]
            if width > bay.width + 1e-6 or height > bay.height + 1e-6:
                continue

            positions = _spatial_positions(bay, active_blocks, bb, max_positions)
            positions = v080._quantile_sample_positions(positions, max_positions)
            for x, y in positions:
                if time.time() >= deadline:
                    break
                new_block = Block(
                    block_id=target_block_id,
                    block_data=block,
                    x=x,
                    y=y,
                    orient_idx=orient_idx,
                )
                if not bay.contains_block(new_block):
                    continue
                entry, exit_time = baseline_greedy._find_earliest_slot(
                    new_block,
                    bay,
                    bay_placed[bay_id],
                    bay_schedule[bay_id],
                    release,
                    proc,
                )
                if entry is None:
                    continue

                tardiness = max(0, exit_time - due)
                pref_penalty = pref_max - prefs[bay_id]
                weighted = baseline_greedy._placement_score(
                    tardiness,
                    workload,
                    bay_loads,
                    bay_id,
                    pref_penalty,
                    bay_weights,
                    w1,
                    w2,
                    w3,
                    top_y=y + bb[3],
                )
                central_void, wall_gap, corner_gap = _fragmentation_score(
                    bay,
                    int(x),
                    int(y),
                    width,
                    height,
                )
                zero_t_entry_key = -int(entry) if tardiness == 0 else int(exit_time)
                key = (
                    tardiness,
                    zero_t_entry_key,
                    weighted,
                    pref_penalty,
                    central_void,
                    wall_gap,
                    corner_gap,
                    x + y,
                    bay_id,
                    orient_idx,
                )
                if best_key is None or key < best_key:
                    best_key = key
                    best = (bay_id, x, y, orient_idx, int(entry), int(exit_time))

    if best is None:
        return None

    bay_id, x, y, orient_idx, entry, exit_time = best
    repaired[target_block_id] = {
        "block_id": target_block_id,
        "bay_id": bay_id,
        "x": x,
        "y": y,
        "orient_idx": orient_idx,
        "entry_time": entry,
        "exit_time": exit_time,
    }
    return repaired


def _try_spatial_primitive_repair(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    timelimit: float,
    tier: str,
    subtype: str,
) -> tuple[dict, dict, list[tuple[int, float, float]]]:
    budget = _repair_budget(remaining, timelimit, subtype, tier)
    if budget <= 0.0:
        return base_solution, base_result, []

    deadline = time.time() + budget
    best_solution = base_solution
    best_result = base_result
    accepted_moves: list[tuple[int, float, float]] = []
    shortlist_limit = 2 if subtype == "prob13like" else 1
    max_positions = 14 if subtype == "prob13like" else 10

    base_assignments = v064._solution_to_assignments(best_solution)
    shortlist = v186._family_a_tardy_shortlist(prob_info, base_assignments, shortlist_limit)
    for block_id in shortlist:
        if time.time() >= deadline:
            break
        candidate_assignments = _spatial_primitive_reinsert(
            prob_info,
            base_assignments,
            block_id,
            max_positions=max_positions,
            deadline=deadline,
        )
        if candidate_assignments is None:
            continue

        candidate_solution = v001._solution_from_assignments(candidate_assignments)
        candidate_result = v001.check_feasibility(prob_info, candidate_solution)
        if not candidate_result.get("feasible"):
            repaired_assignments, repaired_result, _ = v001._repair_with_empty_windows(
                prob_info,
                candidate_assignments,
                max_rounds=3,
            )
            if repaired_result.get("feasible"):
                candidate_solution = v001._solution_from_assignments(repaired_assignments)
                candidate_result = repaired_result

        print(
            f"[baseline_hh reboot_v267] primitive_spatial_candidate instance={prob_info.get('name')} "
            f"subtype={subtype} block={block_id} feasible={candidate_result.get('feasible')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        if v064._result_key(candidate_result) < v064._result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result
            accepted_moves.append(
                (
                    block_id,
                    float(best_result.get("obj1") or 0.0),
                    float(best_result.get("objective") or 0.0),
                )
            )
            break

    return best_solution, best_result, accepted_moves


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    started = time.time()
    tier = v186.v169._time_tier(timelimit)
    features = v186._selector_features(prob_info)
    subtype_features = v252._selector_features(prob_info)
    subtype = v252._subtype(subtype_features)

    fallback_solution = _TRUSTED_WRAPPER_FALLBACK.algorithm(prob_info, timelimit)
    fallback_result = v001.check_feasibility(prob_info, fallback_solution)
    attempted: list[tuple[str, float, float]] = [
        (
            "trusted_active_fallback",
            float(fallback_result.get("obj1") or 0.0),
            float(fallback_result.get("objective") or 0.0),
        )
    ]

    if (
        not fallback_result.get("feasible")
        or float(fallback_result.get("obj1") or 0.0) <= 0.0
        or tier in {"very_short", "short"}
        or not v186._matches_family_a_tightslack(features)
        or subtype is None
    ):
        print(
            f"[baseline_hh reboot_v267] keep_trusted_fallback instance={prob_info.get('name')} "
            f"tier={tier} subtype={subtype} T={fallback_result.get('obj1')} "
            f"objective={fallback_result.get('objective')}"
        )
        return fallback_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    best_solution, best_result, accepted_moves = _try_spatial_primitive_repair(
        prob_info,
        fallback_solution,
        fallback_result,
        remaining,
        timelimit,
        tier,
        subtype,
    )
    attempted.append(
        (
            f"primitive_spatial_{subtype}",
            float(best_result.get("obj1") or 0.0),
            float(best_result.get("objective") or 0.0),
        )
    )

    remaining = max(0.0, timelimit - (time.time() - started))
    exact_budget = _exact_budget(remaining, timelimit, tier)
    if accepted_moves and exact_budget > 0.40 and best_result.get("feasible"):
        exact_solution, exact_result, _ = v216._try_exact_latest_feasible_slice(
            prob_info,
            best_solution,
            best_result,
            exact_budget,
            tier,
        )
        attempted.append(
            (
                f"primitive_exact_{subtype}",
                float(exact_result.get("obj1") or 0.0),
                float(exact_result.get("objective") or 0.0),
            )
        )
        if v064._result_key(exact_result) < v064._result_key(best_result):
            best_solution = exact_solution
            best_result = exact_result

    print(
        f"[baseline_hh reboot_v267] primitive_spatial_repair instance={prob_info.get('name')} "
        f"tier={tier} subtype={subtype} attempted={attempted} "
        f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
    )
    return best_solution
