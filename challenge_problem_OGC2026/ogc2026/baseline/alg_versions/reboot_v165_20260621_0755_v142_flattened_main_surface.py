"""reboot_v165_20260621_0755_v142_flattened_main_surface.py

Strategy:
    Flatten the exact trusted v142 body into a new main-module surface with no
    behavioral change intended.

Metadata:
    version_id: reboot_v165_20260621_0755_v142_flattened_main_surface
    parent_version: reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135
    status: candidate
    timestamp: 2026-06-21 07:55 KST
    strategy:
        - Copy the exact v142 body into a new main algorithm module.
        - Do not add any new selector, search, or budget logic.
        - Use the copy only to test whether main-module flattening reproduces
          direct v142 more faithfully than imported wrapper delegation.
    hypothesis:
        The hidden-risk observed in v164 is caused by imported wrapper
        delegation rather than by the v142 logic itself. Executing the same
        v142 body as the main algorithm module should align much more closely
        with direct v142 on representative non-target rows.
    intended_metric_target:
        - establish a structurally trustworthy direct parent surface for future
          real T-breakthrough candidates
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135
"""

from __future__ import annotations

import time


ACTIVE_VERSION = "reboot_v165_20260621_0755_v142_flattened_main_surface"


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
        slack = due - release - proc
        if slack <= 2.0:
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


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    tier = _time_tier(timelimit)

    from alg_versions import reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135 as v136

    if tier in {"very_short", "short"}:
        return v136.algorithm(prob_info, timelimit)

    features = _selector_features(prob_info)
    if not _matches_prob40like_narrow_tail(features):
        return v136.algorithm(prob_info, timelimit)

    overall_started = time.time()
    base_solution = v136.algorithm(prob_info, timelimit)

    from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
    from alg_versions import reboot_v124_20260620_1125_fourbay_highproc_toptardy_quantile_on_v123 as v124

    base_result = v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or float(base_result.get("obj1") or 0.0) < 5000.0
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - overall_started))
    reserve = _dynamic_reserve(timelimit)
    if remaining <= reserve + 4.5:
        print(
            f"[baseline_hh reboot_v142] skip_prob40like_broad_move instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result = v124._try_toptardy_quantile_reinsert(
        prob_info,
        base_solution,
        base_result,
        timelimit,
        overall_started,
        tier,
    )
    if v124._result_key(best_result) < v124._result_key(base_result):
        print(
            f"[baseline_hh reboot_v142] selected_prob40like_broad_move instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v142] keep_v136_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={best_result.get('obj1')}"
    )
    return base_solution
