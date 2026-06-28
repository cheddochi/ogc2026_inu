"""reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research.py

Strategy:
    Keep trusted v063 as the default path, then greedily re-search only a tiny
    tardy subset on a narrow 3-bay diffuse-moderate-pressure mid-proc class.

Metadata:
    version_id: reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research
    parent_version: reboot_v063_20260618_1605_prob40like_direct_first_due_release
    status: candidate
    timestamp: 2026-06-18 17:15 KST
    strategy:
        - Preserve v063 unchanged outside the target subtype.
        - Build the trusted warm start first.
        - On the target subtype, remove only the top tardy 1-3 blocks and
          re-place them with the full greedy kernel under a strict budget.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The remaining diffuse-moderate 3-bay class is blocked by a few stranded
        tardy blocks rather than by the global order. Tiny greedy re-search on
        that subset can still lower T/objective.
    intended_metric_target:
        - improve prob33-like and prob37-like rows
        - preserve representative smoke rows
        - improve avg objective versus trusted v063
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v063_20260618_1605_prob40like_direct_first_due_release
"""

from __future__ import annotations

import time

import baseline_greedy
from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v063_20260618_1605_prob40like_direct_first_due_release as v063
from utils import Bay, Block


ACTIVE_VERSION = "reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    rel_values = [float(block.get("release_time", 0.0)) for block in blocks]
    due_values = [float(block.get("due_date", 0.0)) for block in blocks]

    top_choices = []
    pref_weight = [0.0] * len(bays)
    for block in blocks:
        prefs = list(block.get("bay_preferences", []))
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += float(pref_value)

    pref_conc = 0.0
    if top_choices and len(blocks) > 0:
        pref_conc = max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)

    imbalance = 0.0
    if top_choices and len(bays) > 1 and len(blocks) > 0:
        counts = [top_choices.count(bay_id) for bay_id in range(len(bays))]
        imbalance = (max(counts) - min(counts)) / len(blocks)

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    slack_values = [
        due - rel - proc
        for due, rel, proc in zip(due_values, rel_values, proc_values)
    ]

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": _mean(proc_values),
        "pref_concentration": pref_conc,
        "pref_pressure": pref_pressure,
        "workload_imbalance_pressure": imbalance,
        "slack_mean": _mean(slack_values),
    }


def _matches_threebay_diffuse_moderate_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and int(features["blocks"]) >= 200
        and 11.0 <= features["proc_mean"] <= 17.5
        and 0.39 <= features["pref_concentration"] <= 0.46
        and 0.39 <= features["pref_pressure"] <= 0.42
        and 0.10 <= features["workload_imbalance_pressure"] <= 0.23
        and features["slack_mean"] <= 4.0
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _repair_budget(timelimit: float, remaining: float, tier: str) -> float:
    reserve = _dynamic_reserve(timelimit)
    available = max(0.0, remaining - reserve)
    fraction = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 0.14,
        "long": 0.18,
        "very_long": 0.24,
    }[tier]
    cap = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 8.0,
        "long": 12.0,
        "very_long": 16.0,
    }[tier]
    return min(cap, max(0.0, min(available, timelimit * fraction)))


def _move_limit(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 3,
        "long": 4,
        "very_long": 6,
    }[tier]


def _checkpoint_counts(move_limit: int, tier: str) -> list[int]:
    if move_limit <= 0:
        return []
    checkpoints = [min(1, move_limit)]
    if move_limit >= 2:
        checkpoints.append(2)
    if move_limit >= 3:
        checkpoints.append(3)
    if tier in {"long", "very_long"} and move_limit >= 4:
        checkpoints.append(4)
    if tier == "very_long" and move_limit >= 6:
        checkpoints.append(6)
    return sorted(set(count for count in checkpoints if 0 < count <= move_limit))


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result["obj1"]),
        float(result["objective"]),
        float(result["obj2"]),
        float(result["obj3"]),
    )


def _solution_to_assignments(solution: dict) -> dict[int, dict]:
    assignments: dict[int, dict] = {}
    for t_str, ops_at_t in solution.get("operations", {}).items():
        t = int(t_str)
        for op in ops_at_t:
            block_id = int(op["block_id"])
            assignment = assignments.setdefault(block_id, {"block_id": block_id})
            if op["type"] == "ENTRY":
                assignment["bay_id"] = int(op["bay_id"])
                assignment["x"] = int(op["x"])
                assignment["y"] = int(op["y"])
                assignment["orient_idx"] = int(op["orient_idx"])
                assignment["entry_time"] = t
            elif op["type"] == "EXIT":
                assignment["exit_time"] = t
    required = {
        "block_id",
        "bay_id",
        "x",
        "y",
        "orient_idx",
        "entry_time",
        "exit_time",
    }
    return {
        block_id: assignment
        for block_id, assignment in assignments.items()
        if required.issubset(assignment)
    }


