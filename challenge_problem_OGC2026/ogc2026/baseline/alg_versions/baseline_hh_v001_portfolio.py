"""baseline_hh_v001_portfolio.py

Strategy:
    Feasibility-first portfolio with safe fallback.

Changes from v000:
    - Always secures a conservative feasible candidate early using the official
      greedy algorithm's short-timelimit serial fallback path.
    - Optionally tries the team solver (`casat_cheddochi`) only when one of its
      optional exact solvers is available and enough time remains.
    - Uses the official greedy repair with the remaining time as the primary
      improvement candidate.
    - Validates every candidate with the official checker and returns the best
      feasible objective found.

Expected strengths:
    Lower risk of returning no solution or an infeasible solution; easy to
    benchmark against other versions because all choices are logged.

Expected weaknesses:
    Sequential portfolio calls can spend time on redundant candidates when the
    optional exact solvers are unavailable; deeper local search is not included
    yet.
"""

from __future__ import annotations

import time
import traceback
from typing import Callable

import baseline_greedy
from utils import check_feasibility


def _time_left(deadline: float) -> float:
    return max(0.0, deadline - time.time())


def _candidate_score(result: dict) -> float:
    if result.get("feasible") and isinstance(result.get("objective"), (int, float)):
        return float(result["objective"])
    return float("inf")


def _try_candidate(
    label: str,
    make_solution: Callable[[float], dict],
    prob_info: dict,
    deadline: float,
    min_time: float,
) -> tuple[dict | None, dict | None]:
    """Run one candidate generator if enough time remains, then validate it."""
    remaining = _time_left(deadline)
    if remaining < min_time:
        print(f"[baseline_hh v001] skip {label}: remaining={remaining:.2f}s")
        return None, None

    try:
        started = time.time()
        solution = make_solution(remaining)
        elapsed = time.time() - started
        result = check_feasibility(prob_info, solution)
        if result["feasible"]:
            print(
                f"[baseline_hh v001] {label}: PASS obj={result['objective']:.2f} "
                f"elapsed={elapsed:.2f}s remaining={_time_left(deadline):.2f}s"
            )
        else:
            print(
                f"[baseline_hh v001] {label}: FAIL stage={result['stage']} "
                f"elapsed={elapsed:.2f}s remaining={_time_left(deadline):.2f}s"
            )
            for violation in result.get("violations", [])[:3]:
                print(f"[baseline_hh v001]   {violation}")
        return solution, result
    except Exception:
        print(f"[baseline_hh v001] {label}: exception")
        print(traceback.format_exc())
        return None, None


def _optional_solver_available() -> bool:
    """Return True only when the team solver can do more than greedy fallback."""
    try:
        import casat_cheddochi

        return bool(
            getattr(casat_cheddochi, "_HAS_GUROBI", False)
            or getattr(casat_cheddochi, "_HAS_ORTOOLS", False)
        )
    except Exception:
        return False


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Return the best feasible candidate found before the wall-clock deadline."""
    started = time.time()
    deadline = started + max(1.0, float(timelimit))
    n_blocks = len(prob_info.get("blocks", []))
    n_bays = len(prob_info.get("bays", []))

    print(
        f"[baseline_hh v001] instance={prob_info.get('name', '?')} "
        f"blocks={n_blocks} bays={n_bays} timelimit={timelimit:.1f}s"
    )

    best_solution: dict | None = None
    best_result: dict | None = None
    last_solution: dict | None = None

    def remember(solution: dict | None, result: dict | None) -> None:
        nonlocal best_solution, best_result, last_solution
        if solution is not None:
            last_solution = solution
        if solution is None or result is None or not result.get("feasible"):
            return
        if best_result is None or _candidate_score(result) < _candidate_score(best_result):
            best_solution = solution
            best_result = result

    # Candidate 1: secure a conservative feasible answer early.  The official
    # greedy uses a serial empty-window fallback when timelimit <= 10.
    fast_budget = min(10.0, max(3.0, float(timelimit) * 0.15))
    sol, res = _try_candidate(
        "greedy_serial_fallback",
        lambda remaining: baseline_greedy.greedyalgorithm(
            prob_info, min(fast_budget, max(1.0, remaining - 0.25))
        ),
        prob_info,
        deadline,
        min_time=1.0,
    )
    remember(sol, res)

    # Candidate 2: use the team solver only when its optional solver backend is
    # present.  Without Gurobi/OR-Tools it mostly delegates back to greedy, so
    # skipping avoids spending duplicate time.
    if _optional_solver_available():
        def run_team_solver(remaining: float) -> dict:
            import casat_cheddochi

            budget = max(3.0, remaining * 0.55)
            return casat_cheddochi.algorithm(prob_info, min(remaining - 0.5, budget))

        sol, res = _try_candidate(
            "team_solver",
            run_team_solver,
            prob_info,
            deadline,
            min_time=6.0,
        )
        remember(sol, res)
    else:
        print("[baseline_hh v001] skip team_solver: no optional exact solver backend")

    # Candidate 3: spend the remaining useful time on the official repaired
    # greedy search, which is currently the robust baseline for this clone.
    sol, res = _try_candidate(
        "greedy_repair_full",
        lambda remaining: baseline_greedy.greedyalgorithm(
            prob_info, max(1.0, remaining - 0.25)
        ),
        prob_info,
        deadline,
        min_time=3.0,
    )
    remember(sol, res)

    if best_solution is not None and best_result is not None:
        print(
            f"[baseline_hh v001] selected feasible obj={best_result['objective']:.2f} "
            f"total_elapsed={time.time() - started:.2f}s"
        )
        return best_solution

    if last_solution is not None:
        print("[baseline_hh v001] no feasible candidate validated; returning last solution")
        return last_solution

    print("[baseline_hh v001] emergency fallback")
    return baseline_greedy.greedyalgorithm(prob_info, min(float(timelimit), 10.0))

