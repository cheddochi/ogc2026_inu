"""reboot_v241_20260627_trackA_split_prob11_guard_from_first20_subgroup_on_v218.py

Strategy:
    Preserve the trusted v217 Track A surface, including the long four-bay
    `prob_19`-like specialist and the five-bay runtime-cliff route.
    Add one extra bounded deep residual-chain specialist for the remaining
    dense `200~250 block / 4-bay / high-w1 / tight-slack` family, so the
    stable-fourbay repair path can try a slightly deeper shortlist after the
    current mid-repair and micro-pair stages.

    On the broader first20 `4-bay / lowproc / diffuse / tight-slack` Family A
    subgroup, wrap the stable-fourbay route in an explicit role-based
    portfolio:
      - trusted fallback candidate = full v218 stable-fourbay chain
      - fast constructive candidate = direct v200 surface
      - specialist candidate = exact latest-feasible slice on fast surface
      - bounded repair candidate = exact latest-feasible slice on primary chain

    But split out the ultra-tight `prob_11`-like four-bay pocket before that
    broader subgroup portfolio opens:
      - preserve the narrow trusted v218 internal stable-fourbay lane for the
        `blocks<=220 / very-high-w1 / ultra-tight-slack` subtype
      - only open the broader role portfolio on the neighboring `prob_13 /
        prob_14 / prob_19`-like subgroup where v240 showed real T signal
    Keep the best feasible candidate by official T-first ordering.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122 as v123
from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
from alg_versions import reboot_v195_20260626_familyA_window_reorder_on_v194 as v195
from alg_versions import reboot_v200_20260626_trackA_stricter_first20_with_stable_prob38_guard as v200
from alg_versions import reboot_v202_20260626_trackA_portfolio_plus_multiblock_sequence_repair as v202
from alg_versions import reboot_v216_20260627_trackA_inline_latest_feasible_slice_on_v212 as v216


ACTIVE_VERSION = "reboot_v241_20260627_trackA_split_prob11_guard_from_first20_subgroup_on_v218"


def _is_runtime_cliff_tightslack(features: dict[str, float]) -> bool:
    return (
        v186._matches_family_a_tightslack(features)
        and int(features.get("bays", 0)) == 5
        and 280 <= int(features.get("blocks", 0)) <= 320
        and float(features.get("w1", 0.0)) >= 20000.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.7
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.50
        and float(features.get("pref_concentration", 1.0)) <= 0.25
        and float(features.get("pref_pressure", 1.0)) <= 0.25
    )


def _is_stable_fourbay_tightslack(features: dict[str, float]) -> bool:
    return (
        v186._matches_family_a_tightslack(features)
        and v202._allow_post_multiblock_repair(features)
        and int(features.get("bays", 0)) == 4
    )


def _allow_mid_fourbay_tardy_repair(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 180 <= int(features.get("blocks", 0)) <= 260
        and float(features.get("w1", 0.0)) >= 17000.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.65
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.52
        and float(features.get("pref_concentration", 1.0)) <= 0.32
        and float(features.get("pref_pressure", 1.0)) <= 0.29
    )


def _allow_long_fourbay_tardy_repair(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 280 <= int(features.get("blocks", 0)) <= 320
        and float(features.get("w1", 0.0)) >= 9000.0
        and float(features.get("proc_mean", 0.0)) <= 7.6
        and float(features.get("slack_mean", 0.0)) <= 1.50
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.55
        and float(features.get("pref_concentration", 1.0)) <= 0.30
        and float(features.get("pref_pressure", 1.0)) <= 0.28
    )


def _allow_any_fourbay_tardy_repair(features: dict[str, float]) -> bool:
    return _allow_mid_fourbay_tardy_repair(features) or _allow_long_fourbay_tardy_repair(features)


def _allow_dense_fourbay_deep_chain(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 190 <= int(features.get("blocks", 0)) <= 260
        and float(features.get("w1", 0.0)) >= 17500.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.60
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.53
        and float(features.get("pref_concentration", 1.0)) <= 0.31
        and float(features.get("pref_pressure", 1.0)) <= 0.28
    )


def _allow_micro_pair_prefix(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 190 <= int(features.get("blocks", 0)) <= 260
        and float(features.get("w1", 0.0)) >= 17000.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.60
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.54
        and float(features.get("pref_concentration", 1.0)) <= 0.31
        and float(features.get("pref_pressure", 1.0)) <= 0.29
    )


def _allow_first20_subgroup_role_portfolio(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 190 <= int(features.get("blocks", 0)) <= 320
        and float(features.get("w1", 0.0)) >= 15000.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.60
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.52
        and float(features.get("pref_concentration", 1.0)) <= 0.31
        and float(features.get("pref_pressure", 1.0)) <= 0.28
    )


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


def _role_specialist_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 1.1,
        "long": 1.4,
        "very_long": 1.7,
    }[tier]
    return min(cap, remaining)


def _micro_repair_budget(remaining: float, tier: str, block_count: int) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    cap = {
        "standard": 1.5,
        "long": 2.25,
        "very_long": 3.0,
    }[tier]
    if block_count >= 230:
        cap += 0.25
    return min(cap, remaining)


def _micro_repair_shortlist_limit(tier: str) -> int:
    return {
        "standard": 2,
        "long": 3,
        "very_long": 3,
    }[tier]


def _micro_pair_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    return min(
        {
            "standard": 1.0,
            "long": 1.4,
            "very_long": 1.8,
        }[tier],
        remaining,
    )


def _reserved_specialist_budget(
    current_result: dict,
    features: dict[str, float],
    tier: str,
    ) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    current_t = float(current_result.get("obj1") or 0.0)
    if current_t < 150.0:
        return 0.0
    if not (
        _allow_any_fourbay_tardy_repair(features)
        or _allow_micro_pair_prefix(features)
        or _allow_dense_fourbay_deep_chain(features)
    ):
        return 0.0
    base = {
        "standard": 2.4,
        "long": 3.0,
        "very_long": 3.6,
    }[tier]
    if int(features.get("blocks", 0)) >= 230:
        base += 0.3
    if _allow_micro_pair_prefix(features):
        base += 0.4
    if _allow_dense_fourbay_deep_chain(features):
        base += 0.3
    return base


def _micro_repair_max_positions(tier: str) -> int:
    return {
        "standard": 12,
        "long": 16,
        "very_long": 20,
    }[tier]


def _deep_chain_budget(remaining: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    return min(
        {
            "standard": 1.2,
            "long": 1.8,
            "very_long": 2.4,
        }[tier],
        remaining,
    )


def _deep_chain_shortlist_limit(tier: str) -> int:
    return {
        "standard": 3,
        "long": 3,
        "very_long": 4,
    }[tier]


def _deep_chain_max_positions(tier: str) -> int:
    return {
        "standard": 18,
        "long": 24,
        "very_long": 28,
    }[tier]


def _try_micro_pair_prefix(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict, list[tuple[int, int, float, float]]]:
    budget = _micro_pair_budget(remaining, tier)
    if budget <= 0.0:
        return base_solution, base_result, []

    deadline = time.time() + budget
    base_assignments = v123._solution_to_assignments(base_solution)
    tardy_block_ids = v123._tardy_block_ids(prob_info, base_assignments, 2)
    if len(tardy_block_ids) < 2:
        return base_solution, base_result, []

    if time.time() >= deadline:
        return base_solution, base_result, []

    candidate_assignments = v123._greedy_research_prefix(
        prob_info,
        base_assignments,
        tardy_block_ids,
        2,
    )
    candidate_solution = v186.v001._solution_from_assignments(candidate_assignments)
    candidate_result = v186.v001.check_feasibility(prob_info, candidate_solution)
    accepted_moves: list[tuple[int, int, float, float]] = []
    print(
        f"[baseline_hh reboot_v212] micro_pair_prefix_candidate instance={prob_info.get('name')} "
        f"tier={tier} blocks={tardy_block_ids[:2]} feasible={candidate_result.get('feasible')} "
        f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
    )
    if v186.v064._result_key(candidate_result) < v186.v064._result_key(base_result):
        accepted_moves.append(
            (
                tardy_block_ids[0],
                tardy_block_ids[1],
                float(candidate_result.get("obj1") or 0.0),
                float(candidate_result.get("objective") or 0.0),
            )
        )
        return candidate_solution, candidate_result, accepted_moves
    return base_solution, base_result, accepted_moves


def _try_mid_fourbay_tardy_repair(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
    features: dict[str, float],
) -> tuple[dict, dict, list[tuple[int, float, float, int]]]:
    budget = _micro_repair_budget(remaining, tier, int(features.get("blocks", 0)))
    shortlist_limit = _micro_repair_shortlist_limit(tier)
    if budget <= 0.0 or shortlist_limit <= 0:
        return base_solution, base_result, []

    deadline = time.time() + budget
    best_solution = base_solution
    best_result = base_result
    accepted_moves: list[tuple[int, float, float, int]] = []

    for _ in range(2):
        if time.time() >= deadline:
            break

        base_assignments = v186.v064._solution_to_assignments(best_solution)
        shortlist = v186._family_a_tardy_shortlist(prob_info, base_assignments, shortlist_limit)
        if not shortlist:
            break

        improved_this_round = False
        for block_id in shortlist:
            if time.time() >= deadline:
                break

            candidate_assignments = v080._quantile_single_reinsert(
                prob_info,
                base_assignments,
                block_id,
                max_positions=_micro_repair_max_positions(tier),
                deadline=deadline,
            )
            if candidate_assignments is None:
                continue

            candidate_solution = v186.v001._solution_from_assignments(candidate_assignments)
            candidate_result = v186.v001.check_feasibility(prob_info, candidate_solution)
            if not candidate_result.get("feasible"):
                repaired_assignments, repaired_result, _ = v186.v001._repair_with_empty_windows(
                    prob_info,
                    candidate_assignments,
                    max_rounds=3,
                )
                if repaired_result.get("feasible"):
                    candidate_assignments = repaired_assignments
                    candidate_solution = v186.v001._solution_from_assignments(candidate_assignments)
                    candidate_result = repaired_result

            print(
                f"[baseline_hh reboot_v212] mid_fourbay_tardy_candidate instance={prob_info.get('name')} "
                f"tier={tier} block={block_id} feasible={candidate_result.get('feasible')} "
                f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
            )
            if v186.v064._result_key(candidate_result) < v186.v064._result_key(best_result):
                best_solution = candidate_solution
                best_result = candidate_result
                accepted_moves.append(
                    (
                        block_id,
                        float(best_result.get("obj1") or 0.0),
                        float(best_result.get("objective") or 0.0),
                        _micro_repair_max_positions(tier),
                    )
                )
                improved_this_round = True
                break

        if not improved_this_round:
            break

    return best_solution, best_result, accepted_moves


def _try_dense_fourbay_deep_chain(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    tier: str,
) -> tuple[dict, dict, list[tuple[int, float, float, int]]]:
    budget = _deep_chain_budget(remaining, tier)
    shortlist_limit = _deep_chain_shortlist_limit(tier)
    if budget <= 0.0 or shortlist_limit <= 0:
        return base_solution, base_result, []

    deadline = time.time() + budget
    best_solution = base_solution
    best_result = base_result
    accepted_moves: list[tuple[int, float, float, int]] = []

    for _ in range(3):
        if time.time() >= deadline:
            break

        base_assignments = v186.v064._solution_to_assignments(best_solution)
        shortlist = v186._family_a_tardy_shortlist(prob_info, base_assignments, shortlist_limit)
        if not shortlist:
            break

        improved_this_round = False
        for block_id in shortlist:
            if time.time() >= deadline:
                break

            candidate_assignments = v080._quantile_single_reinsert(
                prob_info,
                base_assignments,
                block_id,
                max_positions=_deep_chain_max_positions(tier),
                deadline=deadline,
            )
            if candidate_assignments is None:
                continue

            candidate_solution = v186.v001._solution_from_assignments(candidate_assignments)
            candidate_result = v186.v001.check_feasibility(prob_info, candidate_solution)
            if not candidate_result.get("feasible"):
                repaired_assignments, repaired_result, _ = v186.v001._repair_with_empty_windows(
                    prob_info,
                    candidate_assignments,
                    max_rounds=3,
                )
                if repaired_result.get("feasible"):
                    candidate_solution = v186.v001._solution_from_assignments(repaired_assignments)
                    candidate_result = repaired_result

            print(
                f"[baseline_hh reboot_v218] dense_fourbay_chain_candidate instance={prob_info.get('name')} "
                f"tier={tier} block={block_id} feasible={candidate_result.get('feasible')} "
                f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
            )
            if v186.v064._result_key(candidate_result) < v186.v064._result_key(best_result):
                best_solution = candidate_solution
                best_result = candidate_result
                accepted_moves.append(
                    (
                        block_id,
                        float(best_result.get("obj1") or 0.0),
                        float(best_result.get("objective") or 0.0),
                        _deep_chain_max_positions(tier),
                    )
                )
                improved_this_round = True
                break

        if not improved_this_round:
            break

    return best_solution, best_result, accepted_moves


def _runtime_cliff_ordered_candidates(
    prob_info: dict,
    timelimit: float,
    started: float,
    tier: str,
    reserve: float,
    features: dict[str, float],
) -> dict:
    base_solution = v186.algorithm(prob_info, timelimit)
    base_result = v186.v001.check_feasibility(prob_info, base_solution)
    best_solution = base_solution
    best_result = base_result

    if (
        base_result.get("feasible")
        and float(base_result.get("obj1") or 0.0) > 0.0
        and tier not in {"very_short", "short"}
        and v195._allow_window_reorder(features)
    ):
        remaining = max(0.0, timelimit - (time.time() - started))
        spendable = remaining - reserve
        if spendable > 1.0:
            window_solution, window_result, accepted_moves = v195._try_window_reorder(
                prob_info,
                base_solution,
                base_result,
                spendable,
                tier,
                features,
            )
            print(
            f"[baseline_hh reboot_v212] runtime_window_candidate instance={prob_info.get('name')} "
                f"tier={tier} base_T={base_result.get('obj1')} best_T={window_result.get('obj1')} "
                f"accepted_moves={accepted_moves}"
            )
            if v186.v064._result_key(window_result) < v186.v064._result_key(best_result):
                best_solution = window_solution
                best_result = window_result
                print(
                    f"[baseline_hh reboot_v212] selected_runtime_window_candidate instance={prob_info.get('name')} "
                    f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
                )
        else:
            print(
                f"[baseline_hh reboot_v212] skip_runtime_window instance={prob_info.get('name')} "
                f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
                f"base_T={base_result.get('obj1')} objective={base_result.get('objective')}"
            )
    else:
        print(
            f"[baseline_hh reboot_v212] return_runtime_base instance={prob_info.get('name')} "
            f"tier={tier} base_T={base_result.get('obj1')} objective={base_result.get('objective')}"
        )

    remaining = max(0.0, timelimit - (time.time() - started))
    deep_fallback_budget = max(10.0, min(18.0, timelimit * 0.22))
    if remaining > reserve + deep_fallback_budget:
        fallback_solution = v200.algorithm(prob_info, remaining)
        fallback_result = v186.v001.check_feasibility(prob_info, fallback_solution)
        print(
            f"[baseline_hh reboot_v212] runtime_deep_fallback instance={prob_info.get('name')} "
            f"tier={tier} budget={remaining:.2f}s T={fallback_result.get('obj1')} "
            f"objective={fallback_result.get('objective')}"
        )
        if v186.v064._result_key(fallback_result) < v186.v064._result_key(best_result):
            best_solution = fallback_solution
            best_result = fallback_result
            print(
                f"[baseline_hh reboot_v212] selected_runtime_deep_fallback instance={prob_info.get('name')} "
                f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
            )
    else:
        print(
            f"[baseline_hh reboot_v212] skip_runtime_deep_fallback instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"required_headroom={deep_fallback_budget:.2f}s"
        )

    return best_solution


def _stable_fourbay_internal_portfolio(
    prob_info: dict,
    timelimit: float,
    started: float,
    tier: str,
    reserve: float,
    features: dict[str, float],
    portfolio_solution: dict,
    portfolio_result: dict,
) -> dict:
    remaining = max(0.0, timelimit - (time.time() - started))
    spendable = remaining - reserve
    if spendable <= 1.0:
        print(
            f"[baseline_hh reboot_v212] skip_stable_fourbay_portfolio instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"T={portfolio_result.get('obj1')} objective={portfolio_result.get('objective')}"
        )
        return portfolio_solution

    best_solution = portfolio_solution
    best_result = portfolio_result
    specialist_reserve = _reserved_specialist_budget(best_result, features, tier)
    if specialist_reserve > 0.0:
        print(
            f"[baseline_hh reboot_v212] reserve_specialist_budget instance={prob_info.get('name')} "
            f"tier={tier} reserved={specialist_reserve:.2f}s base_T={best_result.get('obj1')} "
            f"objective={best_result.get('objective')}"
        )

    spendable = max(0.0, remaining - reserve - specialist_reserve)
    multiblock_solution, multiblock_result, multiblock_attempted = v202._try_post_multiblock_repair(
        prob_info,
        portfolio_solution,
        portfolio_result,
        spendable,
        tier,
        features,
    )
    print(
        f"[baseline_hh reboot_v212] multiblock_candidate instance={prob_info.get('name')} "
        f"tier={tier} base_T={portfolio_result.get('obj1')} best_T={multiblock_result.get('obj1')} "
        f"attempted={multiblock_attempted}"
    )
    if v186.v064._result_key(multiblock_result) < v186.v064._result_key(best_result):
        best_solution = multiblock_solution
        best_result = multiblock_result
        print(
            f"[baseline_hh reboot_v212] selected_multiblock_candidate instance={prob_info.get('name')} "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )

    remaining = max(0.0, timelimit - (time.time() - started))
    spendable = max(0.0, remaining - reserve - specialist_reserve)
    if spendable > 1.0 and v195._allow_window_reorder(features):
        window_solution, window_result, accepted_moves = v195._try_window_reorder(
            prob_info,
            best_solution,
            best_result,
            spendable,
            tier,
            features,
        )
        print(
            f"[baseline_hh reboot_v212] stable_window_candidate instance={prob_info.get('name')} "
            f"tier={tier} base_T={best_result.get('obj1')} best_T={window_result.get('obj1')} "
            f"accepted_moves={accepted_moves}"
        )
        if v186.v064._result_key(window_result) < v186.v064._result_key(best_result):
            best_solution = window_solution
            best_result = window_result
            print(
                f"[baseline_hh reboot_v212] selected_stable_window_candidate instance={prob_info.get('name')} "
                f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
            )
    else:
        print(
            f"[baseline_hh reboot_v212] skip_stable_window_candidate instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve + specialist_reserve:.2f}s "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )

    remaining = max(0.0, timelimit - (time.time() - started))
    pair_headroom = _micro_pair_budget(max(0.0, remaining - reserve), tier) if _allow_micro_pair_prefix(features) else 0.0
    spendable = max(0.0, remaining - reserve - pair_headroom)
    if (
        spendable > 1.0
        and float(best_result.get("obj1") or 0.0) > 0.0
        and float(best_result.get("obj1") or 0.0) >= 150.0
        and _allow_any_fourbay_tardy_repair(features)
    ):
        residual_solution, residual_result, accepted_moves = _try_mid_fourbay_tardy_repair(
            prob_info,
            best_solution,
            best_result,
            spendable,
            tier,
            features,
        )
        print(
            f"[baseline_hh reboot_v212] mid_fourbay_tardy_repair instance={prob_info.get('name')} "
            f"tier={tier} base_T={best_result.get('obj1')} best_T={residual_result.get('obj1')} "
            f"accepted_moves={accepted_moves}"
        )
        if v186.v064._result_key(residual_result) < v186.v064._result_key(best_result):
            best_solution = residual_solution
            best_result = residual_result
            print(
                f"[baseline_hh reboot_v212] selected_mid_fourbay_tardy_repair instance={prob_info.get('name')} "
                f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
            )
    else:
        print(
            f"[baseline_hh reboot_v212] skip_mid_fourbay_tardy_repair instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve + pair_headroom:.2f}s "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )

    remaining = max(0.0, timelimit - (time.time() - started))
    spendable = max(0.0, remaining - reserve)
    if (
        spendable > 0.5
        and float(best_result.get("obj1") or 0.0) >= 150.0
        and _allow_micro_pair_prefix(features)
    ):
        pair_solution, pair_result, accepted_moves = _try_micro_pair_prefix(
            prob_info,
            best_solution,
            best_result,
            spendable,
            tier,
        )
        print(
            f"[baseline_hh reboot_v212] micro_pair_prefix instance={prob_info.get('name')} "
            f"tier={tier} base_T={best_result.get('obj1')} best_T={pair_result.get('obj1')} "
            f"accepted_moves={accepted_moves}"
        )
        if v186.v064._result_key(pair_result) < v186.v064._result_key(best_result):
            best_solution = pair_solution
            best_result = pair_result
            print(
                f"[baseline_hh reboot_v212] selected_micro_pair_prefix instance={prob_info.get('name')} "
                f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
            )
    else:
        print(
            f"[baseline_hh reboot_v212] skip_micro_pair_prefix instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )

    remaining = max(0.0, timelimit - (time.time() - started))
    spendable = max(0.0, remaining - reserve)
    if (
        spendable > 0.75
        and float(best_result.get("obj1") or 0.0) >= 180.0
        and _allow_dense_fourbay_deep_chain(features)
    ):
        chain_solution, chain_result, accepted_moves = _try_dense_fourbay_deep_chain(
            prob_info,
            best_solution,
            best_result,
            spendable,
            tier,
        )
        print(
            f"[baseline_hh reboot_v218] dense_fourbay_chain instance={prob_info.get('name')} "
            f"tier={tier} base_T={best_result.get('obj1')} best_T={chain_result.get('obj1')} "
            f"accepted_moves={accepted_moves}"
        )
        if v186.v064._result_key(chain_result) < v186.v064._result_key(best_result):
            best_solution = chain_solution
            best_result = chain_result
            print(
                f"[baseline_hh reboot_v218] selected_dense_fourbay_chain instance={prob_info.get('name')} "
                f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
            )
    else:
        print(
            f"[baseline_hh reboot_v218] skip_dense_fourbay_chain instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )

    return best_solution


def _stable_fourbay_role_portfolio(
    prob_info: dict,
    timelimit: float,
    started: float,
    tier: str,
    reserve: float,
    features: dict[str, float],
    portfolio_solution: dict,
    portfolio_result: dict,
) -> dict:
    primary_solution = _stable_fourbay_internal_portfolio(
        prob_info,
        timelimit,
        started,
        tier,
        reserve,
        features,
        portfolio_solution,
        portfolio_result,
    )
    primary_result = v186.v001.check_feasibility(prob_info, primary_solution)

    if _allow_prob11like_ultratight_lane(features):
        print(
            f"[baseline_hh reboot_v241] preserve_prob11like_ultratight_lane instance={prob_info.get('name')} "
            f"tier={tier} T={primary_result.get('obj1')} objective={primary_result.get('objective')}"
        )
        return primary_solution

    if not _allow_first20_subgroup_role_portfolio(features):
        return primary_solution

    candidates: list[tuple[str, dict, dict]] = [
        ("primary_v218_chain", primary_solution, primary_result),
        ("fast_v200", portfolio_solution, portfolio_result),
    ]
    attempted: list[tuple[str, float, float]] = [
        (
            "primary_v218_chain",
            float(primary_result.get("obj1") or 0.0),
            float(primary_result.get("objective") or 0.0),
        ),
        (
            "fast_v200",
            float(portfolio_result.get("obj1") or 0.0),
            float(portfolio_result.get("objective") or 0.0),
        ),
    ]

    remaining = max(0.0, timelimit - (time.time() - started))
    specialist_budget = _role_specialist_budget(max(0.0, remaining - reserve), tier)
    if specialist_budget > 0.45:
        fast_exact_solution, fast_exact_result, _ = v216._try_exact_latest_feasible_slice(
            prob_info,
            portfolio_solution,
            portfolio_result,
            specialist_budget,
            tier,
        )
        attempted.append(
            (
                "specialist_exact_on_fast",
                float(fast_exact_result.get("obj1") or 0.0),
                float(fast_exact_result.get("objective") or 0.0),
            )
        )
        if fast_exact_result.get("feasible"):
            candidates.append(("specialist_exact_on_fast", fast_exact_solution, fast_exact_result))

        remaining = max(0.0, timelimit - (time.time() - started))
        specialist_budget = _role_specialist_budget(max(0.0, remaining - reserve), tier)
        if specialist_budget > 0.45:
            primary_exact_solution, primary_exact_result, _ = v216._try_exact_latest_feasible_slice(
                prob_info,
                primary_solution,
                primary_result,
                specialist_budget,
                tier,
            )
            attempted.append(
                (
                    "specialist_exact_on_primary",
                    float(primary_exact_result.get("obj1") or 0.0),
                    float(primary_exact_result.get("objective") or 0.0),
                )
            )
            if primary_exact_result.get("feasible"):
                candidates.append(("specialist_exact_on_primary", primary_exact_solution, primary_exact_result))

    best_label, best_solution, best_result = min(
        candidates,
        key=lambda item: v186.v064._result_key(item[2]),
    )
    print(
        f"[baseline_hh reboot_v241] stable_fourbay_role_portfolio instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} selected={best_label} "
        f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
    )
    return best_solution


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    started = time.time()
    tier = v186.v169._time_tier(timelimit)
    reserve = v186._dynamic_reserve(timelimit)
    features = v186._selector_features(prob_info)

    if _is_runtime_cliff_tightslack(features):
        print(
            f"[baseline_hh reboot_v212] route_runtime_cliff instance={prob_info.get('name')} "
            f"blocks={int(features.get('blocks', 0))} bays={int(features.get('bays', 0))}"
        )
        return _runtime_cliff_ordered_candidates(
            prob_info,
            timelimit,
            started,
            tier,
            reserve,
            features,
        )

    portfolio_solution = v200.algorithm(prob_info, timelimit)
    portfolio_result = v186.v001.check_feasibility(prob_info, portfolio_solution)

    if (
        not portfolio_result.get("feasible")
        or not v186._matches_family_a_tightslack(features)
        or not v202._allow_post_multiblock_repair(features)
        or float(portfolio_result.get("obj1") or 0.0) < 20.0
        or tier in {"very_short", "short"}
    ):
        print(
            f"[baseline_hh reboot_v212] return_portfolio instance={prob_info.get('name')} "
            f"tier={tier} T={portfolio_result.get('obj1')} objective={portfolio_result.get('objective')}"
        )
        return portfolio_solution

    if _is_stable_fourbay_tightslack(features):
        print(
            f"[baseline_hh reboot_v212] route_stable_fourbay instance={prob_info.get('name')} "
            f"blocks={int(features.get('blocks', 0))} bays={int(features.get('bays', 0))}"
        )
        return _stable_fourbay_role_portfolio(
            prob_info,
            timelimit,
            started,
            tier,
            reserve,
            features,
            portfolio_solution,
            portfolio_result,
        )

    remaining = max(0.0, timelimit - (time.time() - started))
    spendable = remaining - reserve
    if spendable <= 1.0:
        print(
            f"[baseline_hh reboot_v212] skip_default_multiblock instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"T={portfolio_result.get('obj1')} objective={portfolio_result.get('objective')}"
        )
        return portfolio_solution

    repaired_solution, repaired_result, attempted = v202._try_post_multiblock_repair(
        prob_info,
        portfolio_solution,
        portfolio_result,
        spendable,
        tier,
        features,
    )
    print(
        f"[baseline_hh reboot_v212] default_multiblock instance={prob_info.get('name')} "
        f"tier={tier} base_T={portfolio_result.get('obj1')} best_T={repaired_result.get('obj1')} "
        f"attempted={attempted}"
    )
    if v186.v064._result_key(repaired_result) < v186.v064._result_key(portfolio_result):
        print(
            f"[baseline_hh reboot_v212] selected_default_multiblock instance={prob_info.get('name')} "
            f"T={repaired_result.get('obj1')} objective={repaired_result.get('objective')}"
        )
        return repaired_solution
    return portfolio_solution
