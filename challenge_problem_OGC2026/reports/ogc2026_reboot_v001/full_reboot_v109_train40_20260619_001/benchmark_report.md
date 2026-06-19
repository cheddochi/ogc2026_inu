# OGC 2026 Training Benchmark Report

> `reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108` on train set 40, timelimit=60s
>
> Branch: `hh_algorithm_loop`

---

**Feasible 40/40   Total Objective 604,446,090   Total T 61,820   Avg Runtime 24.31s   Max Runtime 58.03s**

Key comparison notes:

- versus `v108`
  - avg objective `15121737.4 -> 15111152.25`
  - avg T `1561.65 -> 1545.5`
  - major row change: `prob_40` objective `6333528 -> 5910122`, T `9268 -> 8622`
- versus historical accepted `v096`
  - avg objective still worse: `15096298.7 -> 15111152.25`
  - avg T now better: `1558.675 -> 1545.5`
  - remaining objective gap is concentrated in `prob_31` and `prob_37`

High-T tail rows:

| Instance | Objective | T | L | P | Runtime |
|----------|-----------|---|---|---|---------|
| prob_38 | 151,254,848 | 11,120 | 3,894 | 9,947 | 44.80s |
| prob_40 | 5,910,122 | 8,622 | 4,587 | 11,897 | 43.86s |
| prob_39 | 48,160,369 | 3,521 | 194 | 8,094 | 58.03s |
| prob_37 | 17,949,088 | 4,040 | 1,192 | 7,465 | 38.73s |
| prob_31 | 40,328,756 | 2,792 | 2,029 | 11,599 | 48.19s |

Decision:

- `candidate`
- reason: scoreable `40/40` current-source recovery candidate with better avg T than historical `v096`, but still not enough avg objective improvement to replace the historical trusted BEST
