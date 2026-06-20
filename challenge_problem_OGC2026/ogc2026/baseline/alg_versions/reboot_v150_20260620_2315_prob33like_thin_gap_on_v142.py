"""reboot_v150_20260620_2315_prob33like_thin_gap_on_v142.py

Strategy:
    Keep trusted v142 as the default line, then replay the same prob33-like
    low-headroom repair as v149 with a much thinner gap-single search.

Metadata:
    version_id: reboot_v150_20260620_2315_prob33like_thin_gap_on_v142
    parent_version: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
    status: rejected
    timestamp: 2026-06-20 23:15 KST
    strategy:
        - Preserve v142 unchanged outside the prob33-like runtime feature class.
        - On that subtype only, build the shallower v065 warm start directly.
        - Replay the same trusted gap-single plus fast-single sequence as v149.
        - Thin only the gap-single position sample width and budget.
        - Keep only strictly better officially feasible candidates.
    hypothesis:
        The v149 timeout cliff is caused by over-searching inside the expensive
        prob33-like gap-single move, not by the move itself. Replaying the same
        move sequence with a much thinner quantile sample should preserve the
        T=3805 row while restoring runtime margin.
    intended_metric_target:
        - keep the prob33-like T/objective gain scoreable on the canonical surface
        - preserve accepted_for_score 40/40
        - improve total T / avg T without reopening non-target rows
    validation_status:
        rejected after full40 reopening on prob_31/prob_32/prob_37
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v150_train40_20260620_001
    rollback_target: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
"""

from __future__ import annotations

import time


ACTIVE_VERSION = "reboot_v150_20260620_2315_prob33like_thin_gap_on_v142"


def _minimum_headroom(timelimit: float) -> float:
    return max(0.9, timelimit * 0.015)


def _thin_gap_budget(remaining: float) -> float:
    return min(1.5, remaining)


def _try_prob33like_thin_gap_repair(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
) -> tuple[dict, dict]:
    from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
    from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
    from alg_versions import reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert as v073
    from alg_versions import reboot_v081_20260619_1948_prob33like_runtime_flatten as v081

    gap_budget = _thin_gap_budget(remaining)
    if gap_budget <= 0.0:
        return base_solution, base_result

    started = time.time()
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = v081.v069._target_block_ids(prob_info, base_assignments)
    if not target_block_ids:
        return base_solution, base_result

    gap_assignments = v081._quantile_gap_single_reinsert(
        prob_info,
        base_assignments,
        target_block_ids[0],
        max_positions=6,
        deadline=started + gap_budget,
    )
    if gap_assignments is None:
        print(
            f"[baseline_hh reboot_v150] no_prob33like_thin_gap instance={prob_info.get('name')} "
            f"budget={gap_budget:.2f}s elapsed={time.time() - started:.2f}s"
        )
        return base_solution, base_result

    gap_solution = v001._solution_from_assignments(gap_assignments)
    gap_result = v001.check_feasibility(prob_info, gap_solution)
    print(
        f"[baseline_hh reboot_v150] prob33like_thin_gap instance={prob_info.get('name')} "
        f"target_block={target_block_ids[0]} feasible={gap_result.get('feasible')} "
        f"T={gap_result.get('obj1')} objective={gap_result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={gap_budget:.2f}s"
    )

    best_solution = base_solution
    best_result = base_result
    if v064._result_key(gap_result) < v064._result_key(best_result):
        best_solution = gap_solution
        best_result = gap_result

    fast_target_ids = v064._tardy_block_ids(prob_info, gap_assignments, 1)
    if fast_target_ids:
        fast_assignments = v073._limited_single_reinsert(
            prob_info,
            gap_assignments,
            fast_target_ids[0],
            max_positions=8,
            max_orients=4,
        )
        if fast_assignments is not None:
            fast_solution = v001._solution_from_assignments(fast_assignments)
            fast_result = v001.check_feasibility(prob_info, fast_solution)
            print(
                f"[baseline_hh reboot_v150] prob33like_fast_single instance={prob_info.get('name')} "
                f"target_block={fast_target_ids[0]} feasible={fast_result.get('feasible')} "
                f"T={fast_result.get('obj1')} objective={fast_result.get('objective')}"
            )
            if v064._result_key(fast_result) < v064._result_key(best_result):
                best_solution = fast_solution
                best_result = fast_result

    return best_solution, best_result


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
            f"[baseline_hh reboot_v150] keep_v065_prob33like_base instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s min_headroom={min_headroom:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result = _try_prob33like_thin_gap_repair(
        prob_info,
        base_solution,
        base_result,
        remaining,
    )
    if v064._result_key(best_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v150] selected_prob33like_thin_gap instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v150] no_prob33like_gain instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={best_result.get('obj1')} "
        f"remaining={remaining:.2f}s"
    )
    return base_solution
