#!/usr/bin/env python3
"""Batch runner for OGC2026 algorithms using the official alg_tester checker.

The GUI tester launches myalgorithm.py in a subprocess and then validates the
returned solution with alg_tester/utils.py.  This script mirrors that flow for
repeatable CLI testing over challenge_problem_OGC2026/train.
"""

import argparse
import csv
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import time
from datetime import datetime


RUNNER_SCRIPT = r"""
import importlib.util
import json
import pathlib
import sys
import traceback

prob_info_file = sys.argv[1]
timelimit = float(sys.argv[2])
alg_folder = pathlib.Path(sys.argv[3]).resolve()
out_file = pathlib.Path(sys.argv[4]).resolve()

folder = str(alg_folder)
if folder not in sys.path:
    sys.path.insert(0, folder)

try:
    spec = importlib.util.spec_from_file_location(
        "myalgorithm", alg_folder / "myalgorithm.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with open(prob_info_file, "r", encoding="utf-8") as f:
        prob_info = json.load(f)

    started = time_time = __import__("time").time()
    solution = mod.algorithm(prob_info, timelimit)
    elapsed = __import__("time").time() - started

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"ok": True, "elapsed": elapsed, "solution": solution}, f)
except Exception:
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"ok": False, "traceback": traceback.format_exc()}, f)
"""


def repo_root_from_here() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def natural_key(path: pathlib.Path):
    parts = []
    token = ""
    for ch in path.name:
        if ch.isdigit():
            token += ch
        else:
            if token:
                parts.append(int(token))
                token = ""
            parts.append(ch)
    if token:
        parts.append(int(token))
    return parts


def load_checker(alg_tester_dir: pathlib.Path):
    utils_path = alg_tester_dir / "utils.py"
    sys.path.insert(0, str(alg_tester_dir))
    spec = importlib.util.spec_from_file_location("ogc_alg_tester_utils", utils_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.check_feasibility


def collect_problem_paths(args, repo_root: pathlib.Path):
    if args.problem:
        paths = [pathlib.Path(p) for p in args.problem]
    else:
        pattern = args.problems
        paths = [pathlib.Path(p) for p in pathlib.Path().glob(pattern)]
    paths = [(p if p.is_absolute() else repo_root / p).resolve() for p in paths]
    paths = sorted(paths, key=natural_key)
    if args.limit is not None:
        paths = paths[: args.limit]
    return paths


def count_assigned(solution: dict) -> int:
    return sum(
        1
        for ops in solution.get("operations", {}).values()
        for op in ops
        if isinstance(op, dict) and op.get("type") == "ENTRY"
    )


def run_one(problem_path, alg_folder, timelimit, timeout_grace, out_dir, python_bin):
    stem = problem_path.stem
    stdout_path = out_dir / "logs" / f"{stem}.log"
    result_path = out_dir / "raw" / f"{stem}.runner.json"
    solution_path = out_dir / "solutions" / f"{stem}.solution.json"
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    solution_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix="_ogc_runner.py", delete=False) as f:
        f.write(RUNNER_SCRIPT)
        runner_path = pathlib.Path(f.name)

    cmd = [
        python_bin,
        "-u",
        str(runner_path),
        str(problem_path),
        str(timelimit),
        str(alg_folder),
        str(result_path),
    ]
    timeout = max(timelimit + timeout_grace, timelimit * 1.5)
    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        stdout_path.write_text(proc.stdout or "", encoding="utf-8")
        wall_time = time.time() - started
        return_code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout_path.write_text(exc.stdout or "", encoding="utf-8")
        wall_time = time.time() - started
        return {
            "problem": problem_path.name,
            "ok": False,
            "feasible": False,
            "stage": "TIMEOUT",
            "objective": None,
            "obj1": None,
            "obj2": None,
            "obj3": None,
            "assigned": 0,
            "blocks": None,
            "runner_elapsed": None,
            "wall_time": wall_time,
            "error": f"subprocess timeout after {timeout:.1f}s",
            "log": str(stdout_path),
        }
    finally:
        try:
            runner_path.unlink()
        except OSError:
            pass

    if return_code != 0:
        return {
            "problem": problem_path.name,
            "ok": False,
            "feasible": False,
            "stage": "RUNNER_EXIT",
            "objective": None,
            "obj1": None,
            "obj2": None,
            "obj3": None,
            "assigned": 0,
            "blocks": None,
            "runner_elapsed": None,
            "wall_time": wall_time,
            "error": f"runner exited with code {return_code}",
            "log": str(stdout_path),
        }

    try:
        runner_result = json.loads(result_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "problem": problem_path.name,
            "ok": False,
            "feasible": False,
            "stage": "BAD_RESULT",
            "objective": None,
            "obj1": None,
            "obj2": None,
            "obj3": None,
            "assigned": 0,
            "blocks": None,
            "runner_elapsed": None,
            "wall_time": wall_time,
            "error": f"could not read runner result: {exc}",
            "log": str(stdout_path),
        }

    if not runner_result.get("ok"):
        return {
            "problem": problem_path.name,
            "ok": False,
            "feasible": False,
            "stage": "EXCEPTION",
            "objective": None,
            "obj1": None,
            "obj2": None,
            "obj3": None,
            "assigned": 0,
            "blocks": None,
            "runner_elapsed": runner_result.get("elapsed"),
            "wall_time": wall_time,
            "error": runner_result.get("traceback", "unknown exception"),
            "log": str(stdout_path),
        }

    solution = runner_result["solution"]
    solution_path.write_text(json.dumps(solution, ensure_ascii=False), encoding="utf-8")
    return {
        "problem": problem_path.name,
        "ok": True,
        "solution": solution,
        "runner_elapsed": runner_result.get("elapsed"),
        "wall_time": wall_time,
        "log": str(stdout_path),
        "solution_file": str(solution_path),
    }


