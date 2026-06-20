# v135 publish validation note (2026-06-20)

- Branch: `hh_algorithm_loop`
- Trusted active line: `reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132`
- Active surface: `ogc2026/baseline/baseline_hh.py`
- Baseline wrapper SHA256: `11DCCC123607A6EBEEA76FF3E9A16ED3C31B37376362159E913BC6A393E2949F`
- v135 source SHA256: `FD4A2AA5A9F1AE442014F4D59B40E8F701831F5BEA041F8C5661D05529BCDF8E`

## Trusted evidence set

- tier-representative smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v135_tier9_20260620_001/`
- targeted subtype smoke:
  `reports/ogc2026_reboot_v001/target_reboot_v135_prob40_headroom_20260620_001/`
- short-limit stress:
  `reports/ogc2026_reboot_v001/stress_reboot_v135_prob40_short45_20260620_001/`
- direct active-surface publish revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v135_publish_20260620_001/`
- full train40 benchmark:
  `reports/ogc2026_reboot_v001/full_reboot_v135_train40_20260620_001/`

## Full train40 headline

- `accepted_for_score=40/40`
- `timed_out=0`
- `invalid/error=0`
- `objective_avg=15069943.325`
- `obj1_avg(T)=1538.825`
- `obj2_avg(L)=2683.325`
- `obj3_avg(P)=4185.775`
- `runtime_max=58.418181`

## Delta versus trusted recovery v132

- avg objective: `15071175.65 -> 15069943.325`
- avg T: `1540.65 -> 1538.825`
- avg L: `2674.325 -> 2683.325`
- avg P: `4187.625 -> 4185.775`
- runtime max: `56.951463 -> 58.418181`

Only one train40 row changed:

- `prob_40`
  - objective `5910122 -> 5860829`
  - `T 8622 -> 8549`
  - `L 4587 -> 4947`
  - `P 11897 -> 11823`

## Active-surface publish revalidation

- path:
  `reports/ogc2026_reboot_v001/verify_active_v135_publish_20260620_001/`
- result:
  - `accepted_for_score=12/12`
  - timeout `0`
  - invalid/error `0`
  - representative tier rows stayed scoreable
  - `prob_39` kept the strong row:
    - objective `48160369`
    - `T=3521`
  - `prob_40` reproduced the accepted improvement:
    - objective `5860829`
    - `T=8549`

## Trust interpretation

- `v135` is not only historically accepted on full40; it also revalidated on the
  direct `baseline_hh.py` active surface for the representative publish subset.
- That closes the `v133` `prob_40` runtime-cliff gap and makes `v135` suitable
  for a trusted accepted BEST checkpoint publish.
