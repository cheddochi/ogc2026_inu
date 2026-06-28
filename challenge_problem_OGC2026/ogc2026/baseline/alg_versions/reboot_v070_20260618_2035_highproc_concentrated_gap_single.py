"""reboot_v070_20260618_2035_highproc_concentrated_gap_single.py

Strategy:
    Keep trusted v069 as the default path, then re-search one selected tardy
    block on a high-proc concentrated-preference roomy-slack subtype.

Metadata:
    version_id: reboot_v070_20260618_2035_highproc_concentrated_gap_single
    parent_version: reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single
    status: accepted BEST
    timestamp: 2026-06-18 20:35 KST
    strategy:
        - Preserve v069 unchanged outside the target subtype.
        - Build the trusted v069 warm start first.
        - On the target subtype, choose one tardy block from the top tardy
          shortlist by the score `2 * current preference penalty + release_time`.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The remaining high-proc concentrated-preference family is limited by
        which tardy block gets repaired, not by whether single-block repair is
        available. A penalty-and-release-aware pick should outperform the old
        target on that subtype.
    intended_metric_target:
        - improve prob25-like, prob27-like, prob31-like, and prob40-like rows
        - preserve representative core-9 smoke rows
        - improve avg objective versus trusted v069
    validation_status:
        full_train40_accepted
    benchmark_evidence_path:
        - reports/ogc2026_reboot_v001/smoke_reboot_v070_core9_20260618_001
        - reports/ogc2026_reboot_v001/target_reboot_v070_highproc_concentrated_probe_20260618_001
        - reports/ogc2026_reboot_v001/stress_reboot_v070_prob31_short45_20260618_001
        - reports/ogc2026_reboot_v001/full_reboot_v070_train40_20260618_001
    rollback_target: reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single
"""

from __future__ import annotations

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single as v069


ACTIVE_VERSION = "reboot_v070_20260618_2035_highproc_concentrated_gap_single"


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


def _matches_highproc_concentrated_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) in {2, 4}
        and int(features["blocks"]) >= 100
        and features["proc_mean"] >= 21.0
        and features["slack_mean"] >= 4.6
        and features["pref_concentration"] >= 0.60
        and features["pref_pressure"] >= 0.59
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 8.0,
        "long": 10.0,
        "very_long": 12.0,
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
        block = blocks[block_id]
        prefs = list(block["bay_preferences"])
        bay_id = int(assignment["bay_id"])
        pref_penalty = max(prefs) - prefs[bay_id]
        ranked.append(
            (
                block_id,
                tardiness,
                pref_penalty,
                float(block.get("release_time", 0.0)),
                due,
            )
        )

    if not ranked:
        return []

    top_tardy = sorted(ranked, key=lambda item: (-item[1], -item[2], item[4]))[:shortlist]
    max_tardiness = max(item[1] for item in top_tardy)
    tardiness_floor = max(40.0, max_tardiness * 0.70)
    eligible = [item for item in top_tardy if item[1] >= tardiness_floor]
    if not eligible:
        eligible = top_tardy[:1]

    best_block_id, _, _, _, _ = max(
        eligible,
        key=lambda item: (2.0 * item[2] + item[3], item[1], -item[4]),
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
        f"[baseline_hh reboot_v070] highproc_concentrated_gap instance={prob_info.get('name')} "
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

    base_solution = v069.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not _matches_highproc_concentrated_class(features)
        or float(base_result.get("obj1") or 0.0) < 2000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (v064.time.time() - started))
    if remaining <= _dynamic_reserve(float(timelimit)) + 5.0:
        print(
            f"[baseline_hh reboot_v070] skip_highproc_concentrated instance={prob_info.get('name')} "
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
            f"[baseline_hh reboot_v070] selected_highproc_concentrated instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v070] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
