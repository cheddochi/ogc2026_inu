# Subtype Backlog after v109

Context:

- historical active surface: `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`
- current status of that surface: historical accepted evidence exists, but current-source rechecks are not trusted
- current-source leading candidate: `reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108`

Current-source candidate summary:

- full path: `reports/ogc2026_reboot_v001/full_reboot_v109_train40_20260619_001/`
- accepted_for_score `40/40`
- timeout `0`
- invalid `0`
- avg objective `15111152.25`
- avg T `1545.5`
- avg L `2623.75`
- avg P `4187.025`

Historical-v096 comparison backlog:

- remaining objective/T gap is concentrated in:
  - `prob_31`: objective `39781302 -> 40328756`, T `2751 -> 2792`
  - `prob_37`: objective `17454197 -> 17949088`, T `3961 -> 4040`
- already repaired or improved families:
  - prob40-like:
    - `prob_40`: objective `6333528 -> 5910122`, T `9268 -> 8622`
  - prob38-like recovered on the accepted benchmark lineage, but single-row
    current-source reruns still show drift risk and must be guarded carefully

31-40 feature taxonomy snapshot:

| Instance | Bays | Blocks | proc_mean | slack_mean | workload_mean | pref_conc | pref_pressure | imbalance | Class note |
|----------|------|--------|-----------|------------|---------------|-----------|---------------|-----------|------------|
| prob_31 | 4 | 200 | 21.495 | 4.930 | 128.560 | 0.795 | 0.731 | 0.790 | 4-bay concentrated runtime-risk |
| prob_32 | 3 | 200 | 11.455 | 2.410 | 94.125 | 0.345 | 0.359 | 0.030 | 3-bay medium low-pressure |
| prob_33 | 3 | 200 | 16.795 | 3.835 | 92.060 | 0.445 | 0.414 | 0.225 | 3-bay mid-proc diffuse |
| prob_34 | 4 | 200 | 16.435 | 3.690 | 128.850 | 0.335 | 0.303 | 0.140 | 4-bay diffuse |
| prob_35 | 3 | 200 | 11.380 | 2.420 | 132.225 | 0.595 | 0.533 | 0.440 | 3-bay mixed pressure |
| prob_36 | 4 | 250 | 11.384 | 2.304 | 89.800 | 0.808 | 0.701 | 0.792 | 4-bay concentrated low-proc |
| prob_37 | 3 | 250 | 11.508 | 2.276 | 143.232 | 0.400 | 0.391 | 0.112 | 3-bay xlarge low-proc diffuse prob37-like |
| prob_38 | 3 | 250 | 21.348 | 4.480 | 112.784 | 0.568 | 0.516 | 0.424 | 3-bay high-proc prob38-like |
| prob_39 | 3 | 250 | 11.120 | 2.200 | 111.832 | 0.572 | 0.538 | 0.424 | 3-bay xlarge low-proc concentrated prob39-like |
| prob_40 | 4 | 250 | 21.688 | 4.928 | 174.664 | 0.760 | 0.695 | 0.744 | 4-bay xlarge high-workload prob40-like |

Implications:

- `prob_37` and `prob_39` are in the same coarse `3-bay xlarge low-proc` family
- they split cleanly by preference concentration / pressure / imbalance:
  - `prob_37` is diffuse / low-pressure
  - `prob_39` is concentrated / higher-pressure / runtime-risk
- a broad family replay is too risky on the current source state:
  - short-45 compare:
    `reports/ogc2026_reboot_v001/compare_v109_v098_prob37_prob39_short45_20260619_001/`
    - `v109 prob_37`: not scoreable at `45.217551s`
    - `v098 prob_37`: subprocess timeout `67.528688s`
    - `v098 prob_39`: runtime `45.442129s`, not scoreable
  - long-60 compare:
    `reports/ogc2026_reboot_v001/compare_v109_v098_prob37_prob39_long60_20260619_001/`
    - `v098 prob_37`: objective improved but runtime `63.290928s`, not scoreable
    - `v098 prob_39`: tiny objective gain only

