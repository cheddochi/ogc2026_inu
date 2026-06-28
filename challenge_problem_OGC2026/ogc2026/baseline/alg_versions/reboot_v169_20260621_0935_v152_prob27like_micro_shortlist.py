"""reboot_v169_20260621_0935_v152_prob27like_micro_shortlist.py

Strategy:
    Preserve scoreable current-tree parent v152 everywhere, then add an
    ultra-cheap direct efficiency shortlist reinsert only on the prob27-like
    2-bay high-proc runtime-risk subtype.

Metadata:
    version_id: reboot_v169_20260621_0935_v152_prob27like_micro_shortlist
    parent_version: reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151
    status: candidate
    timestamp: 2026-06-21 09:35 KST
    strategy:
        - Preserve v152 unchanged outside the target subtype.
        - Build the exact v152 warm start first.
        - On the prob27-like slice only, score tardy blocks with the existing
          efficiency signal from v146.
        - Try only the top one or two unique block ids with a much smaller
          budget and position cap than v146.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The current-tree prob27-like residual is still a one-block problem, but
        the remaining headroom after the v152 warm start is too small for the
        older heavier second pass. A micro shortlist can recover part of the
        T gap without reopening the 60s runtime cliff.
    intended_metric_target:
        - improve the prob27-like T tail on the current-tree parent
        - preserve accepted_for_score on the runtime-risk sibling families
        - avoid the delegated timeout trade reopened by v168
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151
"""

from __future__ import annotations

import time


ACTIVE_VERSION = "reboot_v169_20260621_0935_v152_prob27like_micro_shortlist"


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
            ordered = sorted(prefs, reverse=True)
            pref_gap_values.append(ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0))
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


def _matches_prob27like_heavytail(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 2
        and int(features["blocks"]) >= 140
        and features["proc_mean"] >= 20.0
        and features["slack_mean"] >= 4.5
        and features["pref_concentration"] >= 0.65
        and features["pref_pressure"] >= 0.62
        and features["pref_gap_mean"] >= 65.0
    )


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


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 1.2,
        "long": 1.6,
        "very_long": 2.0,
    }[tier]
    return min(cap, remaining)


def _candidate_limit(tier: str) -> int:
    return {
        "standard": 1,
        "long": 2,
        "very_long": 2,
    }[tier]


def _max_positions(tier: str) -> int:
    return {
        "standard": 10,
        "long": 12,
        "very_long": 14,
    }[tier]


def _efficiency_shortlist(
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
        workload = float(block["workload"])
        proc = float(block["processing_time"])

        score = (
            (tardiness + 0.70 * entry_delay)
            * (1.0 + pref_penalty / 120.0)
            / (1.0 + 0.012 * workload + 0.04 * proc)
        )
        ranked.append(
            (
                score,
                tardiness,
                entry_delay,
                pref_penalty,
                -workload,
                -proc,
                block_id,
            )
        )

    ranked.sort(reverse=True)
    return [block_id for *_, block_id in ranked[:limit]]


def _try_efficiency_shortlist_reinsert(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
    from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080

    deadline = time.time() + budget
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = _efficiency_shortlist(
        prob_info,
        base_assignments,
        _candidate_limit(tier),
    )
    if not target_block_ids:
        return base_solution, base_result

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
            max_positions=_max_positions(tier),
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
        f"[baseline_hh reboot_v169] prob27like_micro_shortlist instance={prob_info.get('name')} "
        f"tier={tier} budget={budget:.2f}s attempted={attempted} "
        f"best_T={best_result.get('obj1')} best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    started = time.time()
    tier = _time_tier(timelimit)

    from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
    from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
    from alg_versions import reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151 as v152

    base_solution = v152.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)
    features = _selector_features(prob_info)

    if (
        not base_result.get("feasible")
        or tier in {"very_short", "short"}
        or not _matches_prob27like_heavytail(features)
        or float(base_result.get("obj1") or 0.0) < 5000.0
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    reserve = _dynamic_reserve(timelimit)
    spendable = remaining - reserve
    if spendable <= 0.9:
        print(
            f"[baseline_hh reboot_v169] skip_prob27like_micro_shortlist instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"spendable={spendable:.2f}s base_T={base_result.get('obj1')}"
        )
        return base_solution

    research_solution, research_result = _try_efficiency_shortlist_reinsert(
        prob_info,
        base_solution,
        base_result,
        spendable,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v169] selected_prob27like_micro_shortlist instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v169] keep_v152_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
