#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v caffeinate >/dev/null 2>&1 \
  && [[ "${OGC_CAFFEINATED:-0}" != "1" ]] \
  && [[ "${OGC_NO_CAFFEINATE:-0}" != "1" ]]; then
  exec env OGC_CAFFEINATED=1 caffeinate -dimsu "$0" "$@"
fi

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
TIMELIMIT="${TIMELIMIT:-10}"
LIMIT="${LIMIT:-3}"

cd "$ROOT"
"$PYTHON_BIN" tools/ogc_quality.py
"$PYTHON_BIN" tools/ogc_batch_test.py \
  --alg-folder "$ALG_FOLDER" \
  --timelimit "$TIMELIMIT" \
  --limit "$LIMIT" \
  "$@"