def _tardy_block_ids(prob_info: dict, assignments: dict[int, dict], limit: int) -> list[int]:
    ranked = []
    blocks = prob_info["blocks"]
    for block_id, assignment in assignments.items():
        due = int(blocks[block_id]["due_date"])
        tardiness = max(0, int(assignment["exit_time"]) - due)
        if tardiness <= 0:
            continue
        prefs = blocks[block_id]["bay_preferences"]
        bay_id = int(assignment["bay_id"])
        pref_penalty = max(prefs) - prefs[bay_id]
        ranked.append((-tardiness, -pref_penalty, due, block_id))
    ranked.sort()
    return [block_id for _, _, _, block_id in ranked[:limit]]


def _rebuild_state(
    prob_info: dict,
    assignments: dict[int, dict],
) -> tuple[list[Bay], list[list[Block]], list[list[tuple[int, int]]], list[float]]:
    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info["bays"])]
    bay_placed: list[list[Block]] = [[] for _ in bays]
    bay_schedule: list[list[tuple[int, int]]] = [[] for _ in bays]
    bay_loads = [0.0 for _ in bays]
    blocks = prob_info["blocks"]
    for assignment in assignments.values():
        block_id = int(assignment["block_id"])
        bay_id = int(assignment["bay_id"])
        bay_placed[bay_id].append(
            Block(
                block_id=block_id,
                block_data=blocks[block_id],
                x=int(assignment["x"]),
                y=int(assignment["y"]),
                orient_idx=int(assignment["orient_idx"]),
            )
        )
        bay_schedule[bay_id].append(
            (int(assignment["entry_time"]), int(assignment["exit_time"]))
        )
        bay_loads[bay_id] += float(blocks[block_id]["workload"])
    return bays, bay_placed, bay_schedule, bay_loads


def _weights(prob_info: dict) -> tuple[float, float, float]:
    weights = prob_info.get("weights", {})
    return (
        float(weights.get("w1", 1.0)),
        float(weights.get("w2", 1.0)),
        float(weights.get("w3", 1.0)),
    )


def _greedy_research_prefix(
    prob_info: dict,
    assignments: dict[int, dict],
    block_ids: list[int],
    prefix_len: int,
) -> dict[int, dict]:
    repaired = dict(assignments)
    target_ids = block_ids[:prefix_len]
    previous_subset = {block_id: repaired[block_id] for block_id in target_ids}
    for block_id in target_ids:
        repaired.pop(block_id, None)

    bays, bay_placed, bay_schedule, bay_loads = _rebuild_state(prob_info, repaired)
    w1, w2, w3 = _weights(prob_info)
    new_assignments = baseline_greedy._place_blocks(
        target_ids,
        prob_info["blocks"],
        bays,
        bay_placed,
        bay_schedule,
        bay_loads,
        w1,
        w2,
        w3,
        forced_ids=set(),
        prev_assignments=previous_subset,
    )
    repaired.update(new_assignments)
    return repaired


def _try_greedy_research(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    timelimit: float,
    tier: str,
) -> tuple[dict, dict]:
    if tier in {"very_short", "short"}:
        return base_solution, base_result

    budget = _repair_budget(timelimit, remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    base_assignments = _solution_to_assignments(base_solution)
    tardy_block_ids = _tardy_block_ids(prob_info, base_assignments, _move_limit(tier))
    if not tardy_block_ids:
        return base_solution, base_result

    deadline = time.time() + budget
    best_solution = base_solution
    best_result = base_result
    for prefix_len in _checkpoint_counts(len(tardy_block_ids), tier):
        if time.time() >= deadline:
            break
        candidate_assignments = _greedy_research_prefix(
            prob_info,
            base_assignments,
            tardy_block_ids,
            prefix_len,
        )
        candidate_solution = v001._solution_from_assignments(candidate_assignments)
        candidate_result = v001.check_feasibility(prob_info, candidate_solution)
        print(
            f"[baseline_hh reboot_v064] diffuse_greedy_research instance={prob_info.get('name')} "
            f"tier={tier} moved={prefix_len} feasible={candidate_result.get('feasible')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        if _result_key(candidate_result) < _result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    features = _selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))

    base_solution = v063.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not _matches_threebay_diffuse_moderate_class(features)
        or float(base_result.get("obj1") or 0.0) <= 3000.0
    ):
        return base_solution

    elapsed = time.time() - started
    remaining = max(0.0, float(timelimit) - elapsed)
    if remaining <= _dynamic_reserve(float(timelimit)) + 2.0:
        print(
            f"[baseline_hh reboot_v064] skip_diffuse_research instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_greedy_research(
        prob_info,
        base_solution,
        base_result,
        remaining,
        float(timelimit),
        tier,
    )
    if _result_key(research_result) < _result_key(base_result):
        print(
            f"[baseline_hh reboot_v064] selected_diffuse_research instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v064] keep_warm_start instance={prob_info.get('name')} "
        f"best_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
