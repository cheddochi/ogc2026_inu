# Validation Note: reboot_v168_20260621_0825_v158_coupled_runtime_slices

- Version:
  `reboot_v168_20260621_0825_v158_coupled_runtime_slices`
- Parent:
  `reboot_v158_20260621_prob40like_narrow_builder_on_v152`
- Decision:
  rejected

## Hypothesis

The `prob27-like` and `prob33-like` rows had become a coupled runtime-risk
family. The version kept the direct `v158` parent surface, but replaced two
feature slices explicitly:

- `prob27-like` -> direct `v146` recovery path
- `prob33-like` -> direct thin-gap repair path proven in `v167`

The expectation was that both siblings could close together without disturbing
the rest of the direct parent.

## Representative smoke

- Path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v168_tier10_20260621_001/`
- Result:
  - parent `v158`: `accepted_for_score=9/10`
  - `v168`: `accepted_for_score=10/10`

Representative positives:

- `prob_27`: stayed scoreable at `55.66s`
- `prob_33`: recovered to `99106198 / T=14714 / 46.41s`
- `prob_38`: improved to `911128161 / T=68115`

This was good enough to justify the mandatory subtype gate.

## Targeted subtype smoke

- Path:
  `reports/ogc2026_reboot_v001/target_reboot_v168_coupled_runtime_20260621_001/`
- Result:
  - parent `v158`: `accepted_for_score=7/8`
  - `v168`: `accepted_for_score=7/8`

Target-family movement:

- improved
  - `prob_25`: `1798973 / T=2609 -> 1499211 / T=2159`
  - `prob_31`: `310854644 / T=23075 -> 200043171 / T=14766`
  - `prob_32`: `16119470 / T=3890 -> 14498408 / T=3436`
  - `prob_33`: TIMEOUT `75146886 / T=11148 / 62.48s ->`
    PASS `39938437 / T=5841 / 46.58s`
  - `prob_38`: `827168422 / T=61818 -> 662283744 / T=49442`
  - `prob_39`: `145091141 / T=10777 -> 136012133 / T=10097`
- regressed
  - `prob_27`: PASS `78787221 / T=5735 / 55.36s ->`
    TIMEOUT `77480587 / T=5637 / 74.01s`
  - `prob_40`: `8393616 / T=12351 -> 9402073 / T=13853`

## Why it is rejected

The candidate cannot proceed to full40 because the targeted subtype smoke is
not fully scoreable. The `prob33-like` repair is real, but delegating
`prob27-like` to `v146` is not a stable current-tree recovery path. On the
current source tree it still inherits a long runtime stack and can fall back
onto the 60-second cliff.

## Implication for the next hypothesis

The next coherent move should keep the direct `prob33-like` repair signal, but
replace the `v146` wholesale delegation with a lighter direct `prob27-like`
stabilizer that reaches the useful 2-bay tail logic earlier.
