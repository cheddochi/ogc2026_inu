"""reboot_v085_20260619_0512_fourbay_dense_extended_reinsert.py

Strategy:
    Keep trusted v084 as the default path, then replay the tiny reinsertion
    portfolio on a slightly longer tardy shortlist for the dense 4-bay
    high-proc family.

Metadata:
    version_id: reboot_v085_20260619_0512_fourbay_dense_extended_reinsert
    parent_version: reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio
    status: candidate
    timestamp: 2026-06-19 05:12 KST
    strategy:
        - Preserve v084 unchanged outside the target family.
        - Build the trusted v084 warm start first.
        - On the dense 4-bay high-proc family, replay the same bounded
          reinsertion move on a tardy shortlist of 6 instead of 3.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The inherited v074 shortlist width is still a little too narrow on the
        dense 4-bay family. A slightly longer shortlist can recover small
        objective gains on prob_31 / prob_40 without waking unrelated rows.
    intended_metric_target:
        - improve dense 4-bay family rows
        - preserve the current 40/40 scoreable contract
        - improve avg objective versus trusted v084
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio
"""

from __future__ import annotations

import time

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert as v073
from alg_versions import reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio as v074
from alg_versions import reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio as v084


ACTIVE_VERSION = "reboot_v085_20260619_0512_fourbay_dense_extended_reinsert"


def _candidate_limit(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 6,
        "long": 6,
        "very_long": 7,
    }[tier]


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 1.4,
        "long": 1.8,
        "very_long": 2.2,
    }[tier]
    return min(cap, remaining)


def _try_extended_reinsert_portfolio(
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
        f"[baseline_hh reboot_v085] fourbay_dense_extended_reinsert instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    features = v074._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v084.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    family_budget = v074._family_direct_budget(float(timelimit), tier)
    if (
        not base_result.get("feasible")
        or not v074._matches_fourbay_highproc_dense_family(features)
        or family_budget < 45.0
        or float(base_result.get("obj1") or 0.0) <= 2500.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= 0.5:
        print(
            f"[baseline_hh reboot_v085] skip_fourbay_dense_extended_reinsert instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_extended_reinsert_portfolio(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v085] selected_fourbay_dense_extended_reinsert instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v085] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
