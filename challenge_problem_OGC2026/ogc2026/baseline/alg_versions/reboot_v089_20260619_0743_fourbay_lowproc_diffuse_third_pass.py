"""reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass.py

Strategy:
    Keep trusted v088 as the default path, then replay one more bounded pass
    on the same 4-bay early-short low-proc diffuse family.

Metadata:
    version_id: reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass
    parent_version: reboot_v088_20260619_0728_fourbay_lowproc_diffuse_wider_second_pass
    status: accepted BEST
    timestamp: 2026-06-19 07:43 KST
    strategy:
        - Preserve v088 unchanged outside the target family.
        - Build the trusted v088 warm start first.
        - On the same low-proc diffuse 4-bay family, replay one extra bounded
          reinsertion pass on the updated assignments.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The residual shortlist is not fully saturated yet. One more bounded
        pass can recover the last local objective slack on a small subset of
        the same family.
    intended_metric_target:
        - improve the already-validated low-proc diffuse 4-bay family further
        - preserve the current 40/40 scoreable contract
        - improve avg objective versus trusted v088
    validation_status:
        smoke accepted 9/9, targeted accepted 6/6, full train40 accepted_for_score 40/40
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v089_train40_20260619_001
    rollback_target: reboot_v088_20260619_0728_fourbay_lowproc_diffuse_wider_second_pass
"""

from __future__ import annotations

import time

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert as v073
from alg_versions import reboot_v088_20260619_0728_fourbay_lowproc_diffuse_wider_second_pass as v088


ACTIVE_VERSION = "reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass"


def _candidate_limit(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 5,
        "long": 6,
        "very_long": 7,
    }[tier]


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 0.9,
        "long": 1.1,
        "very_long": 1.5,
    }[tier]
    return min(cap, remaining)


def _try_third_pass_portfolio(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    started = time.time()
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = v064._tardy_block_ids(prob_info, base_assignments, _candidate_limit(tier))
    if not target_block_ids:
        return base_solution, base_result

    best_solution = base_solution
    best_result = base_result
    attempted = []

    for target_block_id in target_block_ids:
        if time.time() - started > budget:
            break
        candidate_assignments = v073._limited_single_reinsert(
            prob_info,
            base_assignments,
            target_block_id,
            max_positions=8,
            max_orients=4,
        )
        if candidate_assignments is None:
            attempted.append((target_block_id, None, None))
            continue

        candidate_solution = v064.v001._solution_from_assignments(candidate_assignments)
        candidate_result = v064.v001.check_feasibility(prob_info, candidate_solution)
        attempted.append(
            (
                target_block_id,
                candidate_result.get("obj1"),
                candidate_result.get("objective"),
            )
        )
        if v064._result_key(candidate_result) < v064._result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result

    print(
        f"[baseline_hh reboot_v089] fourbay_lowproc_diffuse_third_pass instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    features = v088.v087.v086._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v088.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not v088.v087.v086._matches_fourbay_lowproc_diffuse_family(features)
        or float(base_result.get("obj1") or 0.0) <= 0.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= 0.4:
        print(
            f"[baseline_hh reboot_v089] skip_fourbay_lowproc_diffuse_third_pass instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_third_pass_portfolio(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v089] selected_fourbay_lowproc_diffuse_third_pass instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v089] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
