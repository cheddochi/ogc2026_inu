"""reboot_v124_20260620_1125_fourbay_highproc_toptardy_quantile_on_v123.py

Strategy:
    Keep trusted v123 as the default path, then apply a bounded top-tardy
    quantile single-reinsert only on the four-bay high-proc high-preference
    tail family.

Metadata:
    version_id: reboot_v124_20260620_1125_fourbay_highproc_toptardy_quantile_on_v123
    parent_version: reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122
    status: candidate
    timestamp: 2026-06-20 11:25 KST
    strategy:
        - Preserve v123 unchanged outside the target subtype.
        - Build the trusted v123 warm start first.
        - On the target subtype only, evaluate a short top-tardy shortlist with
          quantile-sampled single-block reinsertion.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The four-bay high-proc high-preference tail has a real one-block local
        improvement signal on the v123 warm start. Replaying that bounded move
        over a short tardy shortlist should improve prob40-like rows while
        remaining a no-op on prob31-like rows.
    intended_metric_target:
        - improve prob40-like rows
        - preserve accepted_for_score 40/40
        - reduce total T, avg T, and the high-T tail
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122 as v123


ACTIVE_VERSION = "reboot_v124_20260620_1125_fourbay_highproc_toptardy_quantile_on_v123"


def _matches_fourbay_highproc_tail(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 4
        and int(features["blocks"]) >= 200
        and features["proc_mean"] >= 20.0
        and features["pref_concentration"] >= 0.75
        and features["pref_gap_mean"] >= 58.0
        and 0.20 <= features["tight_slack_ratio"] <= 0.35
    )


def _research_budget(remaining: float, reserve: float, tier: str) -> float:
    available = max(0.0, remaining - reserve - 0.5)
    cap = {
        "standard": 6.0,
        "long": 8.0,
        "very_long": 10.0,
    }.get(tier, 0.0)
    return min(cap, available)


def _candidate_limit(tier: str) -> int:
    return {
        "standard": 3,
        "long": 4,
        "very_long": 5,
    }.get(tier, 0)


def _max_positions(tier: str) -> int:
    return {
        "standard": 24,
        "long": 32,
        "very_long": 40,
    }.get(tier, 24)


def _solution_to_assignments(solution: dict) -> dict[int, dict]:
    assignments: dict[int, dict] = {}
    for t_str, ops_at_t in solution.get("operations", {}).items():
        t = int(t_str)
        for op in ops_at_t:
            block_id = int(op["block_id"])
            assignment = assignments.setdefault(block_id, {"block_id": block_id})
            if op["type"] == "ENTRY":
                assignment["bay_id"] = int(op["bay_id"])
                assignment["x"] = int(op["x"])
                assignment["y"] = int(op["y"])
                assignment["orient_idx"] = int(op["orient_idx"])
                assignment["entry_time"] = t
            elif op["type"] == "EXIT":
                assignment["exit_time"] = t
    required = {
        "block_id",
        "bay_id",
        "x",
        "y",
        "orient_idx",
        "entry_time",
        "exit_time",
    }
    return {
        block_id: assignment
        for block_id, assignment in assignments.items()
        if required.issubset(assignment)
    }


def _tardy_block_ids(prob_info: dict, assignments: dict[int, dict], limit: int) -> list[int]:
    ranked = []
    blocks = prob_info["blocks"]
    for block_id, assignment in assignments.items():
        due = int(blocks[block_id]["due_date"])
        tardiness = max(0, int(assignment["exit_time"]) - due)
        if tardiness <= 0:
            continue
        prefs = blocks[block_id]["bay_preferences"]
        bay_id = int(assignment["bay_id"])
        pref_penalty = max(prefs) - prefs[bay_id]
        ranked.append((-tardiness, -pref_penalty, due, block_id))
    ranked.sort()
    return [block_id for _, _, _, block_id in ranked[:limit]]


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result.get("obj1", float("inf"))),
        float(result.get("objective", float("inf"))),
        float(result.get("obj2", float("inf"))),
        float(result.get("obj3", float("inf"))),
    )


def _try_toptardy_quantile_reinsert(
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

    from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080

    deadline = time.time() + budget
    base_assignments = _solution_to_assignments(base_solution)
    target_block_ids = _tardy_block_ids(prob_info, base_assignments, candidate_limit)
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
                f"[baseline_hh reboot_v124] fourbay_quantile instance={prob_info.get('name')} "
                f"tier={tier} block={target_block_id} candidate=none"
            )
            continue

        candidate_solution = v001._solution_from_assignments(candidate_assignments)
        candidate_result = v001.check_feasibility(prob_info, candidate_solution)
        print(
            f"[baseline_hh reboot_v124] fourbay_quantile instance={prob_info.get('name')} "
            f"tier={tier} block={target_block_id} feasible={candidate_result.get('feasible')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        if _result_key(candidate_result) < _result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result

    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    overall_started = time.time()
    tier = v123._time_tier(float(timelimit))
    features = v123._selector_features(prob_info)

    base_solution = v123.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)

    if (
        tier in {"very_short", "short"}
        or not base_result.get("feasible")
        or not _matches_fourbay_highproc_tail(features)
        or float(base_result.get("obj1") or 0.0) < 2500.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - overall_started))
    reserve = v123._dynamic_reserve(float(timelimit))
    if remaining <= reserve + 6.0:
        print(
            f"[baseline_hh reboot_v124] skip_fourbay_quantile_guard "
            f"instance={prob_info.get('name')} tier={tier} remaining={remaining:.2f}s "
            f"reserve={reserve:.2f}s base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result = _try_toptardy_quantile_reinsert(
        prob_info,
        base_solution,
        base_result,
        float(timelimit),
        overall_started,
        tier,
    )
    if _result_key(best_result) < _result_key(base_result):
        print(
            f"[baseline_hh reboot_v124] selected_fourbay_quantile "
            f"instance={prob_info.get('name')} T={best_result.get('obj1')} "
            f"objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v124] keep_v123_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={best_result.get('obj1')}"
    )
    return base_solution
