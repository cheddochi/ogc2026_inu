# Validation Note: reboot_v163_20260621_0710_prob27like_pregate_on_v142

- Decision: `rejected`

## What worked

- Representative tier smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v163_tier9_20260621_001/`
- The narrow pre-gate did recover the intended prob27-like runtime family:
  - `prob_25`: TIMEOUT `61.706834s ->` PASS `53.733788s`
  - `prob_27`: watchdog TIMEOUT `90.070134s ->` PASS `58.553613s`
- It also improved the remaining blocked runtime row without fully fixing it:
  - `prob_33`:
    `124920938 / T=18614 / 73.592063s`
    ->
    `99323596 / T=14778 / 65.028617s`

## Why it is still rejected

- The representative smoke is still not fully scoreable:
  - `accepted_for_score=8/9`
  - `prob_33` remained a timeout
- More importantly, the delegated non-target rows were not stable enough for a
  target-only wrapper hypothesis.

## Hidden-risk recheck

- Recheck bundle:
  `reports/ogc2026_reboot_v001/recheck_reboot_v163_nontarget_20260621_001/`
- `prob_25` confirmed the intended sibling-spillover fix:
  - `v142`: TIMEOUT `62.746608s`
  - `v163`: PASS `56.894718s`
- But delegated non-target rows still moved materially:
  - `prob_1`:
    `839356 / T=29 -> 19311629 / T=657`
  - `prob_19`:
    `4715273 / T=389 -> 7593645 / T=650`
  - `prob_38`:
    `1006727224 / T=75430 -> 1024666955 / T=76633`

## Interpretation

- The useful prob27-like recovery signal is real.
- But `v163` was supposed to be a clean pre-gated target-only wrapper. The fact
  that delegated non-target rows still drifted means the current blocker is
  broader runtime/delegation stability, not just selector width.
- The next coherent move should be structurally different:
  - focus on the surviving `prob33-like` timeout, or
  - diagnose / replace the unstable delegated warm-start path instead of adding
    another narrow prob27-like wrapper layer.
