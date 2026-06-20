# Validation Note: `v154` Prob38-like Restore Direct `v142` On `v152`

- Validation date: `2026-06-21`
- Candidate:
  `ogc2026/baseline/alg_versions/reboot_v154_20260621_prob38like_restore_direct_v142_on_v152.py`

## Candidate closed

`reboot_v154_20260621_prob38like_restore_direct_v142_on_v152` is closed as
`rejected`.

## Representative smoke

- path:
  `reports/ogc2026_reboot_v001/smoke_reboot_v154_tier12_20260621_001/`
- accepted_for_score `12/12`
- timeout `0`
- invalid `0`

The representative set stayed scoreable, but the target family was still far
from the trusted historical row:

- `prob_38`: `311325271 / T=23125`

## Targeted comparison

- path:
  `reports/ogc2026_reboot_v001/target_reboot_v154_prob38like_20260621_001/`
- accepted_for_score `5/6`
- timeout `1`
- invalid `0`

Target-family recovery signal existed:

- `prob_38`: `v152 494843363 / T=36895`
  -> `v154 369284609 / T=27467`

But the candidate is still a reject because a non-target high-T tier-mate
reopened a scoreable failure:

- `prob_40`: `v152 10590602 / T=15638 / 58.63s`
  -> `v154 11368359 / T=16805 / 60.50s` (`TIMEOUT`)

## Main lesson

The direct current-tree `v142` path is no longer a trustworthy restore oracle
for the historical prob38-like row, and the inherited prob40-like base path is
already operating near the 60s runtime cliff.
