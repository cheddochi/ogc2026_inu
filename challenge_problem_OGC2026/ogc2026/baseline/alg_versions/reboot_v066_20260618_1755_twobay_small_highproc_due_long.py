"""reboot_v066_20260618_1755_twobay_small_highproc_due_long.py

Strategy:
    Keep trusted v065 as the default path, but run one direct-first due_long
    candidate for a small 2-bay high-processing-time moderate-pressure class.

Metadata:
    version_id: reboot_v066_20260618_1755_twobay_small_highproc_due_long
    parent_version: reboot_v065_20260618_1735_threebay_diffuse_single_research
    status: candidate
    timestamp: 2026-06-18 17:55 KST
    strategy:
        - Preserve v065 unchanged outside the target subtype.
        - On the target subtype, run one direct-first `due_long_proc`
          candidate with a wider position scan.
        - Keep the inherited v065 path for every non-target row.
    hypothesis:
        Small 2-bay high-proc moderate-pressure rows are under-served by the
        current release-first bias; a direct long-job-first search can reduce
        the tardy tail without material runtime risk.
    intended_metric_target:
        - improve prob25-like rows
        - preserve representative smoke rows
        - improve avg objective versus trusted v065
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v065_20260618_1735_threebay_diffuse_single_research
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v065_20260618_1735_threebay_diffuse_single_research as v065


ACTIVE_VERSION = "reboot_v066_20260618_1755_twobay_small_highproc_due_long"


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

    pref_conc = 0.0
    if top_choices and len(blocks) > 0:
        pref_conc = max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)

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
        "pref_concentration": pref_conc,
        "pref_pressure": pref_pressure,
        "slack_mean": _mean(slack_values),
    }


def _matches_twobay_small_highproc_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 2
        and int(features["blocks"]) <= 110
        and features["proc_mean"] >= 20.0
        and features["pref_concentration"] <= 0.63
        and features["pref_pressure"] <= 0.61
        and features["slack_mean"] >= 5.0
    )


def _policy_budget(timelimit: float, tier: str) -> float:
    reserve = max(4.0, timelimit * 0.08)
    fraction = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 0.68,
        "long": 0.68,
        "very_long": 0.68,
    }[tier]
    cap = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 40.0,
        "long": 40.0,
        "very_long": 40.0,
    }[tier]
    return min(cap, max(8.0, timelimit * fraction - reserve))


def _class_solution(prob_info: dict, timelimit: float, tier: str) -> dict:
    started = time.time()
    budget = _policy_budget(float(timelimit), tier)
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="due_long_proc",
        top_bays=2,
        max_positions=24,
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v066] twobay_small_highproc instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s tier={tier}"
    )
    if result.get("feasible"):
        return candidate
    return v065.algorithm(prob_info, timelimit)


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = _selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and _matches_twobay_small_highproc_class(features):
        return _class_solution(prob_info, timelimit, tier)
    return v065.algorithm(prob_info, timelimit)
