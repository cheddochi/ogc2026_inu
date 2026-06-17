"""reboot_v043_20260617_1545_timeaware_release_due_portfolio.py

Strategy:
    Keep trusted v042 as the fast feasible warm start, then use one bounded
    time-aware release_due improvement only when a low-preference-pressure
    3-bay class has enough remaining wall time.

Metadata:
    version_id: reboot_v043_20260617_1545_timeaware_release_due_portfolio
    parent_version: reboot_v042_20260617_1510_balanced_three_bay_release_due
    status: trusted active BEST
    timestamp: 2026-06-17 15:45 KST
    strategy:
        - Build the trusted v042 solution first.
        - If the instance matches a low-preference-pressure 3-bay class and
          enough wall time remains, run one bounded release_due improvement and
          keep the better feasible result.
        - Use timelimit-based time tiers to decide whether the improvement
          phase is even allowed to start.
    hypothesis:
        v042 already improves prob_28. A second feature-similar row, prob_24,
        also benefits from release_due, and an improve-once anytime portfolio
        can capture that gain without disturbing runtime-sensitive delegated
        rows.
    intended_metric_target:
        - prob_24 T 362->166 and objective 5678506->2981583
        - prob_28 holds or improves
    validation_status:
        import smoke passed; smoke-8 accepted 8/8; targeted subset accepted 4/4;
        short-45 and long-120 time-stress smoke accepted; full train40 accepted
        40/40 with timeout 0 and improved aggregate T/P/objective versus
        trusted v042.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v043_core8_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v043_targets_20260617_001/
        reports/ogc2026_reboot_v001/stress_reboot_v043_short45_20260617_001/
        reports/ogc2026_reboot_v001/stress_reboot_v043_long120_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v043_train40_20260617_001/
    rollback_target: reboot_v042_20260617_1510_balanced_three_bay_release_due
"""

from __future__ import annotations

import math
import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v042_20260617_1510_balanced_three_bay_release_due as v042


ACTIVE_VERSION = "reboot_v043_20260617_1545_timeaware_release_due_portfolio"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _pstdev(values: list[float], mean_value: float) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum((value - mean_value) ** 2 for value in values) / len(values))


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    bay_count = len(bays)
    block_count = len(blocks)
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    proc_mean = _mean(proc_values)

    top_choices = []
    pref_weight = [0.0] * bay_count
    for block in blocks:
        prefs = list(block.get("bay_preferences", []))
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < bay_count:
                pref_weight[bay_id] += float(pref_value)

    top_pref_conc = 0.0
    if top_choices and bay_count > 0 and block_count > 0:
        top_pref_conc = max(top_choices.count(bay_id) for bay_id in range(bay_count)) / block_count

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    imbalance_pressure = 0.0
    if top_choices and bay_count > 1 and block_count > 0:
        counts = [top_choices.count(bay_id) for bay_id in range(bay_count)]
        imbalance_pressure = (max(counts) - min(counts)) / block_count

    return {
        "blocks": float(block_count),
        "bays": float(bay_count),
        "proc_mean": proc_mean,
        "top_pref_conc": top_pref_conc,
        "pref_pressure": pref_pressure,
        "workload_imbalance_pressure": imbalance_pressure,
    }


def _matches_release_due_portfolio_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and int(features["blocks"]) <= 150
        and 15.0 <= features["proc_mean"] <= 18.5
        and 0.55 <= features["top_pref_conc"] <= 0.62
        and features["pref_pressure"] <= 0.55
        and features["workload_imbalance_pressure"] >= 0.45
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


def _dynamic_candidate_budget(
    timelimit: float,
    elapsed: float,
    features: dict[str, float],
    tier: str,
) -> tuple[float, int]:
    remaining = max(0.0, timelimit - elapsed)
    reserve = _dynamic_reserve(timelimit)
    budget_cap_fraction = {
        "standard": 0.48,
        "long": 0.62,
        "very_long": 0.72,
    }.get(tier, 0.0)
    budget = min(max(0.0, remaining - reserve), timelimit * budget_cap_fraction)
    if int(features["blocks"]) <= 120:
        max_positions = 14
    elif tier == "standard":
        max_positions = 16
    else:
        max_positions = 18
    return budget, max_positions


def _should_try_improvement(
    timelimit: float,
    elapsed: float,
    features: dict[str, float],
    tier: str,
) -> bool:
    if tier in {"very_short", "short"}:
        return False
    if not _matches_release_due_portfolio_class(features):
        return False
    remaining = max(0.0, timelimit - elapsed)
    reserve = _dynamic_reserve(timelimit)
    return remaining > reserve + timelimit * 0.20


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result.get("obj1", float("inf"))),
        float(result.get("objective", float("inf"))),
        float(result.get("obj2", float("inf"))),
        float(result.get("obj3", float("inf"))),
    )


def _improvement_candidate(
    prob_info: dict,
    budget: float,
    max_positions: int,
    features: dict[str, float],
) -> tuple[dict, dict]:
    started = time.time()
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="release_due",
        top_bays=3,
        max_positions=max_positions,
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v043] improve_once instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f} max_positions={max_positions} "
        f"proc_mean={features['proc_mean']:.2f} top_pref_conc={features['top_pref_conc']:.3f} "
        f"pref_pressure={features['pref_pressure']:.3f}"
    )
    return candidate, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    overall_started = time.time()
    tier = _time_tier(float(timelimit))
    features = _selector_features(prob_info)

    best_solution = v042.algorithm(prob_info, timelimit)
    best_result = v001.check_feasibility(prob_info, best_solution)
    elapsed = time.time() - overall_started
    print(
        f"[baseline_hh reboot_v043] warm_start instance={prob_info.get('name')} "
        f"tier={tier} feasible={best_result.get('feasible')} "
        f"T={best_result.get('obj1')} objective={best_result.get('objective')} "
        f"elapsed={elapsed:.2f}s"
    )

    if not best_result.get("feasible"):
        return best_solution

    if not _should_try_improvement(float(timelimit), elapsed, features, tier):
        print(
            f"[baseline_hh reboot_v043] skip_improvement instance={prob_info.get('name')} "
            f"tier={tier} remaining={max(0.0, float(timelimit) - elapsed):.2f}s"
        )
        return best_solution

    budget, max_positions = _dynamic_candidate_budget(float(timelimit), elapsed, features, tier)
    if budget < max(8.0, float(timelimit) * 0.12):
        print(
            f"[baseline_hh reboot_v043] budget_too_small instance={prob_info.get('name')} "
            f"budget={budget:.2f}s tier={tier}"
        )
        return best_solution

    candidate, candidate_result = _improvement_candidate(prob_info, budget, max_positions, features)
    if _result_key(candidate_result) < _result_key(best_result):
        print(
            f"[baseline_hh reboot_v043] selected_improvement instance={prob_info.get('name')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        return candidate

    print(
        f"[baseline_hh reboot_v043] keep_warm_start instance={prob_info.get('name')} "
        f"best_T={best_result.get('obj1')} cand_T={candidate_result.get('obj1')}"
    )
    return best_solution
