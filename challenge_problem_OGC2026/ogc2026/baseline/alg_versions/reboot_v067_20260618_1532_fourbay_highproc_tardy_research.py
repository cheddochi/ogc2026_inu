"""reboot_v067_20260618_1532_fourbay_highproc_tardy_research.py

Strategy:
    Keep trusted v066 as the default path, then re-search only the top tardy
    1-2 blocks on a narrow 4-bay high-proc dense-preference class.

Metadata:
    version_id: reboot_v067_20260618_1532_fourbay_highproc_tardy_research
    parent_version: reboot_v066_20260618_1755_twobay_small_highproc_due_long
    status: accepted
    timestamp: 2026-06-18 15:32 KST
    strategy:
        - Preserve v066 unchanged outside the target subtype.
        - Build the trusted v066 warm start first.
        - On the target subtype, remove and greedily re-place only the top
          tardy 1-2 blocks under a tight remaining-time guard.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The 4-bay high-proc dense-preference subtype already has the right
        direct-first warm start, but a small tardy tail remains that can be
        improved by re-searching just the worst tardy blocks.
    intended_metric_target:
        - improve prob31-like and prob40-like rows
        - preserve representative core-9 smoke rows
        - improve avg objective versus trusted v066
    validation_status:
        accepted_for_score=40/40 on full train40 benchmark
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v067_train40_20260618_001
    rollback_target: reboot_v066_20260618_1755_twobay_small_highproc_due_long
"""

from __future__ import annotations

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v066_20260618_1755_twobay_small_highproc_due_long as v066


ACTIVE_VERSION = "reboot_v067_20260618_1532_fourbay_highproc_tardy_research"


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


def _matches_fourbay_highproc_dense_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 4
        and int(features["blocks"]) >= 200
        and features["proc_mean"] >= 20.0
        and features["pref_concentration"] >= 0.75
        and features["pref_pressure"] >= 0.69
        and features["slack_mean"] >= 4.8
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _research_budget(timelimit: float, remaining: float, tier: str, blocks: int) -> float:
    reserve = _dynamic_reserve(timelimit)
    available = max(0.0, remaining - reserve)
    if tier in {"very_short", "short"}:
        return 0.0
    if blocks <= 220:
        cap = {"standard": 13.0, "long": 15.0, "very_long": 18.0}[tier]
    else:
        cap = {"standard": 8.5, "long": 10.0, "very_long": 12.0}[tier]
    return min(cap, available)


def _checkpoint_counts(features: dict[str, float], remaining: float, tier: str) -> list[int]:
    if tier in {"very_short", "short"}:
        return []
    counts = [1]
    if int(features["blocks"]) <= 220 and remaining >= _dynamic_reserve(60.0) + 12.0:
        counts.append(2)
    return counts


def _try_tardy_research(
    prob_info: dict,
    features: dict[str, float],
    base_solution: dict,
    base_result: dict,
    remaining: float,
    timelimit: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(timelimit, remaining, tier, int(features["blocks"]))
    if budget <= 0.0:
        return base_solution, base_result

    base_assignments = v064._solution_to_assignments(base_solution)
    tardy_block_ids = v064._tardy_block_ids(prob_info, base_assignments, 2)
    if not tardy_block_ids:
        return base_solution, base_result

    deadline = v064.time.time() + budget
    best_solution = base_solution
    best_result = base_result
    for prefix_len in _checkpoint_counts(features, remaining, tier):
        if prefix_len > len(tardy_block_ids) or v064.time.time() >= deadline:
            break
        candidate_assignments = v064._greedy_research_prefix(
            prob_info,
            base_assignments,
            tardy_block_ids,
            prefix_len,
        )
        candidate_solution = v064.v001._solution_from_assignments(candidate_assignments)
        candidate_result = v064.v001.check_feasibility(prob_info, candidate_solution)
        print(
            f"[baseline_hh reboot_v067] fourbay_highproc_tardy_research "
            f"instance={prob_info.get('name')} tier={tier} moved={prefix_len} "
            f"feasible={candidate_result.get('feasible')} T={candidate_result.get('obj1')} "
            f"objective={candidate_result.get('objective')}"
        )
        if v064._result_key(candidate_result) < v064._result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = v064.time.time()
    features = _selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v066.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not _matches_fourbay_highproc_dense_class(features)
        or float(base_result.get("obj1") or 0.0) < 2500.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (v064.time.time() - started))
    if remaining <= _dynamic_reserve(float(timelimit)) + 6.0:
        print(
            f"[baseline_hh reboot_v067] skip_fourbay_highproc instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_tardy_research(
        prob_info,
        features,
        base_solution,
        base_result,
        remaining,
        float(timelimit),
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v067] selected_fourbay_highproc instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v067] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
