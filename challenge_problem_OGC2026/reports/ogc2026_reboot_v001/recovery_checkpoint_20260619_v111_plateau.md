# Recovery Checkpoint 2026-06-19 22:00 KST

Current active surface still points to historical
`reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`, but that
wrapper is still a recovery surface only and must not be published as the
current trusted BEST.

Why this is a recovery/failure checkpoint instead of an accepted-BEST publish:

- `ogc2026/baseline/baseline_hh.py` still wires historical `v096`.
- `ogc2026/baseline/alg_versions/ACTIVE_VERSION.md` explicitly says that
  historical `v096` is not currently trusted under the present source state.
- the historical `v096` train40 evidence is still scoreable:
  - full path:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`
  - accepted_for_score `40/40`
  - timeout `0`
  - avg objective `15096298.7`
  - avg T `1558.675`
- but current-source rechecks already broke that trust claim:
  - `prob_31` timeout:
    `reports/ogc2026_reboot_v001/target_recheck_v096_fourbay_runtime_20260619_001/`
  - `prob_37` timeout:
    `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/`

Current leading current-source recovery candidate:

- version:
  `reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108`
- full evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v109_train40_20260619_001/`
- scoreable status:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
- averages:
  - avg objective `15111152.25`
  - avg T `1545.5`
  - avg L `2623.75`
  - avg P `4187.025`
  - runtime max `58.032762s`

Why `v109` is still not promoted to trusted BEST:

- it is the best current-source recovery line so far
- it beats historical `v096` on avg T
- but it still loses on avg objective by `14853.55`
- the remaining gap is still concentrated in the historical pain rows:
  - `prob_31`: objective `39781302 -> 40328756`, T `2751 -> 2792`
  - `prob_37`: objective `17454197 -> 17949088`, T `3961 -> 4040`

What closed during this checkpoint cycle:

- `v110` was rejected:
  - cheap prob37-like fast-single replay did not improve the target row
  - off-target `prob_38` drifted worse during the targeted guard
- `v111` stayed only as a plateau-side candidate:
  - scoreable representative smoke and targeted guards passed
  - `prob_31 @ 60s` held the good row but did not beat the existing `v109`
  - `prob_31 @ 45s` improved slightly, but not enough to justify a full train40

What this checkpoint publishes:

- historical accepted benchmark evidence for `v096`
- current-source full evidence for the leading `v109` recovery candidate
- the updated `VERSION_LOG.md` closure for `v110` and `v111`
- plateau backlog notes for the next T-first cycle

Bottom line:

- historical best evidence still belongs to `v096`
- current active wrapper remains a recovery surface only
- no new trusted accepted BEST is being claimed in this publish
- next work should target a genuine T-zero breakthrough that also preserves the
  current-source `40/40` scoreable line
