# v142 subtype backlog analysis

- source readable CSV: `D:\dev\ogc2026_inu\challenge_problem_OGC2026\reports\ogc2026_reboot_v001\full_reboot_v142_train40_20260620_001\readable_results.csv`
- train dir: `D:\dev\ogc2026_inu\challenge_problem_OGC2026\train`
- target keyword for next hypothesis smoke: `3bay/lowproc/runtime-risk`

## Top T backlog

| instance | T | L | P | runtime_sec | family_key | subtype |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| prob_38 | 11120 | 3894 | 9947 | 47.08 | medium/3bay/lowproc/runtime-risk | medium/3bay/lowproc/moderate/runtime-risk/tight/high-T |
| prob_40 | 8429 | 4947 | 11823 | 55.45 | medium/4bay/lowproc/runtime-risk | medium/4bay/lowproc/concentrated/runtime-risk/tight/high-T |
| prob_27 | 5541 | 2033 | 5796 | 46.20 | small/2bay/lowproc/runtime-risk | small/2bay/lowproc/moderate/runtime-risk/tight/high-T |
| prob_37 | 3961 | 3660 | 7380 | 52.68 | medium/3bay/lowproc/runtime-risk | medium/3bay/lowproc/diffuse/runtime-risk/tight/high-T |
| prob_33 | 3805 | 1094 | 5289 | 45.75 | small/3bay/lowproc/runtime-risk | small/3bay/lowproc/diffuse/runtime-risk/tight/high-T |
| prob_39 | 3521 | 194 | 8094 | 57.66 | medium/3bay/lowproc/runtime-risk | medium/3bay/lowproc/moderate/runtime-risk/tight/high-T |
| prob_32 | 2992 | 2434 | 4662 | 50.08 | small/3bay/lowproc/runtime-risk | small/3bay/lowproc/diffuse/runtime-risk/tight/mid-T |
| prob_31 | 2735 | 1843 | 11680 | 53.95 | small/4bay/lowproc/runtime-risk | small/4bay/lowproc/concentrated/runtime-risk/tight/mid-T |
| prob_26 | 2305 | 2556 | 6385 | 25.17 | small/3bay/lowproc/runtime-mid | small/3bay/lowproc/concentrated/runtime-mid/tight/mid-T |
| prob_30 | 2302 | 3211 | 2986 | 22.07 | small/2bay/lowproc/runtime-safe | small/2bay/lowproc/moderate/runtime-safe/tight/mid-T |
| prob_25 | 2089 | 241 | 3044 | 32.11 | small/2bay/lowproc/runtime-mid | small/2bay/lowproc/moderate/runtime-mid/tight/mid-T |
| prob_36 | 2010 | 1381 | 12149 | 44.18 | medium/4bay/lowproc/runtime-mid | medium/4bay/lowproc/concentrated/runtime-mid/tight/mid-T |

## Family summary

| family_key | count | avg_T | high_T_count | nonzero_T_count | max_runtime_sec | instances |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| medium/4bay/lowproc/runtime-risk | 1 | 8429.0 | 1 | 1 | 55.45 | prob_40 |
| medium/3bay/lowproc/runtime-risk | 3 | 6200.7 | 3 | 3 | 57.66 | prob_37,prob_38,prob_39 |
| small/2bay/lowproc/runtime-risk | 1 | 5541.0 | 1 | 1 | 46.20 | prob_27 |
| small/3bay/lowproc/runtime-risk | 2 | 3398.5 | 1 | 2 | 50.09 | prob_32,prob_33 |
| small/4bay/lowproc/runtime-risk | 1 | 2735.0 | 0 | 1 | 53.95 | prob_31 |
| small/2bay/lowproc/runtime-mid | 1 | 2089.0 | 0 | 1 | 32.11 | prob_25 |
| medium/4bay/lowproc/runtime-mid | 1 | 2010.0 | 0 | 1 | 44.18 | prob_36 |
| small/4bay/lowproc/runtime-mid | 1 | 1595.0 | 0 | 1 | 38.60 | prob_34 |
| small/3bay/lowproc/runtime-mid | 7 | 832.6 | 0 | 7 | 36.35 | prob_6,prob_9,prob_24,prob_26,prob_28,prob_29,prob_35 |
| small/2bay/lowproc/runtime-safe | 6 | 640.7 | 0 | 5 | 22.07 | prob_1,prob_4,prob_8,prob_22,prob_23,prob_30 |
| small/4bay/lowproc/runtime-safe | 3 | 375.3 | 0 | 3 | 18.51 | prob_10,prob_11,prob_12 |
| medium/5bay/lowproc/runtime-mid | 1 | 283.0 | 0 | 1 | 37.56 | prob_20 |

## Representative block-tier smoke candidates

| tier | instance | reason | T | runtime_sec | family_key |
| --- | --- | --- | ---: | ---: | --- |
| tier_01_04 | prob_1 | current-high-T | 11 | 12.65 | small/2bay/lowproc/runtime-safe |
| tier_05_08 | prob_6 | current-high-T | 9 | 29.08 | small/3bay/lowproc/runtime-mid |
| tier_09_12 | prob_11 | current-high-T | 739 | 10.27 | small/4bay/lowproc/runtime-safe |
| tier_13_16 | prob_13 | current-high-T | 923 | 11.26 | medium/4bay/lowproc/runtime-safe |
| tier_17_20 | prob_19 | current-high-T | 389 | 12.67 | medium/4bay/lowproc/runtime-safe |
| tier_21_25 | prob_25 | current-high-T | 2089 | 32.11 | small/2bay/lowproc/runtime-mid |
| tier_26_30 | prob_27 | current-high-T | 5541 | 46.20 | small/2bay/lowproc/runtime-risk |
| tier_31_35 | prob_33 | hypothesis-target | 3805 | 45.75 | small/3bay/lowproc/runtime-risk |
| tier_36_40 | prob_38 | hypothesis-target | 11120 | 47.08 | medium/3bay/lowproc/runtime-risk |

## Suggested next subtype

- family_key: `medium/3bay/lowproc/runtime-risk`
- avg T: `6200.7`
- max runtime: `57.66s`
- members: `prob_37,prob_38,prob_39`
- rationale: prefers repeated high-T families with at least two members before single-row outliers under the plateau/T-zero-first contract.
