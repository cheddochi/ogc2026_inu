#!/usr/bin/env python3
"""Lightweight quality checks for the OGC2026 workspace."""

import argparse
import pathlib
import py_compile
import sys


def repo_root_from_here() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def iter_python_files(repo_root: pathlib.Path):
    roots = [
        repo_root / "challenge_problem_OGC2026" / "ogc2026" / "baseline",
        repo_root / "challenge_problem_OGC2026" / "ogc2026" / "alg_tester",
        repo_root / "tools",
    ]
    for root in roots:
        if root.exists():
            for path in sorted(root.rglob("*.py")):
                if "__pycache__" not in path.parts:
                    yield path


def main():
    parser = argparse.ArgumentParser(description="Run syntax checks for OGC2026 Python files.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    repo_root = repo_root_from_here()
    failures = []
    files = list(iter_python_files(repo_root))
    for path in files:
        if args.verbose:
            print(f"[quality] py_compile {path.relative_to(repo_root)}")
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append((path, exc))

    print(f"[quality] checked {len(files)} Python files")
    if failures:
        for path, exc in failures:
            print(f"[quality] FAIL {path.relative_to(repo_root)}")
            print(exc)
        return 1

    print("[quality] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
