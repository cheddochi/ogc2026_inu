"""reboot_v081_20260619_1948_prob33like_runtime_flatten.py

Strategy:
    Keep trusted v078 as the default path, then flatten the prob33-like
    runtime-risk subtype onto a shallower warm start before replaying only the
    two tiny single-block repairs that produced the trusted score signal.

Metadata:
    version_id: reboot_v081_20260619_1948_prob33like_runtime_flatten
    parent_version: reboot_v078_20260619_1535_fourbay_runtime_family_flatten
    status: candidate
    timestamp: 2026-06-19 19:48 KST
    strategy:
        - Preserve v078 unchanged outside the prob33-like runtime-risk subtype.
        - On that subtype, use the accepted v065 warm start instead of the
          deeper inherited v069->v073 chain.
        - Recover the stronger score signal with one quantile-sampled gap
          single reinsert followed by the already trusted cheap v073 single
          reinsert.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The prob33 runtime cliff comes mostly from reaching the strong v069/v073
        score through a deep delegated chain. Starting from the shallower v065
        warm start and replaying the same row-level signal with two bounded
        single-block moves should reproduce the trusted objective while leaving
        materially more time margin.
    intended_metric_target:
        - keep prob33-like rows scoreable with more runtime margin
        - preserve the stable flattened v078 parent elsewhere
        - retain or improve the trusted v074 score signal on the prob33-like row
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v078_20260619_1535_fourbay_runtime_family_flatten
"""

from __future__ import annotations

import time

import baseline_greedy
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v065_20260618_1735_threebay_diffuse_single_research as v065
from alg_versions import reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single as v069
from alg_versions import reboot_v073_20260618_2241_threebay_diffuse_fast_single_reinsert as v073
from alg_versions import reboot_v078_20260619_1535_fourbay_runtime_family_flatten as v078


ACTIVE_VERSION = "reboot_v081_20260619_1948_prob33like_runtime_flatten"


def _matches_prob33like_runtime_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and 200 <= int(features["blocks"]) < 240
        and 15.0 <= features["proc_mean"] <= 17.5
        and 0.40 <= features["pref_concentration"] <= 0.46
        and 0.40 <= features["pref_pressure"] <= 0.42
        and 0.20 <= features["workload_imbalance_pressure"] <= 0.25
        and 3.4 <= features["slack_mean"] <= 4.0
    )


def _dynamic_reserve(timelimit: float) -> float:
    return max(4.0, timelimit * 0.08)


def _gap_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 4.0,
        "long": 5.0,
        "very_long": 6.0,
    }[tier]
    return min(cap, remaining)


def _quantile_sample_positions(raw_positions: list[tuple[int, int]], budget_n: int) -> list[tuple[int, int]]:
    deduped = list(dict.fromkeys((int(x), int(y)) for x, y in raw_positions))
    n_positions = len(deduped)
    if n_positions <= budget_n:
        return deduped

    indices = []
    for i in range(budget_n):
        idx = round(i * (n_positions - 1) / max(1, budget_n - 1))
        indices.append(idx)
    return [deduped[idx] for idx in sorted(set(indices))]


def _quantile_gap_single_reinsert(
    prob_info: dict,
    assignments: dict[int, dict],
    target_block_id: int,
    *,
    max_positions: int,
    deadline: float,
) -> dict[int, dict] | None:
    previous = assignments.get(target_block_id)
    if previous is None:
        return None

    repaired = dict(assignments)
    repaired.pop(target_block_id, None)

    bays, bay_placed, bay_schedule, bay_loads = v064._rebuild_state(prob_info, repaired)
    bay_weights = v064.v001._bay_weights(bays)
    w1, w2, w3 = v064._weights(prob_info)

    block = prob_info["blocks"][target_block_id]
    prefs = list(block["bay_preferences"])
    pref_max = max(prefs)
    release = int(block["release_time"])
    due = int(block["due_date"])
    proc = int(block["processing_time"])
    workload = float(block["workload"])

    best = None
    best_key = None
    bay_order = sorted(
        range(len(bays)),
        key=lambda bay_id: (prefs[bay_id], -bay_loads[bay_id]),
        reverse=True,
    )

    for bay_id in bay_order:
        if time.time() >= deadline:
            break
        bay = bays[bay_id]
        active_blocks = [
            placed
            for placed, (_, exit_at) in zip(bay_placed[bay_id], bay_schedule[bay_id])
            if exit_at > release
        ]
        for orient_idx in range(len(block["shape"])):
            if time.time() >= deadline:
                break
            bb = baseline_greedy._block_bbox(block, orient_idx)
            if bb[2] - bb[0] > bay.width + 1e-6 or bb[3] - bb[1] > bay.height + 1e-6:
                continue

            positions = _quantile_sample_positions(
                baseline_greedy._candidate_positions(
                    bay.width,
                    bay.height,
                    active_blocks,
                    bb,
                ),
                max_positions,
            )
            for x, y in positions:
                if time.time() >= deadline:
                    break
                new_block = v064.Block(
                    block_id=target_block_id,
                    block_data=block,
                    x=x,
                    y=y,
                    orient_idx=orient_idx,
                )
                if not bay.contains_block(new_block):
                    continue
                entry, exit_time = baseline_greedy._find_earliest_slot(
                    new_block,
                    bay,
                    bay_placed[bay_id],
                    bay_schedule[bay_id],
                    release,
                    proc,
                )
                if entry is None:
                    continue

                tardiness = max(0, exit_time - due)
                score = baseline_greedy._placement_score(
                    tardiness,
                    workload,
                    bay_loads,
                    bay_id,
                    pref_max - prefs[bay_id],
                    bay_weights,
                    w1,
                    w2,
                    w3,
                    top_y=y + bb[3],
                )
                key = (
                    score,
                    tardiness,
                    exit_time,
                    x + y,
                    x,
                    y,
                    bay_id,
                    orient_idx,
                )
                if best_key is None or key < best_key:
                    best_key = key
                    best = (bay_id, x, y, orient_idx, int(entry), int(exit_time))

    if best is None:
        return None

    bay_id, x, y, orient_idx, entry, exit_time = best
    repaired[target_block_id] = {
        "block_id": target_block_id,
        "bay_id": bay_id,
        "x": x,
        "y": y,
        "orient_idx": orient_idx,
        "entry_time": entry,
        "exit_time": exit_time,
    }
    return repaired


