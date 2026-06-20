# OGC 2026 Training Benchmark Report

> `reboot_v150_20260620_2315_prob33like_thin_gap_on_v142` on train set 40, timelimit=60s
>
> Branch: `hh_algorithm_loop`

---

**accepted_for_score 37/40   checker_feasible 39/40   timeout 3   Avg Objective 20,235,033.568   Avg T 2,196.892   Avg Runtime 38.17s   Max Runtime 90.03s**

## Decision

`rejected`

The local `prob33-like` thin-gap hypothesis improved the intended `prob_33`
repair path and stayed scoreable on representative smoke, but the full40 run
reopened three non-target timeouts, so it does not satisfy the recovery-first
scoreable gate.

## Reopened failures

- `prob_31`: timeout, runtime `75.27s`, objective `107926981`, `T=7870`
- `prob_32`: timeout, runtime `66.25s`, objective `12935663`, `T=3021`
- `prob_37`: timeout, runtime `90.03s`, objective missing under time limit

## Notable surviving tail regressions

- `prob_38`: objective `346034606`, `T=25718`
- `prob_40`: objective `11209127`, `T=12041`

## Positive signal that was not enough

- `prob_33` recovered to `26172225 / T=3805`
- representative smoke stayed `accepted_for_score 9/9`
- short-limit `45s` stress still returned a scoreable fallback

## Interpretation

This run looks more like a broader parent warm-start/runtime instability than a
remaining `prob33-like` repair-width issue. The next coherent repair should
stabilize the reopened runtime-risk family before another local T-zero pass.
