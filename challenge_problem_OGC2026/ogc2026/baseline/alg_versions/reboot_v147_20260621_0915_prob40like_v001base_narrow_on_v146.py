"""reboot_v147_20260621_0915_prob40like_v001base_narrow_on_v146.py

Strategy:
    Keep the current prob27-like candidate path intact, but recover the
    prob40-like family on the current source tree by bypassing the inherited
    unstable warm-start chain and using the direct v001 warm start before one
    bounded narrow quantile move.

Metadata:
    version_id: reboot_v147_20260621_0915_prob40like_v001base_narrow_on_v146
    parent_version: reboot_v146_20260621_0215_prob27like_efficiency_shortlist_on_v142
    status: candidate
    timestamp: 2026-06-21 09:15 KST
    strategy:
        - Preserve parent v146 unchanged outside the prob40-like selector.
        - On the prob40-like selector only, build the direct v001 warm start.
        - Replay only the bounded v130 narrow quantile move on top of that base.
        - Keep only strictly better officially feasible candidates.
    hypothesis:
        On the current source tree, the inherited v132/v135/v142 warm-start
        chain is the main Family B failure mode. Replacing only that warm-start
        base with the direct v001 surface should restore the prob40-like tail
        without touching the parent prob27-like candidate logic.
    intended_metric_target:
        - recover the prob40-like high-T tail on the current tree
        - preserve accepted_for_score 40/40 and timeout 0
        - keep the parent prob27-like candidate behavior unchanged
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v146_20260621_0215_prob27like_efficiency_shortlist_on_v142
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122 as v123
from alg_versions import reboot_v130_20260620_1125_prob40like_narrow_quantile_on_v123 as v130
from alg_versions import reboot_v146_20260621_0215_prob27like_efficiency_shortlist_on_v142 as v146


ACTIVE_VERSION = "reboot_v147_20260621_0915_prob40like_v001base_narrow_on_v146"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    overall_started = time.time()
    timelimit = float(timelimit)
    tier = v123._time_tier(timelimit)
    features = v130._selector_features(prob_info)

    if (
        tier in {"very_short", "short"}
        or not v130._matches_prob40like_narrow_tail(features)
    ):
        return v146.algorithm(prob_info, timelimit)

    base_solution = v001.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or float(base_result.get("obj1") or 0.0) < 5000.0
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - overall_started))
    reserve = v123._dynamic_reserve(timelimit)
    if remaining <= reserve + 1.5:
        print(
            f"[baseline_hh reboot_v147] skip_prob40like_v001base_guard "
            f"instance={prob_info.get('name')} tier={tier} remaining={remaining:.2f}s "
            f"reserve={reserve:.2f}s base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result = v130._try_narrow_quantile_reinsert(
        prob_info,
        base_solution,
        base_result,
        timelimit,
        overall_started,
        tier,
    )
    if v123._result_key(best_result) < v123._result_key(base_result):
        print(
            f"[baseline_hh reboot_v147] selected_prob40like_v001base_narrow "
            f"instance={prob_info.get('name')} T={best_result.get('obj1')} "
            f"objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v147] keep_v001_prob40like_base "
        f"instance={prob_info.get('name')} base_T={base_result.get('obj1')} "
        f"cand_T={best_result.get('obj1')}"
    )
    return base_solution
