"""reboot_v046_20260617_1835_runtime_sensitive_feature_guard.py

Strategy:
    Keep trusted v045 as the default path, but bypass its delegated near-limit
    runtime-sensitive rows with one feature-based direct policy selector that
    reaches good accepted policies earlier and more predictably.

Metadata:
    version_id: reboot_v046_20260617_1835_runtime_sensitive_feature_guard
    parent_version: reboot_v045_20260617_1705_timeaware_lowproc_release_due
    status: candidate
    timestamp: 2026-06-17 18:35 KST
    strategy:
        - Preserve v045 low-proc class improvements unchanged.
        - For a runtime-sensitive high-pressure class, bypass the delegated
          warm-start chain and run one direct v001 limited-concurrent policy
          chosen from problem features plus timelimit tier.
        - Use trimmed short-limit max_positions so the runtime-sensitive class
          reaches a stable accepted policy earlier under tighter budgets.
    hypothesis:
        v045 materially improves the low-proc class, but some high-risk
        runtime-sensitive rows still drift because their accepted policies sit
        deep in the delegated stack. A direct feature-based policy selector
        should recover those rows while keeping the low-proc gains.
    intended_metric_target:
        - recover or improve prob_31, prob_36, prob_38, prob_40
        - keep v045 low-proc gains on prob_1~prob_9
    validation_status:
        accepted BEST on full train40; keep short-limit-risk note on the
        runtime-sensitive class
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v046_train40_20260617_001
    rollback_target: reboot_v045_20260617_1705_timeaware_lowproc_release_due
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v045_20260617_1705_timeaware_lowproc_release_due as v045


ACTIVE_VERSION = "reboot_v046_20260617_1835_runtime_sensitive_feature_guard"


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


def _runtime_sensitive_policy(features: dict[str, float], tier: str) -> dict | None:
    bays = int(features["bays"])
    blocks = int(features["blocks"])
    proc_mean = features["proc_mean"]
    pref_pressure = features["pref_pressure"]
    imbalance = features["workload_imbalance_pressure"]

    if bays == 4 and blocks >= 200 and pref_pressure >= 0.68 and imbalance >= 0.70:
        if proc_mean >= 18.0:
            if blocks >= 240:
                return {
                    "label": "four_bay_highproc_due_release",
                    "order_strategy": "due_release_proc",
                    "top_bays": 4,
                    "max_positions": {
                        "very_short": 8,
                        "short": 8,
                        "standard": 10,
                        "long": 10,
                        "very_long": 12,
                    }[tier],
                    "budget_cap": 58.0,
                }
            return {
                "label": "four_bay_highproc_preference_spread",
                "order_strategy": "preference_spread",
                "top_bays": 4,
                "max_positions": {
                    "very_short": 10,
                    "short": 12,
                    "standard": 14,
                    "long": 14,
                    "very_long": 16,
                }[tier],
                "budget_cap": 55.0,
            }
        return {
            "label": "four_bay_midproc_due_long",
            "order_strategy": "due_long_proc",
            "top_bays": 4,
            "max_positions": {
                "very_short": 8,
                "short": 10,
                "standard": 14,
                "long": 14,
                "very_long": 16,
            }[tier],
            "budget_cap": 58.0,
        }

    if (
        bays == 3
        and blocks >= 240
        and proc_mean >= 19.0
        and 0.45 <= pref_pressure <= 0.60
        and imbalance >= 0.35
    ):
        return {
            "label": "three_bay_highproc_due_long",
            "order_strategy": "due_long_proc",
            "top_bays": 3,
            "max_positions": {
                "very_short": 10,
                "short": 12,
                "standard": 16,
                "long": 16,
                "very_long": 18,
            }[tier],
            "budget_cap": 59.0,
        }

    return None


def _policy_budget(timelimit: float, tier: str, budget_cap: float) -> float:
    reserve = _dynamic_reserve(timelimit)
    fraction = {
        "very_short": 0.55,
        "short": 0.72,
        "standard": 0.92,
        "long": 0.92,
        "very_long": 0.92,
    }[tier]
    return min(float(budget_cap), max(8.0, timelimit * fraction - reserve))


def _direct_policy_solution(prob_info: dict, timelimit: float, features: dict[str, float], tier: str, policy: dict) -> tuple[dict, dict]:
    started = time.time()
    budget = _policy_budget(float(timelimit), tier, float(policy["budget_cap"]))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(policy["order_strategy"]),
        top_bays=int(policy["top_bays"]),
        max_positions=int(policy["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v046] runtime_sensitive_policy instance={prob_info.get('name')} "
        f"label={policy['label']} feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f} "
        f"tier={tier}"
    )
    return candidate, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = _selector_features(prob_info)
    tier = _time_tier(float(timelimit))
    policy = _runtime_sensitive_policy(features, tier)

    if policy is not None and tier != "very_short":
        candidate, result = _direct_policy_solution(prob_info, timelimit, features, tier, policy)
        if result.get("feasible"):
            return candidate
        print(
            f"[baseline_hh reboot_v046] runtime_sensitive_fallback instance={prob_info.get('name')} "
            f"label={policy['label']}"
        )

    return v045.algorithm(prob_info, timelimit)
