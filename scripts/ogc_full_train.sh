#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${PYTHON:-}" ]]; then
  PYTHON_BIN="$PYTHON"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
elif [[ -x "/private/tmp/ogc2026-venv/bin/python" ]]; then
  PYTHON_BIN="/private/tmp/ogc2026-venv/bin/python"
else
  PYTHON_BIN="python3"
fi
ALG_FOLDER="${ALG_FOLDER:-$ROOT/challenge_problem_OGC2026/ogc2026/baseline}"
TIMELIMIT="${TIMELIMIT:-60}"

cd "$ROOT"
"$PYTHON_BIN" tools/ogc_quality.py
"$PYTHON_BIN" tools/ogc_batch_test.py \
  --alg-folder "$ALG_FOLDER" \
  --timelimit "$TIMELIMIT" \
  "$@"
