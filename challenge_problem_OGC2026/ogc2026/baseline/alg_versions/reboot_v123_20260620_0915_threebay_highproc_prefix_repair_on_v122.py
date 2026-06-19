"""reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122.py

Strategy:
    Keep trusted v122 as the default path, then apply a bounded multi-block
    tardy-prefix rebuild only on the three-bay high-proc tail family.

Metadata:
    version_id: reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122
    parent_version: reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117
    status: candidate
    timestamp: 2026-06-20 09:15 KST
    strategy:
        - Preserve v122 unchanged outside the target subtype.
        - Build the trusted v122 warm start first.
        - On the target subtype only, rebuild a short top-tardy prefix of the
          current assignments with checker validation after each checkpoint.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The three-bay high-proc tail is limited by a small interacting tardy
        set. Single-block reinsertion is too weak and fresh direct rebuilds are
        too destructive, but a bounded multi-block prefix repair can reduce T
        while preserving the rest of the trusted warm start.
    intended_metric_target:
        - improve prob26/prob28/prob33/prob38-like rows
        - preserve accepted_for_score 40/40
        - reduce total T, avg T, and the high-T tail
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117 as v122


ACTIVE_VERSION = "reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]

    top_choices = []
    pref_gap_values = []
    tight_count = 0
    for block in blocks:
        release = float(block.get("release_time", 0.0))
        due = float(block.get("due_date", 0.0))
        proc = float(block.get("processing_time", 0.0))
        if due - release - proc <= 2.0:
            tight_count += 1

        prefs = list(block.get("bay_preferences", []))
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
            ordered = sorted((float(value) for value in prefs), reverse=True)
            pref_gap_values.append(ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0))

    pref_conc = 0.0
    if top_choices and blocks:
        pref_conc = max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": _mean(proc_values),
        "tight_slack_ratio": tight_count / len(blocks) if blocks else 0.0,
        "pref_concentration": pref_conc,
        "pref_gap_mean": _mean(pref_gap_values),
    }


def _time_tier(timelimit: float) -> str:
    if timelimit < 25.0:
        return "very_short"
    if timelimit < 45.0:
        return "short"
    if timelimit < 90.0:
        return "standard"
    if timelimit < 300.0:
        return "long"
    return "very_long"


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _matches_threebay_highproc_tail(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and int(features["blocks"]) >= 150
        and features["proc_mean"] >= 16.0
        and 0.20 <= features["tight_slack_ratio"] <= 0.40
        and features["pref_gap_mean"] >= 48.0
        and 0.40 <= features["pref_concentration"] <= 0.80
    )


def _repair_budget(remaining: float, reserve: float, tier: str) -> float:
    available = max(0.0, remaining - reserve - 0.5)
    cap = {
        "standard": 3.0,
        "long": 5.0,
        "very_long": 7.0,
    }.get(tier, 0.0)
    return min(cap, available)


def _move_limit(tier: str) -> int:
    return {
        "standard": 3,
        "long": 4,
        "very_long": 5,
    }.get(tier, 0)


def _checkpoint_counts(move_limit: int) -> list[int]:
    counts = []
    for prefix_len in (2, 3, 4, 5, 6):
        if prefix_len <= move_limit:
            counts.append(prefix_len)
    return counts


def _min_headroom(tier: str) -> float:
    return {
        "standard": 20.0,
        "long": 18.0,
        "very_long": 16.0,
    }.get(tier, float("inf"))


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result.get("obj1", float("inf"))),
        float(result.get("objective", float("inf"))),
        float(result.get("obj2", float("inf"))),
        float(result.get("obj3", float("inf"))),
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
) -> tuple[list[object], list[list[object]], list[list[tuple[int, int]]], list[float]]:
    from utils import Bay, Block

    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info["bays"])]
    bay_placed: list[list[object]] = [[] for _ in bays]
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
    import baseline_greedy

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


def _try_prefix_repair(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    timelimit: float,
    overall_started: float,
    tier: str,
) -> tuple[dict, dict]:
    remaining = max(0.0, timelimit - (time.time() - overall_started))
    reserve = _dynamic_reserve(timelimit)
    budget = _repair_budget(remaining, reserve, tier)
    move_limit = _move_limit(tier)
    if budget <= 0.0 or move_limit < 2:
        return base_solution, base_result

    base_assignments = _solution_to_assignments(base_solution)
    tardy_block_ids = _tardy_block_ids(prob_info, base_assignments, move_limit)
    if len(tardy_block_ids) < 2:
        return base_solution, base_result

    deadline = time.time() + budget
    best_solution = base_solution
    best_result = base_result

    for prefix_len in _checkpoint_counts(len(tardy_block_ids)):
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
            f"[baseline_hh reboot_v123] highproc_prefix_repair instance={prob_info.get('name')} "
            f"tier={tier} moved={prefix_len} feasible={candidate_result.get('feasible')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        if _result_key(candidate_result) < _result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result

    return best_solution, best_result


def _parent_timelimit(timelimit: float, target_match: bool) -> float:
    if target_match:
        return timelimit
    return max(1.0, timelimit - 1.0)


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    overall_started = time.time()
    tier = _time_tier(float(timelimit))
    features = _selector_features(prob_info)
    target_match = _matches_threebay_highproc_tail(features)

    base_solution = v122.algorithm(prob_info, _parent_timelimit(float(timelimit), target_match))
    base_result = v001.check_feasibility(prob_info, base_solution)

    if (
        tier in {"very_short", "short"}
        or not base_result.get("feasible")
        or not target_match
        or float(base_result.get("obj1") or 0.0) < 2000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - overall_started))
    reserve = _dynamic_reserve(float(timelimit))
    headroom = _min_headroom(tier)
    if remaining <= reserve + headroom:
        print(
            f"[baseline_hh reboot_v123] skip_highproc_prefix_guard "
            f"instance={prob_info.get('name')} tier={tier} remaining={remaining:.2f}s "
            f"reserve={reserve:.2f}s headroom={headroom:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result = _try_prefix_repair(
        prob_info,
        base_solution,
        base_result,
        float(timelimit),
        overall_started,
        tier,
    )
    if _result_key(best_result) < _result_key(base_result):
        print(
            f"[baseline_hh reboot_v123] selected_highproc_prefix_repair "
            f"instance={prob_info.get('name')} T={best_result.get('obj1')} "
            f"objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v123] keep_v122_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={best_result.get('obj1')}"
    )
    return base_solution
