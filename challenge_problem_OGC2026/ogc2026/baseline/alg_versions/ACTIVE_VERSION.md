# Active HH Version

- Active surface: `ogc2026/baseline/baseline_hh.py`
- Active version id: `reboot_v177_20260625_prob27like_micro_shortlist_on_v176`
- Status: current-tree trusted BEST on the tracked baseline_hh surface; the
  historical accepted `v142` full evidence is still slightly stronger, but it
  is not publish-trusted on the current source tree because the wrapper surface
  drifted during revalidation
- Entrypoint chain:
  `myalgorithm.py ACTIVE="hh"` -> `baseline_hh.py` ->
  `alg_versions.reboot_v177_20260625_prob27like_micro_shortlist_on_v176.algorithm`
- Public interface:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
```

- Historical accepted evidence:
  - tier-representative smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v142_tier9_20260620_001/`
  - targeted subtype smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v142_prob40like_20260620_001/`
  - short-limit subtype stress:
    `reports/ogc2026_reboot_v001/stress_reboot_v142_prob40like_short45_20260620_001/`
  - publish-checkpoint revalidation:
    `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_001/`
  - full:
    `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
- Historical accepted train40 result:
  - `accepted_for_score=40/40`
  - `timed_out=0`
  - runtime max `57.660195s`
  - avg T/obj1 `1532.125`
  - avg L/obj2 `2683.325`
  - avg P/obj3 `4185.775`
  - avg objective `15035076.025`
- Historical promotion note:
  - Compared against trusted `v136`, `v142` keeps `accepted_for_score=40/40`
    and improves the official headline on the direct wrapper surface:
    - avg objective `15037077.025 -> 15035076.025`
    - avg T `1535.125 -> 1532.125`
    - avg L `2683.325 -> 2683.325`
    - avg P `4185.775 -> 4185.775`
    - runtime max `56.571143 -> 57.660195`
  - Row-level change versus `v136`:
    - `prob_40`: objective `5860829 -> 5780789`,
      `T 8549 -> 8429`
