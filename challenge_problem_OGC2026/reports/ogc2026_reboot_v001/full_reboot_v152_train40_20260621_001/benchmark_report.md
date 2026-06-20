# OGC 2026 Training Benchmark Report

> `reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151` on train set 40, timelimit=60s
>
> Branch: `hh_algorithm_loop`

---

**accepted_for_score 40/40   checker_feasible 40/40   timeout 0   Avg Objective 21,022,753.400   Avg T 2,259.650   Avg Runtime 35.06s   Max Runtime 59.53s**

## Decision

`rejected`

This version successfully restores a fully scoreable current-tree train40
surface, but it does so with a large score regression versus the trusted
historical `v142` best.

## Recovery success

- reopened timeout backlog closed:
  - `prob_31`: `63963213 / T=4554`, runtime `43.90s`
  - `prob_32`: `13118978 / T=3076`, runtime `35.53s`
  - `prob_33`: `26500068 / T=3854`, runtime `59.53s`
  - `prob_37`: `23949614 / T=5798`, runtime `42.91s`

## Why it is still not promotable

- trusted `v142` avg objective: `15035076.025`
- `v152` avg objective: `21022753.400`
- trusted `v142` avg T: `1532.125`
- `v152` avg T: `2259.650`

## Largest regressions versus trusted `v142`

- `prob_38`: `151254848 / T=11120 -> 346034606 / T=25718`
- `prob_31`: `39589844 / T=2735 -> 63963213 / T=4554`
- `prob_37`: `17644653 / T=3961 -> 23949614 / T=5798`
- `prob_40`: `5780789 / T=8429 -> 9850012 / T=14530`

## Interpretation

`v152` is useful as a scoreable recovery parent because it removes the current
runtime backlog on the reopened families. The next coherent step should be a
single-family T-breakthrough on top of this recovered surface rather than
another broad runtime flatten.
