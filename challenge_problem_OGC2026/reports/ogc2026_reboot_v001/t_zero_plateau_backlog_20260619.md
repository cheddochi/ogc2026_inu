# T-Zero Plateau Backlog - 2026-06-19

Reference full result: `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`

- Reference status: historical accepted `40/40`, but current-source trust is not re-established.
- Total T: `62347`
- Avg T: `1558.675`
- T>0 instance count: `34/40`
- Plateau mode rule: prioritize `accepted_for_score 40/40`, `timeout 0`, `invalid 0`, then lower Total T / Avg T / T>0 count / high-T tail before polishing objective or L/P.

## Tier Smoke Representatives

| Tier | Representative | T | Tags | Runtime |
|---|---:|---:|---|---:|
| 1-5 | prob_1 | 11 | baseline_tail | 11.51s |
| 6-10 | prob_6 | 9 | baseline_tail | 16.83s |
| 11-15 | prob_11 | 739 | baseline_tail | 8.73s |
| 16-20 | prob_19 | 389 | baseline_tail | 10.59s |
| 21-25 | prob_25 | 2159 | 2bay_heavy_tail | 19.92s |
| 26-30 | prob_27 | 5637 | 2bay_heavy_tail | 30.97s |
| 31-35 | prob_31 | 2751 | prob31like_runtime, dense4bay_highproc | 58.48s |
| 36-40 | prob_38 | 11120 | prob38like_pressure | 46.94s |

## High-T Tail Backlog

| Instance | T | Objective | Runtime | Blocks | Bays | ProcMean | SlackMean | PrefPressure | Tags |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| prob_38 | 11120 | 151254848 | 46.94s | 250 | 3 | 21.35 | 4.48 | 0.516 | prob38like_pressure |
| prob_40 | 9268 | 6333528 | 33.79s | 250 | 4 | 21.69 | 4.93 | 0.695 | dense4bay_highproc |
| prob_27 | 5637 | 77480587 | 30.97s | 150 | 2 | 21.27 | 4.77 | 0.643 | 2bay_heavy_tail |
| prob_37 | 3961 | 17454197 | 53.42s | 250 | 3 | 11.51 | 2.28 | 0.391 | prob37like_diffuse |
| prob_33 | 3805 | 26172225 | 42.50s | 200 | 3 | 16.80 | 3.83 | 0.414 | 3bay_runtime_tail |
| prob_39 | 3521 | 48160369 | 57.53s | 250 | 3 | 11.12 | 2.20 | 0.538 | prob39like_opportunity |
| prob_32 | 2992 | 12781706 | 46.10s | 200 | 3 | 11.46 | 2.41 | 0.359 | baseline_tail |
| prob_31 | 2751 | 39781302 | 58.48s | 200 | 4 | 21.50 | 4.93 | 0.731 | prob31like_runtime, dense4bay_highproc |
| prob_26 | 2345 | 32253881 | 18.97s | 150 | 3 | 16.92 | 3.85 | 0.701 | baseline_tail |
| prob_30 | 2302 | 31302610 | 15.71s | 150 | 2 | 11.31 | 2.34 | 0.623 | 2bay_heavy_tail |
| prob_25 | 2159 | 1499211 | 19.92s | 100 | 2 | 21.58 | 5.37 | 0.599 | 2bay_heavy_tail |
| prob_36 | 2010 | 1499988 | 41.07s | 250 | 4 | 11.38 | 2.30 | 0.701 | 4bay_tail |

## Immediate T-Breakthrough Candidates

1. `prob31like_runtime` / `dense4bay_highproc`: current-source runtime cliff first. Any candidate that improves T elsewhere but lets this family timeout is auto-reject.
2. `prob38like_pressure`: biggest single-row T tail. Must stay scoreable while seeking T reduction.
3. `prob37like_diffuse`: cheap local T/objective opportunities exist, but only if they do not consume prob31-like runtime margin.
4. `prob39like_opportunity`: only meaningful after prob31like timeout risk is under control.
5. `2bay_heavy_tail` / `3bay_runtime_tail` rows (`prob_27`, `prob_32`, `prob_33`) remain secondary T backlog once the runtime cliff families are stable.
