"""reboot_v063_20260618_1605_prob40like_direct_first_due_release.py

Strategy:
    Keep trusted v060 as the default path, but run one direct-first bounded
    due_release candidate for a narrow prob40-like 4-bay xlarge high-workload
    subtype when enough time budget is available.

Metadata:
    version_id: reboot_v063_20260618_1605_prob40like_direct_first_due_release
    parent_version: reboot_v060_20260618_2031_threebay_gap_release_due
    status: accepted
    timestamp: 2026-06-18 16:05 KST
    strategy:
        - Preserve v060 unchanged outside the target subtype.
        - On the target subtype, do not spend time building the v060 warm
          start first.
        - Instead run one bounded direct-first `due_release_proc` candidate
          only when the time tier can support about 45s of search budget.
    hypothesis:
        The prob40-like row has a real due-release improvement signal, but the
        previous v061 order of operations starved it of budget. The same probe
        becomes useful when it runs first under a strict time guard.
    intended_metric_target:
        - improve prob40-like T and objective
        - preserve representative smoke rows
        - improve avg objective versus trusted v060
    validation_status:
        accepted_for_score=40/40 on full train40 benchmark
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v063_train40_20260618_001
    rollback_target: reboot_v060_20260618_2031_threebay_gap_release_due
"""

from __future__ import annotations

import time

import baseline_greedy
from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v060_20260618_2031_threebay_gap_release_due as v060


ACTIVE_VERSION = "reboot_v063_20260618_1605_prob40like_direct_first_due_release"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    workload_values = [float(block.get("workload", 0.0)) for block in blocks]

    top_choices = []
    pref_weight = [0.0] * len(bays)
    for block in blocks:
        prefs = list(block.get("bay_preferences", []))
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += float(pref_value)

    pref_conc = 0.0
    if top_choices and len(blocks) > 0:
        pref_conc = max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)

    imbalance = 0.0
    if top_choices and len(bays) > 1 and len(blocks) > 0:
        counts = [top_choices.count(bay_id) for bay_id in range(len(bays))]
        imbalance = (max(counts) - min(counts)) / len(blocks)

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": _mean(proc_values),
        "workload_mean": _mean(workload_values),
        "pref_concentration": pref_conc,
        "pref_pressure": pref_pressure,
        "workload_imbalance_pressure": imbalance,
    }


def _matches_prob40like_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 4
        and int(features["blocks"]) >= 240
        and features["proc_mean"] >= 20.0
        and features["workload_mean"] >= 160.0
        and features["pref_concentration"] >= 0.72
        and features["pref_pressure"] >= 0.68
        and features["workload_imbalance_pressure"] >= 0.70
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _direct_budget(timelimit: float, tier: str) -> float:
    reserve = _dynamic_reserve(timelimit)
    fraction = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 0.86,
        "long": 0.86,
        "very_long": 0.86,
    }[tier]
    cap = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 46.0,
        "long": 46.0,
        "very_long": 46.0,
    }[tier]
    return min(cap, max(0.0, timelimit * fraction - reserve))


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result["obj1"]),
        float(result["objective"]),
        float(result["obj2"]),
        float(result["obj3"]),
    )


def _class_solution(prob_info: dict, timelimit: float, tier: str) -> dict:
    started = time.time()
    budget = _direct_budget(float(timelimit), tier)
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="due_release_proc",
        top_bays=4,
        max_positions=12,
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v063] prob40like_direct_first instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s tier={tier}"
    )
    if result.get("feasible"):
        return candidate

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining > max(6.0, _dynamic_reserve(float(timelimit))):
        fallback = baseline_greedy.greedyalgorithm(
            prob_info,
            timelimit=max(8.0, remaining),
            repair_mode="greedy",
        )
        fallback_result = v001.check_feasibility(prob_info, fallback)
        print(
            f"[baseline_hh reboot_v063] prob40like_greedy_fallback instance={prob_info.get('name')} "
            f"feasible={fallback_result.get('feasible')} T={fallback_result.get('obj1')} "
            f"objective={fallback_result.get('objective')} remaining={remaining:.2f}s"
        )
        if fallback_result.get("feasible"):
            return fallback

    return v060.algorithm(prob_info, timelimit)


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = _selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))
    budget = _direct_budget(float(timelimit), tier)
    if (
        tier not in {"very_short", "short"}
        and budget >= 45.0
        and _matches_prob40like_class(features)
    ):
        return _class_solution(prob_info, timelimit, tier)
    return v060.algorithm(prob_info, timelimit)
