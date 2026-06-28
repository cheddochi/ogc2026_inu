"""reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio.py

Strategy:
    Keep trusted v073 as the default path, then try a tiny bounded one-block
    reinsertion portfolio on the 4-bay high-proc dense-preference family.

Metadata:
    version_id: reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio
    parent_version: reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert
    status: candidate
    timestamp: 2026-06-18 23:02 KST
    strategy:
        - Preserve v073 unchanged outside the target subtype.
        - Build the trusted v073 warm start first.
        - On the target subtype, try bounded one-block reinsertion on a short
          tardy shortlist and keep the best officially feasible result.
        - Keep only strictly better results.
    hypothesis:
        The current warm start is already near a local optimum on the 4-bay
        high-proc family. A tiny portfolio over a few tardy blocks can capture
        residual preference/placement slack without paying for another deep
        search phase.
    intended_metric_target:
        - improve prob40-like rows
        - preserve representative core-9 smoke rows
        - improve avg objective versus trusted v073
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert
"""

from __future__ import annotations

from alg_versions import reboot_v063_20260618_1605_prob40like_direct_first_due_release as v063
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert as v073


ACTIVE_VERSION = "reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio"


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

    imbalance = 0.0
    if top_choices and len(bays) > 1 and blocks:
        counts = [top_choices.count(bay_id) for bay_id in range(len(bays))]
        imbalance = (max(counts) - min(counts)) / len(blocks)

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
        "workload_imbalance_pressure": imbalance,
        "slack_mean": _mean(slack_values),
    }


def _matches_fourbay_highproc_dense_family(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 4
        and int(features["blocks"]) >= 200
        and features["proc_mean"] >= 20.0
        and features["pref_concentration"] >= 0.72
        and features["pref_pressure"] >= 0.68
        and features["workload_imbalance_pressure"] >= 0.70
        and features["slack_mean"] >= 4.8
    )


def _family_direct_budget(timelimit: float, tier: str) -> float:
    return v063._direct_budget(timelimit, tier)


def _candidate_limit(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 3,
        "long": 3,
        "very_long": 4,
    }[tier]


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 0.9,
        "long": 1.2,
        "very_long": 1.6,
    }[tier]
    return min(cap, remaining)


def _try_fast_reinsert_portfolio(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    started = v064.time.time()
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = v064._tardy_block_ids(prob_info, base_assignments, _candidate_limit(tier))
    if not target_block_ids:
        return base_solution, base_result

    best_solution = base_solution
    best_result = base_result
    attempted = []

    for target_block_id in target_block_ids:
        if v064.time.time() - started > budget:
            break
        candidate_assignments = v073._limited_single_reinsert(
            prob_info,
            base_assignments,
            target_block_id,
            max_positions=8,
            max_orients=4,
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
        f"[baseline_hh reboot_v074] fourbay_highproc_fast_reinsert instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = v064.time.time()
    features = _selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v073.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    family_budget = _family_direct_budget(float(timelimit), tier)
    if (
        not base_result.get("feasible")
        or not _matches_fourbay_highproc_dense_family(features)
        or family_budget < 45.0
        or float(base_result.get("obj1") or 0.0) <= 2500.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (v064.time.time() - started))
    if remaining <= 0.5:
        print(
            f"[baseline_hh reboot_v074] skip_fourbay_highproc_fast_reinsert instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_fast_reinsert_portfolio(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v074] selected_fourbay_highproc_fast_reinsert instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v074] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
