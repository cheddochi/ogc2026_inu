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
import hashlib
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
    "algorithm_sha256",
    "checker_sha256",
    "git_branch",
    "git_head",
    "git_dirty",
    "instance_name",
    "requested_timelimit",
    "official_limit",
    "timeout_grace",
    "watchdog_timeout_sec",
    "checker_feasible",
    "timed_out",
    "valid_under_time_limit",
    "accepted_for_score",
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
    "total_bays",
    "error_message",
    "solution_file",
    "log_file",
    "tester_summary",
    "benchmark_command",
]

COMPACT_CSV_FIELDS = [
    "instance",
    "blocks",
    "bays",
    "objective",
    "T",
    "L",
    "P",
    "runtime_sec",
    "checker_feasible",
    "timed_out",
    "valid_under_time_limit",
    "accepted_for_score",
    "error_message",
    "algorithm_version",
    "report_path",
    "solution_file",
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
        if (parent / "train").exists() and (parent / "ogc2026").exists():
            return parent
        if (parent / "challenge_problem_OGC2026" / "train").exists():
            return parent / "challenge_problem_OGC2026"
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


def resolve_repo_relative_path(path_text: str, repo_root: pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(path_text)
    if path.is_absolute():
        return path
    candidate = repo_root / path
    if candidate.exists():
        return candidate
    parts = path.parts
    if parts and parts[0] == "challenge_problem_OGC2026":
        stripped = repo_root.joinpath(*parts[1:])
        if stripped.exists():
            return stripped
    return candidate


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_output(repo_root: pathlib.Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    return (result.stdout or "").strip()


def git_snapshot(repo_root: pathlib.Path) -> dict:
    status = git_output(repo_root, ["status", "--short"])
    return {
        "branch": git_output(repo_root, ["branch", "--show-current"]) or "unknown",
        "head": git_output(repo_root, ["rev-parse", "--short", "HEAD"]) or "unknown",
        "dirty": bool(status),
        "status_short": status.splitlines(),
    }


def algorithm_source_manifest(spec: AlgorithmSpec, repo_root: pathlib.Path) -> list[dict]:
    files: set[pathlib.Path] = {spec.file}
    if spec.path.is_dir():
        files.update(spec.path.glob("*.py"))
        alg_versions = spec.path / "alg_versions"
        if alg_versions.exists():
            files.update(alg_versions.glob("*.py"))
            readme = alg_versions / "README.md"
            if readme.exists():
                files.add(readme)
    return [
        {
            "path": to_repo_path(path, repo_root),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(files, key=lambda p: str(p).lower())
        if path.exists()
    ]


def output_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def bool_text(value: bool) -> str:
    return "true" if bool(value) else "false"


def parse_float(value) -> float | None:
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def acceptance_fields(
    *,
    checker_feasible: bool,
    runtime_sec,
    runner_elapsed_sec,
    official_limit: float,
    timeout_expired: bool,
    error_message: str,
) -> dict:
    runtime_value = parse_float(runtime_sec)
    runner_elapsed_value = parse_float(runner_elapsed_sec)
    over_runtime = runtime_value is not None and runtime_value > official_limit + 1e-9
    over_runner_elapsed = (
        runner_elapsed_value is not None
        and runner_elapsed_value > official_limit + 1e-9
    )
    timed_out = bool(timeout_expired or over_runtime or over_runner_elapsed)
    valid_under_time_limit = (
        runtime_value is not None
        and runtime_value <= official_limit + 1e-9
        and not timed_out
    )
    accepted = (
        checker_feasible
        and valid_under_time_limit
        and not timed_out
        and not (error_message or "").strip()
    )
    return {
        "checker_feasible": bool_text(checker_feasible),
        "timed_out": bool_text(timed_out),
        "valid_under_time_limit": bool_text(valid_under_time_limit),
        "accepted_for_score": bool_text(accepted),
        # Backward-compatible alias. From reboot onward this means accepted,
        # not merely checker PASS.
        "feasible": bool_text(accepted),
    }


def runtime_limit_error(runtime_sec, runner_elapsed_sec, official_limit: float) -> str:
    runtime_value = parse_float(runtime_sec)
    runner_elapsed_value = parse_float(runner_elapsed_sec)
    values = [v for v in (runtime_value, runner_elapsed_value) if v is not None]
    if values and max(values) > official_limit + 1e-9:
        return f"runtime exceeded official_limit {official_limit:.6f}s"
    return ""


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
    path = resolve_repo_relative_path(path_text, repo_root).resolve()
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
            "name=baseline_hh,version=v007_active,path=ogc2026/baseline"
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
        paths = [resolve_repo_relative_path(p, repo_root) for p in args.problem]
    else:
        patterns = [args.problems]
        raw_parts = pathlib.Path(args.problems).parts
        if raw_parts and raw_parts[0] == "challenge_problem_OGC2026":
            patterns.append(str(pathlib.Path(*raw_parts[1:])))
        paths = []
        for pattern in patterns:
            paths.extend(repo_root.glob(pattern))
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
    checker_sha256: str,
    git_meta: dict,
    benchmark_command: str,
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
    algorithm_sha256 = sha256_file(algorithm.file)
    prob_info = json.loads(problem_path.read_text(encoding="utf-8"))
    total_blocks = len(prob_info.get("blocks", []))
    total_bays = len(prob_info.get("bays", []))
    started = time.time()

    base_row = {
        "timestamp": timestamp,
        "run_id": run_id,
        "algorithm_name": algorithm.name,
        "algorithm_version": algorithm.version,
        "algorithm_path": to_repo_path(algorithm.file, repo_root),
        "algorithm_sha256": algorithm_sha256,
        "checker_sha256": checker_sha256,
        "git_branch": git_meta.get("branch", ""),
        "git_head": git_meta.get("head", ""),
        "git_dirty": git_meta.get("dirty", ""),
        "instance_name": instance_name,
        "requested_timelimit": f"{timelimit:.6f}",
        "official_limit": f"{timelimit:.6f}",
        "timeout_grace": f"{timeout_grace:.6f}",
        "watchdog_timeout_sec": f"{timeout:.6f}",
        "checker_feasible": "false",
        "timed_out": "false",
        "valid_under_time_limit": "false",
        "accepted_for_score": "false",
        "feasible": "false",
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
        "total_blocks": total_blocks,
        "total_bays": total_bays,
        "error_message": "",
        "solution_file": "",
        "log_file": to_repo_path(log_path, repo_root),
        "tester_summary": "",
        "benchmark_command": benchmark_command,
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
            error_message = f"runner exited with code {proc.returncode}"
            return {
                **base_row,
                "stage": "RUNNER_EXIT",
                "runtime_sec": f"{wall_time:.6f}",
                "error_message": error_message,
                "tester_summary": "runner process failed",
                **acceptance_fields(
                    checker_feasible=False,
                    runtime_sec=f"{wall_time:.6f}",
                    runner_elapsed_sec="",
                    official_limit=timelimit,
                    timeout_expired=False,
                    error_message=error_message,
                ),
            }
    except subprocess.TimeoutExpired as exc:
        wall_time = time.time() - started
        log_path.write_text(output_text(exc.stdout), encoding="utf-8")
        error_message = f"subprocess timeout after {timeout:.1f}s"
        return {
            **base_row,
            "stage": "TIMEOUT",
            "runtime_sec": f"{wall_time:.6f}",
            "error_message": error_message,
            "tester_summary": "timeout",
            **acceptance_fields(
                checker_feasible=False,
                runtime_sec=f"{wall_time:.6f}",
                runner_elapsed_sec="",
                official_limit=timelimit,
                timeout_expired=True,
                error_message=error_message,
            ),
        }
    finally:
        try:
            runner_path.unlink()
        except OSError:
            pass

    try:
        runner_result = json.loads(raw_path.read_text(encoding="utf-8"))
    except Exception as exc:
        error_message = f"could not read runner result: {exc}"
        return {
            **base_row,
            "stage": "BAD_RESULT",
            "runtime_sec": f"{wall_time:.6f}",
            "error_message": error_message,
            "tester_summary": "bad runner json",
            **acceptance_fields(
                checker_feasible=False,
                runtime_sec=f"{wall_time:.6f}",
                runner_elapsed_sec="",
                official_limit=timelimit,
                timeout_expired=False,
                error_message=error_message,
            ),
        }

    if not runner_result.get("ok"):
        error_message = compact_error(runner_result.get("traceback", "unknown exception"))
        runner_elapsed = runner_result.get("elapsed", "")
        return {
            **base_row,
            "stage": "EXCEPTION",
            "runtime_sec": f"{wall_time:.6f}",
            "runner_elapsed_sec": runner_elapsed,
            "error_message": error_message,
            "tester_summary": "algorithm exception",
            **acceptance_fields(
                checker_feasible=False,
                runtime_sec=f"{wall_time:.6f}",
                runner_elapsed_sec=runner_elapsed,
                official_limit=timelimit,
                timeout_expired=False,
                error_message=error_message,
            ),
        }

    solution = runner_result.get("solution")
    solution_path.write_text(json.dumps(solution, ensure_ascii=False), encoding="utf-8")
    result = check_feasibility(prob_info, solution)
    assigned = count_assigned(solution)
    runner_elapsed = runner_result.get("elapsed", "")
    checker_feasible = bool(result.get("feasible"))
    objective = result.get("objective")
    error_parts = []
    if not checker_feasible:
        error_parts.append("; ".join((result.get("violations") or [])[:5]))
    limit_error = runtime_limit_error(f"{wall_time:.6f}", runner_elapsed, timelimit)
    if limit_error:
        error_parts.append(limit_error)
    error = compact_error("; ".join(part for part in error_parts if part))
    flags = acceptance_fields(
        checker_feasible=checker_feasible,
        runtime_sec=f"{wall_time:.6f}",
        runner_elapsed_sec=runner_elapsed,
        official_limit=timelimit,
        timeout_expired=False,
        error_message=error,
    )
    summary_text = tester_summary(result)
    if flags["timed_out"] == "true":
        summary_text = f"{summary_text} | INVALID runtime exceeded official limit"

    return {
        **base_row,
        "stage": "TIMEOUT" if flags["timed_out"] == "true" else result.get("stage", ""),
        "objective": objective if objective is not None else "",
        "score": objective if objective is not None else "",
        "cost": objective if objective is not None else "",
        "obj1": result.get("obj1", "") if result.get("obj1") is not None else "",
        "obj2": result.get("obj2", "") if result.get("obj2") is not None else "",
        "obj3": result.get("obj3", "") if result.get("obj3") is not None else "",
        "runtime_sec": f"{wall_time:.6f}",
        "runner_elapsed_sec": runner_elapsed,
        "assigned_blocks": assigned,
        "total_blocks": total_blocks,
        "total_bays": total_bays,
        "error_message": compact_error(error),
        "solution_file": to_repo_path(solution_path, repo_root),
        "tester_summary": compact_error(summary_text, 1200),
        **flags,
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
    if exists:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            existing_header = next(reader, [])
        if existing_header != CSV_FIELDS:
            raise SystemExit(
                "Refusing to append to cumulative CSV with a different schema: "
                f"{path}. Use a fresh reboot cumulative CSV."
            )
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not exists:
            writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def write_compact_csv(
    path: pathlib.Path,
    run_rows: list[dict],
    *,
    report_path: pathlib.Path,
    repo_root: pathlib.Path,
) -> None:
    report_repo_path = to_repo_path(report_path, repo_root)
    compact_rows = []
    for row in sorted(run_rows, key=lambda r: natural_key(r.get("instance_name", ""))):
        compact_rows.append(
            {
                "instance": row.get("instance_name", ""),
                "blocks": row.get("total_blocks", ""),
                "bays": row.get("total_bays", ""),
                "objective": row.get("objective", ""),
                "T": row.get("obj1", ""),
                "L": row.get("obj2", ""),
                "P": row.get("obj3", ""),
                "runtime_sec": row.get("runtime_sec", ""),
                "checker_feasible": row.get("checker_feasible", ""),
                "timed_out": row.get("timed_out", ""),
                "valid_under_time_limit": row.get("valid_under_time_limit", ""),
                "accepted_for_score": row.get("accepted_for_score", ""),
                "error_message": row.get("error_message", ""),
                "algorithm_version": row.get("algorithm_version", ""),
                "report_path": report_repo_path,
                "solution_file": row.get("solution_file", ""),
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COMPACT_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(compact_rows)


def as_float(value) -> float | None:
    return parse_float(value)


def is_true(value) -> bool:
    return str(value).lower() == "true"


def is_checker_feasible_row(row: dict) -> bool:
    return is_true(row.get("checker_feasible"))


def is_timed_out_row(row: dict) -> bool:
    return is_true(row.get("timed_out"))


def is_feasible_row(row: dict) -> bool:
    return is_true(row.get("accepted_for_score"))


def row_status(row: dict) -> str:
    if is_feasible_row(row):
        return "PASS"
    if is_timed_out_row(row):
        return "TIMEOUT"
    if is_checker_feasible_row(row):
        return "INVALID"
    stage = row.get("stage", "")
    return f"FAIL stage={stage}" if stage != "" else "FAIL"


def best_by_instance(rows: Iterable[dict], metric: str = "objective") -> dict[str, dict]:
    best: dict[str, dict] = {}
    for row in rows:
        if not is_feasible_row(row):
            continue
        value = as_float(row.get(metric))
        if value is None:
            continue
        instance = row.get("instance_name", "")
        current = best.get(instance)
        current_value = as_float(current.get(metric)) if current is not None else None
        if current is None or current_value is None or value < current_value:
            best[instance] = row
    return best


def summarize_rows(rows: list[dict]) -> dict:
    accepted_rows = [row for row in rows if is_feasible_row(row)]
    checker_feasible_rows = [row for row in rows if is_checker_feasible_row(row)]
    timed_out_rows = [row for row in rows if is_timed_out_row(row)]
    objectives = [as_float(row.get("objective")) for row in accepted_rows]
    objectives = [v for v in objectives if v is not None]
    obj1_values = [as_float(row.get("obj1")) for row in accepted_rows]
    obj1_values = [v for v in obj1_values if v is not None]
    obj2_values = [as_float(row.get("obj2")) for row in accepted_rows]
    obj2_values = [v for v in obj2_values if v is not None]
    obj3_values = [as_float(row.get("obj3")) for row in accepted_rows]
    obj3_values = [v for v in obj3_values if v is not None]
    runtimes = [as_float(row.get("runtime_sec")) for row in rows]
    runtimes = [v for v in runtimes if v is not None]
    return {
        "total": len(rows),
        "feasible": len(accepted_rows),
        "accepted_for_score": len(accepted_rows),
        "checker_feasible": len(checker_feasible_rows),
        "timed_out": len(timed_out_rows),
        "failed": len(rows) - len(accepted_rows),
        "objective_sum": sum(objectives) if objectives else None,
        "objective_avg": (sum(objectives) / len(objectives)) if objectives else None,
        "obj1_sum": sum(obj1_values) if obj1_values else None,
        "obj1_avg": (sum(obj1_values) / len(obj1_values)) if obj1_values else None,
        "obj1_max": max(obj1_values) if obj1_values else None,
        "obj2_avg": (sum(obj2_values) / len(obj2_values)) if obj2_values else None,
        "obj3_avg": (sum(obj3_values) / len(obj3_values)) if obj3_values else None,
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
    compact_csv: pathlib.Path,
    repo_root: pathlib.Path,
) -> None:
    summary = summarize_rows(run_rows)
    current_best = best_by_instance(run_rows, metric="obj1")
    previous_best_t = best_by_instance(previous_rows, metric="obj1")

    alg_labels = [spec.version for spec in algorithms]
    internal_alg_labels = [f"{spec.name}:{spec.version}" for spec in algorithms]
    rows_by_instance_alg = {
        (row["instance_name"], f"{row['algorithm_name']}:{row['algorithm_version']}"): row
        for row in run_rows
    }

    best_rows = []
    for problem in problems:
        instance = problem.name
        row = current_best.get(instance)
        if not row:
            best_rows.append([html.escape(instance), "<span class='bad'>no</span>", "", "", "", "", "", ""])
            continue
        prev = previous_best_t.get(instance)
        t_value = as_float(row.get("obj1"))
        prev_t = as_float(prev.get("obj1")) if prev else None
        if prev_t is None or t_value is None:
            delta = "new"
            cls = "neutral"
        else:
            diff = t_value - prev_t
            delta = f"{diff:,.0f}"
            cls = "good" if diff < 0 else "bad" if diff > 0 else "neutral"
        best_rows.append(
            [
                html.escape(instance),
                "<span class='good'>yes</span>",
                fmt(row.get("obj1")),
                fmt(row.get("obj2")),
                fmt(row.get("obj3")),
                fmt(row.get("objective")),
                fmt(row.get("runtime_sec"), 2) + "s",
                f"<span class='{cls}'>{html.escape(delta)}</span>",
            ]
        )

    infeasible_rows = [
        [
            html.escape(row["instance_name"]),
            html.escape(row_status(row)),
            html.escape(str(row.get("checker_feasible", ""))),
            html.escape(str(row.get("timed_out", ""))),
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
            fmt(row.get("runtime_sec"), 2) + "s",
            html.escape(row_status(row)),
            fmt(row.get("obj1")),
            fmt(row.get("objective")),
        ]

    comparison_rows = []
    for problem in problems:
        line = [html.escape(problem.name)]
        best_t = as_float(current_best.get(problem.name, {}).get("obj1"))
        for label in internal_alg_labels:
            row = rows_by_instance_alg.get((problem.name, label))
            if not row:
                line.append("")
                continue
            if is_feasible_row(row):
                t_value = as_float(row.get("obj1"))
                cls = "best" if best_t is not None and t_value == best_t else ""
                line.append(f"<span class='{cls}'>{fmt(t_value)}</span>")
            else:
                line.append(f"<span class='bad'>{html.escape(row_status(row))}</span>")
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
        html_table(["Instance", "Status", "Checker Feasible", "Timed Out", "Error"], infeasible_rows)
        if infeasible_rows
        else "<p class='good'>No unaccepted rows in this run.</p>"
    )

    content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>OGC2026 Benchmark {html.escape(run_id)}</title>
<style>{style}</style>
</head>
<body>
<h1>OGC2026 T Benchmark</h1>
<div class="meta">
  timestamp=<code>{html.escape(timestamp)}</code> |
  timelimit=<code>{timelimit}s</code>
  <details>
    <summary>Files and internal ids</summary>
    run_id=<code>{html.escape(run_id)}</code><br>
    readable_csv=<code>{html.escape(to_repo_path(compact_csv, repo_root))}</code><br>
    raw_csv=<code>{html.escape(to_repo_path(run_csv, repo_root))}</code><br>
    cumulative_csv=<code>{html.escape(to_repo_path(cumulative_csv, repo_root))}</code>
  </details>
</div>
<div class="cards">
  <div class="card"><div class="label">Rows</div><div class="value">{summary['total']}</div></div>
  <div class="card"><div class="label">Feasible (accepted)</div><div class="value">{summary['feasible']}/{summary['total']}</div></div>
  <div class="card"><div class="label">Checker PASS</div><div class="value">{summary['checker_feasible']}/{summary['total']}</div></div>
  <div class="card"><div class="label">Timed Out</div><div class="value">{summary['timed_out']}</div></div>
  <div class="card"><div class="label">Avg T (obj1)</div><div class="value">{fmt(summary['obj1_avg'], 2)}</div></div>
  <div class="card"><div class="label">Max T (obj1)</div><div class="value">{fmt(summary['obj1_max'])}</div></div>
  <div class="card"><div class="label">Avg obj2</div><div class="value">{fmt(summary['obj2_avg'], 2)}</div></div>
  <div class="card"><div class="label">Avg obj3</div><div class="value">{fmt(summary['obj3_avg'], 2)}</div></div>
  <div class="card"><div class="label">Avg Runtime</div><div class="value">{summary['runtime_avg']:.2f}s</div></div>
</div>
<h2>T By Instance</h2>
{html_table(["Instance", "Accepted", "T (obj1)", "obj2", "obj3", "Objective", "Runtime", "Delta T"], best_rows)}
<h2>T Comparison</h2>
{html_table(["Instance", *alg_labels], comparison_rows)}
<h2>Unaccepted Rows</h2>
{infeasible_html}
<h2>Slowest Rows</h2>
{html_table(["Instance", "Runtime", "Status", "T (obj1)", "Objective"], [runtime_row(r) for r in slowest])}
<h2>Fastest Rows</h2>
{html_table(["Instance", "Runtime", "Status", "T (obj1)", "Objective"], [runtime_row(r) for r in fastest])}
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
        default="train/prob_*.json",
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
    parser.add_argument(
        "--require-fresh-cumulative",
        action="store_true",
        help="Fail if the cumulative CSV already exists; use for clean reboot runs.",
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

    cumulative_csv = pathlib.Path(args.cumulative_csv)
    if not cumulative_csv.is_absolute():
        cumulative_csv = repo_root / cumulative_csv
    cumulative_csv = cumulative_csv.resolve()
    cumulative_preexisting = cumulative_csv.exists()
    if args.require_fresh_cumulative and cumulative_preexisting:
        raise SystemExit(f"--require-fresh-cumulative refused existing file: {cumulative_csv}")

    baseline_dir = repo_root / "ogc2026" / "baseline"
    alg_tester_dir = repo_root / "ogc2026" / "alg_tester"
    checker_path = alg_tester_dir / "utils.py"
    checker_sha256 = sha256_file(checker_path)
    benchmark_path = pathlib.Path(__file__).resolve()
    benchmark_sha256 = sha256_file(benchmark_path)
    git_meta = git_snapshot(repo_root)
    benchmark_command = subprocess.list2cmdline([sys.executable, *sys.argv])
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

    run_dir.mkdir(parents=True, exist_ok=True)

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
                checker_sha256=checker_sha256,
                git_meta=git_meta,
                benchmark_command=benchmark_command,
                repo_root=repo_root,
            )
            run_rows.append(row)
            status = row_status(row)
            obj = f" obj={fmt(row.get('objective'))}" if row.get("objective") != "" else ""
            print(f"[benchmark]   {status}{obj} runtime={fmt(row.get('runtime_sec'), 2)}s")
            if args.fail_fast and not is_feasible_row(row):
                break

    run_csv = run_dir / "results.csv"
    compact_csv = run_dir / "readable_results.csv"
    summary_json = run_dir / "summary.json"
    manifest_json = run_dir / "run_manifest.json"
    report_path = run_dir / "report.html"
    write_csv(run_csv, run_rows)
    append_csv(cumulative_csv, run_rows)
    write_compact_csv(
        compact_csv,
        run_rows,
        report_path=report_path,
        repo_root=repo_root,
    )
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
    manifest_json.write_text(
        json.dumps(
            {
                "schema_version": "ogc2026_benchmark_run_manifest_v1",
                "run_id": run_id,
                "timestamp": timestamp,
                "command": benchmark_command,
                "repo_root": str(repo_root),
                "git": git_meta,
                "python": args.python,
                "timelimit": args.timelimit,
                "timeout_grace": args.timeout_grace,
                "external_watchdog_formula": "max(timelimit + timeout_grace, timelimit * 1.5)",
                "official_checker": {
                    "path": to_repo_path(checker_path, repo_root),
                    "sha256": checker_sha256,
                },
                "benchmark_runner": {
                    "path": to_repo_path(benchmark_path, repo_root),
                    "sha256": benchmark_sha256,
                    "require_fresh_cumulative": bool(args.require_fresh_cumulative),
                    "cumulative_csv_preexisting": cumulative_preexisting,
                },
                "outputs": {
                    "run_csv": to_repo_path(run_csv, repo_root),
                    "readable_results_csv": to_repo_path(compact_csv, repo_root),
                    "summary_json": to_repo_path(summary_json, repo_root),
                    "report_html": to_repo_path(report_path, repo_root),
                    "cumulative_csv": to_repo_path(cumulative_csv, repo_root),
                },
                "row_contract": CSV_FIELDS,
                "readable_row_contract": COMPACT_CSV_FIELDS,
                "official_contract": {
                    "algorithm_interface": "algorithm(prob_info: dict, timelimit: float) -> dict",
                    "checker_feasible_true_requires": "official check_feasibility pass",
                    "accepted_for_score": (
                        "checker_feasible == true AND timed_out == false "
                        "AND runtime_sec <= official_limit AND error_message empty"
                    ),
                    "objective": "w1*obj1 + w2*obj2 + w3*obj3",
                    "obj1": "T total tardiness",
                    "obj2": "L normalized bay workload imbalance",
                    "obj3": "P bay-preference penalty",
                },
                "algorithms": [
                    {
                        "name": spec.name,
                        "version": spec.version,
                        "path": to_repo_path(spec.file, repo_root),
                        "sha256": sha256_file(spec.file),
                        "source_files": algorithm_source_manifest(spec, repo_root),
                    }
                    for spec in algorithms
                ],
                "problems": [to_repo_path(p, repo_root) for p in problems],
                "summary": summary,
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
        compact_csv=compact_csv,
        repo_root=repo_root,
    )

    print("[benchmark] summary")
    print(textwrap.indent(json.dumps(summary, ensure_ascii=False, indent=2), "  "))
    print(f"[benchmark] wrote {run_csv}")
    print(f"[benchmark] wrote {compact_csv}")
    print(f"[benchmark] wrote {summary_json}")
    print(f"[benchmark] wrote {manifest_json}")
    print(f"[benchmark] wrote {report_path}")
    print(f"[benchmark] appended {cumulative_csv}")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
