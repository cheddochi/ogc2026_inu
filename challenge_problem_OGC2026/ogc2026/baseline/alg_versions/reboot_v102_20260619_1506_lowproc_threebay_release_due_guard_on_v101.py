"""reboot_v102_20260619_1506_lowproc_threebay_release_due_guard_on_v101.py

Strategy:
    Keep v101 as the warm start, but add one bounded direct `release_due`
    candidate on the low-proc 3-bay diffuse-preference subtype and keep the
    better feasible result.

Metadata:
    version_id: reboot_v102_20260619_1506_lowproc_threebay_release_due_guard_on_v101
    parent_version: reboot_v101_20260619_1425_prob38like_feature_budget_restore_on_v100
    status: candidate
    timestamp: 2026-06-19 15:06 KST
    strategy:
        - Build the v101 solution first.
        - Detect the low-proc 3-bay diffuse-preference subtype from `prob_info`
          features only.
        - On that subtype, use leftover time for one bounded direct policy:
          `release_due`, `top_bays=3`, `max_positions=12`.
        - Keep the better feasible result and leave every non-target row on the
          exact v101 path.
    hypothesis:
        After the v101 prob38-like repair, the dominant remaining loss versus
        the historical v096 frontier sits in a low-proc 3-bay diffuse class.
        A small direct `release_due` candidate is much stronger on that subtype
        under the current source state than the delegated parent chain, while
        the v101 warm start remains the safer default outside that class.
    intended_metric_target:
        - reduce the current-source prob9-like regression
        - preserve the recovered scoreable contract from v101
        - avoid reopening prob31/prob37/prob38 runtime cliffs
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v101_20260619_1425_prob38like_feature_budget_restore_on_v100
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v101_20260619_1425_prob38like_feature_budget_restore_on_v100 as v101


ACTIVE_VERSION = "reboot_v102_20260619_1506_lowproc_threebay_release_due_guard_on_v101"


def _matches_lowproc_threebay_diffuse_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and 100 <= int(features["blocks"]) <= 210
        and features["proc_mean"] <= 8.0
        and features["pref_concentration"] <= 0.40
        and 42.0 <= features["pref_gap_mean"] <= 52.5
        and 0.33 <= features["pref_pressure"] <= 0.40
        and features["workload_imbalance_pressure"] <= 0.13
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result.get("obj1", float("inf"))),
        float(result.get("objective", float("inf"))),
        float(result.get("obj2", float("inf"))),
        float(result.get("obj3", float("inf"))),
    )


def _should_try_direct(features: dict[str, float], tier: str, remaining: float, reserve: float) -> bool:
    if tier in {"very_short", "short"}:
        return False
    if not _matches_lowproc_threebay_diffuse_class(features):
        return False
    return remaining > reserve + 6.0


def _direct_budget(timelimit: float, remaining: float, reserve: float, tier: str) -> float:
    cap = {
        "standard": 18.0,
        "long": 18.0,
        "very_long": 20.0,
    }.get(tier, 0.0)
    return min(cap, max(8.0, remaining - reserve))


def _direct_candidate(prob_info: dict, budget: float) -> tuple[dict, dict]:
    started = time.time()
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="release_due",
        top_bays=3,
        max_positions=12,
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v102] lowproc_threebay_release_due instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s"
    )
    return candidate, result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    overall_started = time.time()
    tier = v050._time_tier(float(timelimit))
    features = v050._selector_features(prob_info)

    best_solution = v101.algorithm(prob_info, timelimit)
    best_result = v001.check_feasibility(prob_info, best_solution)
    elapsed = time.time() - overall_started
    remaining = max(0.0, float(timelimit) - elapsed)
    reserve = _dynamic_reserve(float(timelimit))
    print(
        f"[baseline_hh reboot_v102] warm_start instance={prob_info.get('name')} "
        f"tier={tier} feasible={best_result.get('feasible')} "
        f"T={best_result.get('obj1')} objective={best_result.get('objective')} "
        f"elapsed={elapsed:.2f}s remaining={remaining:.2f}s"
    )

    if not best_result.get("feasible"):
        return best_solution

    if not _should_try_direct(features, tier, remaining, reserve):
        print(
            f"[baseline_hh reboot_v102] skip_direct instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return best_solution

    budget = _direct_budget(float(timelimit), remaining, reserve, tier)
    if budget < 8.0:
        print(
            f"[baseline_hh reboot_v102] budget_too_small instance={prob_info.get('name')} "
            f"budget={budget:.2f}s"
        )
        return best_solution

    candidate_solution, candidate_result = _direct_candidate(prob_info, budget)
    if _result_key(candidate_result) < _result_key(best_result):
        print(
            f"[baseline_hh reboot_v102] selected_direct instance={prob_info.get('name')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        return candidate_solution

    print(
        f"[baseline_hh reboot_v102] keep_warm_start instance={prob_info.get('name')} "
        f"best_T={best_result.get('obj1')} cand_T={candidate_result.get('obj1')}"
    )
    return best_solution
