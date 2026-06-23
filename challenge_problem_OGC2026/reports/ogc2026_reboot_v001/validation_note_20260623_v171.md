# v171 Validation Note

- Version:
  `reboot_v171_20260621_1215_twobay_concentrated_early_exit_on_v170`
- Decision:
  `rejected`
- meaningful_progress:
  `false`
- plateau_reason:
  `The candidate restored the narrow 2-bay concentrated family, but it did not close the runtime-risk Family B guard because prob_37 still timed out and no full40 scoreable result exists.`

## Hypothesis

Use earlier direct exits for the `2bay/highproc/concentrated` family:

- `prob25-like` rows use the stable `v066` direct builder immediately.
- `prob27-like` rows use the stable direct builder from `v170` and skip the
  expensive gap-single follow-up.
- Preserve the useful `prob33-like` direct restore from `v170`.

Selectors remain feature-based only; no instance-id logic was introduced.

## Representative Tier Smoke

- Path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v171_tier9_20260621_001/`
- Smoke set:
  `prob_1, prob_6, prob_11, prob_13, prob_19, prob_25, prob_27, prob_33, prob_38`
- Result:
  - accepted_for_score `9/9`
  - timeout `0`
  - invalid/error `0`

Recovered rows on the current tree:

- `prob_25`: `1512671 / T=2176 / 32.20s`
- `prob_27`: `78787221 / T=5735 / 44.12s`
- `prob_33`: `66465567 / T=9821 / 33.85s`

## Targeted Runtime-Family Smoke

- Path:
  `reports/ogc2026_reboot_v001/target_reboot_v171_runtime_family_20260621_001/`
- Target set:
  `prob_25, prob_27, prob_31, prob_33, prob_37, prob_38, prob_39, prob_40`
- Result:
  - accepted_for_score `7/8`
  - timeout `1`
  - invalid `0`

Blocking row:

- `prob_37`: TIMEOUT `90944439 / T=25911 / 73.74s`

Large high-T guard rows that remained open:

- `prob_31`: `295623767 / T=21938 / 44.29s`
- `prob_38`: `1120394778 / T=83806 / 51.70s`
- `prob_39`: `251183395 / T=18737 / 59.79s`
- `prob_40`: `8026436 / T=11795 / 59.93s`

## Interpretation

`v171` proved that the `prob25-like` and `prob27-like` early exits are useful
on the current tree, and it kept the `prob33-like` recovery path scoreable.
That is a good local repair signal, but it is not enough for promotion:

- the targeted guard still failed at `prob_37`
- high-T Family B tail rows remained large
- there is still no scoreable full40 evidence for `v171`

So `v171` should be closed as `rejected`, not as `candidate`, and the current
publish state should remain a recovery checkpoint.

## Next Hypothesis Direction

Stay in T-zero-first recovery mode and move the next structural work to the
`3bay/runtime-risk/high-T tail` family:

- earlier direct flattening or guarded portfolio on the `prob37/prob38/prob39`
  slice
- preserve the now-useful `2bay/highproc/concentrated` early exits
- avoid re-opening the late inherited chain that pushes runtime above the
  official limit
