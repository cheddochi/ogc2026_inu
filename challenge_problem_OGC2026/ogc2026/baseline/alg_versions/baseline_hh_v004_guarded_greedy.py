"""baseline_hh_v004_guarded_greedy.py

Strategy:
    Guarded repaired-greedy portfolio.

Changes from v003:
    - Keeps v003's always-feasible hybrid serial candidate as the first fallback.
    - Re-introduces the official repaired greedy search only for small/medium
      instances where prior benchmarks showed it can produce much lower
      objective values without destabilizing runtime.
    - Validates every candidate with the official checker and returns the best
      feasible objective.

Expected strengths:
    Recovers v001's strong results on smaller training instances while
    preserving v003's 40/40 feasibility behavior on harder cases.

Expected weaknesses:
    Quality on large instances is still limited by the conservative serial
    fallback; deeper packing/local-search is not attempted yet.

Smoke result:
    Inactive after 2026-06-16 smoke testing.  The official repaired greedy
    implementation did not honor short internal budgets strongly enough:
    prob_7 timed out and prob_2/3/8 did not improve over v003.  Keep this file
    as an experiment record; do not activate it without an external hard
    timeout around the repaired greedy candidate.
"""

from __future__ import annotations

import time
import traceback

import baseline_greedy
from alg_versions import baseline_hh_v003_hybrid_serial as v003
from utils import check_feasibility


def _candidate_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result["objective"]),
        float(result["obj1"]),
        float(result["obj2"]),
        float(result["obj3"]),
    )


def _time_left(deadline: float) -> float:
    return max(0.0, deadline - time.time())


def _should_try_repaired_greedy(prob_info: dict, timelimit: float, deadline: float) -> bool:
    n_blocks = len(prob_info.get("blocks", []))
    if timelimit <= 12.0:
        return False
    if n_blocks > 150:
        return False
    return _time_left(deadline) > 12.0


def _repaired_greedy_budget(prob_info: dict, deadline: float) -> float:
    n_blocks = len(prob_info.get("blocks", []))
    remaining = _time_left(deadline)
    if n_blocks <= 100:
        target = 24.0
    else:
        target = 36.0
    return max(11.0, min(target, remaining - 1.0))


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    started = time.time()
    deadline = started + max(1.0, float(timelimit))
    n_blocks = len(prob_info.get("blocks", []))
    n_bays = len(prob_info.get("bays", []))
    print(
        f"[baseline_hh v004] instance={prob_info.get('name', '?')} "
        f"blocks={n_blocks} bays={n_bays} timelimit={timelimit:.1f}s"
    )

    candidates: list[tuple[str, dict, dict]] = []

    safe_solution = v003.algorithm(prob_info, timelimit)
    safe_result = check_feasibility(prob_info, safe_solution)
    candidates.append(("v003_hybrid_serial", safe_solution, safe_result))
    print(
        f"[baseline_hh v004] v003_hybrid_serial feasible={safe_result['feasible']} "
        f"obj={safe_result.get('objective')} elapsed={time.time() - started:.2f}s"
    )

    if _should_try_repaired_greedy(prob_info, float(timelimit), deadline):
        budget = _repaired_greedy_budget(prob_info, deadline)
        try:
            greedy_started = time.time()
            greedy_solution = baseline_greedy.greedyalgorithm(prob_info, budget)
            greedy_result = check_feasibility(prob_info, greedy_solution)
            candidates.append(("guarded_repaired_greedy", greedy_solution, greedy_result))
            print(
                f"[baseline_hh v004] guarded_repaired_greedy feasible={greedy_result['feasible']} "
                f"obj={greedy_result.get('objective')} budget={budget:.1f}s "
                f"elapsed={time.time() - greedy_started:.2f}s"
            )
        except Exception:
            print("[baseline_hh v004] guarded_repaired_greedy exception")
            print(traceback.format_exc())
    else:
        print(
            f"[baseline_hh v004] skip guarded_repaired_greedy "
            f"remaining={_time_left(deadline):.2f}s blocks={n_blocks}"
        )

    label, solution, result = min(candidates, key=lambda item: _candidate_key(item[2]))
    if result.get("feasible"):
        print(
            f"[baseline_hh v004] selected={label} obj={result['objective']:.2f} "
            f"elapsed={time.time() - started:.2f}s"
        )
        return solution

    print("[baseline_hh v004] no feasible candidate; returning v003 fallback")
    return safe_solution
