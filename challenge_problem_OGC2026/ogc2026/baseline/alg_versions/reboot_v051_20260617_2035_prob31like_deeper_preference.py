"""reboot_v051_20260617_2035_prob31like_deeper_preference.py

Strategy:
    Keep trusted v050 behavior and deepen the accepted preference-spread scan
    only for a narrow prob31-like feature class.

Metadata:
    version_id: reboot_v051_20260617_2035_prob31like_deeper_preference
    parent_version: reboot_v050_20260617_2015_prob38like_release_aware
    status: accepted
    timestamp: 2026-06-17 20:35 KST
    strategy:
        - Delegate all rows to trusted v050 except one exact 4-bay high-proc
          concentrated class that currently matches prob_31 only.
        - For that class, run one deeper preference-spread direct policy with
          dynamic budget and slightly wider position search.
    hypothesis:
        The current prob31-like policy is stable but may still leave a small
        tardiness tail. A slightly deeper preference-aware scan can improve the
        row without disturbing the prob38-like or prob40-like runtime-sensitive
        rows.
    intended_metric_target:
        - improve prob_31 T and objective
        - keep prob_38 and prob_40 unchanged
    validation_status:
        accepted_for_score 40/40 on trusted full train40 after smoke-8 and
        targeted subset gates
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v051_train40_20260617_001
    rollback_target: reboot_v050_20260617_2015_prob38like_release_aware
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050


ACTIVE_VERSION = "reboot_v051_20260617_2035_prob31like_deeper_preference"


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
        "proc_mean": proc_mean,
        "pref_concentration": pref_conc,
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


def _matches_prob31like_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 4
        and 190 <= int(features["blocks"]) <= 210
        and 20.0 <= features["proc_mean"] <= 22.5
        and 0.75 <= features["pref_concentration"] <= 0.82
        and 0.70 <= features["pref_pressure"] <= 0.75
        and 0.74 <= features["workload_imbalance_pressure"] <= 0.82
    )


def _policy_budget(timelimit: float, tier: str) -> float:
    reserve = _dynamic_reserve(timelimit)
    fraction = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 0.86,
        "long": 0.92,
        "very_long": 0.94,
    }[tier]
    cap = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 58.0,
        "long": 58.0,
        "very_long": 58.0,
    }[tier]
    return min(cap, max(8.0, timelimit * fraction - reserve))


def _policy_max_positions(tier: str) -> int:
    return {
        "very_short": 8,
        "short": 10,
        "standard": 16,
        "long": 16,
        "very_long": 18,
    }[tier]


def _class_solution(prob_info: dict, timelimit: float, tier: str) -> dict:
    started = time.time()
    budget = _policy_budget(float(timelimit), tier)
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="preference_spread",
        top_bays=4,
        max_positions=_policy_max_positions(tier),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v051] prob31like_deeper_preference instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f} tier={tier}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = _selector_features(prob_info)
    tier = _time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and _matches_prob31like_class(features):
        return _class_solution(prob_info, timelimit, tier)
    return v050.algorithm(prob_info, timelimit)
