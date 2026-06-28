"""reboot_v111_20260619_2130_prob31like_stable_direct_cap_on_v109.py

Strategy:
    Keep v109 as the default path, but replace only the prob31-like direct
    warm start with the same repair chain under a smaller feature-based direct
    cap.

Metadata:
    version_id: reboot_v111_20260619_2130_prob31like_stable_direct_cap_on_v109
    parent_version: reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108
    status: candidate
    timestamp: 2026-06-19 21:30 KST
    strategy:
        - Preserve v109 unchanged outside the prob31-like subtype.
        - On the prob31-like subtype, keep the same preference-spread direct
          builder and the accepted v067/v074/v085 repair chain.
        - Lower only the direct builder cap so the downstream repairs receive
          stable slack under current-source reruns.
    hypothesis:
        Current-source prob31 drift is caused by a timing-sensitive direct
        builder, not by the repair chain. A slightly smaller direct cap should
        stabilize the historical 40328756 / T=2792 path without disturbing the
        prob40-like gain already recovered in v109.
    intended_metric_target:
        - recover the stronger prob31-like row under current-source reruns
        - preserve accepted_for_score 40/40
        - avoid changing non-prob31-like families
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v046_20260617_1835_runtime_sensitive_feature_guard as v046
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v067_20260618_1532_fourbay_highproc_tardy_research as v067
from alg_versions import reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio as v074
from alg_versions import reboot_v078_20260619_1535_fourbay_runtime_family_flatten as v078
from alg_versions import reboot_v085_20260619_0512_fourbay_dense_extended_reinsert as v085
from alg_versions import reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108 as v109


ACTIVE_VERSION = "reboot_v111_20260619_2130_prob31like_stable_direct_cap_on_v109"

_PROB31LIKE_DIRECT_CAP = 46.0


def _build_prob31like_stable_base(prob_info: dict, timelimit: float, tier: str) -> tuple[dict, dict]:
    started = time.time()
    budget = v046._policy_budget(float(timelimit), tier, _PROB31LIKE_DIRECT_CAP)
    solution = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="preference_spread",
        top_bays=4,
        max_positions=14,
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, solution)
    print(
        f"[baseline_hh reboot_v111] prob31like_stable_direct instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s tier={tier}"
    )
    return solution, result


def _prob31like_stable_solution(prob_info: dict, timelimit: float, tier: str) -> tuple[dict, dict]:
    started = time.time()
    features67 = v067._selector_features(prob_info)
    features74 = v074._selector_features(prob_info)

    solution, result = _build_prob31like_stable_base(prob_info, timelimit, tier)
    if not result.get("feasible"):
        return solution, result

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining > v067._dynamic_reserve(float(timelimit)) + 6.0:
        solution, result = v067._try_tardy_research(
            prob_info,
            features67,
            solution,
            result,
            remaining,
            float(timelimit),
            tier,
        )

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if (
        remaining > 0.5
        and v074._family_direct_budget(float(timelimit), tier) >= 45.0
        and v074._matches_fourbay_highproc_dense_family(features74)
    ):
        solution, result = v074._try_fast_reinsert_portfolio(
            prob_info,
            solution,
            result,
            remaining,
            tier,
        )

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining > 0.5:
        solution, result = v085._try_extended_reinsert_portfolio(
            prob_info,
            solution,
            result,
            remaining,
            tier,
        )

    return solution, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v078._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    if tier not in {"very_short", "short"} and v078._matches_prob31like_class(features):
        candidate_solution, candidate_result = _prob31like_stable_solution(
            prob_info,
            timelimit,
            tier,
        )
        if candidate_result.get("feasible"):
            return candidate_solution
        print(
            f"[baseline_hh reboot_v111] prob31like_stable_direct_fallback "
            f"instance={prob_info.get('name')} feasible={candidate_result.get('feasible')} "
            f"objective={candidate_result.get('objective')}"
        )

    return v109.algorithm(prob_info, timelimit)
