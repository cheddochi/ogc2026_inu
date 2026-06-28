"""reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151.py

Strategy:
    Extend the direct runtime-family flattening from v151 to the remaining
    reopened diffuse 3-bay runtime-risk backlog while preserving v151
    elsewhere.

Metadata:
    version_id: reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151
    parent_version: reboot_v151_20260620_prob31like_direct_stabilizer_on_v142
    status: candidate
    timestamp: 2026-06-21 KST
    strategy:
        - Preserve v151 unchanged outside the reopened runtime-backlog
          families.
        - Keep the prob31-like direct stabilizer unchanged.
        - On the diffuse 3-bay runtime-risk family only, bypass the inherited
          repair chain and use one capped direct release_due warm start.
        - Keep the direct candidate only when it is officially feasible.
    hypothesis:
        The remaining current-tree timeout backlog is still mostly a delegated
        warm-start/runtime-cliff issue. Replacing that slice with a direct
        release_due warm start should recover 40/40 scoreability before any
        further T-breakthrough tuning.
    intended_metric_target:
        - restore accepted_for_score 40/40 on the reopened runtime backlog
        - keep prob31-like stabilized
        - preserve the trusted surface outside the targeted runtime families
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v151_20260620_prob31like_direct_stabilizer_on_v142
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v046_20260617_1835_runtime_sensitive_feature_guard as v046


ACTIVE_VERSION = "reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151"

_DIFFUSE_RUNTIME_DIRECT_CAP = 43.0


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]

    top_choices = []
    pref_gap_values = []
    tight_count = 0
    for block in blocks:
        release = float(block.get("release_time", 0.0))
        due = float(block.get("due_date", 0.0))
        proc = float(block.get("processing_time", 0.0))
        if due - release - proc <= 2.0:
            tight_count += 1

        prefs = list(block.get("bay_preferences", []))
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
            ordered = sorted((float(value) for value in prefs), reverse=True)
            pref_gap_values.append(ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0))

    pref_concentration = 0.0
    if top_choices and blocks:
        pref_concentration = (
            max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)
        )

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": _mean(proc_values),
        "tight_slack_ratio": tight_count / len(blocks) if blocks else 0.0,
        "pref_concentration": pref_concentration,
        "pref_gap_mean": _mean(pref_gap_values),
    }


def _matches_threebay_diffuse_runtime_backlog(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and int(features["blocks"]) >= 200
        and 10.5 <= features["proc_mean"] <= 17.5
        and features["tight_slack_ratio"] >= 0.50
        and features["pref_concentration"] <= 0.45
        and features["pref_gap_mean"] <= 50.0
    )


def _direct_policy_params(features: dict[str, float], tier: str) -> dict[str, object]:
    proc_mean = features["proc_mean"]
    if proc_mean >= 14.5:
        return {
            "label": "threebay_diffuse_midproc_release_due",
            "order_strategy": "release_due",
            "top_bays": 3,
            "max_positions": 14,
        }
    return {
        "label": "threebay_diffuse_lowproc_release_due",
        "order_strategy": "release_due",
        "top_bays": 3,
        "max_positions": 14,
    }


def _build_threebay_diffuse_direct_solution(
    prob_info: dict,
    timelimit: float,
    tier: str,
    features: dict[str, float],
) -> tuple[dict, dict]:
    params = _direct_policy_params(features, tier)
    started = time.time()
    budget = v046._policy_budget(float(timelimit), tier, _DIFFUSE_RUNTIME_DIRECT_CAP)
    solution = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(params["order_strategy"]),
        top_bays=int(params["top_bays"]),
        max_positions=int(params["max_positions"]),
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, solution)
    print(
        f"[baseline_hh reboot_v152] diffuse_runtime_direct instance={prob_info.get('name')} "
        f"label={params['label']} tier={tier} feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}s "
        f"max_positions={params['max_positions']}"
    )
    return solution, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)

    from alg_versions import reboot_v078_20260619_1535_fourbay_runtime_family_flatten as v078
    from alg_versions import reboot_v151_20260620_prob31like_direct_stabilizer_on_v142 as v151

    tier = v078._time_tier(timelimit)
    if tier in {"very_short", "short"}:
        return v151.algorithm(prob_info, timelimit)

    features = _selector_features(prob_info)
    if not _matches_threebay_diffuse_runtime_backlog(features):
        return v151.algorithm(prob_info, timelimit)

    candidate_solution, candidate_result = _build_threebay_diffuse_direct_solution(
        prob_info,
        timelimit,
        tier,
        features,
    )
    if candidate_result.get("feasible"):
        return candidate_solution

    print(
        f"[baseline_hh reboot_v152] diffuse_runtime_direct_fallback "
        f"instance={prob_info.get('name')} feasible={candidate_result.get('feasible')} "
        f"objective={candidate_result.get('objective')}"
    )
    return v151.algorithm(prob_info, timelimit)
