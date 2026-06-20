# Publish Checkpoint: v136

- Date: `2026-06-20`
- Branch: `hh_algorithm_loop`
- Active trusted BEST:
  `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`

## Why this is a trusted publish

- Active wrapper:
  `ogc2026/baseline/baseline_hh.py`
- Canonical full evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v136_train40_20260620_001/`
- Full train40 headline:
  - `accepted_for_score=40/40`
  - `timeout=0`
  - `invalid/error=0`
  - avg objective `15037077.025`
  - avg T `1535.125`
  - avg L `2683.325`
  - avg P `4185.775`
  - max runtime `56.571143s`
- Canonical active-surface revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v136_surface_20260620_001/`
- Publish-checkpoint revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v136_publish_20260620_002/`
  - accepted `6/6`
  - timeout `0`
  - invalid `0`
  - reproduced the trusted target-family rows on the live wrapper surface:
    - `prob_25`: objective `1454484`, `T=2089`
    - `prob_27`: objective `76200619`, `T=5541`
    - `prob_39`: objective `48160369`, `T=3521`
    - `prob_40`: objective `5860829`, `T=8549`

## Current non-active history

- `v137` remains `training-best-only`:
  direct-file train40 improved `prob_40`, but the canonical wrapper surface
  did not reproduce that gain.
- `v138` and `v139` remain rejected:
  both were guard-stabilization attempts on the same four-bay stack and did not
  hold the trusted `v136` canonical row on the wrapper-like surface.

## Share scope

This checkpoint intentionally shares only the trusted accepted BEST, the
supporting trust metadata, and minimal evidence artifacts. Raw logs, raw JSON,
solution bulk, scratch probes, and non-active candidate code remain excluded
from the publish set.
