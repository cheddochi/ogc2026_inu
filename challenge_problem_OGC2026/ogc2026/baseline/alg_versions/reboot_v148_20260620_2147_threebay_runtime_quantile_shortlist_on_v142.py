"""reboot_v148_20260620_2147_threebay_runtime_quantile_shortlist_on_v142.py

Strategy:
    Keep trusted v142 as the default line, then replay a bounded tardy-block
    quantile reinsertion only on the repeated 3-bay runtime-risk low-proc
    tight-slack subtype.

Metadata:
    version_id: reboot_v148_20260620_2147_threebay_runtime_quantile_shortlist_on_v142
    parent_version: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
    status: candidate
    timestamp: 2026-06-20 21:47 KST
    strategy:
        - Preserve v142 unchanged outside the target subtype.
        - Build the exact v142 warm start first.
        - On the target subtype only, try bounded quantile-sampled reinsertion
          on the top tardy 1-2 blocks.
        - Keep only strictly better officially feasible candidates.
    hypothesis:
        The repeated 3-bay low-proc runtime-risk family is blocked by a tiny
        set of stranded tardy blocks that the parent warm start never relocates
        deeply enough. A quantile-sampled tardy shortlist should have a better
        chance of reducing T than the earlier tiny greedy-prefix replay while
        staying inside the canonical wrapper budget.
    intended_metric_target:
        - improve the repeated prob32/prob33/prob37/prob39-like family
        - preserve accepted_for_score 40/40
        - reduce total T / avg T / high-T tail before polish-only work
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
"""

from __future__ import annotations

import time


ACTIVE_VERSION = "reboot_v148_20260620_2147_threebay_runtime_quantile_shortlist_on_v142"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    workload_values = [float(block.get("workload", 0.0)) for block in blocks]
    top_choices = []
    pref_gap_values = []
    tight_count = 0

    for block in blocks:
        release = float(block.get("release_time", 0.0))
        due = float(block.get("due_date", 0.0))
        proc = float(block.get("processing_time", 0.0))
        slack = due - release - proc
        if slack <= 2.0:
            tight_count += 1

        prefs = list(block.get("bay_preferences", []))
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
            ordered = sorted((float(value) for value in prefs), reverse=True)
            pref_gap_values.append(ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0))

    pref_concentration = 0.0
    if top_choices and bays and blocks:
        pref_concentration = (
            max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)
        )

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": _mean(proc_values),
        "tight_slack_ratio": tight_count / len(blocks) if blocks else 0.0,
        "pref_concentration": pref_concentration,
        "pref_gap_mean": _mean(pref_gap_values),
        "workload_mean": _mean(workload_values),
    }


def _matches_threebay_runtime_quantile_family(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and int(features["blocks"]) >= 180
        and features["proc_mean"] <= 17.0
        and features["tight_slack_ratio"] >= 0.28
        and 0.34 <= features["pref_concentration"] <= 0.60
        and features["pref_gap_mean"] >= 45.0
        and features["workload_mean"] >= 90.0
    )


def _time_tier(timelimit: float) -> str:
    if timelimit < 25.0:
        return "very_short"
    if timelimit < 45.0:
        return "short"
    if timelimit < 90.0:
        return "standard"
    if timelimit < 300.0:
        return "long"
    return "very_long"


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 7.0,
        "long": 9.0,
        "very_long": 11.0,
    }[tier]
    return min(cap, remaining)


def _candidate_limit(tier: str) -> int:
    return {
        "very_short": 0,
        "short": 0,
        "standard": 2,
        "long": 2,
        "very_long": 3,
    }[tier]


def _max_positions(tier: str) -> int:
    return {
        "standard": 48,
        "long": 64,
        "very_long": 80,
    }[tier]


def _try_threebay_runtime_quantile_shortlist(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
    from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
    from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080

    deadline = time.time() + budget
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = v064._tardy_block_ids(prob_info, base_assignments, _candidate_limit(tier))
    if not target_block_ids:
        return base_solution, base_result

    best_solution = base_solution
    best_result = base_result
    attempted = []

    for target_block_id in target_block_ids:
        if time.time() >= deadline:
            break

        current_assignments = v064._solution_to_assignments(best_solution)
        candidate_assignments = v080._quantile_single_reinsert(
            prob_info,
            current_assignments,
            target_block_id,
            max_positions=_max_positions(tier),
            deadline=deadline,
        )
        if candidate_assignments is None:
            attempted.append((target_block_id, None, None))
            continue

        candidate_solution = v001._solution_from_assignments(candidate_assignments)
        candidate_result = v001.check_feasibility(prob_info, candidate_solution)
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
        f"[baseline_hh reboot_v148] threebay_runtime_quantile_shortlist instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"best_objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    tier = _time_tier(timelimit)

    from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
    from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
    from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as v142

    overall_started = time.time()
    base_solution = v142.algorithm(prob_info, timelimit)

    if tier in {"very_short", "short"}:
        return base_solution

    features = _selector_features(prob_info)
    if not _matches_threebay_runtime_quantile_family(features):
        return base_solution

    base_result = v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or float(base_result.get("obj1") or 0.0) < 2500.0
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - overall_started))
    reserve = _dynamic_reserve(timelimit)
    if remaining <= reserve + 5.0:
        print(
            f"[baseline_hh reboot_v148] skip_threebay_runtime_quantile instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result = _try_threebay_runtime_quantile_shortlist(
        prob_info,
        base_solution,
        base_result,
        remaining - reserve,
        tier,
    )
    if v064._result_key(best_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v148] selected_threebay_runtime_quantile instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v148] keep_v142_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={best_result.get('obj1')}"
    )
    return base_solution
