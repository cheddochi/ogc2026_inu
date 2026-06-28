"""reboot_v057_20260618_0006_prob38like_dual_policy_portfolio.py

Strategy:
    Keep current-source v050 as the default path, but upgrade the prob38-like
    high-proc large 3-bay class from one fixed direct policy to a bounded
    two-policy portfolio.

Metadata:
    version_id: reboot_v057_20260618_0006_prob38like_dual_policy_portfolio
    parent_version: reboot_v050_20260617_2015_prob38like_release_aware
    status: accepted
    timestamp: 2026-06-18 00:06 KST
    strategy:
        - Preserve v050 behavior on every non-target row.
        - On the prob38-like feature class, run the existing release-aware
          direct policy first.
        - If safe time remains, compare one shallower due_long direct policy
          and keep the better officially feasible result.
    hypothesis:
        The current-source top contributor is still the high-proc large 3-bay
        prob38-like class. v050 already proves one direct policy is feasible
        there, but a second shallow large-job-biased order may lower T without
        perturbing the rest of the portfolio.
    intended_metric_target:
        - improve prob_38 T and objective
        - preserve smoke-8 rows unchanged
        - improve avg T and objective versus current-source active v050
    validation_status:
        accepted_for_score=40/40 on current-source full train40 benchmark
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v057_train40_20260618_001
    rollback_target: reboot_v050_20260617_2015_prob38like_release_aware
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050


ACTIVE_VERSION = "reboot_v057_20260618_0006_prob38like_dual_policy_portfolio"


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result["obj1"]),
        float(result["objective"]),
        float(result["obj2"]),
        float(result["obj3"]),
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _due_long_budget(remaining: float, tier: str) -> float:
    cap = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 42.0,
        "long": 46.0,
        "very_long": 50.0,
    }[tier]
    reserve = _dynamic_reserve(remaining)
    fraction = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 0.74,
        "long": 0.78,
        "very_long": 0.80,
    }[tier]
    return min(cap, max(8.0, remaining * fraction - reserve))


def _due_long_positions(tier: str) -> int:
    return {
        "very_short": 8,
        "short": 10,
        "standard": 14,
        "long": 16,
        "very_long": 16,
    }[tier]


def _build_candidate(
    prob_info: dict,
    *,
    budget: float,
    order_strategy: str,
    max_positions: int,
) -> tuple[dict, dict]:
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=order_strategy,
        top_bays=3,
        max_positions=max_positions,
        max_orients=4,
    )
    return candidate, v001.check_feasibility(prob_info, candidate)


def _class_solution(prob_info: dict, timelimit: float, tier: str) -> dict:
    started = time.time()

    release_budget = v050._policy_budget(float(timelimit), tier)
    release_positions = v050._policy_max_positions(tier)
    release_candidate, release_result = _build_candidate(
        prob_info,
        budget=release_budget,
        order_strategy="due_release_proc",
        max_positions=release_positions,
    )

    best_candidate = release_candidate
    best_result = release_result
    attempted = [
        (
            "due_release_proc",
            release_result.get("feasible"),
            release_result.get("obj1"),
            release_result.get("objective"),
        )
    ]

    elapsed = time.time() - started
    remaining = max(0.0, float(timelimit) - elapsed)
    reserve = _dynamic_reserve(float(timelimit))

    if tier not in {"very_short", "short"} and remaining > reserve + 10.0:
        long_budget = _due_long_budget(remaining, tier)
        long_candidate, long_result = _build_candidate(
            prob_info,
            budget=long_budget,
            order_strategy="due_long_proc",
            max_positions=_due_long_positions(tier),
        )
        attempted.append(
            (
                "due_long_proc",
                long_result.get("feasible"),
                long_result.get("obj1"),
                long_result.get("objective"),
            )
        )
        if _result_key(long_result) < _result_key(best_result):
            best_candidate = long_candidate
            best_result = long_result

    print(
        f"[baseline_hh reboot_v057] prob38like_dual_policy instance={prob_info.get('name')} "
        f"best_feasible={best_result.get('feasible')} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"tier={tier} attempted={attempted}"
    )

    if best_result.get("feasible"):
        return best_candidate

    print(
        f"[baseline_hh reboot_v057] prob38like_fallback instance={prob_info.get('name')} "
        f"tier={tier}"
    )
    return v050.algorithm(prob_info, timelimit)


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v050._selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and v050._matches_prob38like_class(features):
        return _class_solution(prob_info, timelimit, tier)
    return v050.algorithm(prob_info, timelimit)
