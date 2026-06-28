"""reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single.py

Strategy:
    Keep trusted v070 as the default path, then re-search one selected tardy
    block only on the long-limit-opportunity slice of the 3-bay xlarge
    low-proc tight-slack family.

Metadata:
    version_id: reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single
    parent_version: reboot_v070_20260618_2035_highproc_concentrated_gap_single
    status: accepted BEST
    timestamp: 2026-06-18 21:35 KST
    strategy:
        - Preserve v070 unchanged outside the target subtype.
        - Build the trusted v070 warm start first.
        - On the target subtype, run the v071 penalty-and-release single-block
          selector only when the warm start leaves large headroom.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The xlarge 3-bay low-proc family splits into runtime-risk and
        long-limit-opportunity cases. The extra single-block repair should be
        reserved for the latter.
    intended_metric_target:
        - improve prob39-like rows
        - preserve representative core-9 smoke rows
        - improve avg objective versus trusted v070
    validation_status:
        full_train40_accepted
    benchmark_evidence_path:
        - reports/ogc2026_reboot_v001/smoke_reboot_v072_core9_20260618_001
        - reports/ogc2026_reboot_v001/target_reboot_v072_threebay_xlarge_probe_20260618_001
        - reports/ogc2026_reboot_v001/stress_reboot_v072_prob39_short45_20260618_001
        - reports/ogc2026_reboot_v001/full_reboot_v072_train40_20260618_001
    rollback_target: reboot_v070_20260618_2035_highproc_concentrated_gap_single
"""

from __future__ import annotations

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v070_20260618_2035_highproc_concentrated_gap_single as v070


ACTIVE_VERSION = "reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single"


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
    slack_values = [
        due - rel - proc
        for due, rel, proc in zip(due_values, rel_values, proc_values)
    ]
    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": _mean(proc_values),
        "slack_mean": _mean(slack_values),
    }


def _matches_threebay_xlarge_lowproc_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and int(features["blocks"]) >= 240
        and features["proc_mean"] < 12.0
        and features["slack_mean"] <= 2.3
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 6.0,
        "long": 8.0,
        "very_long": 10.0,
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
    tardiness_floor = max(20.0, max_tardiness * 0.40)
    eligible = [item for item in top_tardy if item[1] >= tardiness_floor]
    if not eligible:
        eligible = top_tardy[:1]

    best_block_id, _, _, _, _ = max(
        eligible,
        key=lambda item: (2.0 * item[2] + item[3], item[1], -item[4]),
    )
    return [best_block_id]


def _try_penalty_single_research(
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
        f"[baseline_hh reboot_v072] threebay_xlarge_lowproc_opportunity instance={prob_info.get('name')} "
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

    base_solution = v070.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not _matches_threebay_xlarge_lowproc_class(features)
        or float(base_result.get("obj1") or 0.0) < 3000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (v064.time.time() - started))
    if remaining <= _dynamic_reserve(float(timelimit)) + 12.0:
        print(
            f"[baseline_hh reboot_v072] skip_threebay_xlarge_lowproc instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_penalty_single_research(
        prob_info,
        base_solution,
        base_result,
        remaining - _dynamic_reserve(float(timelimit)),
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v072] selected_threebay_xlarge_lowproc instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v072] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
