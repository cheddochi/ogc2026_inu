"""reboot_v278_20260628_trackA_coarse_gate_lazy_prob20_plus_lowproc_replay_on_active_v267.py

Strategy:
    Keep the trusted v267 surface as the default line, preserve the proven
    prob20 runtime-cliff specialist from v275, and keep the v276 deterministic
    low-proc Family A replay lane. Add a coarse pre-gate ahead of the O(n)
    feature extraction so obvious non-target rows return the trusted fallback
    immediately, then lazy-load the prob20 specialist only after the five-bay
    runtime-cliff gate is confirmed.
"""

from __future__ import annotations

import importlib.util
import time
from pathlib import Path


ACTIVE_VERSION = (
    "reboot_v278_20260628_trackA_coarse_gate_lazy_prob20_plus_lowproc_replay_on_active_v267"
)


def _load_module_from_peer(filename: str, module_name: str):
    module_path = Path(__file__).resolve().with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_TRUSTED_WRAPPER_FALLBACK = _load_module_from_peer(
    "reboot_v278_20260628_trusted_wrapper_fallback_v267.py",
    "_ogc2026_v278_trusted_wrapper_fallback_v267",
)


def _load_prob20_specialist_module():
    return _load_module_from_peer(
        "reboot_v275_20260628_trackA_runtimecliff_specialist_first_on_active_v267.py",
        "_ogc2026_v278_reuse_v275_specialist",
    )


def _coarse_gate(prob_info: dict) -> str:
    blocks = len(prob_info.get("blocks", []))
    bays = len(prob_info.get("bays", []))

    if bays == 5 and 280 <= blocks <= 320:
        return "runtimecliff_candidate"
    if bays in {2, 3} and 100 <= blocks <= 210:
        return "lowproc_candidate"
    return "fallback_only"


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
    pref_gap_values = []
    for block in blocks:
        prefs = [float(value) for value in block.get("bay_preferences", [])]
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
            ordered = sorted(prefs, reverse=True)
            pref_gap_values.append(ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0))
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += pref_value

    pref_concentration = 0.0
    workload_imbalance_pressure = 0.0
    if top_choices and blocks:
        counts = [top_choices.count(bay_id) for bay_id in range(len(bays))]
        pref_concentration = max(counts) / len(blocks)
        workload_imbalance_pressure = (max(counts) - min(counts)) / len(blocks)

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0.0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    slack_values = [
        due - rel - proc
        for due, rel, proc in zip(due_values, rel_values, proc_values)
    ]
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
        "pref_gap_mean": _mean(pref_gap_values),
        "workload_imbalance_pressure": workload_imbalance_pressure,
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


def _is_lowproc_constructive_family_a(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) in {2, 3}
        and 100 <= int(features.get("blocks", 0)) <= 210
        and float(features.get("w1", 0.0)) >= 10000.0
        and float(features.get("proc_mean", 0.0)) <= 8.0
        and float(features.get("pref_pressure", 1.0)) <= 0.55
        and float(features.get("workload_imbalance_pressure", 1.0)) <= 0.12
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


def _safety_margin(timelimit: float) -> float:
    return max(1.0, min(10.0, timelimit * 0.08))


def _lazy_lowproc_modules():
    from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
    from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186

    return v001, v186


def _lowproc_candidates(prob_info: dict) -> list[tuple[int, int]]:
    bays = max(1, min(3, len(prob_info.get("bays", []))))
    if bays >= 3:
        return [(3, 14), (3, 16)]
    return [(2, 14), (2, 16)]


def _constructive_budget(timelimit: float, tier: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    return min(16.0 if tier == "standard" else 18.0, max(10.0, timelimit * 0.28))


def _repair_budget(remaining: float, timelimit: float) -> float:
    spendable = max(0.0, remaining - _safety_margin(timelimit))
    if spendable < 0.8:
        return 0.0
    return min(4.0, spendable)


def _result_key(v186, result: dict) -> tuple[float, float, float, float]:
    return v186.v064._result_key(result)


def _build_release_due_candidate(prob_info: dict, budget: float, top_bays: int, max_positions: int, v001):
    started = time.time()
    solution = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="release_due",
        top_bays=top_bays,
        max_positions=max_positions,
    )
    result = v001.check_feasibility(prob_info, solution)
    print(
        f"[baseline_hh reboot_v278] lowproc_seed instance={prob_info.get('name')} "
        f"top_bays={top_bays} max_positions={max_positions} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s"
    )
    return solution, result


