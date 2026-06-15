"""baseline_hh_v003_hybrid_serial.py

Strategy:
    Hybrid safe-serial portfolio.

Changes from v002:
    - Builds two deadline-safe empty-bay candidates:
        1. official greedy serial fallback,
        2. v002 objective-aware safe serial.
    - Validates both with the official checker and returns the lower objective.

Expected strengths:
    Keeps v002's broad improvements while eliminating regressions against the
    official serial fallback.

Expected weaknesses:
    Still forbids concurrent occupancy within each bay, so it is a stable
    feasibility baseline rather than a deep packing/local-search solver.
"""

from __future__ import annotations

import time

import baseline_greedy
from alg_versions import baseline_hh_v002_safe_serial as v002
from utils import Bay, check_feasibility


def _official_serial_solution(prob_info: dict) -> dict:
    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info["bays"])]
    assignments = baseline_greedy._serial_empty_bay_fallback(prob_info, bays, prob_info["blocks"])
    return {"operations": baseline_greedy._build_operations(list(assignments.values()))}


def _candidate_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result["objective"]),
        float(result["obj1"]),
        float(result["obj2"]),
        float(result["obj3"]),
    )


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    started = time.time()
    print(
        f"[baseline_hh v003] instance={prob_info.get('name', '?')} "
        f"blocks={len(prob_info.get('blocks', []))} bays={len(prob_info.get('bays', []))} "
        f"timelimit={timelimit:.1f}s"
    )

    candidates: list[tuple[str, dict, dict]] = []

    official = _official_serial_solution(prob_info)
    official_result = check_feasibility(prob_info, official)
    candidates.append(("official_serial", official, official_result))
    print(
        f"[baseline_hh v003] official_serial feasible={official_result['feasible']} "
        f"obj={official_result.get('objective')}"
    )

    aware = v002._build_safe_serial_solution(prob_info)
    aware_result = check_feasibility(prob_info, aware)
    candidates.append(("objective_aware_serial", aware, aware_result))
    print(
        f"[baseline_hh v003] objective_aware_serial feasible={aware_result['feasible']} "
        f"obj={aware_result.get('objective')}"
    )

    label, solution, result = min(candidates, key=lambda item: _candidate_key(item[2]))
    if result.get("feasible"):
        print(
            f"[baseline_hh v003] selected={label} obj={result['objective']:.2f} "
            f"elapsed={time.time() - started:.2f}s"
        )
        return solution

    print("[baseline_hh v003] no feasible candidate; returning official serial fallback")
    for violation in official_result.get("violations", [])[:3]:
        print(f"[baseline_hh v003]   {violation}")
    return official

