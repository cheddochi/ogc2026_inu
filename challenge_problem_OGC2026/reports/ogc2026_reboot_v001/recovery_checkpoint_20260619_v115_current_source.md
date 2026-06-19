# Recovery Checkpoint 2026-06-19 23:23 KST

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
  - shared report:
    `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/benchmark_report.md`
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
  `reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114`
- full evidence:
  `reports/ogc2026_reboot_v001/full_reboot_v115_train40_20260620_001/`
- scoreable status:
  - accepted_for_score `40/40`
  - timeout `0`
  - invalid `0`
- averages:
  - avg objective `15106365.725`
  - avg T `1545.1`
  - avg L `2616.85`
  - avg P `4189.15`
  - runtime max `58.029289s`

Why `v115` is still not promoted to trusted BEST:

- it is the best current-source recovery line so far
- it improves the prior current-source `v109` line without creating any new
  scoreability failures
- it beats historical `v096` on avg T, avg L, and runtime max
- but it still loses on avg objective by `10067.025`
- that remaining gap is now concentrated mainly in:
  - `prob_37`: objective `17454197 -> 17949088`, T `3961 -> 4040`
  - `prob_31`: objective `39781302 -> 40137295`, T `2751 -> 2776`
- offsetting improvements already exist in:
  - `prob_40`: objective `6333528 -> 5910122`, T `9268 -> 8622`
  - `prob_3`: objective `213297 -> 188500`, T `1 -> 0`

What closed during this checkpoint cycle:

- `v115` finished all remaining gates cleanly:
  - target sanity passed
  - representative smoke passed
  - targeted sibling guards passed
  - `prob_31 @ 45s` stress passed
  - full train40 passed at `40/40`
- versus `v109`, only the intended prob31-like row changed:
  - `prob_31`: objective `40328756 -> 40137295`
  - T `2792 -> 2776`
  - runtime about `49.71s -> 44.91s`

What this checkpoint publishes:

- updated `VERSION_LOG.md` closure for `v115`
- the updated subtype backlog after the prob31-like recovery cycle
- historical accepted benchmark evidence for `v096`, including the shared
  markdown report
- current-source full evidence for the leading `v115` recovery candidate
- targeted guard and short-stress evidence that explain why `v115` is real but
  still not yet a trusted accepted BEST

Bottom line:

- historical best evidence still belongs to `v096`
- current active wrapper remains a recovery surface only
- `v115` is now the leading current-source `40/40` recovery candidate
- no new trusted accepted BEST is being claimed in this publish
