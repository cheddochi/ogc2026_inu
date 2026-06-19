# Recovery Checkpoint 2026-06-19

Current active surface still points to historical `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`, but that chain is not currently trusted under the present source state.

Why this is not an accepted-BEST publish:

- `baseline_hh.py` and `ACTIVE_VERSION.md` still reference historical `v096` only as an explicit recovery surface.
- current-source rechecks already showed runtime drift on the historical active chain:
  - `prob_31` timeout in `reports/ogc2026_reboot_v001/target_recheck_v096_fourbay_runtime_20260619_001/`
  - `prob_37` timeout in `reports/ogc2026_reboot_v001/probe_v096_prob37_20260619_001/`
- because of that drift, publishing the current wrapper as a trusted accepted BEST would be misleading.

Current best recovery candidate:

- candidate version: `reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108`
- full evidence: `reports/ogc2026_reboot_v001/full_reboot_v109_train40_20260619_001/`
- scoreable status: `accepted_for_score=40/40`, timeout `0`, invalid `0`
- full averages:
  - avg objective `15111152.25`
  - avg T `1545.5`
  - avg L `2623.75`
  - avg P `4187.025`
  - runtime max `58.032762s`

Why `v109` is still only a candidate:

- it improves the current-source recovery line and now beats historical `v096` on avg T
- but it still trails historical `v096` on avg objective by `14853.55`
- the remaining gap is concentrated in:
  - `prob_31`: objective `39781302 -> 40328756`, T `2751 -> 2792`
  - `prob_37`: objective `17454197 -> 17949088`, T `3961 -> 4040`

What this checkpoint preserves:

- the completed `v108` and `v109` source files
- the closed `VERSION_LOG.md` record for both candidates
- the historical accepted benchmark report for `v096`
- the current candidate full/smoke/target evidence for `v109`

Bottom line:

- historical best evidence still belongs to `v096`
- current active wrapper is a recovery target, not a freshly revalidated trusted BEST
- current source recovery is in progress, with `v109` as the leading candidate before the next family-specific hypothesis
