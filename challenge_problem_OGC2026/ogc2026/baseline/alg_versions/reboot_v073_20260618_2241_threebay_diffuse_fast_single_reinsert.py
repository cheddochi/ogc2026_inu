"""reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert.py

Strategy:
    Keep trusted v072 as the default path, then apply a cheap single-block
    local reinsertion on the 3-bay diffuse-moderate mid-proc subtype.

Metadata:
    version_id: reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert
    parent_version: reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single
    status: candidate
    timestamp: 2026-06-18 22:41 KST
    strategy:
        - Preserve v072 unchanged outside the target subtype.
        - Build the trusted v072 warm start first.
        - On the target subtype, remove exactly one tardy block and reinsert
          it with a bounded candidate-position search instead of the older
          full greedy prefix rebuild.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The subtype still has small local packing slack, but the earlier
        greedy-prefix repair was too expensive. A faster one-block bounded
        reinsertion should capture the objective gain without threatening the
        time limit.
    intended_metric_target:
        - improve prob33-like and prob37-like rows
        - preserve representative core-9 smoke rows
        - improve avg objective versus trusted v072
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single
"""

from __future__ import annotations

import math

import baseline_greedy
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single as v072


ACTIVE_VERSION = "reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert"


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 0.6,
        "long": 0.9,
        "very_long": 1.2,
    }[tier]
    return min(cap, remaining)


def _limited_single_reinsert(
    prob_info: dict,
    assignments: dict[int, dict],
    target_block_id: int,
    *,
    max_positions: int,
    max_orients: int,
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
    prefs = list(block["bay_preferences"])
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
        bay = bays[bay_id]
        min_entry = max(release, int(previous["entry_time"]))
        active_blocks = [
            placed
            for placed, (_, exit_time) in zip(bay_placed[bay_id], bay_schedule[bay_id])
            if exit_time > min_entry
        ]
        for orient_idx in range(min(len(block["shape"]), max_orients)):
            bb = baseline_greedy._block_bbox(block, orient_idx)
            if bb[2] - bb[0] > bay.width + 1e-6 or bb[3] - bb[1] > bay.height + 1e-6:
                continue
            positions = sorted(
                {
                    (int(x), int(y))
                    for x, y in baseline_greedy._candidate_positions(
                        bay.width,
                        bay.height,
                        active_blocks,
                        bb,
                    )
                },
                key=lambda pos: (pos[0] + pos[1], pos[0], pos[1]),
            )[:max_positions]
            for x, y in positions:
                new_block = v064.Block(
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
                    min_entry,
                    proc,
                )
                if entry is None:
                    continue
                if not v064.v001._candidate_preserves_existing_exits(
                    bay,
                    new_block,
                    int(entry),
                    int(exit_time),
                    bay_placed[bay_id],
                    bay_schedule[bay_id],
                ):
                    continue
                tardiness = max(0, exit_time - due)
                pref_penalty = pref_max - prefs[bay_id]
                imbalance = math.floor(
                    v064.v001._imbalance_after(bay_loads, bay_weights, bay_id, workload)
                )
                key = (
                    tardiness,
                    exit_time,
                    pref_penalty,
                    imbalance,
                    x + y,
                    x,
                    y,
                    bay_id,
                    orient_idx,
                    w1 + w2 + w3,
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


def _try_fast_single_reinsert(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    started = v064.time.time()
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = v064._tardy_block_ids(prob_info, base_assignments, 1)
    if not target_block_ids:
        return base_solution, base_result

    candidate_assignments = _limited_single_reinsert(
        prob_info,
        base_assignments,
        target_block_ids[0],
        max_positions=6,
        max_orients=4,
    )
    if candidate_assignments is None:
        return base_solution, base_result

    if v064.time.time() - started > budget + 0.2:
        print(
            f"[baseline_hh reboot_v073] skip_slow_reinsert instance={prob_info.get('name')} "
            f"tier={tier} elapsed={v064.time.time() - started:.2f}s budget={budget:.2f}s"
        )
        return base_solution, base_result

    candidate_solution = v064.v001._solution_from_assignments(candidate_assignments)
    candidate_result = v064.v001.check_feasibility(prob_info, candidate_solution)
    print(
        f"[baseline_hh reboot_v073] threebay_diffuse_fast_reinsert instance={prob_info.get('name')} "
        f"tier={tier} target_block={target_block_ids[0]} feasible={candidate_result.get('feasible')} "
        f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
    )
    if v064._result_key(candidate_result) < v064._result_key(base_result):
        return candidate_solution, candidate_result
    return base_solution, base_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = v064.time.time()
    features = v064._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v072.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not v064._matches_threebay_diffuse_moderate_class(features)
        or float(base_result.get("obj1") or 0.0) <= 3000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (v064.time.time() - started))
    if remaining <= 0.5:
        print(
            f"[baseline_hh reboot_v073] skip_diffuse_fast_reinsert instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_fast_single_reinsert(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v073] selected_diffuse_fast_reinsert instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v073] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
