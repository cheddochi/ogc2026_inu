"""reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114.py

Strategy:
    Keep v114 as the default path, then add one tiny displaced-block earlier-
    entry move only on the prob31-like subtype.

Metadata:
    version_id: reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114
    parent_version: reboot_v114_20260619_2358_prob31like_direct_prefix2_stable_on_v109
    status: candidate
    timestamp: 2026-06-20 00:32 KST
    strategy:
        - Preserve v114 unchanged outside the prob31-like subtype.
        - Reuse the v114 runtime-stable parent exactly.
        - On top of that parent, try a very short displaced-block earlier-entry
          reinsertion over a tiny shortlist and stop on the first strict
          improvement.
    hypothesis:
        The v114 parent restores enough runtime margin that the displaced
        earlier-entry move can finally be added back safely, giving a real
        prob31-like T improvement without reintroducing the runtime cliff.
    intended_metric_target:
        - improve the prob31-like official-limit row beyond v114
        - preserve accepted_for_score on representative smoke
        - keep the prob40-like recovery already present in the parent
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v114_20260619_2358_prob31like_direct_prefix2_stable_on_v109
"""

from __future__ import annotations

import math
import time

import baseline_greedy
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v078_20260619_1535_fourbay_runtime_family_flatten as v078
from alg_versions import reboot_v114_20260619_2358_prob31like_direct_prefix2_stable_on_v109 as v114


ACTIVE_VERSION = "reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114"


def _candidate_limit(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 2,
        "long": 3,
        "very_long": 4,
    }[tier]


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 1.2,
        "long": 1.6,
        "very_long": 2.0,
    }[tier]
    return min(cap, remaining)


def _displaced_target_block_ids(
    prob_info: dict,
    assignments: dict[int, dict],
    limit: int,
) -> list[int]:
    if limit <= 0:
        return []

    ranked = []
    blocks = prob_info["blocks"]
    for block_id, assignment in assignments.items():
        block = blocks[block_id]
        due = int(block["due_date"])
        release = int(block["release_time"])
        tardiness = max(0, int(assignment["exit_time"]) - due)
        if tardiness <= 0:
            continue

        prefs = list(block["bay_preferences"])
        bay_id = int(assignment["bay_id"])
        pref_penalty = max(prefs) - prefs[bay_id]
        entry_delay = int(assignment["entry_time"]) - release
        if pref_penalty < 75 or tardiness < 25 or entry_delay < 30:
            continue

        ranked.append((entry_delay, tardiness, pref_penalty, block_id))

    ranked.sort(reverse=True)
    return [block_id for _, _, _, block_id in ranked[:limit]]


def _relaxed_single_reinsert(
    prob_info: dict,
    assignments: dict[int, dict],
    target_block_id: int,
) -> dict[int, dict] | None:
    previous = assignments.get(target_block_id)
    if previous is None:
        return None

    repaired = dict(assignments)
    repaired.pop(target_block_id, None)

    bays, bay_placed, bay_schedule, bay_loads = v064._rebuild_state(prob_info, repaired)
    bay_weights = v064.v001._bay_weights(bays)

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
        min_entry = release
        active_blocks = [
            placed
            for placed, (_, exit_time) in zip(bay_placed[bay_id], bay_schedule[bay_id])
            if exit_time > min_entry
        ]
        for orient_idx in range(min(len(block["shape"]), 3)):
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
            )[:6]

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


def _try_displaced_fast_reinsert(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    started = time.time()
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = _displaced_target_block_ids(
        prob_info,
        base_assignments,
        _candidate_limit(tier),
    )
    if not target_block_ids:
        return base_solution, base_result

    attempted = []
    best_solution = base_solution
    best_result = base_result

    for target_block_id in target_block_ids:
        if time.time() - started > budget:
            break
        candidate_assignments = _relaxed_single_reinsert(
            prob_info,
            base_assignments,
            target_block_id,
        )
        if candidate_assignments is None:
            attempted.append((target_block_id, None, None))
            continue

        candidate_solution = v064.v001._solution_from_assignments(candidate_assignments)
        candidate_result = v064.v001.check_feasibility(prob_info, candidate_solution)
        attempted.append(
            (
                target_block_id,
                candidate_result.get("obj1"),
                candidate_result.get("objective"),
            )
        )
        if v064._result_key(candidate_result) < v064._result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result
            break

    print(
        f"[baseline_hh reboot_v115] prob31like_displaced_fast instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v078._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    if (
        tier not in {"very_short", "short"}
        and float(timelimit) >= 55.0
        and v078._matches_prob31like_class(features)
    ):
        started = time.time()
        base_solution, base_result = v114._prob31like_runtime_stable_solution(
            prob_info,
            timelimit,
            tier,
        )
        if not base_result.get("feasible"):
            print(
                f"[baseline_hh reboot_v115] prob31like_parent_fallback "
                f"instance={prob_info.get('name')} feasible={base_result.get('feasible')} "
                f"objective={base_result.get('objective')}"
            )
            return v114.algorithm(prob_info, timelimit)

        remaining = max(0.0, float(timelimit) - (time.time() - started))
        if remaining <= 0.5:
            return base_solution

        candidate_solution, candidate_result = _try_displaced_fast_reinsert(
            prob_info,
            base_solution,
            base_result,
            remaining,
            tier,
        )
        if v064._result_key(candidate_result) < v064._result_key(base_result):
            print(
                f"[baseline_hh reboot_v115] selected_prob31like_displaced_fast "
                f"instance={prob_info.get('name')} T={candidate_result.get('obj1')} "
                f"objective={candidate_result.get('objective')}"
            )
            return candidate_solution
        return base_solution

    return v114.algorithm(prob_info, timelimit)
