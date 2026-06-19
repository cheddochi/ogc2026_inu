# v118 wrapper revalidation note (2026-06-20)

- version:
  `reboot_v118_20260620_0835_prob31like_gap_hard_margin_on_v116`
- validation surface:
  synthetic wrapper mirroring
  `myalgorithm.py -> baseline_hh.py -> v118`
- path:
  `reports/ogc2026_reboot_v001/verify_v118_wrapper_surface_20260620_001/`

## Result

- accepted_for_score: `2/3`
- checker_feasible: `3/3`
- timed_out: `1`
- invalid: `0`

Rows:

- `prob_31`
  - accepted_for_score `true`
  - objective `40137295`
  - T `2776`
  - runtime `54.430620s`
  - note: this is the weaker keep-result from the `v115` stage, not the
    stronger `v117`/direct-`v118` row
- `prob_37`
  - checker-feasible but timeout
  - objective `17644653`
  - T `3961`
  - runtime `60.343678s`
- `prob_40`
  - accepted_for_score `true`
  - objective `5910122`
  - T `8622`
  - runtime `53.632671s`

## Key log evidence

`prob_31` log shows the harder margin doing exactly what it was designed to do,
but too conservatively under wrapper overhead:

- `v114` after prefix2: T `2792`
- `v115` best displaced result: T `2776`, objective `40137295`
- `v118` final note:
  `skip_prob31like_concentrated_gap ... remaining=6.12s required=9.80s`

That skip protects runtime but also throws away the `v117` improvement to
`T=2735`, objective `39589844`.

## Judgment

- decision: `rejected`

## Why rejected

The goal of `v118` was not merely to stay scoreable on direct execution. It was
to recover a publish-safe active line for the prob31/prob37 runtime-risk family.
On the wrapper surface that matters for promotion, the hypothesis still fails:

1. `prob_37` remains a timeout.
2. `prob_31` loses the intended T improvement.

So `v118` is useful diagnostic evidence, but not a promotable recovery line.
