# Validation Note: `v153` Prob33-like Thin Gap On `v152`

- Validation date: `2026-06-21`
- Candidate:
  `ogc2026/baseline/alg_versions/reboot_v153_20260621_prob33like_thin_gap_on_v152.py`

## Candidate closed

`reboot_v153_20260621_prob33like_thin_gap_on_v152` is closed as `rejected`.

- Representative block-tier smoke failed:
  `reports/ogc2026_reboot_v001/smoke_reboot_v153_tier12_20260621_001/`

## Failure headline

- accepted_for_score `11/12`
- timeout `1`
- invalid `0`
- reopened non-target timeout:
  - `prob_27` at `64.94s`

## Target-row outcome

- `prob_33`: `26672250 / T=3880`, runtime `59.19s`
- versus `v152` target smoke: `26500068 / T=3854`, runtime `59.05s`

The local thin-gap replay did not improve the intended row, so there is no
reason to tolerate the reopened non-target runtime failure.