def write_outputs(rows, summary, out_dir):
    json_path = out_dir / "summary.json"
    csv_path = out_dir / "results.csv"
    json_path.write_text(
        json.dumps({"summary": summary, "results": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    fieldnames = [
        "problem",
        "ok",
        "feasible",
        "stage",
        "objective",
        "obj1",
        "obj2",
        "obj3",
        "assigned",
        "blocks",
        "runner_elapsed",
        "wall_time",
        "error",
        "log",
        "solution_file",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})
    return json_path, csv_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run OGC2026 algorithms over train JSON files with alg_tester validation."
    )
    parser.add_argument(
        "--alg-folder",
        default="challenge_problem_OGC2026/ogc2026/baseline",
        help="Folder containing myalgorithm.py.",
    )
    parser.add_argument(
        "--problems",
        default="challenge_problem_OGC2026/train/prob_*.json",
        help="Glob of problem JSON files, relative to repo root.",
    )
    parser.add_argument(
        "--problem",
        action="append",
        help="Specific problem JSON file. May be passed more than once.",
    )
    parser.add_argument("--limit", type=int, help="Run only the first N problems.")
    parser.add_argument("--timelimit", type=float, default=30.0)
    parser.add_argument("--timeout-grace", type=float, default=15.0)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Defaults to reports/ogc_batch/<timestamp>.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    repo_root = repo_root_from_here()
    alg_folder = pathlib.Path(args.alg_folder)
    if not alg_folder.is_absolute():
        alg_folder = repo_root / alg_folder
    alg_folder = alg_folder.resolve()

    alg_tester_dir = repo_root / "challenge_problem_OGC2026" / "ogc2026" / "alg_tester"
    check_feasibility = load_checker(alg_tester_dir)
    problems = collect_problem_paths(args, repo_root)

    if not (alg_folder / "myalgorithm.py").exists():
        raise SystemExit(f"Algorithm folder does not contain myalgorithm.py: {alg_folder}")
    if not problems:
        raise SystemExit("No problem files matched.")

    if args.out_dir:
        out_dir = pathlib.Path(args.out_dir)
        if not out_dir.is_absolute():
            out_dir = repo_root / out_dir
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = repo_root / "reports" / "ogc_batch" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[ogc_batch] repo       = {repo_root}")
    print(f"[ogc_batch] alg_folder = {alg_folder}")
    print(f"[ogc_batch] problems   = {len(problems)}")
    print(f"[ogc_batch] timelimit  = {args.timelimit}s")
    print(f"[ogc_batch] out_dir    = {out_dir}")

    if args.dry_run:
        for problem in problems:
            print(problem)
        return 0

    rows = []
    started_all = time.time()
    for idx, problem in enumerate(problems, start=1):
        print(f"[ogc_batch] ({idx}/{len(problems)}) {problem.name}")
        row = run_one(
            problem,
            alg_folder,
            args.timelimit,
            args.timeout_grace,
            out_dir,
            args.python,
        )

        if row.get("ok"):
            prob_info = json.loads(problem.read_text(encoding="utf-8"))
            result = check_feasibility(prob_info, row.pop("solution"))
            n_blocks = len(prob_info.get("blocks", []))
            row.update(
                {
                    "feasible": result["feasible"],
                    "stage": result["stage"],
                    "objective": result["objective"],
                    "obj1": result["obj1"],
                    "obj2": result["obj2"],
                    "obj3": result["obj3"],
                    "assigned": count_assigned(
                        json.loads(
                            pathlib.Path(row["solution_file"]).read_text(encoding="utf-8")
                        )
                    ),
                    "blocks": n_blocks,
                    "error": "" if result["feasible"] else "; ".join(result["violations"][:3]),
                }
            )
        rows.append(row)

        status = "PASS" if row.get("feasible") else f"FAIL stage={row.get('stage')}"
        obj = row.get("objective")
        obj_text = f" obj={obj:.2f}" if isinstance(obj, (int, float)) else ""
        print(f"[ogc_batch]   {status}{obj_text} wall={row.get('wall_time', 0):.2f}s")

        if args.fail_fast and not row.get("feasible"):
            break

    passed = sum(1 for row in rows if row.get("feasible"))
    failed = len(rows) - passed
    objectives = [row["objective"] for row in rows if isinstance(row.get("objective"), (int, float))]
    summary = {
        "passed": passed,
        "failed": failed,
        "total": len(rows),
        "timelimit": args.timelimit,
        "elapsed": time.time() - started_all,
        "objective_sum": sum(objectives) if objectives else None,
        "objective_avg": (sum(objectives) / len(objectives)) if objectives else None,
        "alg_folder": str(alg_folder),
    }
    json_path, csv_path = write_outputs(rows, summary, out_dir)

    print("[ogc_batch] summary")
    print(textwrap.indent(json.dumps(summary, ensure_ascii=False, indent=2), "  "))
    print(f"[ogc_batch] wrote {json_path}")
    print(f"[ogc_batch] wrote {csv_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
