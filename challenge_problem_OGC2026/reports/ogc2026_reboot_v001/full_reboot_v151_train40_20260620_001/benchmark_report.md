# OGC 2026 Training Benchmark Report

> `reboot_v151_20260620_prob31like_direct_stabilizer_on_v142` on train set 40, timelimit=60s
>
> Branch: `hh_algorithm_loop`

---

**accepted_for_score 37/40   checker_feasible 39/40   timeout 3   Avg Objective 24,237,775.486   Avg T 2,847.514   Avg Runtime 38.18s   Max Runtime 90.02s**

## Decision

`rejected`

The direct prob31-like stabilizer did recover a scoreable `prob_31` row with
comfortable runtime margin, but the broader diffuse 3-bay runtime-risk family
still failed the full40 gate.

## Reopened failures

- `prob_32`: timeout, runtime `69.31s`, objective `12935663`, `T=3021`
- `prob_33`: timeout, runtime `62.88s`, objective `40099563`, `T=5899`
- `prob_37`: timeout, runtime `90.02s`, objective missing under time limit

## Target-family signal

- `prob_31` stayed scoreable:
  - representative smoke: `49464822 / T=3465`, runtime `43.04s`
  - targeted rerun: `50953901 / T=3578`, runtime `43.81s`
  - full40: `54081413 / T=3815`, runtime `43.80s`

## Notable surviving tail regressions versus trusted `v142`

- `prob_38`: `403577150 / T=30038`
- `prob_40`: `14097605 / T=20891`
- `prob_34`: `58800095 / T=16766`

## Interpretation

This candidate confirms that the isolated 4-bay prob31-like timeout cliff can
be flattened with one capped direct warm start. That is useful diagnosis, but
it is not enough for promotion because the remaining diffuse 3-bay lowproc
runtime-risk family (`prob_32`, `prob_33`, `prob_37`) still blocks
`accepted_for_score 40/40`.
