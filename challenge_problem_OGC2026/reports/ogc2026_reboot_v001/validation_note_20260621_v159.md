# Validation Note: reboot_v159_20260621_prob33_guard_on_v158

- Decision: `rejected`
- Reason:
  - The new prob33-like direct guard worked on its own target row.
  - But tier-representative smoke reopened a timeout on untouched `prob_27`,
    which means the inherited `v158` parent surface is still too unstable to
    use as the base for promotion.

## Evidence

- Pre-candidate family diagnosis:
  - `reports/ogc2026_reboot_v001/diag_reboot_v159_prob33family_20260621_001/`
  - `reports/ogc2026_reboot_v001/diag_reboot_v159_prob33direct_20260621_001/`
  - these showed:
    - delegated `v152/v141/v142` paths can drift into timeout on `prob_33`
    - a direct `release_due` builder with a thin gap repair gives a stable
      current-tree fallback around:
      - `31180651 / T=4523`
      - total runtime about `46-48s`
- Tier-representative smoke:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v159_tier9_20260621_001/`
  - targeted rows:
    - `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_19`,
      `prob_25`, `prob_27`, `prob_33`, `prob_40`
  - `v159` outcome:
    - `prob_33`: PASS `28906951 / T=4204 / runtime=40.70s`
    - `prob_40`: PASS `7117822 / T=10439 / runtime=45.16s`
    - `prob_27`: TIMEOUT `77480587 / T=5637 / runtime=69.01s`

## Interpretation

- The prob33-like direct guard is usable.
- The actual failure came from selecting `v158` as the parent surface:
  - even untouched rows did not stay stable enough under smoke.
- The next coherent move should reuse the prob33-like direct guard, but place
  it on the more stable `v152` recovery parent while lifting in the prob40-like
  narrow direct builder explicitly instead of inheriting the whole `v158`
  surface.