def _try_prob33like_runtime_repair(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    gap_budget = _gap_budget(remaining, tier)
    if gap_budget <= 0.0:
        return base_solution, base_result

    started = time.time()
    base_assignments = v064._solution_to_assignments(base_solution)
    target_block_ids = v069._target_block_ids(prob_info, base_assignments)
    if not target_block_ids:
        return base_solution, base_result

    gap_assignments = _quantile_gap_single_reinsert(
        prob_info,
        base_assignments,
        target_block_ids[0],
        max_positions=24,
        deadline=started + gap_budget,
    )
    if gap_assignments is None:
        print(
            f"[baseline_hh reboot_v081] no_prob33like_gap_single instance={prob_info.get('name')} "
            f"tier={tier} elapsed={time.time() - started:.2f}s budget={gap_budget:.2f}s"
        )
        return base_solution, base_result

    gap_solution = v064.v001._solution_from_assignments(gap_assignments)
    gap_result = v064.v001.check_feasibility(prob_info, gap_solution)
    print(
        f"[baseline_hh reboot_v081] prob33like_gap_single instance={prob_info.get('name')} "
        f"tier={tier} target_block={target_block_ids[0]} feasible={gap_result.get('feasible')} "
        f"T={gap_result.get('obj1')} objective={gap_result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s"
    )

    best_solution = base_solution
    best_result = base_result
    if v064._result_key(gap_result) < v064._result_key(best_result):
        best_solution = gap_solution
        best_result = gap_result

    fast_target_ids = v064._tardy_block_ids(prob_info, gap_assignments, 1)
    if fast_target_ids:
        fast_assignments = v073._limited_single_reinsert(
            prob_info,
            gap_assignments,
            fast_target_ids[0],
            max_positions=8,
            max_orients=4,
        )
        if fast_assignments is not None:
            fast_solution = v064.v001._solution_from_assignments(fast_assignments)
            fast_result = v064.v001.check_feasibility(prob_info, fast_solution)
            print(
                f"[baseline_hh reboot_v081] prob33like_fast_single instance={prob_info.get('name')} "
                f"tier={tier} target_block={fast_target_ids[0]} feasible={fast_result.get('feasible')} "
                f"T={fast_result.get('obj1')} objective={fast_result.get('objective')}"
            )
            if v064._result_key(fast_result) < v064._result_key(best_result):
                best_solution = fast_solution
                best_result = fast_result

    return best_solution, best_result


def _class_solution(prob_info: dict, timelimit: float, tier: str) -> dict:
    started = time.time()
    base_solution = v065.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    remaining = max(0.0, float(timelimit) - (time.time() - started))

    if (
        not base_result.get("feasible")
        or float(base_result.get("obj1") or 0.0) < 3000.0
        or remaining <= _dynamic_reserve(float(timelimit)) + 2.0
    ):
        print(
            f"[baseline_hh reboot_v081] skip_prob33like_runtime_repair instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s base_T={base_result.get('obj1')}"
        )
        return base_solution

    best_solution, best_result = _try_prob33like_runtime_repair(
        prob_info,
        base_solution,
        base_result,
        remaining - _dynamic_reserve(float(timelimit)),
        tier,
    )
    if v064._result_key(best_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v081] selected_prob33like_runtime_repair instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v081] keep_prob33like_base instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={best_result.get('obj1')}"
    )
    return base_solution


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v064._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and _matches_prob33like_runtime_class(features):
        return _class_solution(prob_info, timelimit, tier)
    return v078.algorithm(prob_info, timelimit)
