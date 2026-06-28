"""reboot_v186_20260625_familyA_warm_tardy_repair_on_v178.py

Strategy:
    Keep trusted v178 as the default line, then run a bounded Family A
    warm-start tardy repair loop on top of the exact v178 solution.

Metadata:
    version_id: reboot_v186_20260625_familyA_warm_tardy_repair_on_v178
    parent_version: reboot_v178_20260625_v142_specialist_slices_on_v177
    status: candidate
    timestamp: 2026-06-25 KST
    strategy:
        - Preserve v178 unchanged outside the Family A tight-slack feature band.
        - Build the exact v178 warm start first and require it to already be
          scoreable before spending any extra budget.
        - On the target band only, rank warm-start tardy blocks and try a short
          quantile single-reinsert sequence under a hard deadline.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The remaining first20 backlog is not a from-scratch constructive issue;
        it is a small tardy-cluster repair problem on top of the trusted v178
        warm start. Repairing that cluster directly should be stronger than
        replaying weaker direct builders.
    intended_metric_target:
        - reduce first20 Total T / Avg T / T>0 count
        - preserve accepted_for_score 40/40
        - keep Family B guard behavior from v178
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v178_20260625_v142_specialist_slices_on_v177
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v169_20260621_0935_v152_prob27like_micro_shortlist as v169
from alg_versions import reboot_v178_20260625_v142_specialist_slices_on_v177 as v178


ACTIVE_VERSION = "reboot_v186_20260625_familyA_warm_tardy_repair_on_v178"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    weights = prob_info.get("weights", {})

    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    rel_values = [float(block.get("release_time", 0.0)) for block in blocks]
    due_values = [float(block.get("due_date", 0.0)) for block in blocks]

    top_choices = []
    pref_weight = [0.0] * len(bays)
    for block in blocks:
        prefs = [float(value) for value in block.get("bay_preferences", [])]
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += pref_value

    pref_concentration = 0.0
    if top_choices and blocks:
        pref_concentration = (
            max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)
        )

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    slack_values = [
        due - rel - proc
        for due, rel, proc in zip(due_values, rel_values, proc_values)
    ]
    tight_slack_ratio = 0.0
    if slack_values:
        tight_slack_ratio = sum(1 for value in slack_values if value <= 1.0) / len(slack_values)

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "w1": float(weights.get("w1", 1.0)),
        "proc_mean": _mean(proc_values),
        "slack_mean": _mean(slack_values),
        "tight_slack_ratio": tight_slack_ratio,
        "pref_concentration": pref_concentration,
        "pref_pressure": pref_pressure,
    }


def _matches_family_a_tightslack(features: dict[str, float]) -> bool:
    return (
        2 <= int(features["bays"]) <= 5
        and int(features["blocks"]) >= 90
        and features["w1"] >= 10000.0
        and features["proc_mean"] <= 8.6
        and features["slack_mean"] <= 1.8
        and features["tight_slack_ratio"] >= 0.48
        and features["pref_concentration"] <= 0.55
        and features["pref_pressure"] <= 0.55
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _repair_budget(remaining: float, tier: str, features: dict[str, float]) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 6.0,
        "long": 9.0,
        "very_long": 12.0,
    }[tier]
    if features["blocks"] >= 240:
        cap += 1.5
    return min(cap, remaining)


def _repair_steps(tier: str) -> int:
    return {
        "standard": 2,
        "long": 3,
        "very_long": 4,
    }[tier]


def _max_positions(tier: str) -> int:
    return {
        "standard": 24,
        "long": 32,
        "very_long": 40,
    }[tier]


def _family_a_tardy_shortlist(
    prob_info: dict,
    assignments: dict[int, dict],
    limit: int,
) -> list[int]:
    ranked = []
    blocks = prob_info["blocks"]
    for block_id, assignment in assignments.items():
        block = blocks[block_id]
        due = int(block["due_date"])
        release = int(block["release_time"])
        proc = int(block["processing_time"])
        tardiness = max(0, int(assignment["exit_time"]) - due)
        if tardiness <= 0:
            continue
        slack = due - release - proc
        prefs = [float(value) for value in block["bay_preferences"]]
        bay_id = int(assignment["bay_id"])
        pref_penalty = max(prefs) - prefs[bay_id]
        ranked.append(
            (
                -tardiness,
                slack,
                pref_penalty,
                due,
                -proc,
                block_id,
            )
        )
    ranked.sort()
    return [block_id for *_, block_id in ranked[:limit]]


def _try_family_a_warm_repair(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
    features: dict[str, float],
) -> tuple[dict, dict, list[tuple[int, float, float]]]:
    budget = _repair_budget(remaining, tier, features)
    if budget <= 0.0:
        return base_solution, base_result, []

    deadline = time.time() + budget
    best_solution = base_solution
    best_result = base_result
    accepted_moves: list[tuple[int, float, float]] = []

    for _ in range(_repair_steps(tier)):
        if time.time() >= deadline:
            break

        base_assignments = v064._solution_to_assignments(best_solution)
        shortlist = _family_a_tardy_shortlist(prob_info, base_assignments, 3)
        if not shortlist:
            break

        improved_this_round = False
        for block_id in shortlist:
            if time.time() >= deadline:
                break
            candidate_assignments = v080._quantile_single_reinsert(
                prob_info,
                base_assignments,
                block_id,
                max_positions=_max_positions(tier),
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
                    max_rounds=4,
                )
                if repaired_result.get("feasible"):
                    candidate_assignments = repaired_assignments
                    candidate_solution = v001._solution_from_assignments(candidate_assignments)
                    candidate_result = repaired_result

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
                improved_this_round = True
                break

        if not improved_this_round:
            break

    return best_solution, best_result, accepted_moves


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    started = time.time()
    tier = v169._time_tier(timelimit)

    base_solution = v178.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)
    features = _selector_features(prob_info)

    if (
        not base_result.get("feasible")
        or not _matches_family_a_tightslack(features)
        or float(base_result.get("obj1") or 0.0) <= 0.0
        or tier in {"very_short", "short"}
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    reserve = _dynamic_reserve(timelimit)
    spendable = remaining - reserve
    if spendable <= 1.0:
        print(
            f"[baseline_hh reboot_v186] skip_familyA_warm_repair instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result, accepted_moves = _try_family_a_warm_repair(
        prob_info,
        base_solution,
        base_result,
        spendable,
        tier,
        features,
    )
    print(
        f"[baseline_hh reboot_v186] familyA_warm_repair instance={prob_info.get('name')} "
        f"tier={tier} base_T={base_result.get('obj1')} best_T={best_result.get('obj1')} "
        f"accepted_moves={accepted_moves}"
    )
    if v064._result_key(best_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v186] selected_familyA_warm_repair instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution
    return base_solution
