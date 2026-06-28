"""reboot_v200_20260626_trackA_stricter_first20_with_stable_prob38_guard.py

Strategy:
    Build the trusted v195 solution once, then run a small Track A portfolio on
    top of that shared warm start:
      - trusted fallback candidate
      - optional stable prob38 guard candidate
      - strict first20-like cross-bay candidate
      - narrower low-preference-pressure extended candidate
    Keep the best officially feasible result by T-first ordering.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v047_20260617_1935_three_bay_moderate_pressure_due_long as v047
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
from alg_versions import reboot_v195_20260626_familyA_window_reorder_on_v194 as v195
from alg_versions import reboot_v196_20260626_trackA_crossbay_tardy_migration_on_v195 as v196
from alg_versions import reboot_v197_20260626_trackA_stricter_first20_gate_on_v196 as v197


ACTIVE_VERSION = "reboot_v200_20260626_trackA_stricter_first20_with_stable_prob38_guard"


def _allow_extended_track(features: dict[str, float]) -> bool:
    blocks = int(features.get("blocks", 0))
    bays = int(features.get("bays", 0))
    return (
        bays == 4
        and (190 <= blocks <= 210 or 290 <= blocks <= 320)
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.60
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.49
        and float(features.get("pref_concentration", 0.0)) <= 0.31
        and float(features.get("pref_pressure", 0.0)) <= 0.275
    )


def _use_prob38_guard(prob_info: dict) -> bool:
    features = v050._selector_features(prob_info)
    return v050._matches_prob38like_class(features)


def _remaining_budget(started: float, timelimit: float) -> float:
    return max(0.0, timelimit - (time.time() - started))


def _append_candidate(
    candidates: list[tuple[str, dict, dict]],
    label: str,
    solution: dict,
    result: dict,
) -> None:
    if result.get("feasible"):
        candidates.append((label, solution, result))


def _best_candidate(candidates: list[tuple[str, dict, dict]]) -> tuple[str, dict, dict]:
    return min(candidates, key=lambda item: v186.v064._result_key(item[2]))


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    started = time.time()
    tier = v186.v169._time_tier(timelimit)
    reserve = v186._dynamic_reserve(timelimit)

    base_solution = v195.algorithm(prob_info, timelimit)
    base_result = v186.v001.check_feasibility(prob_info, base_solution)
    features = v186._selector_features(prob_info)

    candidates: list[tuple[str, dict, dict]] = [("fallback_v195", base_solution, base_result)]
    attempted: list[tuple[str, float, float]] = [
        (
            "fallback_v195",
            float(base_result.get("obj1") or float("inf")),
            float(base_result.get("objective") or float("inf")),
        )
    ]

    remaining = _remaining_budget(started, timelimit)
    if (
        _use_prob38_guard(prob_info)
        and tier not in {"very_short", "short"}
        and remaining > reserve + 2.0
    ):
        guard_budget = max(1.0, remaining - reserve)
        guard_solution = v047.algorithm(prob_info, guard_budget)
        guard_result = v186.v001.check_feasibility(prob_info, guard_solution)
        attempted.append(
            (
                "guard_v047",
                float(guard_result.get("obj1") or float("inf")),
                float(guard_result.get("objective") or float("inf")),
            )
        )
        _append_candidate(candidates, "guard_v047", guard_solution, guard_result)

    if (
        not base_result.get("feasible")
        or not v186._matches_family_a_tightslack(features)
        or float(base_result.get("obj1") or 0.0) <= 0.0
        or tier in {"very_short", "short"}
    ):
        best_label, best_solution, best_result = _best_candidate(candidates)
        print(
            f"[baseline_hh reboot_v200] return_non_trackA instance={prob_info.get('name')} "
            f"tier={tier} selected={best_label} T={best_result.get('obj1')} "
            f"objective={best_result.get('objective')} attempted={attempted}"
        )
        return best_solution

    remaining = _remaining_budget(started, timelimit)
    spendable = remaining - reserve
    if spendable <= 1.0:
        best_label, best_solution, best_result = _best_candidate(candidates)
        print(
            f"[baseline_hh reboot_v200] skip_trackA_portfolio instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"selected={best_label} T={best_result.get('obj1')} "
            f"objective={best_result.get('objective')} attempted={attempted}"
        )
        return best_solution

    if v197._allow_crossbay_track(features):
        strict_solution, strict_result, strict_attempted = v197._try_crossbay_postpass(
            prob_info,
            base_solution,
            base_result,
            spendable,
            tier,
        )
        attempted.append(
            (
                "strict_v197_like",
                float(strict_result.get("obj1") or float("inf")),
                float(strict_result.get("objective") or float("inf")),
            )
        )
        if strict_attempted:
            _append_candidate(candidates, "strict_v197_like", strict_solution, strict_result)

    remaining = _remaining_budget(started, timelimit)
    spendable = remaining - reserve
    if spendable > 1.0 and _allow_extended_track(features):
        extended_solution, extended_result, extended_attempted = v196._try_crossbay_postpass(
            prob_info,
            base_solution,
            base_result,
            spendable,
            tier,
        )
        attempted.append(
            (
                "extended_v196_like",
                float(extended_result.get("obj1") or float("inf")),
                float(extended_result.get("objective") or float("inf")),
            )
        )
        if extended_attempted:
            _append_candidate(candidates, "extended_v196_like", extended_solution, extended_result)

    best_label, best_solution, best_result = _best_candidate(candidates)
    print(
        f"[baseline_hh reboot_v200] trackA_portfolio instance={prob_info.get('name')} "
        f"tier={tier} base_T={base_result.get('obj1')} selected={best_label} "
        f"best_T={best_result.get('obj1')} objective={best_result.get('objective')} "
        f"attempted={attempted}"
    )
    return best_solution
