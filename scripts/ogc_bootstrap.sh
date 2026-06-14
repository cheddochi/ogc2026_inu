#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-/private/tmp/ogc2026-venv}"

cd "$ROOT"

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

ln -sfn "$VENV_DIR" "$ROOT/.venv"

"$VENV_DIR/bin/python" -m pip install --upgrade "pip<26"
"$VENV_DIR/bin/python" -m pip install "numpy<2" "shapely==2.0.4"

cat <<EOF
Bootstrap complete.

Use this Python for local OGC loops:
  export PYTHON="$VENV_DIR/bin/python"
  scripts/ogc_loop.sh

Or run directly:
  "$VENV_DIR/bin/python" tools/ogc_batch_test.py --timelimit 10 --limit 3
EOF
