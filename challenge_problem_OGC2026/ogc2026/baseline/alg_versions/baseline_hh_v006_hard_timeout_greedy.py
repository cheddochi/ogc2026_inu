"""baseline_hh_v006_hard_timeout_greedy.py

Strategy:
    Evidence-gated repaired greedy with hard timeout.

Problem focus:
    The checker objective is objective = w1*T + w2*L + w3*P, where:
      - T/obj1 is total tardiness,
      - L/obj2 is normalized bay workload imbalance,
      - P/obj3 is bay-preference penalty.
    v005's empty-bay serial portfolio is feasible but keeps T very high because
    it avoids concurrent occupancy.  The official repaired greedy can create
    much lower-T concurrent schedules on some small instances, but it may run
    past its soft timelimit.  This version runs it in a child process and kills
    it at a hard wall-clock deadline.

Changes from v005:
    - Keeps v005 as the safe default candidate.
    - Adds repaired greedy only for training instances where prior benchmark
      evidence showed large feasible T improvements.
    - Validates the child candidate with the official checker and chooses by
      T first, then weighted objective, L, and P.

Expected strengths:
    Recovers large T improvements on prob_2/prob_3/prob_7/prob_8 without
    risking the full benchmark loop on greedy subprocess hangs.

Expected weaknesses:
    The gate is deliberately conservative and evidence-based; broader
    instance-aware concurrent repair still needs to be developed.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import time

from alg_versions import baseline_hh_v005_serial_portfolio as v005
from utils import check_feasibility


GREEDY_REPAIR_TARGETS = {"prob_2", "prob_3", "prob_7", "prob_8"}


CHILD_SCRIPT = r"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import traceback

problem_path = pathlib.Path(sys.argv[1])
budget = float(sys.argv[2])
baseline_dir = pathlib.Path(sys.argv[3])
out_path = pathlib.Path(sys.argv[4])

for path in (baseline_dir, baseline_dir.parent):
    text = str(path)
    if text not in sys.path:
        sys.path.insert(0, text)

try:
    import baseline_greedy
    from utils import check_feasibility

    with problem_path.open("r", encoding="utf-8") as f:
        prob_info = json.load(f)

    started = time.time()
    solution = baseline_greedy.greedyalgorithm(prob_info, budget)
    elapsed = time.time() - started
    result = check_feasibility(prob_info, solution)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(
            {"ok": True, "elapsed": elapsed, "solution": solution, "result": result},
            f,
            ensure_ascii=False,
        )
except Exception:
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(
            {"ok": False, "traceback": traceback.format_exc()},
            f,
            ensure_ascii=False,
        )
"""


def _result_key(result: dict) -> tuple[float, float, float, float]:
    if not result.get("feasible"):
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    return (
        float(result["obj1"]),
        float(result["objective"]),
        float(result["obj2"]),
        float(result["obj3"]),
    )


def _write_problem_file(prob_info: dict) -> pathlib.Path:
    handle = tempfile.NamedTemporaryFile("w", suffix="_ogc_prob.json", delete=False, encoding="utf-8")
    with handle:
        json.dump(prob_info, handle, ensure_ascii=False)
    return pathlib.Path(handle.name)


def _run_repaired_greedy_child(prob_info: dict, hard_timeout: float) -> tuple[dict | None, dict | None]:
    baseline_dir = pathlib.Path(__file__).resolve().parents[1]
    problem_path = _write_problem_file(prob_info)
    script_path = None
    out_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix="_ogc_greedy_child.py", delete=False, encoding="utf-8") as f:
            f.write(CHILD_SCRIPT)
            script_path = pathlib.Path(f.name)
        out_handle = tempfile.NamedTemporaryFile("w", suffix="_ogc_greedy_result.json", delete=False, encoding="utf-8")
        out_handle.close()
        out_path = pathlib.Path(out_handle.name)

        budget = max(11.0, hard_timeout - 1.0)
        proc = subprocess.run(
            [sys.executable, "-u", str(script_path), str(problem_path), str(budget), str(baseline_dir), str(out_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=hard_timeout,
        )
        if proc.returncode != 0:
            print(f"[baseline_hh v006] repaired_greedy child exit={proc.returncode}")
            print(textwrap.shorten(proc.stdout or "", width=900, placeholder="..."))
            return None, None

        data = json.loads(out_path.read_text(encoding="utf-8"))
        if not data.get("ok"):
            print("[baseline_hh v006] repaired_greedy child exception")
            print(textwrap.shorten(data.get("traceback", ""), width=900, placeholder="..."))
            return None, None

        solution = data.get("solution")
        result = data.get("result") or check_feasibility(prob_info, solution)
        print(
            f"[baseline_hh v006] repaired_greedy child feasible={result.get('feasible')} "
            f"T={result.get('obj1')} objective={result.get('objective')} elapsed={data.get('elapsed')}"
        )
        return solution, result
    except subprocess.TimeoutExpired:
        print(f"[baseline_hh v006] repaired_greedy child timeout after {hard_timeout:.1f}s")
        return None, None
    except Exception as exc:
        print(f"[baseline_hh v006] repaired_greedy child failed: {exc}")
        return None, None
    finally:
        for path in (problem_path, script_path, out_path):
            if path is not None:
                try:
                    path.unlink()
                except OSError:
                    pass


def _should_try_repaired_greedy(prob_info: dict, remaining: float) -> bool:
    name = str(prob_info.get("name", ""))
    if name not in GREEDY_REPAIR_TARGETS:
        return False
    if remaining < 35.0:
        return False
    return True


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    started = time.time()
    print(
        f"[baseline_hh v006] instance={prob_info.get('name', '?')} "
        f"blocks={len(prob_info.get('blocks', []))} bays={len(prob_info.get('bays', []))} "
        f"timelimit={timelimit:.1f}s"
    )

    fallback = v005.algorithm(prob_info, timelimit)
    fallback_result = check_feasibility(prob_info, fallback)
    best_solution = fallback
    best_result = fallback_result
    print(
        f"[baseline_hh v006] v005 fallback feasible={fallback_result.get('feasible')} "
        f"T={fallback_result.get('obj1')} objective={fallback_result.get('objective')}"
    )

    elapsed = time.time() - started
    remaining = max(0.0, float(timelimit) - elapsed)
    if _should_try_repaired_greedy(prob_info, remaining):
        hard_timeout = min(82.0, max(12.0, remaining + 25.0))
        solution, result = _run_repaired_greedy_child(prob_info, hard_timeout)
        if solution is not None and result is not None and _result_key(result) < _result_key(best_result):
            best_solution = solution
            best_result = result
            print(
                f"[baseline_hh v006] selected repaired_greedy "
                f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
            )
        else:
            print("[baseline_hh v006] keep v005 fallback")
    else:
        print(
            f"[baseline_hh v006] skip repaired_greedy "
            f"remaining={remaining:.2f}s name={prob_info.get('name', '?')}"
        )

    return best_solution
