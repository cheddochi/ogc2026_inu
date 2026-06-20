# OGC 2026 Training Benchmark Report

> `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135` on train set 40, timelimit=60s
>
> Branch: `hh_algorithm_loop`

---

**Accepted 40/40   Avg Objective 15,037,077.025   Avg T 1,535.125   Avg Runtime 27.76s   Max Runtime 56.57s**

## Headline

- accepted_for_score: `40/40`
- timeout: `0`
- invalid/error: `0`
- avg objective: `15037077.025`
- avg T: `1535.125`
- avg L: `2683.325`
- avg P: `4185.775`
- max runtime: `56.571143s`

## Delta vs trusted v135

- avg objective: `15069943.325 -> 15037077.025`
- avg T: `1538.825 -> 1535.125`
- avg L: `2683.325 -> 2683.325`
- avg P: `4185.775 -> 4185.775`
- max runtime: `58.418181 -> 56.571143`

## Per-instance change summary

Only two rows changed versus trusted `v135`:

- `prob_25`
  - objective `1489168 -> 1454484`
  - `T 2141 -> 2089`
  - `L 241 -> 241`
  - `P 3044 -> 3044`
- `prob_27`
  - objective `77480587 -> 76200619`
  - `T 5637 -> 5541`
  - `L 4754 -> 4754`
  - `P 5945 -> 5945`

All other train40 rows stayed unchanged.

## Short-limit stress snapshot

- candidate path:
  `reports/ogc2026_reboot_v001/stress_reboot_v136_twobay_short45_20260620_001/`
- same-limit v135 comparison:
  `reports/ogc2026_reboot_v001/stress_reboot_v135_twobay_short45_20260620_001/`
- `prob_25` still improved under `45s`:
  - objective `1948687 -> 1906284`
  - `T 2851 -> 2790`
- `prob_27` stayed tied under `45s`:
  - objective `78787221`
  - `T=5735`

## High-T tail after v136

- `prob_38`: `T=11120`, objective `151254848`
- `prob_40`: `T=8549`, objective `5860829`
- `prob_27`: `T=5541`, objective `76200619`
- `prob_37`: `T=3961`, objective `17644653`
- `prob_33`: `T=3805`, objective `26172225`
- `prob_39`: `T=3521`, objective `48160369`

## Companion evidence

- readable CSV:
  `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/readable_results.csv`
- HTML report:
  `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/report.html`
- targeted subtype smoke:
  `reports/ogc2026_reboot_v001/target_reboot_v136_twobay_tail_20260620_001/`
