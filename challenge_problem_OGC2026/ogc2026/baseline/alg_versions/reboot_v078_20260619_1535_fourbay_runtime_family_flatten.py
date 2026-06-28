"""reboot_v078_20260619_1535_fourbay_runtime_family_flatten.py

Strategy:
    Keep trusted v074 as the default path, but flatten the unstable 4-bay
    runtime-sensitive family into subtype-specific direct warm starts before
    reusing only the already trusted tiny repair phases.

Metadata:
    version_id: reboot_v078_20260619_1535_fourbay_runtime_family_flatten
    parent_version: reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio
    status: candidate
    timestamp: 2026-06-19 15:35 KST
    strategy:
        - Preserve trusted v074 unchanged outside the 4-bay runtime-sensitive
          family.
        - Replace the deep delegated warm-start chain on the targeted family
          with direct subtype-specific limited-concurrent warm starts.
        - Reuse only the already accepted small repair phases that proved
          useful on each subtype.
    hypothesis:
        The current v074 family-level score is strong when the direct builders
        behave well, but the deep delegated chain can drift into runtime
        cliffs on reruns. Flattening the 4-bay runtime-sensitive family into
        direct warm starts should preserve the good row-level policies while
        making the family more reliable under the official time limit.
    intended_metric_target:
        - keep the four-bay runtime-sensitive family scoreable
        - preserve prob31/prob36/prob40-like score signal
        - improve confidence that full-train40 reruns stay accepted
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v046_20260617_1835_runtime_sensitive_feature_guard as v046
from alg_versions import reboot_v063_20260618_1605_prob40like_direct_first_due_release as v063
from alg_versions import reboot_v067_20260618_1532_fourbay_highproc_tardy_research as v067
from alg_versions import reboot_v070_20260618_2035_highproc_concentrated_gap_single as v070
from alg_versions import reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio as v074


ACTIVE_VERSION = "reboot_v078_20260619_1535_fourbay_runtime_family_flatten"


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

    pref_concentration = 0.0
    if top_choices and blocks:
        pref_concentration = (
            max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)
        )

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    imbalance = 0.0
    if top_choices and len(bays) > 1 and blocks:
        counts = [top_choices.count(bay_id) for bay_id in range(len(bays))]
        imbalance = (max(counts) - min(counts)) / len(blocks)

    slack_values = [
        due - rel - proc
        for due, rel, proc in zip(due_values, rel_values, proc_values)
    ]

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": _mean(proc_values),
        "workload_mean": _mean(workload_values),
        "pref_concentration": pref_concentration,
        "pref_pressure": pref_pressure,
        "workload_imbalance_pressure": imbalance,
        "slack_mean": _mean(slack_values),
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


def _matches_prob31like_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 4
        and 190 <= int(features["blocks"]) <= 210
        and 20.0 <= features["proc_mean"] <= 22.5
        and 0.75 <= features["pref_concentration"] <= 0.82
        and 0.70 <= features["pref_pressure"] <= 0.75
        and 0.74 <= features["workload_imbalance_pressure"] <= 0.82
    )


def _matches_prob36like_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 4
        and int(features["blocks"]) >= 230
        and 10.0 <= features["proc_mean"] <= 14.0
        and features["pref_concentration"] >= 0.78
        and features["pref_pressure"] >= 0.69
        and features["workload_imbalance_pressure"] >= 0.75
        and features["slack_mean"] <= 3.0
    )


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


def _build_prob31like_base(prob_info: dict, timelimit: float, tier: str) -> tuple[dict, dict]:
    started = time.time()
    budget = v046._policy_budget(float(timelimit), tier, 55.0)
    solution = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="preference_spread",
        top_bays=4,
        max_positions=14,
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, solution)
    print(
        f"[baseline_hh reboot_v078] prob31like_direct instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s tier={tier}"
    )
    return solution, result


def _build_prob36like_base(prob_info: dict, timelimit: float, tier: str) -> tuple[dict, dict]:
    started = time.time()
    budget = v046._policy_budget(float(timelimit), tier, 58.0)
    solution = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="due_long_proc",
        top_bays=4,
        max_positions=14,
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, solution)
    print(
        f"[baseline_hh reboot_v078] prob36like_direct instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s tier={tier}"
    )
    return solution, result


def _build_prob40like_base(prob_info: dict, timelimit: float, tier: str) -> tuple[dict, dict]:
    started = time.time()
    budget = v063._direct_budget(float(timelimit), tier)
    solution = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="due_release_proc",
        top_bays=4,
        max_positions=12,
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, solution)
    print(
        f"[baseline_hh reboot_v078] prob40like_direct instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s tier={tier}"
    )
    return solution, result


def _apply_prob31like_postphases(
    prob_info: dict,
    solution: dict,
    result: dict,
    started: float,
    timelimit: float,
    tier: str,
) -> tuple[dict, dict]:
    features67 = v067._selector_features(prob_info)

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining > v067._dynamic_reserve(float(timelimit)) + 6.0:
        solution, result = v067._try_tardy_research(
            prob_info,
            features67,
            solution,
            result,
            remaining,
            float(timelimit),
            tier,
        )

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining > v070._dynamic_reserve(float(timelimit)) + 8.0:
        solution, result = v070._try_gap_single_research(
            prob_info,
            solution,
            result,
            max(0.0, remaining - v070._dynamic_reserve(float(timelimit))),
            tier,
        )

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if (
        remaining > 0.5
        and v074._family_direct_budget(float(timelimit), tier) >= 45.0
        and v074._matches_fourbay_highproc_dense_family(v074._selector_features(prob_info))
    ):
        solution, result = v074._try_fast_reinsert_portfolio(
            prob_info,
            solution,
            result,
            remaining,
            tier,
        )

    return solution, result


def _apply_prob40like_postphases(
    prob_info: dict,
    solution: dict,
    result: dict,
    started: float,
    timelimit: float,
    tier: str,
) -> tuple[dict, dict]:
    features67 = v067._selector_features(prob_info)

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining > v067._dynamic_reserve(float(timelimit)) + 6.0:
        solution, result = v067._try_tardy_research(
            prob_info,
            features67,
            solution,
            result,
            remaining,
            float(timelimit),
            tier,
        )

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if (
        remaining > 0.5
        and v074._family_direct_budget(float(timelimit), tier) >= 45.0
        and v074._matches_fourbay_highproc_dense_family(v074._selector_features(prob_info))
    ):
        solution, result = v074._try_fast_reinsert_portfolio(
            prob_info,
            solution,
            result,
            remaining,
            tier,
        )

    return solution, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    features = _selector_features(prob_info)
    tier = _time_tier(float(timelimit))

    if tier in {"very_short", "short"}:
        return v074.algorithm(prob_info, timelimit)

    if _matches_prob31like_class(features):
        solution, result = _build_prob31like_base(prob_info, timelimit, tier)
        if result.get("feasible"):
            solution, result = _apply_prob31like_postphases(
                prob_info,
                solution,
                result,
                started,
                timelimit,
                tier,
            )
        return solution

    if _matches_prob40like_class(features):
        solution, result = _build_prob40like_base(prob_info, timelimit, tier)
        if result.get("feasible"):
            solution, result = _apply_prob40like_postphases(
                prob_info,
                solution,
                result,
                started,
                timelimit,
                tier,
            )
        return solution

    if _matches_prob36like_class(features):
        solution, _ = _build_prob36like_base(prob_info, timelimit, tier)
        return solution

    return v074.algorithm(prob_info, timelimit)
