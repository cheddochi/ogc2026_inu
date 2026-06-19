"""reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117.py

Strategy:
    Keep trusted v117 as the default path, then apply a bounded deep
    quantile-sampled single-block reinsertion on the two-bay concentrated
    high-proc tail subtype using the pure top-tardy shortlist.

Metadata:
    version_id: reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117
    parent_version: reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116
    status: candidate
    timestamp: 2026-06-20 02:45 KST
    strategy:
        - Preserve v117 unchanged outside the target subtype.
        - Build the trusted v117 warm start first.
        - On the target subtype, evaluate a short pure top-tardy shortlist and
          reinsert exactly one block with a deep quantile-sampled position
          search.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The two-bay concentrated high-proc tail still has real one-block local
        improvement signal, but recovering it depends on using the same top-
        tardy shortlist that produced the live probe improvement.
    intended_metric_target:
        - improve prob25-like and prob27-like rows
        - preserve accepted_for_score 40/40
        - reduce total T, avg T, and the high-T tail
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116
"""

from __future__ import annotations

import time

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v121_20260620_0239_twobay_concentrated_quantile_reinsert_on_v117 as v121
from alg_versions import reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116 as v117


ACTIVE_VERSION = "reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117"


def _target_block_ids(
    prob_info: dict,
    assignments: dict[int, dict],
    limit: int,
) -> list[int]:
    if limit <= 0:
        return []

    ranked = []
    blocks = prob_info["blocks"]
    for block_id, assignment in assignments.items():
        block = blocks[block_id]
        due = int(block["due_date"])
        release = int(block["release_time"])
        tardiness = max(0, int(assignment["exit_time"]) - due)
        if tardiness <= 0:
            continue

        prefs = [float(value) for value in block["bay_preferences"]]
        bay_id = int(assignment["bay_id"])
        pref_penalty = max(prefs) - prefs[bay_id]
        entry_delay = int(assignment["entry_time"]) - release
        ranked.append((tardiness, pref_penalty, entry_delay, block_id))

    ranked.sort(reverse=True)
    return [block_id for _, _, _, block_id in ranked[:limit]]


def _try_quantile_shortlist_reinsert(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = v121._research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    deadline = time.time() + budget
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = _target_block_ids(
        prob_info,
        base_assignments,
        v121._candidate_limit(tier),
    )
    if not target_block_ids:
        return base_solution, base_result

    max_positions = {
        "standard": 24,
        "long": 32,
        "very_long": 40,
    }[tier]

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
            max_positions=max_positions,
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
        f"[baseline_hh reboot_v122] twobay_toptardy_quantile instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    tier = v064.v050._time_tier(float(timelimit))
    features = v121._selector_features(prob_info)

    base_solution = v117.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or tier in {"very_short", "short"}
        or not v121._matches_twobay_concentrated_tail_class(features)
        or float(base_result.get("obj1") or 0.0) < 2000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= v121._dynamic_reserve(float(timelimit)) + 2.0:
        print(
            f"[baseline_hh reboot_v122] skip_twobay_toptardy_quantile instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = _try_quantile_shortlist_reinsert(
        prob_info,
        base_solution,
        base_result,
        remaining - v121._dynamic_reserve(float(timelimit)),
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v122] selected_twobay_toptardy_quantile instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v122] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
