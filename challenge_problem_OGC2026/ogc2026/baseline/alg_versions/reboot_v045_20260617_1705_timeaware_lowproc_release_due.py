"""reboot_v045_20260617_1705_timeaware_lowproc_release_due.py

Strategy:
    Keep trusted v044 as the fast feasible warm start, then use one bounded
    time-aware release_due candidate on a low-processing-time easy class.

Metadata:
    version_id: reboot_v045_20260617_1705_timeaware_lowproc_release_due
    parent_version: reboot_v044_20260617_1625_timeaware_two_bay_selector
    status: candidate
    timestamp: 2026-06-17 17:05 KST
    strategy:
        - Build the trusted v044 solution first.
        - For the low-proc 2/3-bay easy class, run one bounded `release_due`
          candidate only when enough wall time remains.
        - Keep the better feasible result.
    hypothesis:
        The current trusted BEST still leaves a cheap low-proc class on the
        table; a bounded release_due pass can improve many early/easy rows
        without threatening the runtime budget.
    intended_metric_target:
        - strong gains on prob_1, prob_2, prob_5, prob_6, prob_7, prob_9
    validation_status:
        accepted BEST on full train40; keep short-limit-risk and
        runtime-risk long-limit-utilization caution in metadata
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v045_train40_20260617_001
    rollback_target: reboot_v044_20260617_1625_timeaware_two_bay_selector
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v044_20260617_1625_timeaware_two_bay_selector as v044


ACTIVE_VERSION = "reboot_v045_20260617_1705_timeaware_lowproc_release_due"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    proc_mean = _mean(proc_values)

    top_choices = []
    pref_weight = [0.0] * len(bays)
    for block in blocks:
        prefs = list(block.get("bay_preferences", []))
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += float(pref_value)

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    imbalance_pressure = 0.0
    if top_choices and len(bays) > 1 and len(blocks) > 0:
        counts = [top_choices.count(bay_id) for bay_id in range(len(bays))]
        imbalance_pressure = (max(counts) - min(counts)) / len(blocks)

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": proc_mean,
        "pref_pressure": pref_pressure,
        "workload_imbalance_pressure": imbalance_pressure,
    }


def _matches_lowproc_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) in {2, 3}
        and int(features["blocks"]) <= 200
        and features["proc_mean"] <= 8.0
        and features["pref_pressure"] <= 0.55
        and features["workload_imbalance_pressure"] <= 0.12
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


def _should_try_improvement(timelimit: float, elapsed: float, features: dict[str, float], tier: str) -> bool:
    if tier in {"very_short", "short"}:
        return False
    if not _matches_lowproc_class(features):
        return False
    remaining = max(0.0, timelimit - elapsed)
    reserve = _dynamic_reserve(timelimit)
    return remaining > reserve + timelimit * 0.10


def _dynamic_budget(timelimit: float, elapsed: float, tier: str) -> float:
    remaining = max(0.0, timelimit - elapsed)
    reserve = _dynamic_reserve(timelimit)
    cap_fraction = {
        "standard": 0.30,
        "long": 0.40,
        "very_long": 0.50,
    }.get(tier, 0.0)
    return min(max(0.0, remaining - reserve), timelimit * cap_fraction)


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result.get("obj1", float("inf"))),
        float(result.get("objective", float("inf"))),
        float(result.get("obj2", float("inf"))),
        float(result.get("obj3", float("inf"))),
    )


def _improvement_candidate(prob_info: dict, budget: float, features: dict[str, float]) -> tuple[dict, dict]:
    started = time.time()
    top_bays = min(len(prob_info.get("bays", [])), 3)
    max_positions = 14
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="release_due",
        top_bays=top_bays,
        max_positions=max_positions,
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v045] improve_once instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f} proc_mean={features['proc_mean']:.2f}"
    )
    return candidate, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    overall_started = time.time()
    tier = _time_tier(float(timelimit))
    features = _selector_features(prob_info)

    best_solution = v044.algorithm(prob_info, timelimit)
    best_result = v001.check_feasibility(prob_info, best_solution)
    elapsed = time.time() - overall_started
    print(
        f"[baseline_hh reboot_v045] warm_start instance={prob_info.get('name')} "
        f"tier={tier} feasible={best_result.get('feasible')} "
        f"T={best_result.get('obj1')} objective={best_result.get('objective')} "
        f"elapsed={elapsed:.2f}s"
    )

    if not best_result.get("feasible"):
        return best_solution

    if not _should_try_improvement(float(timelimit), elapsed, features, tier):
        print(
            f"[baseline_hh reboot_v045] skip_improvement instance={prob_info.get('name')} "
            f"tier={tier} remaining={max(0.0, float(timelimit) - elapsed):.2f}s"
        )
        return best_solution

    budget = _dynamic_budget(float(timelimit), elapsed, tier)
    if budget < max(5.0, float(timelimit) * 0.08):
        print(
            f"[baseline_hh reboot_v045] budget_too_small instance={prob_info.get('name')} "
            f"budget={budget:.2f}s tier={tier}"
        )
        return best_solution

    candidate, candidate_result = _improvement_candidate(prob_info, budget, features)
    if _result_key(candidate_result) < _result_key(best_result):
        print(
            f"[baseline_hh reboot_v045] selected_improvement instance={prob_info.get('name')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        return candidate

    print(
        f"[baseline_hh reboot_v045] keep_warm_start instance={prob_info.get('name')} "
        f"best_T={best_result.get('obj1')} cand_T={candidate_result.get('obj1')}"
    )
    return best_solution
