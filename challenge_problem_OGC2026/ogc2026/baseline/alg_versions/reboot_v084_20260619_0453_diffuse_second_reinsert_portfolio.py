"""reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio.py

Strategy:
    Keep trusted v083 as the default path, then try one extra tiny bounded
    reinsertion portfolio on the 3-bay diffuse-moderate mid-proc subtype.

Metadata:
    version_id: reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio
    parent_version: reboot_v083_20260619_2106_prob38like_on_stable_prob33_parent
    status: candidate
    timestamp: 2026-06-19 04:53 KST
    strategy:
        - Preserve v083 unchanged outside the targeted subtype.
        - Build the trusted v083 warm start first.
        - On the diffuse-moderate subtype, replay a tiny second one-block
          reinsertion portfolio over the current tardy shortlist.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The trusted v083 warm start already includes the right first repair on
        this subtype, but direct probes show that one more tiny reinsertion can
        still lower objective on long-headroom rows such as prob_37.
    intended_metric_target:
        - improve diffuse-moderate target rows
        - preserve the current 40/40 scoreable contract
        - improve avg objective versus trusted v083
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v083_20260619_2106_prob38like_on_stable_prob33_parent
"""

from __future__ import annotations

import time

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert as v073
from alg_versions import reboot_v083_20260619_2106_prob38like_on_stable_prob33_parent as v083


ACTIVE_VERSION = "reboot_v084_20260619_0453_diffuse_second_reinsert_portfolio"


def _candidate_limit(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 5,
        "long": 5,
        "very_long": 6,
    }[tier]


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 1.2,
        "long": 1.6,
        "very_long": 2.0,
    }[tier]
    return min(cap, remaining)


def _try_second_reinsert_portfolio(
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
        f"[baseline_hh reboot_v084] diffuse_second_reinsert instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    features = v064._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v083.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not v064._matches_threebay_diffuse_moderate_class(features)
        or float(base_result.get("obj1") or 0.0) <= 3500.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= 0.5:
        print(
            f"[baseline_hh reboot_v084] skip_diffuse_second_reinsert instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_second_reinsert_portfolio(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v084] selected_diffuse_second_reinsert instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v084] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
