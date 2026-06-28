"""reboot_v275_20260628_trackA_runtimecliff_specialist_first_on_active_v267.py

Strategy:
    Preserve trusted v267 everywhere outside one feature-only five-bay Family A
    runtime-cliff lane. Use local O(n) feature extraction before any heavy
    imports. On the gated lane, run the direct specialist first and only fall
    back to the frozen trusted wrapper if the specialist fails quickly enough
    to leave real headroom.
"""

from __future__ import annotations

import importlib.util
import time
from pathlib import Path


ACTIVE_VERSION = "reboot_v275_20260628_trackA_runtimecliff_specialist_first_on_active_v267"


def _load_trusted_wrapper_fallback_module():
    wrapper_path = Path(__file__).resolve().with_name(
        "reboot_v275_20260628_trusted_wrapper_fallback_v267.py"
    )
    spec = importlib.util.spec_from_file_location(
        "_ogc2026_v275_trusted_wrapper_fallback_v267",
        wrapper_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load trusted wrapper fallback from {wrapper_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_TRUSTED_WRAPPER_FALLBACK = _load_trusted_wrapper_fallback_module()


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    weights = prob_info.get("weights", {})

    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    rel_values = [float(block.get("release_time", 0.0)) for block in blocks]
    due_values = [float(block.get("due_date", 0.0)) for block in blocks]

    top_choices = []
    pref_weight = [0.0] * len(bays)
    for block in blocks:
        prefs = [float(value) for value in block.get("bay_preferences", [])]
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += pref_value

    pref_concentration = 0.0
    if top_choices and blocks:
        pref_concentration = max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    slack_values = [due - rel - proc for due, rel, proc in zip(due_values, rel_values, proc_values)]
    tight_slack_ratio = 0.0
    if slack_values:
        tight_slack_ratio = sum(1 for value in slack_values if value <= 1.0) / len(slack_values)

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "w1": float(weights.get("w1", 1.0)),
        "proc_mean": _mean(proc_values),
        "slack_mean": _mean(slack_values),
        "tight_slack_ratio": tight_slack_ratio,
        "pref_concentration": pref_concentration,
        "pref_pressure": pref_pressure,
    }


def _is_runtime_cliff_tightslack(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 5
        and 280 <= int(features.get("blocks", 0)) <= 320
        and float(features.get("w1", 0.0)) >= 20000.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.7
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.50
        and float(features.get("pref_concentration", 1.0)) <= 0.25
        and float(features.get("pref_pressure", 1.0)) <= 0.25
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


def _lazy_modules():
    from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
    from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
    from alg_versions import reboot_v195_20260626_familyA_window_reorder_on_v194 as v195

    return v001, v186, v195


def _safety_margin(timelimit: float) -> float:
    return max(1.0, min(10.0, timelimit * 0.08))


def _runtimecliff_policy(timelimit: float) -> dict[str, float]:
    return {
        "budget": min(52.0, max(8.0, timelimit - 0.1)),
        "top_bays": 4.0,
        "max_positions": 12.0,
        "order_strategy": "due_release_proc",
    }


def _result_key(v186, result: dict) -> tuple[float, float, float, float]:
    return v186.v064._result_key(result)


def _build_direct_runtimecliff_seed(prob_info: dict, timelimit: float, v001) -> tuple[dict, dict]:
    policy = _runtimecliff_policy(timelimit)
    started = time.time()
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=float(policy["budget"]),
        order_strategy=str(policy["order_strategy"]),
        top_bays=int(policy["top_bays"]),
        max_positions=int(policy["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v275] direct_runtimecliff_seed instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={policy['budget']:.1f}s"
    )
    return candidate, result


def _try_direct_runtimecliff_specialist(
    prob_info: dict,
    timelimit: float,
    features: dict[str, float],
    tier: str,
    v001,
    v186,
    v195,
) -> tuple[dict, dict]:
    started = time.time()
    best_solution, best_result = _build_direct_runtimecliff_seed(prob_info, timelimit, v001)
    reserve = max(v186._dynamic_reserve(timelimit), _safety_margin(timelimit))

    if (
        best_result.get("feasible")
        and float(best_result.get("obj1") or 0.0) > 0.0
        and tier not in {"very_short", "short"}
        and v186._matches_family_a_tightslack(features)
    ):
        remaining = max(0.0, timelimit - (time.time() - started))
        spendable = remaining - reserve
        if spendable > 1.0:
            repaired_solution, repaired_result, accepted_moves = v186._try_family_a_warm_repair(
                prob_info,
                best_solution,
                best_result,
                spendable,
                tier,
                features,
            )
            print(
                f"[baseline_hh reboot_v275] direct_warm_repair instance={prob_info.get('name')} "
                f"tier={tier} base_T={best_result.get('obj1')} best_T={repaired_result.get('obj1')} "
                f"accepted_moves={accepted_moves}"
            )
            if _result_key(v186, repaired_result) < _result_key(v186, best_result):
                best_solution = repaired_solution
                best_result = repaired_result

    if (
        best_result.get("feasible")
        and float(best_result.get("obj1") or 0.0) > 0.0
        and tier not in {"very_short", "short"}
        and v195._allow_window_reorder(features)
    ):
        remaining = max(0.0, timelimit - (time.time() - started))
        spendable = remaining - reserve
        if spendable > 1.0:
            window_solution, window_result, accepted_moves = v195._try_window_reorder(
                prob_info,
                best_solution,
                best_result,
                spendable,
                tier,
                features,
            )
            print(
                f"[baseline_hh reboot_v275] direct_window_candidate instance={prob_info.get('name')} "
                f"tier={tier} base_T={best_result.get('obj1')} best_T={window_result.get('obj1')} "
                f"accepted_moves={accepted_moves}"
            )
            if _result_key(v186, window_result) < _result_key(v186, best_result):
                best_solution = window_solution
                best_result = window_result

    print(
        f"[baseline_hh reboot_v275] direct_runtimecliff_final instance={prob_info.get('name')} "
        f"tier={tier} T={best_result.get('obj1')} objective={best_result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s"
    )
    return best_solution, best_result


def _try_fallback_recovery_if_headroom(
    prob_info: dict,
    timelimit: float,
    spent: float,
) -> dict | None:
    remaining = max(0.0, timelimit - spent)
    reserve = _safety_margin(timelimit)
    fallback_estimate = max(42.0, min(56.0, timelimit * 0.92))
    if remaining <= reserve + fallback_estimate:
        print(
            f"[baseline_hh reboot_v275] skip_fallback_recovery instance={prob_info.get('name')} "
            f"remaining={remaining:.2f}s reserve={reserve:.2f}s "
            f"fallback_estimate={fallback_estimate:.2f}s"
        )
        return None
    return _TRUSTED_WRAPPER_FALLBACK.algorithm(prob_info, timelimit)


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    timelimit = float(timelimit)
    features = _selector_features(prob_info)
    tier = _time_tier(timelimit)

    if not _is_runtime_cliff_tightslack(features):
        print(
            f"[baseline_hh reboot_v275] keep_trusted_fallback_postgate instance={prob_info.get('name')} "
            f"tier={tier} runtime_cliff_gate=False"
        )
        return _TRUSTED_WRAPPER_FALLBACK.algorithm(prob_info, timelimit)

    v001, v186, v195 = _lazy_modules()
    specialist_solution, specialist_result = _try_direct_runtimecliff_specialist(
        prob_info,
        timelimit,
        features,
        tier,
        v001,
        v186,
        v195,
    )
    if specialist_result.get("feasible"):
        print(
            f"[baseline_hh reboot_v275] select_direct_runtimecliff_specialist instance={prob_info.get('name')} "
            f"tier={tier} T={specialist_result.get('obj1')} objective={specialist_result.get('objective')}"
        )
        return specialist_solution

    fallback_solution = _try_fallback_recovery_if_headroom(
        prob_info,
        timelimit,
        time.time() - started,
    )
    if fallback_solution is not None:
        fallback_result = v001.check_feasibility(prob_info, fallback_solution)
        if fallback_result.get("feasible"):
            print(
                f"[baseline_hh reboot_v275] select_fallback_recovery instance={prob_info.get('name')} "
                f"tier={tier} T={fallback_result.get('obj1')} objective={fallback_result.get('objective')}"
            )
            return fallback_solution

    print(
        f"[baseline_hh reboot_v275] keep_specialist_result_after_recovery_check instance={prob_info.get('name')} "
        f"tier={tier} feasible={specialist_result.get('feasible')} "
        f"T={specialist_result.get('obj1')} objective={specialist_result.get('objective')}"
    )
    return specialist_solution
