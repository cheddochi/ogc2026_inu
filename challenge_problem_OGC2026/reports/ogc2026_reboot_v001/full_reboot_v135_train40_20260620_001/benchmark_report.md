# OGC 2026 Training Benchmark Report

> `reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132` on train set 40, timelimit=60s
>
> Branch: `hh_algorithm_loop`

---

**Accepted 40/40   Avg Objective 15,069,943.325   Avg T 1,538.825   Avg Runtime 27.00s   Max Runtime 58.42s**

## Headline

- accepted_for_score: `40/40`
- timeout: `0`
- invalid/error: `0`
- avg objective: `15069943.325`
- avg T: `1538.825`
- avg L: `2683.325`
- avg P: `4185.775`
- max runtime: `58.418181s`

## Delta vs trusted recovery v132

- avg objective: `15071175.65 -> 15069943.325`
- avg T: `1540.65 -> 1538.825`
- avg L: `2674.325 -> 2683.325`
- avg P: `4187.625 -> 4185.775`
- max runtime: `56.951463 -> 58.418181`

## Per-instance change summary

Only one row changed versus trusted `v132`:

- `prob_40`
  - objective `5910122 -> 5860829`
  - `T 8622 -> 8549`
  - `L 4587 -> 4947`
  - `P 11897 -> 11823`

All other train40 rows stayed unchanged.

## High-T tail after v135

- `prob_38`: `T=11120`, objective `151254848`
- `prob_40`: `T=8549`, objective `5860829`
- `prob_27`: `T=5637`, objective `77480587`
- `prob_37`: `T=3961`, objective `17644653`
- `prob_33`: `T=3805`, objective `26172225`
- `prob_39`: `T=3521`, objective `48160369`

## Companion evidence

- readable CSV:
  `reports/ogc2026_reboot_v001/full_reboot_v135_train40_20260620_001/readable_results.csv`
- HTML report:
  `reports/ogc2026_reboot_v001/full_reboot_v135_train40_20260620_001/report.html`
- direct active-surface revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v135_publish_20260620_001/`