def _try_lowproc_constructive_portfolio(
    prob_info: dict,
    timelimit: float,
    features: dict[str, float],
    tier: str,
    v001,
    v186,
):
    started = time.time()
    budget = _constructive_budget(timelimit, tier)
    best_solution = None
    best_result = None
    attempted = []

    for top_bays, max_positions in _lowproc_candidates(prob_info):
        solution, result = _build_release_due_candidate(
            prob_info,
            budget,
            top_bays,
            max_positions,
            v001,
        )
        remaining = max(0.0, timelimit - (time.time() - started))
        repair_budget = _repair_budget(remaining, timelimit)
        if result.get("feasible") and repair_budget > 0.0 and v186._matches_family_a_tightslack(features):
            repaired_solution, repaired_result, accepted_moves = v186._try_family_a_warm_repair(
                prob_info,
                solution,
                result,
                repair_budget,
                tier,
                features,
            )
            print(
                f"[baseline_hh reboot_v278] lowproc_warm_repair instance={prob_info.get('name')} "
                f"top_bays={top_bays} max_positions={max_positions} "
                f"base_T={result.get('obj1')} best_T={repaired_result.get('obj1')} "
                f"accepted_moves={accepted_moves}"
            )
            if _result_key(v186, repaired_result) < _result_key(v186, result):
                solution = repaired_solution
                result = repaired_result

        attempted.append(
            (
                f"release_due_b{top_bays}_p{max_positions}",
                float(result.get("obj1") or 0.0),
                float(result.get("objective") or 0.0),
            )
        )
        if best_result is None or _result_key(v186, result) < _result_key(v186, best_result):
            best_solution = solution
            best_result = result

    print(
        f"[baseline_hh reboot_v278] lowproc_portfolio instance={prob_info.get('name')} "
        f"tier={tier} attempted={attempted} best_T={best_result.get('obj1')} "
        f"objective={best_result.get('objective')}"
    )
    return best_solution, best_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    coarse_gate = _coarse_gate(prob_info)

    if coarse_gate == "fallback_only":
        return _TRUSTED_WRAPPER_FALLBACK.algorithm(prob_info, timelimit)

    features = _selector_features(prob_info)
    tier = _time_tier(timelimit)

    if coarse_gate == "runtimecliff_candidate" and _is_runtime_cliff_tightslack(features):
        print(
            f"[baseline_hh reboot_v278] delegate_prob20_specialist instance={prob_info.get('name')} "
            f"tier={tier}"
        )
        specialist = _load_prob20_specialist_module()
        return specialist.algorithm(prob_info, timelimit)

    if coarse_gate == "lowproc_candidate" and _is_lowproc_constructive_family_a(features):
        v001, v186 = _lazy_lowproc_modules()
        candidate_solution, candidate_result = _try_lowproc_constructive_portfolio(
            prob_info,
            timelimit,
            features,
            tier,
            v001,
            v186,
        )
        if candidate_result.get("feasible"):
            print(
                f"[baseline_hh reboot_v278] select_lowproc_constructive instance={prob_info.get('name')} "
                f"tier={tier} T={candidate_result.get('obj1')} "
                f"objective={candidate_result.get('objective')}"
            )
            return candidate_solution
        print(
            f"[baseline_hh reboot_v278] lowproc_constructive_failed_keep_fallback instance={prob_info.get('name')} "
            f"tier={tier}"
        )

    print(
        f"[baseline_hh reboot_v278] keep_trusted_fallback instance={prob_info.get('name')} "
        f"tier={tier}"
    )
    return _TRUSTED_WRAPPER_FALLBACK.algorithm(prob_info, timelimit)
