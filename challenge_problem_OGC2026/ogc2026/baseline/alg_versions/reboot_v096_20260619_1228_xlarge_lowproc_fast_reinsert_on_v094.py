"""reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094.py

Strategy:
    Keep trusted v094 as the default path, then apply a cheap bounded
    single-block reinsertion on top of the current warm start for the 3-bay
    xlarge low-proc tight-slack family.

Metadata:
    version_id: reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094
    parent_version: reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093
    status: accepted
    timestamp: 2026-06-19 12:28 KST
    strategy:
        - Preserve v094 unchanged outside the target subtype.
        - Build the trusted v094 warm start first.
        - On the target family, use the v072 target-block selector but replace
          the slow greedy-prefix replay with the fast bounded v073 reinsertion.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The xlarge 3-bay low-proc family still has a small local repair signal
        after the v093/v094 improvements, but only a micro local move is safe
        under the 60s official limit.
    intended_metric_target:
        - improve prob37-like rows
        - keep the sibling prob39-like row neutral or better
        - preserve the current 40/40 scoreable contract
        - improve avg objective versus trusted v094
    validation_status:
        accepted_for_score=40/40 on full train40 benchmark
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001
    rollback_target: reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093
"""

from __future__ import annotations

import time

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single as v072
from alg_versions import reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert as v073
from alg_versions import reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093 as v094


ACTIVE_VERSION = "reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094"


def _try_fast_targeted_reinsert(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
) -> tuple[dict, dict]:
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = v072._target_block_ids(prob_info, base_assignments)
    if not target_block_ids:
        return base_solution, base_result

    candidate_assignments = v073._limited_single_reinsert(
        prob_info,
        base_assignments,
        target_block_ids[0],
        max_positions=6,
        max_orients=4,
    )
    if candidate_assignments is None:
        return base_solution, base_result

    candidate_solution = v064.v001._solution_from_assignments(candidate_assignments)
    candidate_result = v064.v001.check_feasibility(prob_info, candidate_solution)
    print(
        f"[baseline_hh reboot_v096] xlarge_lowproc_fast_reinsert instance={prob_info.get('name')} "
        f"target_block={target_block_ids[0]} feasible={candidate_result.get('feasible')} "
        f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
    )
    if v064._result_key(candidate_result) < v064._result_key(base_result):
        return candidate_solution, candidate_result
    return base_solution, base_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    features = v072._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v094.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not v072._matches_threebay_xlarge_lowproc_class(features)
        or float(base_result.get("obj1") or 0.0) < 3000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if tier in {"very_short", "short"} or remaining <= 0.5:
        print(
            f"[baseline_hh reboot_v096] skip_xlarge_lowproc_fast_reinsert instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_fast_targeted_reinsert(
        prob_info,
        base_solution,
        base_result,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v096] selected_xlarge_lowproc_fast_reinsert instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v096] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
