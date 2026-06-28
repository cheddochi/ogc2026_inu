"""reboot_v090_20260619_0802_threebay_midproc_slackband_reinsert.py

Strategy:
    Keep trusted v089 as the default path, then replay one tiny bounded
    reinsertion portfolio on a 3-bay mid-proc slack-band family.

Metadata:
    version_id: reboot_v090_20260619_0802_threebay_midproc_slackband_reinsert
    parent_version: reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass
    status: rejected
    timestamp: 2026-06-19 08:02 KST
    strategy:
        - Preserve v089 unchanged outside the target family.
        - Build the trusted v089 warm start first.
        - On the target family, replay a bounded one-block reinsertion
          portfolio over the current tardy shortlist.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The current warm start still leaves local L/P slack on a narrow
        3-bay mid-proc slack-band family. One extra bounded reinsertion pass
        can recover objective on rows like prob_35 and prob_37 without
        disturbing the rest of train40.
    intended_metric_target:
        - improve the 3-bay mid-proc slack-band family
        - preserve the current 40/40 scoreable contract
        - improve avg objective versus trusted v089
    validation_status:
        smoke accepted 9/9, targeted accepted 3/3, short45 matched prior timeout risk, full train40 rejected on score regression
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v090_train40_20260619_001
    rollback_target: reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass
"""

from __future__ import annotations

import time

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert as v073
from alg_versions import reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass as v089


ACTIVE_VERSION = "reboot_v090_20260619_0802_threebay_midproc_slackband_reinsert"


def _matches_threebay_midproc_slackband_family(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and int(features["blocks"]) >= 200
        and 11.0 <= features["proc_mean"] <= 12.0
        and 2.15 <= features["slack_mean"] <= 2.5
        and 0.38 <= features["pref_pressure"] <= 0.55
        and 0.10 <= features["workload_imbalance_pressure"] <= 0.45
    )


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
        "standard": 1.0,
        "long": 1.3,
        "very_long": 1.7,
    }[tier]
    return min(cap, remaining)


def _try_midproc_slackband_reinsert_portfolio(
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
        f"[baseline_hh reboot_v090] threebay_midproc_slackband_reinsert instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    features = v064._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v089.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not _matches_threebay_midproc_slackband_family(features)
        or float(base_result.get("obj1") or 0.0) <= 0.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= 0.45:
        print(
            f"[baseline_hh reboot_v090] skip_threebay_midproc_slackband_reinsert instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_midproc_slackband_reinsert_portfolio(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v090] selected_threebay_midproc_slackband_reinsert instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v090] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
