"""reboot_v044_20260617_1625_timeaware_two_bay_selector.py

Strategy:
    Keep trusted v043 as the fast feasible warm start, then use one bounded
    time-aware candidate on a small 2-bay medium-processing class.

Metadata:
    version_id: reboot_v044_20260617_1625_timeaware_two_bay_selector
    parent_version: reboot_v043_20260617_1545_timeaware_release_due_portfolio
    status: trusted active BEST
    timestamp: 2026-06-17 16:25 KST
    strategy:
        - Build the trusted v043 solution first.
        - For a 100-block / 2-bay / medium-processing / high-gap class, use
          `pref_pressure` to choose one bounded candidate:
            - concentrated: `release_due`
            - otherwise: `preference_spread`
        - Keep the better feasible result.
    hypothesis:
        Two low-runtime 2-bay rows still have large objective gaps that a
        bounded class selector can close without stressing the global runtime.
    intended_metric_target:
        - prob_22 T 101->26 and objective 2855766->1837996
        - prob_23 T 2228->1497 and objective 30675473->20686068
    validation_status:
        import smoke passed; smoke-8 accepted 8/8; targeted subset accepted 4/4;
        short-45 and long-120 time-stress smoke accepted; full train40 accepted
        40/40 with timeout 0 and improved aggregate T/L/P/objective versus
        trusted v043.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v044_core8_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v044_targets_20260617_001/
        reports/ogc2026_reboot_v001/stress_reboot_v044_short45_20260617_001/
        reports/ogc2026_reboot_v001/stress_reboot_v044_long120_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v044_train40_20260617_001/
    rollback_target: reboot_v043_20260617_1545_timeaware_release_due_portfolio
"""

from __future__ import annotations

import math
import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v043_20260617_1545_timeaware_release_due_portfolio as v043


ACTIVE_VERSION = "reboot_v044_20260617_1625_timeaware_two_bay_selector"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    proc_mean = _mean(proc_values)

    pref_gap_values = []
    pref_weight = [0.0] * len(bays)
    for block in blocks:
        prefs = sorted((float(value) for value in block.get("bay_preferences", [])), reverse=True)
        if prefs:
            pref_gap_values.append(prefs[0] - (prefs[1] if len(prefs) > 1 else 0.0))
        for bay_id, value in enumerate(block.get("bay_preferences", [])):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += float(value)

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": proc_mean,
        "pref_gap_mean": _mean(pref_gap_values),
        "pref_pressure": pref_pressure,
    }


def _matches_two_bay_class(features: dict[str, float]) -> bool:
    return (
        int(features["blocks"]) == 100
        and int(features["bays"]) == 2
        and 9.0 <= features["proc_mean"] <= 18.0
        and features["pref_gap_mean"] >= 60.0
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
    if not _matches_two_bay_class(features):
        return False
    remaining = max(0.0, timelimit - elapsed)
    reserve = _dynamic_reserve(timelimit)
    return remaining > reserve + timelimit * 0.12


def _dynamic_budget(timelimit: float, elapsed: float, tier: str) -> float:
    remaining = max(0.0, timelimit - elapsed)
    reserve = _dynamic_reserve(timelimit)
    cap_fraction = {
        "standard": 0.35,
        "long": 0.45,
        "very_long": 0.55,
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


def _candidate_order(features: dict[str, float]) -> str:
    if features["pref_pressure"] >= 0.72:
        return "release_due"
    return "preference_spread"


def _improvement_candidate(prob_info: dict, budget: float, order_strategy: str, features: dict[str, float]) -> tuple[dict, dict]:
    started = time.time()
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=order_strategy,
        top_bays=2,
        max_positions=14,
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v044] improve_once instance={prob_info.get('name')} "
        f"order={order_strategy} feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f} "
        f"pref_pressure={features['pref_pressure']:.3f}"
    )
    return candidate, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    overall_started = time.time()
    tier = _time_tier(float(timelimit))
    features = _selector_features(prob_info)

    best_solution = v043.algorithm(prob_info, timelimit)
    best_result = v001.check_feasibility(prob_info, best_solution)
    elapsed = time.time() - overall_started
    print(
        f"[baseline_hh reboot_v044] warm_start instance={prob_info.get('name')} "
        f"tier={tier} feasible={best_result.get('feasible')} "
        f"T={best_result.get('obj1')} objective={best_result.get('objective')} "
        f"elapsed={elapsed:.2f}s"
    )

    if not best_result.get("feasible"):
        return best_solution

    if not _should_try_improvement(float(timelimit), elapsed, features, tier):
        print(
            f"[baseline_hh reboot_v044] skip_improvement instance={prob_info.get('name')} "
            f"tier={tier} remaining={max(0.0, float(timelimit) - elapsed):.2f}s"
        )
        return best_solution

    budget = _dynamic_budget(float(timelimit), elapsed, tier)
    if budget < max(6.0, float(timelimit) * 0.10):
        print(
            f"[baseline_hh reboot_v044] budget_too_small instance={prob_info.get('name')} "
            f"budget={budget:.2f}s tier={tier}"
        )
        return best_solution

    order_strategy = _candidate_order(features)
    candidate, candidate_result = _improvement_candidate(prob_info, budget, order_strategy, features)
    if _result_key(candidate_result) < _result_key(best_result):
        print(
            f"[baseline_hh reboot_v044] selected_improvement instance={prob_info.get('name')} "
            f"order={order_strategy} T={candidate_result.get('obj1')} "
            f"objective={candidate_result.get('objective')}"
        )
        return candidate

    print(
        f"[baseline_hh reboot_v044] keep_warm_start instance={prob_info.get('name')} "
        f"best_T={best_result.get('obj1')} cand_T={candidate_result.get('obj1')}"
    )
    return best_solution
