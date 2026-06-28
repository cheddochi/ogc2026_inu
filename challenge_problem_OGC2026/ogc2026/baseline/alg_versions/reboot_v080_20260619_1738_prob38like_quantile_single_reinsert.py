"""reboot_v080_20260619_1738_prob38like_quantile_single_reinsert.py

Strategy:
    Keep trusted v078 as the default path, then replace the expensive
    prob38-like full greedy-prefix retry with a cheaper one-block reinsertion
    that samples deep candidate positions at quantile checkpoints.

Metadata:
    version_id: reboot_v080_20260619_1738_prob38like_quantile_single_reinsert
    parent_version: reboot_v078_20260619_1535_fourbay_runtime_family_flatten
    status: candidate
    timestamp: 2026-06-19 17:38 KST
    strategy:
        - Preserve v078 unchanged outside the prob38-like subtype.
        - On the prob38-like family, build the trusted release-aware direct
          candidate first.
        - Remove exactly one top-tardy block and reinsert it with an
          all-bay/all-orientation search over quantile-sampled candidate
          positions instead of the older full greedy prefix rebuild.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The v079 improvement signal came from a single deep candidate position,
        not from a broad multi-block repair. Quantile-sampling the candidate
        position list should keep that signal while trimming the local-search
        runtime enough to stay under the official 60s limit.
    intended_metric_target:
        - improve prob38-like rows
        - preserve the stable flattened parent elsewhere
        - improve avg objective versus trusted v074/v078
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v078_20260619_1535_fourbay_runtime_family_flatten
"""

from __future__ import annotations

import time

import baseline_greedy
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v078_20260619_1535_fourbay_runtime_family_flatten as v078


ACTIVE_VERSION = "reboot_v080_20260619_1738_prob38like_quantile_single_reinsert"


def _research_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 6.0,
        "long": 8.0,
        "very_long": 10.0,
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


def _quantile_single_reinsert(
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

            raw_positions = baseline_greedy._candidate_positions(
                bay.width,
                bay.height,
                active_blocks,
                bb,
            )
            positions = _quantile_sample_positions(raw_positions, max_positions)
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
                pref_penalty = pref_max - prefs[bay_id]
                score = baseline_greedy._placement_score(
                    tardiness,
                    workload,
                    bay_loads,
                    bay_id,
                    pref_penalty,
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


def _try_quantile_single_reinsert(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict]:
    budget = _research_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result

    started = time.time()
    base_assignments = v064._solution_to_assignments(base_solution)
    tardy_block_ids = v064._tardy_block_ids(prob_info, base_assignments, 1)
    if not tardy_block_ids:
        return base_solution, base_result

    candidate_assignments = _quantile_single_reinsert(
        prob_info,
        base_assignments,
        tardy_block_ids[0],
        max_positions=40,
        deadline=started + budget,
    )
    elapsed = time.time() - started
    if candidate_assignments is None:
        print(
            f"[baseline_hh reboot_v080] no_quantile_reinsert instance={prob_info.get('name')} "
            f"tier={tier} elapsed={elapsed:.2f}s budget={budget:.2f}s"
        )
        return base_solution, base_result

    candidate_solution = v064.v001._solution_from_assignments(candidate_assignments)
    candidate_result = v064.v001.check_feasibility(prob_info, candidate_solution)
    print(
        f"[baseline_hh reboot_v080] prob38like_quantile_reinsert instance={prob_info.get('name')} "
        f"tier={tier} target_block={tardy_block_ids[0]} feasible={candidate_result.get('feasible')} "
        f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')} "
        f"elapsed={elapsed:.2f}s budget={budget:.2f}s"
    )
    if v064._result_key(candidate_result) < v064._result_key(base_result):
        return candidate_solution, candidate_result
    return base_solution, base_result


def _class_solution(prob_info: dict, timelimit: float, tier: str) -> dict:
    started = time.time()

    direct_budget = v050._policy_budget(float(timelimit), tier)
    direct_solution = v050._class_solution(prob_info, timelimit, tier)
    direct_result = v064.v001.check_feasibility(prob_info, direct_solution)
    remaining = max(0.0, float(timelimit) - (time.time() - started))

    if direct_budget < 45.0 or remaining <= 4.5:
        print(
            f"[baseline_hh reboot_v080] skip_prob38like_quantile_reinsert instance={prob_info.get('name')} "
            f"tier={tier} direct_budget={direct_budget:.2f} remaining={remaining:.2f}s"
        )
        return direct_solution

    best_solution, best_result = _try_quantile_single_reinsert(
        prob_info,
        direct_solution,
        direct_result,
        remaining,
        tier,
    )
    if v064._result_key(best_result) < v064._result_key(direct_result):
        print(
            f"[baseline_hh reboot_v080] selected_prob38like_quantile_reinsert instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v080] keep_prob38like_direct instance={prob_info.get('name')} "
        f"base_T={direct_result.get('obj1')} cand_T={best_result.get('obj1')} "
        f"direct_budget={direct_budget:.2f} remaining={remaining:.2f}s"
    )
    return direct_solution


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v050._selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and v050._matches_prob38like_class(features):
        return _class_solution(prob_info, timelimit, tier)
    return v078.algorithm(prob_info, timelimit)
