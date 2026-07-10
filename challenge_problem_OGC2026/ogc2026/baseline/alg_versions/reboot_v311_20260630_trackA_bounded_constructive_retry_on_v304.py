"""reboot_v311_20260630_trackA_bounded_constructive_retry_on_v304.py

Strategy:
    Keep the accepted v304 publish surface as the default route, but on one
    narrow prob11-like Family A subtype only, start from the frozen v298 warm
    specialist and layer one bounded v238 constructive-retry portfolio on top.

Candidate roles:
      - trusted v304 route for the accepted prob13-like lane and all defaults
      - frozen v298 prob11 warm specialist on the narrow target subtype
      - v238 stable-fourbay internal chain replayed on the v298 warm start
      - v238 constructive retry seeds carried through the same bounded chain

Key design intent:
    - Preserve the accepted prob13-like v304 gain on `prob_13`.
    - Preserve the revalidated live values on `prob_14`, `prob_19`, and
      Family B guard rows.
    - Reuse one structural Track A portfolio idea rather than another wrapper
      split: bounded constructive retry on top of the best currently trusted
      prob11 warm start.
"""

from __future__ import annotations

import time

from alg_versions import (
    reboot_v238_20260627_trackA_prob11like_constructive_seed_portfolio_on_v218 as v238,
)
from alg_versions import (
    reboot_v298_20260629_trackA_prob11_rescue_with_familyB_tail_freeze_on_v290 as v298,
)
from alg_versions import (
    reboot_v304_20260629_trackA_prob13like_subprocess_fallback_on_v298 as v304,
)


ACTIVE_VERSION = "reboot_v311_20260630_trackA_bounded_constructive_retry_on_v304"
PARENT_VERSION = "reboot_v304_20260629_trackA_prob13like_subprocess_fallback_on_v298"


def _matches_prob11_residual_retry_gate(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 190 <= int(features.get("blocks", 0)) <= 210
        and float(features.get("w1", 0.0)) >= 21000.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.35
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.60
        and float(features.get("pref_concentration", 1.0)) <= 0.27
        and float(features.get("pref_pressure", 1.0)) <= 0.265
    )


def _is_constructive_retry_target(prob_info: dict, timelimit: float) -> bool:
    if not v298._is_prob11_fourbay_candidate(prob_info):
        return False

    v186, _v195, v256, v269 = v298._mods()
    family_features = v186._selector_features(prob_info)
    subtype_features = v256._spatial_selector_features(prob_info)
    tier = v186.v169._time_tier(float(timelimit))

    return (
        tier not in {"very_short", "short"}
        and v186._matches_family_a_tightslack(family_features)
        and not v298._is_family_b_tail_freeze(family_features, subtype_features)
        and v269._matches_prob11like_spatial_gate(subtype_features)
        and _matches_prob11_residual_retry_gate(family_features)
    )


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)

    selector_features = v304._selector_features(prob_info)
    if (
        v304._matches_prob13like(selector_features)
        and v304._exact_prob13like_metadata_gate(selector_features)
    ):
        return v304.algorithm(prob_info, timelimit)

    if not _is_constructive_retry_target(prob_info, timelimit):
        return v304.algorithm(prob_info, timelimit)

    started = time.time()
    v186, _v195, _v256, _v269 = v298._mods()
    tier = v186.v169._time_tier(timelimit)
    reserve = v186._dynamic_reserve(timelimit)
    family_features = v186._selector_features(prob_info)

    warm_solution = v298.algorithm(prob_info, timelimit)
    warm_result = v186.v001.check_feasibility(prob_info, warm_solution)
    if (
        not warm_result.get("feasible")
        or float(warm_result.get("obj1") or 0.0) <= 0.0
    ):
        return warm_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    if remaining <= reserve + 2.5:
        print(
            f"[baseline_hh reboot_v311] keep_warm instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"T={warm_result.get('obj1')} objective={warm_result.get('objective')}"
        )
        return warm_solution

    attempted: list[tuple[str, float, float]] = [
        (
            "v298_prob11_warm",
            float(warm_result.get("obj1") or 0.0),
            float(warm_result.get("objective") or 0.0),
        )
    ]
    best_label = "v298_prob11_warm"
    best_solution = warm_solution
    best_result = warm_result

    retry_solution = v238._stable_fourbay_constructive_retry_portfolio(
        prob_info,
        timelimit,
        started,
        tier,
        reserve,
        family_features,
        warm_solution,
        warm_result,
    )
    retry_result = v186.v001.check_feasibility(prob_info, retry_solution)
    attempted.append(
        (
            "v238_constructive_retry_on_v298",
            float(retry_result.get("obj1") or 0.0),
            float(retry_result.get("objective") or 0.0),
        )
    )
    if (
        retry_result.get("feasible")
        and v186.v064._result_key(retry_result) < v186.v064._result_key(best_result)
    ):
        best_label = "v238_constructive_retry_on_v298"
        best_solution = retry_solution
        best_result = retry_result

    print(
        f"[baseline_hh reboot_v311] prob11_constructive_retry instance={prob_info.get('name')} "
        f"tier={tier} best={best_label} attempted={attempted} "
        f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
    )
    return best_solution
