# Validation Note: v117 Publish Recheck (2026-06-20)

## Command

```powershell
C:\Python314\python.exe ogc2026\batchrunner\benchmark.py `
  --algorithm name=hh,version=active,path=ogc2026\baseline `
  --problem train\prob_31.json `
  --problem train\prob_37.json `
  --problem train\prob_40.json `
  --timelimit 60 `
  --run-id verify_active_v117_publish_20260620_001 `
  --out-dir reports\ogc2026_reboot_v001\verify_active_v117_publish_20260620_001 `
  --cumulative-csv reports\ogc2026_reboot_v001\benchmark_results_reboot.csv
```

## Outcome

- accepted_for_score `1/3`
- checker_feasible `3/3`
- timed_out `2`
- failed rows:
  - `prob_31`: objective `39589844`, T `2735`, runtime `61.996197s`
  - `prob_37`: objective `17644653`, T `3961`, runtime `60.427098s`
- passing row:
  - `prob_40`: objective `5910122`, T `8622`, runtime `52.389308s`

## Conclusion

- The active surface is currently not publish-safe at the official 60s limit.
- Use this result together with the historical accepted v117 full run to track
  the gap between historical evidence and current publish reliability.
