"""reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135.py

Strategy:
    Preserve trusted v135 as the default line, then replay a deeper pure
    top-tardy quantile single-reinsert only on the two-bay concentrated
    high-proc tail subtype.

Metadata:
    version_id: reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135
    parent_version: reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132
    status: candidate
    timestamp: 2026-06-20 23:35 KST
    strategy:
        - Keep the trusted v135 line unchanged outside the target subtype.
        - Build the exact v135 warm start first.
        - On the two-bay concentrated high-proc tail, evaluate a deeper pure
          top-tardy shortlist than v122 used.
        - Keep only strictly better officially feasible candidates.
    hypothesis:
        The v135 warm start still has real one-block T-improvement signal on
        the twobay concentrated high-proc family, but the older v122 replay is
        under-budgeted on the heavier current parent and stops before reaching
        the improving blocks.
    intended_metric_target:
        - improve prob25-like and prob27-like rows
        - preserve accepted_for_score 40/40
        - reduce total T / avg T / high-T tail and avg objective versus v135
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v121_20260620_0239_twobay_concentrated_quantile_reinsert_on_v117 as v121
from alg_versions import reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117 as v122
from alg_versions import reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132 as v135


ACTIVE_VERSION = "reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135"


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 10.0,
        "long": 12.0,
        "very_long": 14.0,
    }[tier]
    return min(cap, remaining)


def _candidate_limit(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 6,
        "long": 7,
        "very_long": 8,
    }[tier]


def _max_positions(tier: str) -> int:
    return {
        "standard": 24,
        "long": 32,
        "very_long": 40,
    }[tier]


def _try_deeper_toptardy_quantile_reinsert(
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
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = v122._target_block_ids(
        prob_info,
        base_assignments,
        _candidate_limit(tier),
    )
    if not target_block_ids:
        return base_solution, base_result

    best_solution = base_solution
    best_result = base_result
    attempted = []

    for target_block_id in target_block_ids:
        if time.time() >= deadline:
            break

        candidate_assignments = v080._quantile_single_reinsert(
            prob_info,
            base_assignments,
            target_block_id,
            max_positions=_max_positions(tier),
            deadline=deadline,
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
        f"[baseline_hh reboot_v136] twobay_deeper_toptardy instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    timelimit = float(timelimit)
    tier = v064.v050._time_tier(timelimit)
    features = v121._selector_features(prob_info)

    base_solution = v135.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or tier in {"very_short", "short"}
        or not v121._matches_twobay_concentrated_tail_class(features)
        or float(base_result.get("obj1") or 0.0) < 2000.0
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    reserve = v121._dynamic_reserve(timelimit)
    if remaining <= reserve + 10.0:
        print(
            f"[baseline_hh reboot_v136] skip_twobay_deeper_toptardy instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    research_solution, research_result = _try_deeper_toptardy_quantile_reinsert(
        prob_info,
        base_solution,
        base_result,
        remaining - reserve,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v136] selected_twobay_deeper_toptardy instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v136] keep_v135_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
