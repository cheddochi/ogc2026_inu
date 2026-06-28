"""reboot_v130_20260620_1125_prob40like_narrow_quantile_on_v123.py

Strategy:
    Preserve trusted v123 as the default line, then apply a narrower
    warm-start-preserving four-bay quantile reinsertion only on the prob40-like
    xlarge high-workload tail.

Metadata:
    version_id: reboot_v130_20260620_1125_prob40like_narrow_quantile_on_v123
    parent_version: reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122
    status: rejected
    timestamp: 2026-06-20 11:25 KST
    strategy:
        - Keep the accepted v123 three-bay high-proc prefix repair unchanged.
        - Build the exact trusted v123 base path first.
        - Add a narrow four-bay quantile single-reinsert only on the xlarge
          very-high-workload prob40-like slice.
        - Stop early after the first strictly better officially feasible
          candidate.
    hypothesis:
        The useful v125 local-move signal belongs to the narrower prob40-like
        xlarge high-workload tail, not the broader 4-bay high-proc family.
        Restricting the selector and cutting the search width should keep the
        prob40 T drop while reducing spillover risk.
    intended_metric_target:
        - improve the prob40-like high-T tail row
        - preserve accepted_for_score 40/40
        - reduce total T / avg T / high-T tail if the local move remains safe
    validation_status:
        rejected after full train40 objective regression despite small total-T gain
    benchmark_evidence_path:
        - reports/ogc2026_reboot_v001/smoke_reboot_v130_tier9_20260620_001
        - reports/ogc2026_reboot_v001/target_reboot_v130_prob40like_20260620_001
        - reports/ogc2026_reboot_v001/full_reboot_v130_train40_20260620_001
    rollback_target: reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117 as v122
from alg_versions import reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122 as v123


ACTIVE_VERSION = "reboot_v130_20260620_1125_prob40like_narrow_quantile_on_v123"


def _selector_features(prob_info: dict) -> dict[str, float]:
    features = dict(v123._selector_features(prob_info))
    blocks = list(prob_info.get("blocks", []))
    workload_values = [float(block.get("workload", 0.0)) for block in blocks]
    features["workload_mean"] = (
        sum(workload_values) / len(workload_values) if workload_values else 0.0
    )
    return features


def _matches_prob40like_narrow_tail(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 4
        and int(features["blocks"]) >= 240
        and features["proc_mean"] >= 20.0
        and 0.28 <= features["tight_slack_ratio"] <= 0.34
        and features["pref_concentration"] >= 0.74
        and features["pref_gap_mean"] >= 58.0
        and features["workload_mean"] >= 160.0
    )


def _research_budget(remaining: float, reserve: float, tier: str) -> float:
    available = max(0.0, remaining - reserve - 0.5)
    cap = {
        "standard": 4.0,
        "long": 5.5,
        "very_long": 7.0,
    }.get(tier, 0.0)
    return min(cap, available)


def _candidate_limit(tier: str) -> int:
    return {
        "standard": 2,
        "long": 3,
        "very_long": 4,
    }.get(tier, 0)


def _max_positions(tier: str) -> int:
    return {
        "standard": 20,
        "long": 24,
        "very_long": 28,
    }.get(tier, 20)


def _try_narrow_quantile_reinsert(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    timelimit: float,
    overall_started: float,
    tier: str,
) -> tuple[dict, dict]:
    remaining = max(0.0, timelimit - (time.time() - overall_started))
    reserve = v123._dynamic_reserve(timelimit)
    budget = _research_budget(remaining, reserve, tier)
    candidate_limit = _candidate_limit(tier)
    if budget <= 0.0 or candidate_limit <= 0:
        return base_solution, base_result

    deadline = time.time() + budget
    base_assignments = v123._solution_to_assignments(base_solution)
    target_block_ids = v123._tardy_block_ids(prob_info, base_assignments, candidate_limit)
    if not target_block_ids:
        return base_solution, base_result

    best_solution = base_solution
    best_result = base_result
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
            print(
                f"[baseline_hh reboot_v130] prob40like_quantile instance={prob_info.get('name')} "
                f"tier={tier} block={target_block_id} candidate=none"
            )
            continue

        candidate_solution = v001._solution_from_assignments(candidate_assignments)
        candidate_result = v001.check_feasibility(prob_info, candidate_solution)
        print(
            f"[baseline_hh reboot_v130] prob40like_quantile instance={prob_info.get('name')} "
            f"tier={tier} block={target_block_id} feasible={candidate_result.get('feasible')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        if v123._result_key(candidate_result) < v123._result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result
            break

    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    overall_started = time.time()
    timelimit = float(timelimit)
    tier = v123._time_tier(timelimit)
    features = _selector_features(prob_info)
    threebay_target = v123._matches_threebay_highproc_tail(features)
    prob40like_target = _matches_prob40like_narrow_tail(features)

    current_solution = v122.algorithm(
        prob_info,
        v123._parent_timelimit(timelimit, threebay_target),
    )
    current_result = v001.check_feasibility(prob_info, current_solution)

    if (
        tier not in {"very_short", "short"}
        and current_result.get("feasible")
        and threebay_target
        and float(current_result.get("obj1") or 0.0) >= 2000.0
    ):
        remaining = max(0.0, timelimit - (time.time() - overall_started))
        reserve = v123._dynamic_reserve(timelimit)
        headroom = v123._min_headroom(tier)
        if remaining > reserve + headroom:
            candidate_solution, candidate_result = v123._try_prefix_repair(
                prob_info,
                current_solution,
                current_result,
                timelimit,
                overall_started,
                tier,
            )
            if v123._result_key(candidate_result) < v123._result_key(current_result):
                current_solution = candidate_solution
                current_result = candidate_result

    if (
        tier in {"very_short", "short"}
        or not current_result.get("feasible")
        or not prob40like_target
        or float(current_result.get("obj1") or 0.0) < 5000.0
    ):
        return current_solution

    remaining = max(0.0, timelimit - (time.time() - overall_started))
    reserve = v123._dynamic_reserve(timelimit)
    if remaining <= reserve + 8.0:
        print(
            f"[baseline_hh reboot_v130] skip_prob40like_guard "
            f"instance={prob_info.get('name')} tier={tier} remaining={remaining:.2f}s "
            f"reserve={reserve:.2f}s base_T={current_result.get('obj1')}"
        )
        return current_solution

    best_solution, best_result = _try_narrow_quantile_reinsert(
        prob_info,
        current_solution,
        current_result,
        timelimit,
        overall_started,
        tier,
    )
    if v123._result_key(best_result) < v123._result_key(current_result):
        print(
            f"[baseline_hh reboot_v130] selected_prob40like_quantile "
            f"instance={prob_info.get('name')} T={best_result.get('obj1')} "
            f"objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v130] keep_trusted_base instance={prob_info.get('name')} "
        f"base_T={current_result.get('obj1')} cand_T={best_result.get('obj1')}"
    )
    return current_solution
