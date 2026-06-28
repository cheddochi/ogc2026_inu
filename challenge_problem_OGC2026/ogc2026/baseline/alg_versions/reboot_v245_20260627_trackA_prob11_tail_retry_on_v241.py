"""reboot_v245_20260627_trackA_prob11_tail_retry_on_v241.py

Strategy:
    Keep trusted v241 as the only constructive path, then add one very cheap
    Track A specialist only on the ultra-tight prob11-like lane:
      - trusted fallback candidate = direct v241.algorithm
      - cheap specialist candidate = bounded tail-stage retry on the finished
        fallback solution (micro-pair retry, then dense-fourbay-chain retry)

    This extracts just the last local-search stages instead of rerunning a full
    second route, aiming to preserve runtime while still offering a narrow
    prob11 recovery opportunity.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
from alg_versions import reboot_v241_20260627_trackA_split_prob11_guard_from_first20_subgroup_on_v218 as v241


ACTIVE_VERSION = "reboot_v245_20260627_trackA_prob11_tail_retry_on_v241"


def _allow_prob11like_ultratight_lane(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 190 <= int(features.get("blocks", 0)) <= 220
        and float(features.get("w1", 0.0)) >= 20000.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.35
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.60
        and float(features.get("pref_concentration", 1.0)) <= 0.28
        and float(features.get("pref_pressure", 1.0)) <= 0.27
    )


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    timelimit = float(timelimit)
    features = v186._selector_features(prob_info)
    tier = v186.v169._time_tier(timelimit)
    reserve = v186._dynamic_reserve(timelimit)

    fallback_solution = v241.algorithm(prob_info, timelimit)
    if not _allow_prob11like_ultratight_lane(features):
        return fallback_solution

    best_solution = fallback_solution
    best_result = v186.v001.check_feasibility(prob_info, best_solution)
    attempted: list[tuple[str, float, float]] = [
        (
            "fallback_v241",
            float(best_result.get("obj1") or 0.0),
            float(best_result.get("objective") or 0.0),
        )
    ]

    remaining = max(0.0, timelimit - (time.time() - started))
    spendable = max(0.0, remaining - reserve)
    pair_budget = min(0.9, spendable)
    if pair_budget > 0.45 and float(best_result.get("obj1") or 0.0) >= 360.0:
        pair_solution, pair_result, _ = v241._try_micro_pair_prefix(
            prob_info,
            best_solution,
            best_result,
            pair_budget,
            tier,
        )
        attempted.append(
            (
                "tail_retry_micro_pair",
                float(pair_result.get("obj1") or 0.0),
                float(pair_result.get("objective") or 0.0),
            )
        )
        if v186.v064._result_key(pair_result) < v186.v064._result_key(best_result):
            best_solution = pair_solution
            best_result = pair_result

    remaining = max(0.0, timelimit - (time.time() - started))
    spendable = max(0.0, remaining - reserve)
    chain_budget = min(1.2, spendable)
    if chain_budget > 0.55 and float(best_result.get("obj1") or 0.0) >= 360.0:
        chain_solution, chain_result, _ = v241._try_dense_fourbay_deep_chain(
            prob_info,
            best_solution,
            best_result,
            chain_budget,
            tier,
        )
        attempted.append(
            (
                "tail_retry_dense_chain",
                float(chain_result.get("obj1") or 0.0),
                float(chain_result.get("objective") or 0.0),
            )
        )
        if v186.v064._result_key(chain_result) < v186.v064._result_key(best_result):
            best_solution = chain_solution
            best_result = chain_result

    print(
        f"[baseline_hh reboot_v245] prob11_tail_retry instance={prob_info.get('name')} "
        f"attempted={attempted} selected_T={best_result.get('obj1')} "
        f"selected_objective={best_result.get('objective')}"
    )
    return best_solution
