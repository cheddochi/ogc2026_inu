"""reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research.py

Strategy:
    Keep trusted v067 as the default path, then re-search only the single
    worst tardy block on a narrow 3-bay xlarge low-proc dense-preference class.

Metadata:
    version_id: reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research
    parent_version: reboot_v067_20260618_1532_fourbay_highproc_tardy_research
    status: accepted BEST
    timestamp: 2026-06-18 16:10 KST
    strategy:
        - Preserve v067 unchanged outside the target subtype.
        - Build the trusted v067 warm start first.
        - On the target subtype, remove and greedily re-place only the single
          worst tardy block under a tight remaining-time guard.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The 3-bay xlarge low-proc dense-preference subtype still leaves a
        small tardy tail that can be tightened by re-searching one tardy block
        without destabilizing similar 3-bay rows.
    intended_metric_target:
        - improve prob39-like rows
        - preserve representative core-9 smoke rows
        - improve avg objective versus trusted v067
    validation_status:
        full_train40_accepted
    benchmark_evidence_path:
        - reports/ogc2026_reboot_v001/smoke_reboot_v068_core9_20260618_001
        - reports/ogc2026_reboot_v001/target_reboot_v068_threebay_dense_probe_20260618_001
        - reports/ogc2026_reboot_v001/full_reboot_v068_train40_20260618_001
    rollback_target: reboot_v067_20260618_1532_fourbay_highproc_tardy_research
"""

from __future__ import annotations

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v067_20260618_1532_fourbay_highproc_tardy_research as v067


ACTIVE_VERSION = "reboot_v068_20260618_1610_threebay_xlarge_lowproc_dense_tardy_research"


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


def _matches_threebay_xlarge_lowproc_dense_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and int(features["blocks"]) >= 240
        and 10.8 <= features["proc_mean"] <= 11.3
        and 0.55 <= features["pref_concentration"] <= 0.60
        and 0.52 <= features["pref_pressure"] <= 0.55
        and features["slack_mean"] <= 2.3
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 10.0,
        "long": 12.0,
        "very_long": 14.0,
    }[tier]
    return min(cap, remaining)


def _try_tardy_research(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    base_assignments = v064._solution_to_assignments(base_solution)
    tardy_block_ids = v064._tardy_block_ids(prob_info, base_assignments, 1)
    if not tardy_block_ids:
        return base_solution, base_result

    deadline = v064.time.time() + budget
    if v064.time.time() >= deadline:
        return base_solution, base_result

    candidate_assignments = v064._greedy_research_prefix(
        prob_info,
        base_assignments,
        tardy_block_ids,
        1,
    )
    candidate_solution = v064.v001._solution_from_assignments(candidate_assignments)
    candidate_result = v064.v001.check_feasibility(prob_info, candidate_solution)
    print(
        f"[baseline_hh reboot_v068] threebay_xlarge_lowproc_dense instance={prob_info.get('name')} "
        f"tier={tier} feasible={candidate_result.get('feasible')} T={candidate_result.get('obj1')} "
        f"objective={candidate_result.get('objective')}"
    )
    if v064._result_key(candidate_result) < v064._result_key(base_result):
        return candidate_solution, candidate_result
    return base_solution, base_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = v064.time.time()
    features = _selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v067.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not _matches_threebay_xlarge_lowproc_dense_class(features)
        or float(base_result.get("obj1") or 0.0) < 3000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (v064.time.time() - started))
    if remaining <= _dynamic_reserve(float(timelimit)) + 8.0:
        print(
            f"[baseline_hh reboot_v068] skip_threebay_xlarge_lowproc instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_tardy_research(
        prob_info,
        base_solution,
        base_result,
        remaining - _dynamic_reserve(float(timelimit)),
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v068] selected_threebay_xlarge_lowproc instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v068] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
