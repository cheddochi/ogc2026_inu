"""reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single.py

Strategy:
    Keep trusted v068 as the default path, then re-search one selected tardy
    block on a 3-bay medium diffuse-preference tight-slack subtype.

Metadata:
    version_id: reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single
    parent_version: reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research
    status: accepted BEST
    timestamp: 2026-06-18 19:50 KST
    strategy:
        - Preserve v068 unchanged outside the target subtype.
        - Build the trusted v068 warm start first.
        - On the target subtype, choose one tardy block from the top tardy
          shortlist by preference-gap pressure instead of by raw tardiness.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The medium 3-bay diffuse-preference class is sensitive to which tardy
        block gets repaired. A preference-gap-aware single-block choice should
        outperform the old worst-tardy pick on that subtype.
    intended_metric_target:
        - improve prob32-like and prob33-like rows
        - preserve representative core-9 smoke rows
        - improve avg objective versus trusted v068
    validation_status:
        full_train40_accepted
    benchmark_evidence_path:
        - reports/ogc2026_reboot_v001/smoke_reboot_v069_core9_20260618_001
        - reports/ogc2026_reboot_v001/target_reboot_v069_medium_diffuse_probe_20260618_001
        - reports/ogc2026_reboot_v001/full_reboot_v069_train40_20260618_001
    rollback_target: reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research
"""

from __future__ import annotations

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research as v068


ACTIVE_VERSION = "reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single"


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
        "pref_concentration": pref_concentration,
        "pref_pressure": pref_pressure,
        "slack_mean": _mean(slack_values),
    }


def _matches_threebay_medium_diffuse_gap_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and 200 <= int(features["blocks"]) < 240
        and 11.0 <= features["proc_mean"] <= 17.5
        and 0.34 <= features["pref_concentration"] <= 0.46
        and 0.35 <= features["pref_pressure"] <= 0.42
        and features["slack_mean"] <= 4.0
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 12.0,
        "long": 14.0,
        "very_long": 18.0,
    }[tier]
    return min(cap, remaining)


def _target_block_ids(prob_info: dict, assignments: dict[int, dict], shortlist: int = 8) -> list[int]:
    ranked = []
    blocks = prob_info["blocks"]
    for block_id, assignment in assignments.items():
        due = int(blocks[block_id]["due_date"])
        tardiness = max(0, int(assignment["exit_time"]) - due)
        if tardiness <= 0:
            continue
        prefs = list(blocks[block_id]["bay_preferences"])
        sorted_prefs = sorted(float(value) for value in prefs)
        pref_gap = sorted_prefs[-1] - sorted_prefs[-2] if len(sorted_prefs) >= 2 else sorted_prefs[-1]
        ranked.append((block_id, tardiness, pref_gap, due))

    if not ranked:
        return []

    max_tardiness = max(tardiness for _, tardiness, _, _ in ranked)
    tardiness_floor = max(15.0, max_tardiness * 0.25)
    tardy_shortlist = [
        item for item in sorted(ranked, key=lambda item: (-item[1], -item[2], item[3]))[:shortlist]
        if item[1] >= tardiness_floor
    ]
    if not tardy_shortlist:
        tardy_shortlist = sorted(ranked, key=lambda item: (-item[1], -item[2], item[3]))[:1]

    best_block_id, _, _, _ = max(
        tardy_shortlist,
        key=lambda item: (item[2], item[1], -item[3]),
    )
    return [best_block_id]


def _try_gap_single_research(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    deadline = v064.time.time() + budget
    if v064.time.time() >= deadline:
        return base_solution, base_result

    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = _target_block_ids(prob_info, base_assignments)
    if not target_block_ids:
        return base_solution, base_result

    candidate_assignments = v064._greedy_research_prefix(
        prob_info,
        base_assignments,
        target_block_ids,
        1,
    )
    candidate_solution = v064.v001._solution_from_assignments(candidate_assignments)
    candidate_result = v064.v001.check_feasibility(prob_info, candidate_solution)
    print(
        f"[baseline_hh reboot_v069] threebay_medium_diffuse_gap instance={prob_info.get('name')} "
        f"tier={tier} target_block={target_block_ids[0]} feasible={candidate_result.get('feasible')} "
        f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
    )
    if v064._result_key(candidate_result) < v064._result_key(base_result):
        return candidate_solution, candidate_result
    return base_solution, base_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = v064.time.time()
    features = _selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v068.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not _matches_threebay_medium_diffuse_gap_class(features)
        or float(base_result.get("obj1") or 0.0) < 3000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (v064.time.time() - started))
    if remaining <= _dynamic_reserve(float(timelimit)) + 10.0:
        print(
            f"[baseline_hh reboot_v069] skip_threebay_medium_diffuse instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_gap_single_research(
        prob_info,
        base_solution,
        base_result,
        remaining - _dynamic_reserve(float(timelimit)),
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v069] selected_threebay_medium_diffuse instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v069] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
