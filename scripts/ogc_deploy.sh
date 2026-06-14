#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCH="${BRANCH:-codex/ogc-iteration}"
MESSAGE="${MESSAGE:-Update OGC2026 algorithm iteration}"
RUN_FULL="${RUN_FULL:-0}"

cd "$ROOT"

git switch -C "$BRANCH"

if [[ "$RUN_FULL" == "1" ]]; then
  scripts/ogc_full_train.sh
else
  scripts/ogc_loop.sh
fi

git status --short
git add .gitignore tools scripts challenge_problem_OGC2026/ogc2026/baseline
git commit -m "$MESSAGE"
git push -u origin "$BRANCH"

echo "Pushed $BRANCH. Open a PR from this branch on GitHub."
