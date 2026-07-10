"""reboot_v317_20260630_trackA_prob13_only_window_multiblock_on_v314.py

Strategy:
    Keep the accepted v314 surface as the default route, but on one exact
    prob13like Family A residual envelope only, compare a bounded local
    portfolio on top of the trusted v314 result:
      - base v314
      - window reorder
      - multiblock repair
      - window repair then multiblock repair
      - multiblock repair then window reorder

Key design intent:
    - Preserve the accepted prob10/prob11/prob14/prob19 improvements already
      living inside v314.
    - Salvage the strongest v316 Track A signal without paying the prob14like
      timeout cost.
    - Leave Family B rows untouched by keeping the gate exact and feature-only.
"""

from __future__ import annotations

from alg_versions import (
    reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186,
)
from alg_versions import (
    reboot_v195_20260626_familyA_window_reorder_on_v194 as v195,
)
from alg_versions import (
    reboot_v202_20260626_trackA_portfolio_plus_multiblock_sequence_repair as v202,
)
from alg_versions import (
    reboot_v303_20260629_trackA_prob13like_exact_portfolio_on_v298 as v303,
)
from alg_versions import (
    reboot_v314_20260630_trackA_prob10_warm_multiblock_on_v312 as v314,
)


ACTIVE_VERSION = "reboot_v317_20260630_trackA_prob13_only_window_multiblock_on_v314"
PARENT_VERSION = "reboot_v314_20260630_trackA_prob10_warm_multiblock_on_v312"


def _target_prob13like(prob_info: dict, timelimit: float) -> dict[str, float] | None:
    features = v186._selector_features(prob_info)
    tier = v186.v169._time_tier(float(timelimit))
    if tier in {"very_short", "short"}:
        return None
    if int(features.get("bays", 0)) != 4:
        return None
    if not 240 <= int(features.get("blocks", 0)) <= 260:
        return None
    if not 17500.0 <= float(features.get("w1", 0.0)) <= 19500.0:
        return None
    if float(features.get("proc_mean", 0.0)) > 7.8:
        return None
    if float(features.get("slack_mean", 0.0)) > 1.35:
        return None
    if float(features.get("tight_slack_ratio", 0.0)) < 0.60:
        return None
    if float(features.get("pref_concentration", 1.0)) > 0.29:
        return None
    if float(features.get("pref_pressure", 1.0)) > 0.27:
        return None
    if not v186._matches_family_a_tightslack(features):
        return None

    rich_features = v303._selector_features(prob_info)
    if not v303._exact_prob13like_metadata_gate(rich_features):
        return None
    return features


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)

    base_solution = v314.algorithm(prob_info, timelimit)
    features = _target_prob13like(prob_info, timelimit)
    if features is None:
        return base_solution

    base_result = v186.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or float(base_result.get("obj1") or 0.0) <= 0.0
    ):
        return base_solution

    tier = v186.v169._time_tier(timelimit)
    attempted: list[tuple[str, float, float]] = [
        (
            "base_v314",
            float(base_result.get("obj1") or 0.0),
            float(base_result.get("objective") or 0.0),
        )
    ]
    best_label = "base_v314"
    best_solution = base_solution
    best_result = base_result

    window_solution, window_result, window_moves = v195._try_window_reorder(
        prob_info,
        base_solution,
        base_result,
        remaining=4.0,
        tier=tier,
        features=features,
    )
    attempted.append(
        (
            "window_reorder",
            float(window_result.get("obj1") or 0.0),
            float(window_result.get("objective") or 0.0),
        )
    )
    if v186.v064._result_key(window_result) < v186.v064._result_key(best_result):
        best_label = "window_reorder"
        best_solution = window_solution
        best_result = window_result

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

    window_multi_solution, window_multi_result, window_multi_moves = v202._try_post_multiblock_repair(
        prob_info,
        window_solution,
        window_result,
        4.0,
        tier,
        features,
    )
    attempted.append(
        (
            "window_then_multiblock",
            float(window_multi_result.get("obj1") or 0.0),
            float(window_multi_result.get("objective") or 0.0),
        )
    )
    if v186.v064._result_key(window_multi_result) < v186.v064._result_key(best_result):
        best_label = "window_then_multiblock"
        best_solution = window_multi_solution
        best_result = window_multi_result

    multi_window_solution, multi_window_result, multi_window_moves = v195._try_window_reorder(
        prob_info,
        multi_solution,
        multi_result,
        remaining=4.0,
        tier=tier,
        features=features,
    )
    attempted.append(
        (
            "multiblock_then_window",
            float(multi_window_result.get("obj1") or 0.0),
            float(multi_window_result.get("objective") or 0.0),
        )
    )
    if v186.v064._result_key(multi_window_result) < v186.v064._result_key(best_result):
        best_label = "multiblock_then_window"
        best_solution = multi_window_solution
        best_result = multi_window_result

    print(
        f"[baseline_hh reboot_v317] prob13_local_portfolio instance={prob_info.get('name')} "
        f"tier={tier} best={best_label} attempted={attempted} "
        f"window_moves={window_moves} multi_moves={multi_moves} "
        f"window_multi_moves={window_multi_moves} multi_window_moves={multi_window_moves}"
    )
    return best_solution
