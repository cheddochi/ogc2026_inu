"""reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long.py

Strategy:
    Keep trusted v046 as the default path, but intercept one narrow 3-bay
    moderate-pressure subtype with a direct due_long_proc policy that reaches a
    stronger accepted row faster than the delegated chain.

Metadata:
    version_id: reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long
    parent_version: reboot_v046_20260617_1835_runtime_sensitive_feature_guard
    status: accepted
    timestamp: 2026-06-17 19:35 KST
    strategy:
        - Preserve v046 low-proc gains and runtime-sensitive recovery.
        - For one exact 3-bay subtype, bypass the delegated chain and run one
          direct `due_long_proc` limited-concurrent policy with time-aware
          positions/budget.
    hypothesis:
        v046 is now strong on the runtime-sensitive rows, but one remaining
        3-bay subtype still benefits from a direct `due_long_proc` policy that
        the delegated chain never reaches soon enough.
    intended_metric_target:
        - improve prob_28
        - improve prob_35
        - keep all v046 gains elsewhere
    validation_status:
        accepted_for_score=40/40 on trusted full train40 benchmark
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v047_train40_20260617_001
    rollback_target: reboot_v046_20260617_1835_runtime_sensitive_feature_guard
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v046_20260617_1835_runtime_sensitive_feature_guard as v046


ACTIVE_VERSION = "reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long"


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
    pref_gap_values = []
    for block in blocks:
        prefs = list(block.get("bay_preferences", []))
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
            ordered = sorted((float(value) for value in prefs), reverse=True)
            pref_gap_values.append(ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0))

    pref_conc = 0.0
    if top_choices and len(blocks) > 0:
        pref_conc = max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)

    imbalance = 0.0
    if top_choices and len(bays) > 1 and len(blocks) > 0:
        counts = [top_choices.count(bay_id) for bay_id in range(len(bays))]
        imbalance = (max(counts) - min(counts)) / len(blocks)

    pref_pressure = 0.0
    if len(bays) > 0:
        pref_weight = [0.0] * len(bays)
        for block in blocks:
            for bay_id, pref_value in enumerate(block.get("bay_preferences", [])):
                if bay_id < len(pref_weight):
                    pref_weight[bay_id] += float(pref_value)
        if sum(pref_weight) > 0:
            pref_pressure = max(pref_weight) / sum(pref_weight)

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": proc_mean,
        "pref_concentration": pref_conc,
        "pref_gap_mean": _mean(pref_gap_values),
        "pref_pressure": pref_pressure,
        "workload_imbalance_pressure": imbalance,
    }


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


def _matches_three_bay_moderate_pressure_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and 150 <= int(features["blocks"]) <= 200
        and 10.5 <= features["proc_mean"] <= 17.0
        and 0.55 <= features["pref_concentration"] <= 0.61
        and 45.0 <= features["pref_gap_mean"] <= 52.0
        and 0.52 <= features["pref_pressure"] <= 0.61
        and 0.40 <= features["workload_imbalance_pressure"] <= 0.50
    )


def _policy_budget(timelimit: float, tier: str) -> float:
    reserve = _dynamic_reserve(timelimit)
    fraction = {
        "very_short": 0.0,
        "short": 0.62,
        "standard": 0.72,
        "long": 0.72,
        "very_long": 0.72,
    }[tier]
    return min(36.0, max(8.0, timelimit * fraction - reserve))


def _policy_max_positions(tier: str) -> int:
    return {
        "very_short": 8,
        "short": 12,
        "standard": 16,
        "long": 16,
        "very_long": 18,
    }[tier]


def _direct_policy_solution(prob_info: dict, timelimit: float, tier: str, features: dict[str, float]) -> tuple[dict, dict]:
    started = time.time()
    budget = _policy_budget(float(timelimit), tier)
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="due_long_proc",
        top_bays=3,
        max_positions=_policy_max_positions(tier),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v047] direct_three_bay_policy instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f} tier={tier} proc_mean={features['proc_mean']:.2f}"
    )
    return candidate, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = _selector_features(prob_info)
    tier = _time_tier(float(timelimit))

    if tier not in {"very_short", "short"} and _matches_three_bay_moderate_pressure_class(features):
        candidate, result = _direct_policy_solution(prob_info, timelimit, tier, features)
        if result.get("feasible"):
            return candidate
        print(
            f"[baseline_hh reboot_v047] class_fallback instance={prob_info.get('name')} "
            f"tier={tier}"
        )

    return v046.algorithm(prob_info, timelimit)
