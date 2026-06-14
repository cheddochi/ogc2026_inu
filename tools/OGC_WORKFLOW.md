# OGC2026 Iteration Workflow

This workspace is set up for a repeatable loop:

1. Edit the algorithm in `challenge_problem_OGC2026/ogc2026/baseline/`.
2. Run syntax checks.
3. Run the official `alg_tester` feasibility checker over train data.
4. Compare objective/runtime results in `reports/ogc_batch/`.
5. Commit and push a GitHub branch when the iteration is good enough.

## Bootstrap

```bash
scripts/ogc_bootstrap.sh
```

This creates `.venv/` and installs the minimum package needed by the official
checker, `shapely`. The loop scripts automatically use `.venv/bin/python` when
it exists.

## Fast Loop

```bash
scripts/ogc_loop.sh
```

Defaults:

- algorithm folder: `challenge_problem_OGC2026/ogc2026/baseline`
- train cases: first 3 files from `challenge_problem_OGC2026/train`
- timelimit: 10 seconds per case

Override defaults:

```bash
LIMIT=5 TIMELIMIT=20 scripts/ogc_loop.sh
```

## Full Train Run

```bash
TIMELIMIT=60 scripts/ogc_full_train.sh
```

This uses all 40 JSON instances under `challenge_problem_OGC2026/train`.

## Direct Batch Runner

```bash
python3 tools/ogc_batch_test.py \
  --alg-folder challenge_problem_OGC2026/ogc2026/baseline \
  --timelimit 30 \
  --problem challenge_problem_OGC2026/train/prob_1.json
```

Each run writes:

- `summary.json`
- `results.csv`
- per-problem stdout logs
- per-problem solution JSON

under `reports/ogc_batch/<timestamp>/`.

## Deploy Branch

```bash
BRANCH=codex/ogc-casat-fix MESSAGE="Improve OGC2026 feasibility repair" scripts/ogc_deploy.sh
```

By default this runs the fast loop before commit/push. To require the full train
run before pushing:

```bash
RUN_FULL=1 TIMELIMIT=60 scripts/ogc_deploy.sh
```
