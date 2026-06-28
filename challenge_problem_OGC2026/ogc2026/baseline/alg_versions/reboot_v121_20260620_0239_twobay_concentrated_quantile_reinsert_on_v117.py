"""reboot_v121_20260620_0239_twobay_concentrated_quantile_reinsert_on_v117.py

Strategy:
    Keep trusted v117 as the default path, then apply a bounded deep
    quantile-sampled single-block reinsertion only on the two-bay concentrated
    high-proc tail subtype.

Metadata:
    version_id: reboot_v121_20260620_0239_twobay_concentrated_quantile_reinsert_on_v117
    parent_version: reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116
    status: candidate
    timestamp: 2026-06-20 02:39 KST
    strategy:
        - Preserve v117 unchanged outside the target subtype.
        - Build the trusted v117 warm start first.
        - On the target subtype, try a small shortlist of tardy blocks and
          reinsert exactly one block with a deep quantile-sampled position
          search.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The remaining two-bay concentrated high-proc tail is driven by one
        poorly placed tardy block. A deeper one-block local move on top of the
        v117 warm start can improve T without reopening the destructive fresh
        rebuild failure mode.
    intended_metric_target:
        - improve prob25-like and prob27-like rows
        - preserve accepted_for_score 40/40
        - reduce total T, avg T, and the high-T tail
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116
"""

from __future__ import annotations

import time

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116 as v117


ACTIVE_VERSION = "reboot_v121_20260620_0239_twobay_concentrated_quantile_reinsert_on_v117"


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
    pref_gap_values = []
    for block in blocks:
        prefs = [float(value) for value in block.get("bay_preferences", [])]
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
            sorted_prefs = sorted(prefs, reverse=True)
            if len(sorted_prefs) >= 2:
                pref_gap_values.append(sorted_prefs[0] - sorted_prefs[1])
            else:
                pref_gap_values.append(sorted_prefs[0])
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

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": _mean(proc_values),
        "slack_mean": _mean(slack_values),
        "pref_concentration": pref_concentration,
        "pref_pressure": pref_pressure,
        "pref_gap_mean": _mean(pref_gap_values),
    }


def _matches_twobay_concentrated_tail_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 2
        and int(features["blocks"]) >= 100
        and features["proc_mean"] >= 20.0
        and features["slack_mean"] >= 4.5
        and features["pref_concentration"] >= 0.60
        and features["pref_pressure"] >= 0.59
        and features["pref_gap_mean"] >= 60.0
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 2.4,
        "long": 3.0,
        "very_long": 3.6,
    }[tier]
    return min(cap, remaining)


def _candidate_limit(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 4,
        "long": 5,
        "very_long": 6,
    }[tier]


def _target_block_ids(
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

        prefs = [float(value) for value in block["bay_preferences"]]
        bay_id = int(assignment["bay_id"])
        pref_penalty = max(prefs) - prefs[bay_id]
        entry_delay = int(assignment["entry_time"]) - release
        score = tardiness + 0.60 * entry_delay + 0.20 * pref_penalty
        ranked.append((score, tardiness, entry_delay, pref_penalty, block_id))

    ranked.sort(reverse=True)
    return [block_id for _, _, _, _, block_id in ranked[:limit]]


def _try_quantile_shortlist_reinsert(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    deadline = time.time() + budget
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = _target_block_ids(
        prob_info,
        base_assignments,
        _candidate_limit(tier),
    )
    if not target_block_ids:
        return base_solution, base_result

    max_positions = {
        "standard": 24,
        "long": 32,
        "very_long": 40,
    }[tier]

    best_solution = base_solution
    best_result = base_result
    attempted = []

    for target_block_id in target_block_ids:
        if time.time() >= deadline:
            break

        candidate_assignments = v080._quantile_single_reinsert(
            prob_info,
            base_assignments,
            target_block_id,
            max_positions=max_positions,
            deadline=deadline,
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

    print(
        f"[baseline_hh reboot_v121] twobay_concentrated_quantile instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    tier = v064.v050._time_tier(float(timelimit))
    features = _selector_features(prob_info)

    base_solution = v117.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or tier in {"very_short", "short"}
        or not _matches_twobay_concentrated_tail_class(features)
        or float(base_result.get("obj1") or 0.0) < 2000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= _dynamic_reserve(float(timelimit)) + 2.0:
        print(
            f"[baseline_hh reboot_v121] skip_twobay_concentrated_quantile instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_quantile_shortlist_reinsert(
        prob_info,
        base_solution,
        base_result,
        remaining - _dynamic_reserve(float(timelimit)),
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v121] selected_twobay_concentrated_quantile instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v121] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
