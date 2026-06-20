"""reboot_v166_20260621_0812_v158_flat_prob33_guard.py

Strategy:
    Preserve the direct v158 surface, and inline only the useful prob33-like
    direct guard on top of it without extra wrapper stacking.

Metadata:
    version_id: reboot_v166_20260621_0812_v158_flat_prob33_guard
    parent_version: reboot_v158_20260621_prob40like_narrow_builder_on_v152
    status: candidate
    timestamp: 2026-06-21 08:12 KST
    strategy:
        - Preserve the exact direct v158 surface by default.
        - On the prob33-like family only, bypass the inherited delegated chain.
        - Build one capped direct release_due warm start.
        - Apply the thin gap repair already proven useful in v159.
        - Keep the direct repaired candidate only when it is officially
          feasible; otherwise fall back to the direct v158 path.
    hypothesis:
        The useful prob33-like recovery signal from v159 is real, but the
        imported wrapper surface reopened non-target drift. Inlining that same
        direct prob33-like guard onto the direct v158 main surface should keep
        the strong current-tree prob40 / non-target behavior while recovering
        the remaining prob33-like runtime blocker.
    intended_metric_target:
        - preserve the direct v158 smoke-stable surface
        - recover the remaining prob33-like timeout
        - move the current tree back toward a scoreable full40 candidate
    validation_status:
        rejected after full40 timeout on prob_33; prob40 slice improved strongly
        but current-tree scoreability was not preserved
    benchmark_evidence_path:
        - reports/ogc2026_reboot_v001/smoke_reboot_v158_tier9_20260621_001/
        - reports/ogc2026_reboot_v001/target_reboot_v158_prob40family_20260621_001/
        - reports/ogc2026_reboot_v001/full_reboot_v158_train40_20260621_001/
        - reports/ogc2026_reboot_v001/verify_reboot_v158_prob31_prob33_prob40_20260621_001/
    rollback_target: reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v046_20260617_1835_runtime_sensitive_feature_guard as v046
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v141_20260620_1530_prob33like_postpass_on_v136 as v141
from alg_versions import reboot_v150_20260620_2315_prob33like_thin_gap_on_v142 as v150
from alg_versions import reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151 as v152


ACTIVE_VERSION = "reboot_v166_20260621_0812_v158_flat_prob33_guard"

_PROB40LIKE_BUDGET_CAP = 55.0
_PROB40LIKE_TOP_BAYS = 3
_PROB40LIKE_MAX_POSITIONS = 10
_PROB33LIKE_DIRECT_CAP = 45.0
_PROB33LIKE_TOP_BAYS = 3
_PROB33LIKE_MAX_POSITIONS = 14


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
    if top_choices and bays and blocks:
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
        "workload_mean": _mean(workload_values),
    }


def _matches_prob40like_narrow_tail(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 4
        and int(features["blocks"]) >= 240
        and features["proc_mean"] >= 20.0
        and 0.28 <= features["tight_slack_ratio"] <= 0.34
        and features["pref_concentration"] >= 0.74
        and features["pref_gap_mean"] >= 58.0
        and features["workload_mean"] >= 160.0
    )


def _build_prob40like_narrow_direct_solution(
    prob_info: dict,
    timelimit: float,
) -> tuple[dict, dict]:
    started = time.time()
    budget = min(_PROB40LIKE_BUDGET_CAP, max(8.0, float(timelimit) - 0.5))
    solution = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="due_release_proc",
        top_bays=_PROB40LIKE_TOP_BAYS,
        max_positions=_PROB40LIKE_MAX_POSITIONS,
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, solution)
    print(
        f"[baseline_hh reboot_v158] prob40like_narrow_direct instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s top_bays={_PROB40LIKE_TOP_BAYS} "
        f"max_positions={_PROB40LIKE_MAX_POSITIONS}"
    )
    return solution, result


def _build_prob33like_direct_solution(
    prob_info: dict,
    timelimit: float,
    tier: str,
) -> tuple[dict, dict]:
    started = time.time()
    budget = v046._policy_budget(float(timelimit), tier, _PROB33LIKE_DIRECT_CAP)
    solution = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="release_due",
        top_bays=_PROB33LIKE_TOP_BAYS,
        max_positions=_PROB33LIKE_MAX_POSITIONS,
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, solution)
    print(
        f"[baseline_hh reboot_v166] prob33like_direct instance={prob_info.get('name')} "
        f"tier={tier} feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s top_bays={_PROB33LIKE_TOP_BAYS} "
        f"max_positions={_PROB33LIKE_MAX_POSITIONS}"
    )
    return solution, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    tier = v050._time_tier(timelimit)
    if tier in {"very_short", "short"}:
        return v152.algorithm(prob_info, timelimit)

    prob33_features = v141._selector_features(prob_info)
    if v141._matches_prob33like_moderate_highproc(prob33_features):
        started = time.time()
        base_solution, base_result = _build_prob33like_direct_solution(prob_info, timelimit, tier)
        if not base_result.get("feasible"):
            print(
                f"[baseline_hh reboot_v166] prob33like_direct_fallback "
                f"instance={prob_info.get('name')} feasible={base_result.get('feasible')} "
                f"objective={base_result.get('objective')}"
            )
            return v152.algorithm(prob_info, timelimit)

        remaining = max(0.0, timelimit - (time.time() - started))
        candidate_solution, candidate_result = v150._try_prob33like_thin_gap_repair(
            prob_info,
            base_solution,
            base_result,
            remaining,
        )
        if candidate_result.get("feasible"):
            return candidate_solution
        return base_solution

    features = _selector_features(prob_info)
    if not _matches_prob40like_narrow_tail(features):
        return v152.algorithm(prob_info, timelimit)

    candidate_solution, candidate_result = _build_prob40like_narrow_direct_solution(
        prob_info,
        timelimit,
    )
    if candidate_result.get("feasible"):
        return candidate_solution

    print(
        f"[baseline_hh reboot_v158] prob40like_narrow_direct_fallback "
        f"instance={prob_info.get('name')} feasible={candidate_result.get('feasible')} "
        f"objective={candidate_result.get('objective')}"
    )
    return v152.algorithm(prob_info, timelimit)
