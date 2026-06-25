# OGC 2026 Training Benchmark Report

## Run

- report version id: `verify_reboot_v152_recheck_20260625_001`
- algorithm version: `reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151`
- decision label: `recovery`
- promotion status: `not trusted BEST`

## Summary

- Feasible pass/40: `11/11` for this recovery subset
- Total Objective: `366,166,724`
- Avg Objective: `33,287,884.0`
- Total T: `33,381`
- Avg T: `3,034.64`
- Total L: `27,111`
- Avg L: `2,464.64`
- Total P: `55,101`
- Avg P: `5,009.18`
- Avg Runtime: `32.16s`
- Max Runtime: `55.96s`
- timed_out count: `0`
- invalid/error count: `0`

## Main Table

| Instance | Blocks | Bays | Objective | T | L | P | Runtime | Feas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| prob_1 | 50 | 2 | 693,901 | 11 | 1,700.0 | 1,810.0 | 14.63s | Y |
| prob_6 | 100 | 3 | 756,030 | 9 | 1,980.0 | 3,170.0 | 35.38s | Y |
| prob_11 | 150 | 4 | 17,206,722 | 739 | 407.0 | 2,350.0 | 11.68s | Y |
| prob_13 | 200 | 4 | 17,775,043 | 923 | 4,390.0 | 4,366.0 | 12.86s | Y |
| prob_19 | 250 | 4 | 4,715,273 | 389 | 7,056.0 | 4,042.0 | 14.99s | Y |
| prob_25 | 150 | 2 | 1,454,484 | 2,089 | 241.0 | 3,044.0 | 37.20s | Y |
| prob_27 | 200 | 2 | 76,200,619 | 5,541 | 2,033.0 | 5,796.0 | 51.64s | Y |
| prob_33 | 200 | 3 | 26,172,225 | 3,805 | 1,094.0 | 5,289.0 | 44.72s | Y |
| prob_37 | 250 | 3 | 21,777,210 | 5,234 | 4,122.0 | 7,193.0 | 28.06s | Y |
| prob_38 | 250 | 3 | 151,254,848 | 11,120 | 3,894.0 | 9,947.0 | 46.62s | Y |
| prob_39 | 250 | 3 | 48,160,369 | 3,521 | 194.0 | 8,094.0 | 55.96s | Y |

## Recovery Reading

- This run is not a BEST claim.
- It proves that `v152` is currently a scoreable recovery parent on the
  current tree after the active `baseline_hh.py` wrapper reopened drift.
- Largest remaining high-T rows in this subset are `prob_38`, `prob_27`,
  `prob_37`, `prob_33`, and `prob_39`.
- The next bounded cycle should treat `v152` as the parent and pursue a
  structurally different Family B T-breakthrough hypothesis.
