"""reboot_v042_20260617_1510_balanced_three_bay_release_due.py

Strategy:
    Add one feature-based release_due class on top of trusted v039.

Metadata:
    version_id: reboot_v042_20260617_1510_balanced_three_bay_release_due
    parent_version: reboot_v039_20260617_1304_runtime_sensitive_budget_guard
    status: trusted active BEST
    timestamp: 2026-06-17 15:10 KST
    strategy:
        - If an instance is a balanced 150-block / 3-bay medium-processing
          class with lower workload CV, run
          release_due top_bays=3 max_positions=16 budget=48.
        - Delegate all other rows to trusted v039.
    hypothesis:
        The current BEST still leaves prob_28 as a nearby residual-T row.
        A feature-derived class around balanced 150x3 instances can absorb the
        trusted prob_29 policy and improve prob_28 without reaching into the
        brittle runtime-sensitive high-T rows.
    intended_metric_target:
        - prob_28 T 1666->1506 and objective 23901034->21478323
        - prob_29 hold accepted row
    validation_status:
        import smoke passed; smoke-8 accepted 8/8; targeted subset accepted 4/4;
        full train40 accepted 40/40 with timeout 0 and improved aggregate
        T/L/P/objective versus trusted v039.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v042_core8_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v042_targets_20260617_001/
        reports/ogc2026_reboot_v001/full_reboot_v042_train40_20260617_001/
    rollback_target: reboot_v039_20260617_1304_runtime_sensitive_budget_guard
    training_specific_risk:
        reduced but not eliminated because delegated fallback layers still
        contain earlier training-tuned row policies.
"""

from __future__ import annotations

import math
import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v039_20260617_1304_runtime_sensitive_budget_guard as v039


ACTIVE_VERSION = "reboot_v042_20260617_1510_balanced_three_bay_release_due"


BALANCED_THREE_BAY_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 16,
    "budget": 48.0,
}


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
    bay_count = len(prob_info.get("bays", []))
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    workload_values = [float(block.get("workload", 0.0)) for block in blocks]
    proc_mean = _mean(proc_values)
    work_mean = _mean(workload_values)
    work_cv = _pstdev(workload_values, work_mean) / work_mean if work_mean > 0 else 0.0

    top_choices = []
    for block in blocks:
        prefs = list(block.get("bay_preferences", []))
        if not prefs:
            continue
        top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))

    top_pref_conc = 0.0
    if top_choices and bay_count > 0:
        top_pref_conc = max(top_choices.count(bay_id) for bay_id in range(bay_count)) / len(blocks)

    return {
        "blocks": float(len(blocks)),
        "bays": float(bay_count),
        "proc_mean": proc_mean,
        "work_cv": work_cv,
        "top_pref_conc": top_pref_conc,
    }


def _matches_balanced_three_bay_class(features: dict[str, float]) -> bool:
    return (
        int(features["blocks"]) == 150
        and int(features["bays"]) == 3
        and features["proc_mean"] >= 10.0
        and features["work_cv"] <= 0.95
        and features["top_pref_conc"] >= 0.55
    )


def _feature_class_solution(prob_info: dict, timelimit: float, features: dict[str, float]) -> dict:
    started = time.time()
    budget = min(float(BALANCED_THREE_BAY_POLICY["budget"]), max(8.0, float(timelimit) - 0.1))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(BALANCED_THREE_BAY_POLICY["order_strategy"]),
        top_bays=int(BALANCED_THREE_BAY_POLICY["top_bays"]),
        max_positions=int(BALANCED_THREE_BAY_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v042] class=balanced_three_bay_release_due "
        f"instance={prob_info.get('name')} feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f} "
        f"proc_mean={features['proc_mean']:.2f} work_cv={features['work_cv']:.3f} "
        f"top_pref_conc={features['top_pref_conc']:.3f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = _selector_features(prob_info)
    if _matches_balanced_three_bay_class(features):
        return _feature_class_solution(prob_info, timelimit, features)
    return v039.algorithm(prob_info, timelimit)
