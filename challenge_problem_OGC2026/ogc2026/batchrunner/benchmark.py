#!/usr/bin/env python
"""OGC2026 benchmark runner.

Runs one or more algorithm variants over training instances, validates every
solution with the official checker, appends cumulative CSV rows, and writes an
HTML report for the current run.

Examples:
    python challenge_problem_OGC2026/ogc2026/batchrunner/benchmark.py --limit 3

    python challenge_problem_OGC2026/ogc2026/batchrunner/benchmark.py \
        --algorithm name=hh,version=v001,path=challenge_problem_OGC2026/ogc2026/baseline \
        --timelimit 60
"""

from __future__ import annotations

import argparse
import csv
import html
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


RUNNER_SCRIPT = r"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import time
import traceback

problem_file = pathlib.Path(sys.argv[1]).resolve()
timelimit = float(sys.argv[2])
algorithm_file = pathlib.Path(sys.argv[3]).resolve()
baseline_dir = pathlib.Path(sys.argv[4]).resolve()
alg_tester_dir = pathlib.Path(sys.argv[5]).resolve()
out_file = pathlib.Path(sys.argv[6]).resolve()

search_paths = [
    algorithm_file.parent,
    baseline_dir,
    alg_tester_dir,
    baseline_dir.parent,
]
for path in reversed([str(p) for p in search_paths]):
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    spec = importlib.util.spec_from_file_location("ogc_candidate_algorithm", algorithm_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load algorithm file: {algorithm_file}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)

    with problem_file.open("r", encoding="utf-8") as f:
        prob_info = json.load(f)

    started = time.time()
    solution = mod.algorithm(prob_info, timelimit)
    elapsed = time.time() - started

    with out_file.open("w", encoding="utf-8") as f:
        json.dump(
            {"ok": True, "elapsed": elapsed, "solution": solution},
            f,
            ensure_ascii=False,
        )
except Exception:
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(
            {"ok": False, "traceback": traceback.format_exc()},
            f,
            ensure_ascii=False,
        )
