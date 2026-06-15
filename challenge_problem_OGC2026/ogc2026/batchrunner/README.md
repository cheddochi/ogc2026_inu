# OGC2026 Batchrunner

CLI benchmark runner for OGC2026 algorithm variants.

Default smoke run:

```powershell
python challenge_problem_OGC2026\ogc2026\batchrunner\benchmark.py --limit 3 --timelimit 10
```

Full 40-instance run for the active HH entrypoint:

```powershell
python challenge_problem_OGC2026\ogc2026\batchrunner\benchmark.py --timelimit 60
```

Compare multiple variants:

```powershell
python challenge_problem_OGC2026\ogc2026\batchrunner\benchmark.py `
  --algorithm name=greedy,version=v000,path=challenge_problem_OGC2026\ogc2026\baseline\alg_versions\baseline_hh_v000_original.py `
  --algorithm name=hh,version=v001,path=challenge_problem_OGC2026\ogc2026\baseline `
  --limit 3 --timelimit 30
```

Outputs:

- Per-run CSV: `reports/ogc2026_benchmark/<run_id>/results.csv`
- Per-run HTML: `reports/ogc2026_benchmark/<run_id>/report.html`
- Cumulative CSV: `reports/ogc2026_benchmark/benchmark_results.csv`
- Solutions/logs/raw runner JSON under the per-run directory