Representative tier smoke set for the next post-v110 cycle:

- tier `1-4`: `prob_1`
- tier `5-8`: `prob_6`
- tier `9-12`: `prob_11`
- tier `13-16`: `prob_13`
- tier `17-20`: `prob_19`
- tier `21-25`: `prob_25`
- tier `26-30`: `prob_27`
- tier `31-35`: `prob_31`
- tier `36-40`: `prob_37` or `prob_39` depending on whether the next hypothesis targets diffuse or concentrated xlarge-lowproc subtype

Next hypothesis direction after v110 rejection:

- do not reopen the entire xlarge-lowproc family
- the prob37-like cheap move stack no longer improves the `v109` warm start
- the next structural T-breakthrough hypothesis should shift toward the prob31-like 4-bay concentrated runtime-risk family or a more stable source of prob38-like recovery under current-source drift

## Late probe notes after the v111 plateau checkpoint

These probes were run on top of the current-source `v109` warm start before
creating the next candidate. They are not official benchmark claims; they are
used only to narrow the next subtype.

### 2-bay heavy-tail family: likely local plateau on top of `v109`

- representative rows:
  - `prob_25`: objective `1499211`, T `2159`
  - `prob_27`: objective `77480587`, T `5637`
  - `prob_30`: objective `31302610`, T `2302`
- current `v109` already inherits the accepted `v070` high-proc concentrated
  gap-single signal on this family:
  - historical `v070` improvement note:
    - `prob_25`: `1512671 / T 2176 -> 1499211 / T 2159`
    - `prob_27`: `78787221 / T 5735 -> 77480587 / T 5637`
- late direct probes on the `v109` warm start tested alternative one-block
  greedy-prefix repairs on the top tardy shortlist for `prob_25` and `prob_27`
  and found no new feasible improvement:
  - `prob_25` top alternatives (`91`, `56`, `40`) all failed to yield a better
    feasible candidate
  - `prob_27` top alternatives (`65`, `64`, `55`) all failed to yield a better
    feasible candidate
- implication:
  the current `v109` warm start appears to have already captured the usable
  single-block improvement signal for this family. Reopening the 2-bay tail
  with another tiny local move is unlikely to produce a meaningful T-first
  breakthrough.

### prob39-like concentrated xlarge-lowproc: only polish signal so far

- the earlier guarded replay remained the best current evidence:
  - long-60 compare:
    `compare_v109_v098_prob37_prob39_long60_20260619_001`
  - `prob_39`: objective `48598605 -> 48587025`
  - T stayed flat at `3553`
- implication:
  this subtype currently offers only same-T L/P/objective polish, which is not
  enough for plateau/T-zero-first mode.

### Narrowed next-direction recommendation

- do not spend the next candidate on:
  - 2-bay heavy-tail single-block variations
  - prob39-like polish-only replay
- the best remaining structural candidates are now:
  - a true prob31-like T breakthrough that beats the current `40328756 / T 2792`
    row instead of merely stabilizing it
  - a prob33-like runtime-stable parent branch only if it directly enables a
    new T-moving follow-up rather than standing alone as runtime polish

## Late-night runtime cliff note after v112 / v113

- `v112` confirmed that a displaced-block earlier-entry reinsertion can beat
  the saved `v111` prob31 row:
  - `40328756 / T 2792 -> 40115695 / T 2776`
- however, the representative smoke run
  `smoke_reboot_v112_tier9_20260619_001`
  still failed scoreability because `prob_31` finished at `60.389299s`
- the follow-up lite replay
  `target_reboot_v113_prob31_20260619_001`
  showed the deeper issue:
  - the inherited current-source `v111` prob31-like chain itself now reruns at
    `60.077600s`
  - the extra displaced-block phase did not even get a chance to execute
- updated recommendation:
  - do not spend the immediate next candidate on a larger prob31-like T move
    on top of `v111`
  - first rebuild a scoreable prob31-like runtime-stable parent under the
    current source state, then reapply the displaced-block idea only if that
    parent leaves enough remaining wall time

