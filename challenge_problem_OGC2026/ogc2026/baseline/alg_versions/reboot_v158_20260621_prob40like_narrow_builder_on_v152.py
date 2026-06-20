"""reboot_v158_20260621_prob40like_narrow_builder_on_v152.py

Strategy:
    Preserve the current-tree recovery-safe parent v152 everywhere except the
    narrow prob40-like family, where the widened internal builder is replaced by
    a stable narrow direct due_release_proc builder.

Metadata:
    version_id: reboot_v158_20260621_prob40like_narrow_builder_on_v152
    parent_version: reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151
    status: rejected
    timestamp: 2026-06-21 KST
    strategy:
        - Preserve v152 unchanged outside the target subtype.
        - On the narrow prob40-like family only, bypass the inherited widened
          base builder.
        - Replace it with one stable direct due_release_proc build using
          narrower bay and position scope.
        - Keep the narrow direct builder only when it is officially feasible;
          otherwise fall back to v152.
    hypothesis:
        The current-tree prob40-like regression is being driven by an
        over-broad internal builder that lives on a 58-60s cliff. A narrower
        direct builder should improve both quality and runtime stability on
        that family.
    intended_metric_target:
        - improve prob40-like T/objective on the current tree
        - preserve accepted_for_score 40/40 behavior inherited from v152
        - reduce runtime-cliff risk on the target family
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
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151 as v152


ACTIVE_VERSION = "reboot_v158_20260621_prob40like_narrow_builder_on_v152"

_PROB40LIKE_BUDGET_CAP = 55.0
_PROB40LIKE_TOP_BAYS = 3
_PROB40LIKE_MAX_POSITIONS = 10


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


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    tier = v050._time_tier(timelimit)
    if tier in {"very_short", "short"}:
        return v152.algorithm(prob_info, timelimit)

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