"""


CSV_FIELDS = [
    "timestamp",
    "run_id",
    "algorithm_name",
    "algorithm_version",
    "algorithm_path",
    "instance_name",
    "feasible",
    "stage",
    "objective",
    "score",
    "cost",
    "obj1",
    "obj2",
    "obj3",
    "runtime_sec",
    "runner_elapsed_sec",
    "assigned_blocks",
    "total_blocks",
    "error_message",
    "solution_file",
    "log_file",
    "tester_summary",
]


@dataclass(frozen=True)
class AlgorithmSpec:
    name: str
    version: str
    path: pathlib.Path
    file: pathlib.Path

    @property
    def key(self) -> str:
        return f"{self.name}__{self.version}"


def repo_root_from_here() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "challenge_problem_OGC2026" / "train").exists():
            return parent
    raise RuntimeError("could not locate repository root")


def natural_key(path_or_name) -> list:
    name = pathlib.Path(path_or_name).name
    parts: list[object] = []
    token = ""
    for ch in name:
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


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "unnamed"


def to_repo_path(path: pathlib.Path, repo_root: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path.resolve())


def output_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def load_checker(alg_tester_dir: pathlib.Path):
    utils_path = alg_tester_dir / "utils.py"
    sys.path.insert(0, str(alg_tester_dir))
    spec = importlib.util.spec_from_file_location("ogc2026_checker_utils", utils_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load checker: {utils_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.check_feasibility


def resolve_algorithm_path(path_text: str, repo_root: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    path = pathlib.Path(path_text)
    if not path.is_absolute():
        path = repo_root / path
    path = path.resolve()
    if path.is_dir():
        algorithm_file = path / "myalgorithm.py"
    else:
        algorithm_file = path
        path = algorithm_file.parent
    if not algorithm_file.exists():
        raise SystemExit(f"algorithm file not found: {algorithm_file}")
    return path, algorithm_file


def parse_algorithm_specs(values: list[str] | None, repo_root: pathlib.Path) -> list[AlgorithmSpec]:
    if not values:
        values = [
            "name=baseline_hh,version=v003_active,path=challenge_problem_OGC2026/ogc2026/baseline"
        ]

    specs: list[AlgorithmSpec] = []
    for raw in values:
        data: dict[str, str] = {}
        for part in raw.split(","):
            if "=" not in part:
                raise SystemExit(
                    "--algorithm values must use key=value comma syntax, "
                    "for example name=hh,version=v001,path=..."
                )
            key, value = part.split("=", 1)
            data[key.strip()] = value.strip()
        if "path" not in data:
            raise SystemExit(f"--algorithm missing path: {raw}")
        path, algorithm_file = resolve_algorithm_path(data["path"], repo_root)
        name = data.get("name") or path.name
        version = data.get("version") or algorithm_file.stem
        specs.append(AlgorithmSpec(name=name, version=version, path=path, file=algorithm_file))
    return specs


def collect_problem_paths(args, repo_root: pathlib.Path) -> list[pathlib.Path]:
    if args.problem:
        paths = [pathlib.Path(p) for p in args.problem]
    else:
        paths = list((repo_root).glob(args.problems))
    resolved = []
    for path in paths:
        if not path.is_absolute():
            path = repo_root / path
        path = path.resolve()
        if path.exists() and re.fullmatch(r"prob_\d+\.json", path.name):
            resolved.append(path)
    resolved = sorted(resolved, key=natural_key)
    if args.limit is not None:
        resolved = resolved[: args.limit]
    return resolved


def count_assigned(solution: dict) -> int:
    operations = solution.get("operations", {}) if isinstance(solution, dict) else {}
    return sum(
        1
        for ops in operations.values()
        if isinstance(ops, list)
        for op in ops
        if isinstance(op, dict) and op.get("type") == "ENTRY"
    )


def compact_error(message: str, limit: int = 900) -> str:
    text = " ".join((message or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def tester_summary(result: dict) -> str:
    if result.get("feasible"):
        return (
            f"PASS objective={result.get('objective')} obj1={result.get('obj1')} "
            f"obj2={result.get('obj2')} obj3={result.get('obj3')}"
        )
    violations = result.get("violations") or []
    return f"FAIL stage={result.get('stage')} " + " | ".join(violations[:3])


def run_one(
    *,
    run_id: str,
    timestamp: str,
    algorithm: AlgorithmSpec,
    problem_path: pathlib.Path,
    timelimit: float,
    timeout_grace: float,
    run_dir: pathlib.Path,
    baseline_dir: pathlib.Path,
    alg_tester_dir: pathlib.Path,
    python_bin: str,
    check_feasibility,
    repo_root: pathlib.Path,
) -> dict:
    alg_dir_name = safe_name(algorithm.key)
    instance_name = problem_path.name
    stem = problem_path.stem
    log_path = run_dir / "logs" / alg_dir_name / f"{stem}.log"
    raw_path = run_dir / "raw" / alg_dir_name / f"{stem}.runner.json"
    solution_path = run_dir / "solutions" / alg_dir_name / f"{stem}.solution.json"
    for path in (log_path.parent, raw_path.parent, solution_path.parent):
        path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix="_ogc2026_runner.py", delete=False, encoding="utf-8") as f:
        f.write(RUNNER_SCRIPT)
        runner_path = pathlib.Path(f.name)

    cmd = [
        python_bin,
        "-u",
        str(runner_path),
        str(problem_path),
        str(timelimit),
        str(algorithm.file),
        str(baseline_dir),
        str(alg_tester_dir),
        str(raw_path),
    ]
    timeout = max(timelimit + timeout_grace, timelimit * 1.5)
    started = time.time()

    base_row = {
        "timestamp": timestamp,
        "run_id": run_id,
        "algorithm_name": algorithm.name,
        "algorithm_version": algorithm.version,
        "algorithm_path": to_repo_path(algorithm.file, repo_root),
        "instance_name": instance_name,
        "feasible": False,
        "stage": "",
        "objective": "",
        "score": "",
        "cost": "",
        "obj1": "",
        "obj2": "",
        "obj3": "",
        "runtime_sec": "",
        "runner_elapsed_sec": "",
        "assigned_blocks": "",
        "total_blocks": "",
        "error_message": "",
        "solution_file": "",
        "log_file": to_repo_path(log_path, repo_root),
        "tester_summary": "",
    }

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        wall_time = time.time() - started
        log_path.write_text(proc.stdout or "", encoding="utf-8")
        if proc.returncode != 0:
            return {
                **base_row,
                "stage": "RUNNER_EXIT",
                "runtime_sec": f"{wall_time:.6f}",
                "error_message": f"runner exited with code {proc.returncode}",
                "tester_summary": "runner process failed",
            }
    except subprocess.TimeoutExpired as exc:
        wall_time = time.time() - started
        log_path.write_text(output_text(exc.stdout), encoding="utf-8")
        return {
            **base_row,
            "stage": "TIMEOUT",
            "runtime_sec": f"{wall_time:.6f}",
            "error_message": f"subprocess timeout after {timeout:.1f}s",
            "tester_summary": "timeout",
        }
    finally:
        try:
            runner_path.unlink()
        except OSError:
            pass

    try:
        runner_result = json.loads(raw_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            **base_row,
            "stage": "BAD_RESULT",
            "runtime_sec": f"{wall_time:.6f}",
            "error_message": f"could not read runner result: {exc}",
            "tester_summary": "bad runner json",
        }

    if not runner_result.get("ok"):
        return {
            **base_row,
            "stage": "EXCEPTION",
            "runtime_sec": f"{wall_time:.6f}",
            "runner_elapsed_sec": runner_result.get("elapsed", ""),
            "error_message": compact_error(runner_result.get("traceback", "unknown exception")),
            "tester_summary": "algorithm exception",
        }

    solution = runner_result.get("solution")
    solution_path.write_text(json.dumps(solution, ensure_ascii=False), encoding="utf-8")
    prob_info = json.loads(problem_path.read_text(encoding="utf-8"))
    result = check_feasibility(prob_info, solution)
    assigned = count_assigned(solution)
    total_blocks = len(prob_info.get("blocks", []))
    feasible = bool(result.get("feasible"))
    objective = result.get("objective")
    error = "" if feasible else "; ".join((result.get("violations") or [])[:5])

    return {
        **base_row,
        "feasible": feasible,
        "stage": result.get("stage", ""),
        "objective": objective if objective is not None else "",
        "score": objective if objective is not None else "",
        "cost": objective if objective is not None else "",
        "obj1": result.get("obj1", "") if result.get("obj1") is not None else "",
        "obj2": result.get("obj2", "") if result.get("obj2") is not None else "",
        "obj3": result.get("obj3", "") if result.get("obj3") is not None else "",
        "runtime_sec": f"{wall_time:.6f}",
        "runner_elapsed_sec": runner_result.get("elapsed", ""),
        "assigned_blocks": assigned,
        "total_blocks": total_blocks,
        "error_message": compact_error(error),
        "solution_file": to_repo_path(solution_path, repo_root),
        "tester_summary": compact_error(tester_summary(result), 1200),
    }


def read_csv_rows(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def append_csv(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not exists:
            writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def as_float(value) -> float | None:
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def is_feasible_row(row: dict) -> bool:
    return str(row.get("feasible")).lower() == "true"


def best_by_instance(rows: Iterable[dict]) -> dict[str, dict]:
    best: dict[str, dict] = {}
    for row in rows:
        if not is_feasible_row(row):
            continue
        obj = as_float(row.get("objective"))
        if obj is None:
            continue
        instance = row.get("instance_name", "")
        current = best.get(instance)
        if current is None or obj < as_float(current.get("objective")):
            best[instance] = row
    return best


def summarize_rows(rows: list[dict]) -> dict:
    feasible_rows = [row for row in rows if is_feasible_row(row)]
    objectives = [as_float(row.get("objective")) for row in feasible_rows]
    objectives = [v for v in objectives if v is not None]
    runtimes = [as_float(row.get("runtime_sec")) for row in rows]
    runtimes = [v for v in runtimes if v is not None]
    return {
        "total": len(rows),
        "feasible": len(feasible_rows),
        "failed": len(rows) - len(feasible_rows),
        "objective_sum": sum(objectives) if objectives else None,
        "objective_avg": (sum(objectives) / len(objectives)) if objectives else None,
        "runtime_sum": sum(runtimes) if runtimes else 0.0,
        "runtime_avg": (sum(runtimes) / len(runtimes)) if runtimes else 0.0,
        "runtime_max": max(runtimes) if runtimes else 0.0,
    }


def fmt(value, decimals: int = 0) -> str:
    number = as_float(value)
    if number is None:
        return ""
    if decimals == 0:
        return f"{number:,.0f}"
    return f"{number:,.{decimals}f}"


def html_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def write_html_report(
    *,
    report_path: pathlib.Path,
    run_rows: list[dict],
    previous_rows: list[dict],
    algorithms: list[AlgorithmSpec],
    problems: list[pathlib.Path],
    run_id: str,
    timestamp: str,
    timelimit: float,
    cumulative_csv: pathlib.Path,
    run_csv: pathlib.Path,
    repo_root: pathlib.Path,
) -> None:
    summary = summarize_rows(run_rows)
    current_best = best_by_instance(run_rows)
    previous_best = best_by_instance(previous_rows)

    alg_labels = [f"{spec.name}:{spec.version}" for spec in algorithms]
    rows_by_instance_alg = {
        (row["instance_name"], f"{row['algorithm_name']}:{row['algorithm_version']}"): row
        for row in run_rows
    }

    best_rows = []
    for problem in problems:
        instance = problem.name
        row = current_best.get(instance)
        if not row:
            best_rows.append([html.escape(instance), "<span class='bad'>no feasible</span>", "", "", ""])
            continue
        prev = previous_best.get(instance)
        obj = as_float(row.get("objective"))
        prev_obj = as_float(prev.get("objective")) if prev else None
        if prev_obj is None or obj is None:
            delta = "new"
            cls = "neutral"
        else:
            diff = obj - prev_obj
            delta = f"{diff:,.0f}"
            cls = "good" if diff < 0 else "bad" if diff > 0 else "neutral"
        best_rows.append(
            [
                html.escape(instance),
                html.escape(f"{row['algorithm_name']}:{row['algorithm_version']}"),
                fmt(row.get("objective")),
                fmt(row.get("runtime_sec"), 2) + "s",
                f"<span class='{cls}'>{html.escape(delta)}</span>",
            ]
        )

    infeasible_rows = [
        [
            html.escape(row["instance_name"]),
            html.escape(f"{row['algorithm_name']}:{row['algorithm_version']}"),
            html.escape(str(row.get("stage", ""))),
            html.escape(row.get("error_message", "")),
        ]
        for row in run_rows
        if not is_feasible_row(row)
    ]

    runtime_sorted = sorted(run_rows, key=lambda r: as_float(r.get("runtime_sec")) or 0.0)
    fastest = runtime_sorted[:10]
    slowest = list(reversed(runtime_sorted[-10:]))

    def runtime_row(row: dict) -> list[str]:
        return [
            html.escape(row["instance_name"]),
            html.escape(f"{row['algorithm_name']}:{row['algorithm_version']}"),
            fmt(row.get("runtime_sec"), 2) + "s",
            "PASS" if is_feasible_row(row) else html.escape(str(row.get("stage", ""))),
            fmt(row.get("objective")),
        ]

    comparison_rows = []
    for problem in problems:
        line = [html.escape(problem.name)]
        best_obj = as_float(current_best.get(problem.name, {}).get("objective"))
        for label in alg_labels:
            row = rows_by_instance_alg.get((problem.name, label))
            if not row:
                line.append("")
                continue
            if is_feasible_row(row):
                obj = as_float(row.get("objective"))
                cls = "best" if best_obj is not None and obj == best_obj else ""
                line.append(f"<span class='{cls}'>{fmt(obj)}</span>")
            else:
                line.append(f"<span class='bad'>FAIL {html.escape(str(row.get('stage', '')))}</span>")
        comparison_rows.append(line)

    style = """
    body { font-family: Segoe UI, Arial, sans-serif; margin: 24px; color: #1f2933; }
    h1 { font-size: 24px; margin-bottom: 4px; }
    h2 { font-size: 18px; margin-top: 28px; border-bottom: 1px solid #d8dee9; padding-bottom: 4px; }
    .meta { color: #52606d; margin-bottom: 18px; }
    .cards { display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0; }
    .card { border: 1px solid #d8dee9; border-radius: 6px; padding: 10px 12px; min-width: 150px; }
    .card .label { color: #52606d; font-size: 12px; }
    .card .value { font-size: 20px; font-weight: 700; margin-top: 4px; }
    table { border-collapse: collapse; width: 100%; margin-top: 10px; font-size: 13px; }
    th, td { border: 1px solid #d8dee9; padding: 6px 8px; text-align: right; vertical-align: top; }
    th:first-child, td:first-child { text-align: left; }
    th { background: #243447; color: #ffffff; position: sticky; top: 0; }
    tr:nth-child(even) td { background: #f7f9fb; }
    .good { color: #0f7b35; font-weight: 700; }
    .bad { color: #b42318; font-weight: 700; }
    .neutral { color: #52606d; }
    .best { color: #0f7b35; font-weight: 700; }
    code { background: #eef2f7; padding: 2px 4px; border-radius: 4px; }
    """

    infeasible_html = (
        html_table(["Instance", "Algorithm", "Stage", "Error"], infeasible_rows)
        if infeasible_rows
        else "<p class='good'>No infeasible rows in this run.</p>"
    )

    content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>OGC2026 Benchmark {html.escape(run_id)}</title>
<style>{style}</style>
</head>
<body>
<h1>OGC2026 Benchmark Report</h1>
<div class="meta">
  run_id=<code>{html.escape(run_id)}</code> |
  timestamp=<code>{html.escape(timestamp)}</code> |
  timelimit=<code>{timelimit}s</code><br>
  run_csv=<code>{html.escape(to_repo_path(run_csv, repo_root))}</code> |
  cumulative_csv=<code>{html.escape(to_repo_path(cumulative_csv, repo_root))}</code>
</div>
<div class="cards">
  <div class="card"><div class="label">Rows</div><div class="value">{summary['total']}</div></div>
  <div class="card"><div class="label">Feasible</div><div class="value">{summary['feasible']}/{summary['total']}</div></div>
  <div class="card"><div class="label">Objective Sum</div><div class="value">{fmt(summary['objective_sum'])}</div></div>
  <div class="card"><div class="label">Avg Runtime</div><div class="value">{summary['runtime_avg']:.2f}s</div></div>
  <div class="card"><div class="label">Max Runtime</div><div class="value">{summary['runtime_max']:.2f}s</div></div>
</div>
<h2>Instance Best</h2>
{html_table(["Instance", "Best Algorithm", "Objective", "Runtime", "Delta vs Previous Best"], best_rows)}
<h2>Score Comparison</h2>
{html_table(["Instance", *alg_labels], comparison_rows)}
<h2>Infeasible Instances</h2>
{infeasible_html}
<h2>Slowest Rows</h2>
{html_table(["Instance", "Algorithm", "Runtime", "Status", "Objective"], [runtime_row(r) for r in slowest])}
<h2>Fastest Rows</h2>
{html_table(["Instance", "Algorithm", "Runtime", "Status", "Objective"], [runtime_row(r) for r in fastest])}
</body>
</html>
"""
    report_path.write_text(content, encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Run OGC2026 benchmark loops.")
    parser.add_argument(
        "--algorithm",
        action="append",
        help=(
            "Algorithm spec: name=NAME,version=VERSION,path=PATH. "
            "PATH may be a folder containing myalgorithm.py or a .py file."
        ),
    )
    parser.add_argument(
        "--problems",
        default="challenge_problem_OGC2026/train/prob_*.json",
        help="Problem glob relative to repo root.",
    )
    parser.add_argument("--problem", action="append", help="Specific problem path; repeatable.")
    parser.add_argument("--limit", type=int, help="Only run the first N naturally sorted instances.")
    parser.add_argument("--timelimit", type=float, default=60.0)
    parser.add_argument("--timeout-grace", type=float, default=20.0)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--out-dir", default=None, help="Defaults to reports/ogc2026_benchmark/<run_id>.")
    parser.add_argument(
        "--cumulative-csv",
        default="reports/ogc2026_benchmark/benchmark_results.csv",
        help="Append-only benchmark CSV path.",
    )
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_here()
    timestamp = datetime.now().isoformat(timespec="seconds")
    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")

    run_dir = pathlib.Path(args.out_dir) if args.out_dir else pathlib.Path("reports") / "ogc2026_benchmark" / run_id
    if not run_dir.is_absolute():
        run_dir = repo_root / run_dir
    run_dir = run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    cumulative_csv = pathlib.Path(args.cumulative_csv)
    if not cumulative_csv.is_absolute():
        cumulative_csv = repo_root / cumulative_csv
    cumulative_csv = cumulative_csv.resolve()

    baseline_dir = repo_root / "challenge_problem_OGC2026" / "ogc2026" / "baseline"
    alg_tester_dir = repo_root / "challenge_problem_OGC2026" / "ogc2026" / "alg_tester"
    check_feasibility = load_checker(alg_tester_dir)
    algorithms = parse_algorithm_specs(args.algorithm, repo_root)
    problems = collect_problem_paths(args, repo_root)

    if not problems:
        raise SystemExit("No problem files matched.")

    print(f"[benchmark] repo        = {repo_root}")
    print(f"[benchmark] run_id      = {run_id}")
    print(f"[benchmark] algorithms  = {len(algorithms)}")
    for spec in algorithms:
        print(f"[benchmark]   {spec.name}:{spec.version} -> {spec.file}")
    print(f"[benchmark] problems    = {len(problems)}")
    print(f"[benchmark] timelimit   = {args.timelimit}s")
    print(f"[benchmark] out_dir     = {run_dir}")
    print(f"[benchmark] cumulative = {cumulative_csv}")

    if args.dry_run:
        for problem in problems:
            print(problem)
        return 0

    previous_rows = read_csv_rows(cumulative_csv)
    run_rows: list[dict] = []

    total_jobs = len(algorithms) * len(problems)
    job_idx = 0
    for spec in algorithms:
        for problem in problems:
            job_idx += 1
            print(f"[benchmark] ({job_idx}/{total_jobs}) {spec.name}:{spec.version} {problem.name}")
            row = run_one(
                run_id=run_id,
                timestamp=timestamp,
                algorithm=spec,
                problem_path=problem,
                timelimit=args.timelimit,
                timeout_grace=args.timeout_grace,
                run_dir=run_dir,
                baseline_dir=baseline_dir,
                alg_tester_dir=alg_tester_dir,
                python_bin=args.python,
                check_feasibility=check_feasibility,
                repo_root=repo_root,
            )
            run_rows.append(row)
            status = "PASS" if is_feasible_row(row) else f"FAIL stage={row.get('stage')}"
            obj = f" obj={fmt(row.get('objective'))}" if row.get("objective") != "" else ""
            print(f"[benchmark]   {status}{obj} runtime={fmt(row.get('runtime_sec'), 2)}s")
            if args.fail_fast and not is_feasible_row(row):
                break

    run_csv = run_dir / "results.csv"
    summary_json = run_dir / "summary.json"
    report_path = run_dir / "report.html"
    write_csv(run_csv, run_rows)
    append_csv(cumulative_csv, run_rows)
    summary = summarize_rows(run_rows)
    summary_json.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "timestamp": timestamp,
                "summary": summary,
                "algorithms": [
                    {
                        "name": spec.name,
                        "version": spec.version,
                        "path": to_repo_path(spec.file, repo_root),
                    }
                    for spec in algorithms
                ],
                "problems": [to_repo_path(p, repo_root) for p in problems],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_html_report(
        report_path=report_path,
        run_rows=run_rows,
        previous_rows=previous_rows,
        algorithms=algorithms,
        problems=problems,
        run_id=run_id,
        timestamp=timestamp,
        timelimit=args.timelimit,
        cumulative_csv=cumulative_csv,
        run_csv=run_csv,
        repo_root=repo_root,
    )

    print("[benchmark] summary")
    print(textwrap.indent(json.dumps(summary, ensure_ascii=False, indent=2), "  "))
    print(f"[benchmark] wrote {run_csv}")
    print(f"[benchmark] wrote {summary_json}")
    print(f"[benchmark] wrote {report_path}")
    print(f"[benchmark] appended {cumulative_csv}")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