## prob31-like runtime-stable parent update after v114

- `v114` tested the lighter parent idea:
  stable capped base from the `v111` branch plus one direct top-2 tardy prefix
  rebuild, skipping the later `v074/v085` polish stages
- evidence:
  - target sanity:
    `target_reboot_v114_prob31_20260619_001`
    - `prob_31`: `40349837 / T 2792 / 47.782863s`
  - representative smoke:
    `smoke_reboot_v114_tier9_20260619_001`
    - accepted_for_score `9/9`
    - `prob_31`: `40349837 / T 2792 / 42.783250s`
  - official-limit repeats:
    `compare_v109_v114_prob31_prob36_prob40_20260619_001`
    `compare_v109_v114_prob31_rerun_20260620_001`
    - `v109 prob_31`: `40328756 / T 2792 / ~49.1-49.8s`
    - `v114 prob_31`: `40349837 / T 2792 / ~42.6-42.9s`
  - short-45 stress:
    `stress_v109_v114_prob31_short45_20260619_001`
    - `v109`: `45309349`
    - `v114`: `40956985`
- implication:
  - `v114` is not an accepted BEST candidate because the official-limit target
    row still loses a small amount of objective versus the current `v109` rerun
  - however, it is a much better runtime-stable parent for the prob31-like
    subtype than the heavier `v111` chain
- updated next-direction recommendation:
  - if the next cycle returns to prob31-like T breakthrough work, use `v114`
    as the parent rather than `v111`
  - the most natural next follow-up is to reapply the displaced-block earlier-
    entry idea on top of `v114`, but only under a much tighter remaining-time
    gate and only after checking that the parent still leaves enough wall time

## Current-source recovery update after v115

- `v115` closed that follow-up cleanly:
  - target sanity:
    `target_reboot_v115_prob31_20260620_001`
    - `prob_31`: `40137295 / T 2776 / 50.343847s`
  - representative smoke:
    `smoke_reboot_v115_tier9_20260620_001`
    - accepted_for_score `9/9`
  - short-45 stress:
    `stress_v109_v115_prob31_short45_20260620_001`
    - `v109`: `67601421`
    - `v115`: `45309349`
  - full train40:
    `full_reboot_v115_train40_20260620_001`
    - accepted_for_score `40/40`
    - avg objective `15106365.725`
    - avg T `1545.1`
    - avg L `2616.85`
    - avg P `4189.15`
- immediate implication:
  - `v115` is now the leading current-source recovery candidate
  - versus `v109`, only the intended prob31-like row changed:
    - `prob_31`: objective `40328756 -> 40137295`
    - T `2792 -> 2776`
    - runtime `49.71s -> 44.91s`
  - but `v115` still does not beat the historical trusted `v096` objective
    baseline:
    - historical `v096` avg objective `15096298.7`
    - current-source `v115` avg objective `15106365.725`
- residual historical gap shape after `v115`:
  - remaining regressions versus historical `v096` are now concentrated mainly
    in:
    - `prob_37`: objective `17454197 -> 17949088`, T `3961 -> 4040`
    - `prob_31`: objective `39781302 -> 40137295`, T `2751 -> 2776`
  - offsetting improvements already exist in:
    - `prob_40`: objective `6333528 -> 5910122`, T `9268 -> 8622`
    - `prob_3`: objective `213297 -> 188500`, T `1 -> 0`

## Next publish-after-checkpoint direction

- do not start a new candidate before the publish checkpoint closes
- after publish, the next T-zero-first subtype should move from the now-recovered
  prob31-like branch to the residual prob37-like diffuse xlarge-lowproc gap
- guardrails for that next cycle:
  - use `v115` as the parent
  - do not reopen the whole xlarge-lowproc family
  - require a true official-limit improvement on `prob_37` without giving back
    the newly recovered prob31-like row or the prob40-like gains
