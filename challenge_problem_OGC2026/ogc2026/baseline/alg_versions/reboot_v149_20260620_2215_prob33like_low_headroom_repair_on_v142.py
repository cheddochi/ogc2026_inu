"""reboot_v149_20260620_2215_prob33like_low_headroom_repair_on_v142.py

Strategy:
    Keep trusted v142 as the default line, then restore the existing
    prob33-like runtime repair under a shallower warm start and a lower
    headroom gate.

Metadata:
    version_id: reboot_v149_20260620_2215_prob33like_low_headroom_repair_on_v142
    parent_version: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
    status: candidate
    timestamp: 2026-06-20 22:15 KST
    strategy:
        - Preserve v142 unchanged outside the prob33-like runtime feature class.
        - On that subtype only, build the shallower v065 warm start directly.
        - If there is small positive headroom, replay the trusted v081 runtime
          repair instead of skipping it under the old conservative gate.
        - Keep only strictly better officially feasible candidates.
    hypothesis:
        The current prob33-like regression is caused by budget starvation, not
        by the repair logic itself. Reusing the shallower v065 warm start and
        allowing the already trusted v081 repair to run under lower headroom
        should recover the 3805 row with more time margin on the current tree.
    intended_metric_target:
        - restore the prob33-like T/objective gain on the canonical surface
        - preserve accepted_for_score 40/40
        - improve total T / avg T without reopening non-target rows
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
"""

from __future__ import annotations

import time


ACTIVE_VERSION = "reboot_v149_20260620_2215_prob33like_low_headroom_repair_on_v142"


def _minimum_headroom(timelimit: float) -> float:
    return max(0.9, timelimit * 0.015)


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)

    from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
    from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
    from alg_versions import reboot_v065_20260618_1735_threebay_diffuse_single_research as v065
    from alg_versions import reboot_v081_20260619_1948_prob33like_runtime_flatten as v081
    from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as v142

    features = v064._selector_features(prob_info)
    tier = v064.v050._time_tier(timelimit)
    if tier in {"very_short", "short"} or not v081._matches_prob33like_runtime_class(features):
        return v142.algorithm(prob_info, timelimit)

    started = time.time()
    base_solution = v065.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)
    remaining = max(0.0, timelimit - (time.time() - started))
    min_headroom = _minimum_headroom(timelimit)

    if (
        not base_result.get("feasible")
        or float(base_result.get("obj1") or 0.0) < 3800.0
        or remaining < min_headroom
    ):
        print(
            f"[baseline_hh reboot_v149] keep_v065_prob33like_base instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s min_headroom={min_headroom:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result = v081._try_prob33like_runtime_repair(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if v064._result_key(best_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v149] selected_prob33like_low_headroom_repair instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v149] no_prob33like_gain instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={best_result.get('obj1')} "
        f"remaining={remaining:.2f}s"
    )
    return base_solution
