"""reboot_v100_20260619_1355_prob37like_flattened_iterative_reinsert_on_v099.py

Strategy:
    Keep v099 as the default path, but flatten the current-source prob37-like
    runtime-cliff subtype to a scoreable v057-family direct base and spend only
    the remaining headroom on a tiny iterative bounded reinsertion portfolio.

Metadata:
    version_id: reboot_v100_20260619_1355_prob37like_flattened_iterative_reinsert_on_v099
    parent_version: reboot_v099_20260619_1845_prob31like_runtime_flatten_on_v096
    status: candidate
    timestamp: 2026-06-19 13:55 KST
    strategy:
        - Preserve v099 unchanged outside the targeted prob37-like subtype.
        - On the targeted subtype, bypass the inherited v060/v065/v093/v096
          delegated warm-start chain that currently starves later repair phases.
        - Start from the still-scoreable v057-family direct base.
        - Reapply a very small iterative one-block reinsertion portfolio using
          the remaining wall-clock time only.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The current prob37-like failure is primarily a warm-start runtime cliff,
        not a lack of local improvement signal. A shallower direct base plus a
        few cheap reinsertion steps should recover a scoreable row with better
        objective than the raw v057 fallback while preserving the prob31-like
        recovery already introduced in v099.
    intended_metric_target:
        - restore prob37-like scoreability under the current source state
        - preserve the v099 prob31-like runtime recovery
        - keep non-target rows on the exact v099 path
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v099_20260619_1845_prob31like_runtime_flatten_on_v096
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v057_20260618_0006_prob38like_dual_policy_portfolio as v057
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single as v072
from alg_versions import reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert as v073
from alg_versions import reboot_v090_20260619_0802_threebay_midproc_slackband_reinsert as v090
from alg_versions import reboot_v099_20260619_1845_prob31like_runtime_flatten_on_v096 as v099


ACTIVE_VERSION = "reboot_v100_20260619_1355_prob37like_flattened_iterative_reinsert_on_v099"


def _matches_prob37like_runtime_class(prob_info: dict) -> bool:
    features64 = v064._selector_features(prob_info)
    features72 = v072._selector_features(prob_info)
    return (
        v064._matches_threebay_diffuse_moderate_class(features64)
        and v090._matches_threebay_midproc_slackband_family(features64)
        and v072._matches_threebay_xlarge_lowproc_class(features72)
    )


def _step_cap(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 3,
        "long": 4,
        "very_long": 5,
    }[tier]


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 8.0,
        "long": 10.0,
        "very_long": 12.0,
    }[tier]
    return max(0.0, min(cap, remaining - 0.5))


def _candidate_block_ids(prob_info: dict, assignments: dict[int, dict]) -> list[int]:
    seen: list[int] = []
    for block_id in v064._tardy_block_ids(prob_info, assignments, 8) + v072._target_block_ids(
        prob_info,
        assignments,
    ):
        if block_id not in seen:
            seen.append(block_id)
    return seen


def _result_key(result: dict) -> tuple[float, float, float, float]:
    return (
        float(result.get("obj1") if result.get("feasible") else float("inf")),
        float(result.get("objective") if result.get("feasible") else float("inf")),
        float(result.get("obj2") if result.get("feasible") else float("inf")),
        float(result.get("obj3") if result.get("feasible") else float("inf")),
    )


def _try_iterative_reinsert_portfolio(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    deadline = time.time() + budget
    best_solution = base_solution
    best_result = base_result
    attempted_steps: list[tuple[int, int | None, float | None, float | None]] = []

    for step_idx in range(_step_cap(tier)):
        if time.time() >= deadline:
            break

        assignments = v064._solution_to_assignments(best_solution)
        best_step = None
        for target_block_id in _candidate_block_ids(prob_info, assignments):
            if time.time() >= deadline:
                break
            candidate_assignments = v073._limited_single_reinsert(
                prob_info,
                assignments,
                target_block_id,
                max_positions=12,
                max_orients=4,
            )
            if candidate_assignments is None:
                continue

            candidate_solution = v001._solution_from_assignments(candidate_assignments)
            candidate_result = v001.check_feasibility(prob_info, candidate_solution)
            if best_step is None or _result_key(candidate_result) < _result_key(best_step[2]):
                best_step = (target_block_id, candidate_solution, candidate_result)

        if best_step is None or _result_key(best_step[2]) >= _result_key(best_result):
            attempted_steps.append((step_idx + 1, None, None, None))
            break

        target_block_id, best_solution, best_result = best_step
        attempted_steps.append(
            (
                step_idx + 1,
                target_block_id,
                float(best_result.get("obj1", 0.0)),
                float(best_result.get("objective", 0.0)),
            )
        )

    print(
        f"[baseline_hh reboot_v100] prob37like_iterative_reinsert instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted_steps} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    tier = v050._time_tier(float(timelimit))
    if tier in {"very_short", "short"} or not _matches_prob37like_runtime_class(prob_info):
        return v099.algorithm(prob_info, timelimit)

    started = time.time()
    base_solution = v057.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)
    if not base_result.get("feasible"):
        return v099.algorithm(prob_info, timelimit)

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= 0.5:
        print(
            f"[baseline_hh reboot_v100] keep_prob37like_direct_base instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_iterative_reinsert_portfolio(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if _result_key(research_result) < _result_key(base_result):
        print(
            f"[baseline_hh reboot_v100] selected_prob37like_iterative_reinsert instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v100] keep_prob37like_direct_base instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