- Historical publish-checkpoint revalidation:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_001/`
  - accepted `7/7`; timeout `0`, invalid `0`
  - current active wrapper reproduced the same canonical subset rows:
    - `prob_1`: objective `693901`, `T=11`
    - `prob_11`: objective `17206722`, `T=739`
    - `prob_25`: objective `1454484`, `T=2089`
    - `prob_27`: objective `76200619`, `T=5541`
    - `prob_31`: objective `39589844`, `T=2735`
    - `prob_39`: objective `48160369`, `T=3521`
    - `prob_40`: objective `5780789`, `T=8429`
- Historical trust recheck:
  - path:
    `reports/ogc2026_reboot_v001/verify_active_v142_publish_20260620_002/`
  - accepted `7/7`; timeout `0`, invalid `0`
  - the current wrapper surface reproduced the same canonical subset rows again,
    including the historically sensitive tail rows:
    - `prob_27`: objective `76200619`, `T=5541`
    - `prob_40`: objective `5780789`, `T=8429`
  - interpretation:
    - exploratory tail probes showed drift signals on direct-file runs, but the
      canonical `baseline_hh.py` wrapper surface still revalidated cleanly
      under the publish subset on the current source tree
- Current recovery note:
  - the active wrapper moved from `v176` to `v177` because `v177` preserved
    the `v176` Family B guard rows while reducing the remaining prob27-like
    T tail on the current tree
  - canonical evidence for the active trusted line:
    - representative tier smoke:
      `reports/ogc2026_reboot_v001/smoke_reboot_v177_tier9_20260625_001/`
    - targeted subtype smoke:
      `reports/ogc2026_reboot_v001/target_reboot_v177_prob27family_20260625_001/`
    - active wrapper publish subset:
      `reports/ogc2026_reboot_v001/verify_active_v177_publish_20260625_001/`
    - full:
      `reports/ogc2026_reboot_v001/full_reboot_v177_train40_20260625_001/`
    `reports/ogc2026_reboot_v001/verify_active_v142_restore_tail_20260621_001/`
    - `prob_27` timed out
    - `prob_40` passed with a large objective/T regression
  - interpretation:
    - the workspace is currently in recovery mode
    - keep the active wrapper on the historical rollback line for now, but do
      not describe the current tree as re-trusted until a fresh canonical
      revalidation closes cleanly
  - latest recovery subset check on the current wrapper surface:
    `reports/ogc2026_reboot_v001/verify_active_v142_recovery_subset_20260620_001/`
    - accepted `4/4`; timeout `0`, invalid `0`
    - but the historically sensitive tail rows still did not reproduce their
      trusted values:
      - `prob_27`: `76200619 / T=5541 -> 77480587 / T=5637`
      - `prob_33`: `26172225 / T=3805 -> 26500068 / T=3854`
      - `prob_38`: `151254848 / T=11120 -> 326689940 / T=24272`
      - `prob_40`: `5780789 / T=8429 -> 10130800 / T=10950`
    - interpretation:
      - the wrapper is still scoreable on this subset, but it is not currently
        trustworthy as a reproduced accepted BEST surface
  - latest rejected candidate checkpoint:
    `reports/ogc2026_reboot_v001/full_reboot_v150_train40_20260620_001/`
    - `v150` recovered the local `prob_33` row on representative smoke and on
      a targeted rerun, but full40 still failed at `accepted_for_score=37/40`
    - reopened runtime failures:
      - `prob_31` timeout at `75.27s`
      - `prob_32` timeout at `66.25s`
      - `prob_37` timeout at `90.03s`
    - surviving tail regressions remained large:
      - `prob_38`: `346034606 / T=25718`
      - `prob_40`: `11209127 / T=12041`
    - interpretation:
      - this confirms the current tree is still in recovery mode
      - do not publish the active wrapper as a re-trusted BEST yet
      - the next repair should stabilize the reopened runtime-risk family
        before any further `prob33-like` local tuning
  - latest scoreable recovery candidate:
    `reports/ogc2026_reboot_v001/full_reboot_v152_train40_20260621_001/`
    - accepted_for_score `40/40`
    - timeout `0`, invalid `0`
    - it closed the reopened current-tree runtime backlog on
      `prob_31`, `prob_32`, `prob_33`, `prob_37`
    - but it remains far worse than the trusted historical `v142` full40
      benchmark on avg objective and avg T, so it is a recovery parent only,
      not the trusted active BEST
- Historical note:
  - `v123` remains the historical score-improving step over `v122`.
  - `v132` remains the last plateau-stable recovery line and rollback target.
  - `v133` remains a historical accepted improvement over `v132`, but only as
    non-active evidence because of the `prob_40` runtime cliff.
  - `v136` remains the accepted parent line and rollback target for the new
    prob40-like tail repair.
  - `v137` remains a training-best-only direct-file improvement over `v136`,
    but it is not the trusted active BEST because the direct
    `baseline_hh.py` surface did not reproduce the accepted `prob_40` gain.
  - `v146` remains a score-improving candidate over `v142` on direct/full and
    wrapper/publish-subset evidence, but it is not the trusted active BEST
    because the canonical wrapper full40 recheck reopened `prob_39` and
    `prob_40` regressions outside its intended target slice.
- Latest current-tree trusted BEST note (`2026-06-25`, v176 full40 publish):
  - canonical full evidence:
    `reports/ogc2026_reboot_v001/full_reboot_v176_train40_20260625_001/`
  - accepted `40/40`; timeout `0`, invalid `0`
  - current-tree improvement versus recovery parent `v152`:
    - Total Objective `840,910,136 -> 615,747,848`
    - Avg Objective `21,022,753.4 -> 15,393,696.2`
    - Total T `90,386 -> 63,372`
    - Avg T `2,259.65 -> 1,584.3`
    - Max Runtime `59.53s -> 55.68s`
  - historical comparison:
    - historical `v142` still has stronger old full evidence
      (`601,403,041`, `T=61,285`)
    - but the current wrapper surface did not reproduce that line cleanly on
      revalidation, so `v142` is not being published as the active BEST
  - interpretation:
    - `v176` is the strongest current-tree reproducible full40 line
    - publish `v176` as the tracked active wrapper target
    - keep the historical `v142` evidence recorded only as stronger-but-drifted
      reference history, not as the current trusted active BEST
  - active wrapper publish subset recheck:
    `reports/ogc2026_reboot_v001/verify_active_v176_publish_20260625_001/`
    - accepted `5/5`; timeout `0`, invalid `0`
    - sensitive tail rows stayed scoreable on the wrapper surface:
      - `prob_38`: `151254848 / T=11120`
      - `prob_39`: `48160369 / T=3521`
      - `prob_40`: `5780789 / T=8429`
- `v096` remains the last team-shared historical benchmark report reference:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
- Rollback target:
  `reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135`
- Canonical note:
  - the direct `baseline_hh` surface is the only canonical score-claim surface.
  - the current active wrapper is the historical `v142` rollback line, not a
    freshly re-trusted canonical BEST on the current source tree.
  - `v146` is held as candidate-only evidence until its `prob_27` gain is
    reproduced on a full canonical wrapper surface without reopening non-target
    tail regressions.
  - the `v146` selector stack is feature-based and time-aware.
  - inherited legacy fallback layers below some historical branches still
    contain older name-based branches; removing that legacy identity
    dependence remains future cleanup work.
- Recovery checkpoint note (`2026-06-21`):
  - `v151` and `v153` are now closed as rejected family experiments.
  - `v152` is the newest scoreable current-tree recovery parent
    (`accepted_for_score=40/40`), but not a trusted BEST promotion candidate.
  - publish the current state as recovery evidence only unless a fresh
    canonical wrapper revalidation reproduces trusted `v142` behavior again.
- Latest recovery checkpoint note (`2026-06-25`, active drift recheck):
  - active wrapper recheck:
    `reports/ogc2026_reboot_v001/verify_active_v142_recheck_20260625_001/`
    - accepted `9/11`; timeout `2`, invalid `0`
    - blocking rows:
      - `prob_33`: timeout at `63.50s`
      - `prob_37`: subprocess timeout at `90.02s`
    - major current-tree drift reopened on historical tail rows:
      - `prob_27`: `76200619 / T=5541 -> 77480587 / T=5637`
      - `prob_38`: `151254848 / T=11120 -> 382903971 / T=28497`
      - `prob_39`: `48160369 / T=3521 -> 48743275 / T=3563`
  - recovery parent recheck:
    `reports/ogc2026_reboot_v001/verify_reboot_v152_recheck_20260625_001/`
    - accepted `11/11`; timeout `0`, invalid `0`
    - current-tree parent rows stayed scoreable:
      - `prob_27`: `76200619 / T=5541`
      - `prob_33`: `26172225 / T=3805`
      - `prob_37`: `21777210 / T=5234`
      - `prob_38`: `151254848 / T=11120`
      - `prob_39`: `48160369 / T=3521`
  - interpretation:
    - the current `baseline_hh.py` wrapper surface is not trustworthy as a
      reproduced accepted BEST on this source tree
    - the newest smoke-valid current-tree recovery parent is now `v152`
    - keep the active wrapper on the historical rollback line for now, but do
      not describe it as trusted BEST until a fresh canonical full surface is
      revalidated cleanly
- Latest recovery checkpoint note (`2026-06-21`, prob40-family narrow-builder audit):
  - `v158` closed as rejected for promotion:
    `reports/ogc2026_reboot_v001/validation_note_20260621_v158.md`
  - `v158` did prove a strong current-tree prob40-family improvement:
    - targeted compare:
      `prob_40: 13048125 / T=19319 -> 7117822 / T=10439`
  - but its canonical full40 run failed scoreability:
    `reports/ogc2026_reboot_v001/full_reboot_v158_train40_20260621_001/`
    - `accepted_for_score=39/40`
    - `prob_33` timed out at `61.069551s`
  - the same drift also reopened under the parent `v152` on a focused recheck:
    `reports/ogc2026_reboot_v001/verify_reboot_v158_prob31_prob33_prob40_20260621_001/`
    - `v152 prob_33`: timeout at `62.243792s`
  - interpretation:
    - the current tree is still in runtime-reliability recovery mode
    - keep the wrapper on historical `v142` rollback semantics
    - do not publish the active surface as a newly trusted BEST
    - the next repair target is the prob33-like runtime cliff, while preserving
      the prob40-family signal isolated by `v158`
- Latest live runtime note (`2026-06-21`, tier-smoke drift after publish):
  - fresh tier smoke on the current recovery parent surface:
    `reports/ogc2026_reboot_v001/smoke_reboot_v160_tier9_20260621_001/`
  - the same current-tree runtime backlog has now shifted again:
    - `v152 prob_33`: TIMEOUT `61.470279s`
    - `v160 prob_27`: TIMEOUT `60.687807s`
  - interpretation:
    - the current tree does not currently have a trustworthy scoreable parent
      surface, even at the tier-representative smoke layer
    - next work should treat `prob_27` and `prob_33` as a joint runtime
      stabilization problem before any renewed BEST claim
- Latest joint-guard note (`2026-06-21`, v161 smoke):
  - joint runtime guards on top of trusted `v142`:
    `reports/ogc2026_reboot_v001/smoke_reboot_v161_tier9_20260621_001/`
  - targeted runtime families did recover:
    - `prob_27`: TIMEOUT under direct `v142` row -> PASS under `v161`
    - `prob_33`: TIMEOUT under direct `v142` row -> PASS under `v161`
  - but non-target `prob_40` still timed out under `v161`, even though that
    row should have delegated to the inherited `v142` path
  - interpretation:
    - the current blocker is no longer just feature-family runtime risk
    - same-process drift / inherited mutable state is now a first-class hidden
      risk on the current tree
- Latest delegated-budget note (`2026-06-21`, v162 smoke):
  - remaining-budget propagation on top of the same `v161` family selectors:
    `reports/ogc2026_reboot_v001/smoke_reboot_v162_tier9_20260621_001/`
  - it did improve part of the current-tree runtime picture:
    - `prob_33`: TIMEOUT under direct `v142` row -> PASS under `v162`
    - `prob_40`: remained PASS and improved
      `18230025 / T=27087 -> 17499131 / T=25996`
  - but the smoke still failed:
    - `prob_27`: TIMEOUT persisted under `v162` at `65.196941s`
    - `prob_6`: accepted, but regressed badly
      `3991577 / T=118 -> 16554568 / T=542`
  - interpretation:
    - delegated budget reset was a real hidden cost in the wrapper chain
    - fixing only that is not enough to restore a trustworthy parent surface
    - the current tree remains in recovery mode; do not publish the active
      wrapper as a re-trusted BEST yet
- Latest subtype-audit note (`2026-06-21`, post-v162 plateau checkpoint):
  - trusted historical full40 evidence is still:
    `reports/ogc2026_reboot_v001/full_reboot_v142_train40_20260620_001/`
    with `accepted_for_score=40/40`, timeout `0`, invalid `0`
  - but fresh current-tree targeted revalidation still does not justify a BEST
    publish:
    - `prob27-like` direct probe:
      `reports/ogc2026_reboot_v001/probe_v142_v146_prob27like_20260621_001/`
      - `v146` restored `prob_27` to PASS `58.677993s`
      - but the same path made sibling `prob_25` fail by time limit
        at `64.784196s`
    - xlarge-lowproc direct audit:
      `reports/ogc2026_reboot_v001/probe_v142_v072_xlarge_lowproc_20260621_001/`
      - direct `v072` did not beat current-tree `v142` on `prob_39`
      - `prob_37` remained unstable / timed out
    - xlarge-lowproc guarded audit:
      `reports/ogc2026_reboot_v001/target_v142_v143_xlarge_lowproc_20260621_001/`
      - `v143` improved `prob_39` and `prob_40`
      - but still did not recover `prob_37`
  - interpretation:
    - current active wrapper remains a recovery rollback surface only
    - the strongest next coherent hypothesis is now a narrow
      `prob27-like`-only guard that preserves the useful `v146` runtime fix
      without activating on sibling `prob_25`
    - do not publish the active wrapper as a re-trusted BEST until that
      current-tree recovery line reproduces scoreable canonical behavior
- Latest recovery checkpoint note (`2026-06-23`, v171 family guard audit):
  - representative tier smoke:
    `reports/ogc2026_reboot_v001/smoke_reboot_v171_tier9_20260621_001/`
    - `accepted_for_score=9/9`, timeout `0`, invalid `0`
    - recovered the intended early-exit rows on the current tree:
      - `prob_25`: `1512671 / T=2176 / 32.20s`
      - `prob_27`: `78787221 / T=5735 / 44.12s`
      - `prob_33`: `66465567 / T=9821 / 33.85s`
  - targeted runtime-family smoke:
    `reports/ogc2026_reboot_v001/target_reboot_v171_runtime_family_20260621_001/`
    - `accepted_for_score=7/8`, timeout `1`, invalid `0`
    - remaining blocker:
      - `prob_37`: TIMEOUT `90944439 / T=25911 / 73.74s`
    - large high-T tail also remained open:
      - `prob_31`: `295623767 / T=21938`
      - `prob_38`: `1120394778 / T=83806`
      - `prob_39`: `251183395 / T=18737`
      - `prob_40`: `8026436 / T=11795`
  - interpretation:
    - `v171` restored the narrow `2bay/highproc/concentrated` slice and kept
      the `prob33-like` direct restore alive
    - but the runtime-risk Family B guard still failed on `prob_37`, so the
      candidate is not scoreable enough to justify full40 or BEST promotion
    - publish this checkpoint as recovery-only, not as a trusted BEST refresh
