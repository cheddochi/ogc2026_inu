# Publish Checkpoint 2026-06-20 07:44 KST

## Active trusted BEST

- Active surface:
  `ogc2026/baseline/baseline_hh.py`
- Active version:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Trusted full evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`
- Current wrapper/active revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_002/`

## Current trusted score claim

- Full 40:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - `avg T=1540.65`
  - `avg L=2674.325`
  - `avg P=4187.625`
  - `avg objective=15071175.65`
  - `runtime_max=59.416431s`
- Wrapper/active revalidation:
  - `accepted_for_score=8/8`
  - `timed_out=0`
  - rows:
    - `prob_31`
    - `prob_37`
    - `prob_39`
    - `prob_40`

## This cycle

- `v125`:
  - full 40 stayed scoreable
  - improved `prob_40`
  - regressed `prob_39`
  - worse avg objective than trusted `v123`
  - decision: rejected
- `v126`:
  - scoreable smoke
  - no measurable target-family movement
  - decision: rejected
- `v127`:
  - target-family timeout on smoke
  - decision: rejected
- `v128`:
  - narrowed 2-bay heavy-tail pair-prefix retry
  - target-family timeout on smoke (`prob_27`, `61.972116s`)
  - decision: rejected

## Checkpoint judgment

- No new accepted improvement was found after `v123`.
- The active trusted BEST remains `v123`.
- This checkpoint is an accepted-BEST plateau publish, not a promotion.

## Next hypothesis

- Stay on the trusted `v123` surface.
- Keep the next search focused on T-tail rows that remain scoreable:
  - avoid any 2-bay paired-prefix phase that can push `prob_27` over the
    runtime cliff
  - prefer narrower T-zero or near-T-zero repair moves on the remaining
    high-T families instead of broader multi-block rebuilds
