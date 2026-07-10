"""reboot_v314_20260630_trackA_prob10_warm_multiblock_on_v312.py

Strategy:
    Keep the accepted v312 surface as the default route, but on one narrow
    prob10-like Family A subtype only, add a bounded local portfolio on top of
    the trusted v312 result:
      - base v312
      - warm repair
      - warm repair then multiblock repair
      - multiblock repair then warm repair

Key design intent:
    - Preserve the accepted prob11/prob13/prob19 specialist lanes from v312.
    - Exploit the new helper-level signal on the low-w1 200-block four-bay
      residual pocket without reopening Family B rows.
"""

from __future__ import annotations

from alg_versions import (
    reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186,
)
from alg_versions import (
    reboot_v202_20260626_trackA_portfolio_plus_multiblock_sequence_repair as v202,
)
from alg_versions import (
    reboot_v312_20260630_trackA_prob11_retry_with_prob19_guard_on_v304 as v312,
)


ACTIVE_VERSION = "reboot_v314_20260630_trackA_prob10_warm_multiblock_on_v312"
PARENT_VERSION = "reboot_v312_20260630_trackA_prob11_retry_with_prob19_guard_on_v304"


def _is_prob10_residual_target(prob_info: dict, timelimit: float) -> bool:
    features = v186._selector_features(prob_info)
    tier = v186.v169._time_tier(float(timelimit))
    return (
        tier not in {"very_short", "short"}
        and int(features.get("bays", 0)) == 4
        and 190 <= int(features.get("blocks", 0)) <= 210
        and 13000.0 <= float(features.get("w1", 0.0)) <= 16000.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and 1.35 <= float(features.get("slack_mean", 0.0)) <= 1.65
        and 0.45 <= float(features.get("tight_slack_ratio", 0.0)) <= 0.54
        and 0.27 <= float(features.get("pref_concentration", 1.0)) <= 0.31
        and 0.25 <= float(features.get("pref_pressure", 1.0)) <= 0.285
        and v186._matches_family_a_tightslack(features)
    )


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)

    base_solution = v312.algorithm(prob_info, timelimit)
    if not _is_prob10_residual_target(prob_info, timelimit):
        return base_solution

    base_result = v186.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or float(base_result.get("obj1") or 0.0) <= 0.0
    ):
        return base_solution

    features = v186._selector_features(prob_info)
    tier = v186.v169._time_tier(timelimit)

    attempted: list[tuple[str, float, float]] = [
        (
            "base_v312",
            float(base_result.get("obj1") or 0.0),
            float(base_result.get("objective") or 0.0),
        )
    ]
    best_label = "base_v312"
    best_solution = base_solution
    best_result = base_result

    warm_solution, warm_result, warm_moves = v186._try_family_a_warm_repair(
        prob_info,
        base_solution,
        base_result,
        remaining=1.0,
        tier=tier,
        features=features,
    )
    attempted.append(
        (
            "warm_repair",
            float(warm_result.get("obj1") or 0.0),
            float(warm_result.get("objective") or 0.0),
        )
    )
    if v186.v064._result_key(warm_result) < v186.v064._result_key(best_result):
        best_label = "warm_repair"
        best_solution = warm_solution
        best_result = warm_result

    warm_multi_solution, warm_multi_result, warm_multi_moves = v202._try_post_multiblock_repair(
        prob_info,
        warm_solution,
        warm_result,
        4.0,
        tier,
        features,
    )
    attempted.append(
        (
            "warm_then_multiblock",
            float(warm_multi_result.get("obj1") or 0.0),
            float(warm_multi_result.get("objective") or 0.0),
        )
    )
    if v186.v064._result_key(warm_multi_result) < v186.v064._result_key(best_result):
        best_label = "warm_then_multiblock"
        best_solution = warm_multi_solution
        best_result = warm_multi_result

    multi_solution, multi_result, multi_moves = v202._try_post_multiblock_repair(
        prob_info,
        base_solution,
        base_result,
        4.0,
        tier,
        features,
    )
    attempted.append(
        (
            "multiblock_only",
            float(multi_result.get("obj1") or 0.0),
            float(multi_result.get("objective") or 0.0),
        )
    )
    if v186.v064._result_key(multi_result) < v186.v064._result_key(best_result):
        best_label = "multiblock_only"
        best_solution = multi_solution
        best_result = multi_result

    multi_warm_solution, multi_warm_result, multi_warm_moves = v186._try_family_a_warm_repair(
        prob_info,
        multi_solution,
        multi_result,
        remaining=1.0,
        tier=tier,
        features=features,
    )
    attempted.append(
        (
            "multiblock_then_warm",
            float(multi_warm_result.get("obj1") or 0.0),
            float(multi_warm_result.get("objective") or 0.0),
        )
    )
    if v186.v064._result_key(multi_warm_result) < v186.v064._result_key(best_result):
        best_label = "multiblock_then_warm"
        best_solution = multi_warm_solution
        best_result = multi_warm_result

    print(
        f"[baseline_hh reboot_v314] prob10_local_portfolio instance={prob_info.get('name')} "
        f"tier={tier} best={best_label} attempted={attempted} "
        f"warm_moves={warm_moves} warm_multi_moves={warm_multi_moves} "
        f"multi_moves={multi_moves} multi_warm_moves={multi_warm_moves}"
    )
    return best_solution
