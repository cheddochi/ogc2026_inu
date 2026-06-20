# Validation Note: reboot_v162_20260621_budget_propagation_guards_on_v142

- Decision: `rejected`
- Reason:
  - The remaining-budget propagation hypothesis did recover useful behavior:
    - `prob_33` became scoreable again with strong runtime margin
    - `prob_40` stayed scoreable and improved on both objective and T
  - But the representative smoke still failed because:
    - `prob_27` remained a timeout at `65.196941s`
    - `prob_6` took a large accepted-but-bad regression
      (`3991577 / T=118 -> 16554568 / T=542`)
  - That means delegated timelimit reset is part of the runtime cliff, but not
    the whole `prob27-like` bottleneck.

## Evidence

- Tier-representative smoke:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v162_tier9_20260621_001/`
  - smoke rows:
    - `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_19`,
      `prob_25`, `prob_27`, `prob_33`, `prob_40`
  - `v142` in the same run:
    - `prob_27`: TIMEOUT `77480587 / T=5637 / 68.53s`
    - `prob_33`: TIMEOUT `40984512 / T=6036 / 63.95s`
    - `prob_40`: PASS `18230025 / T=27087 / 58.74s`
  - `v162` in the same run:
    - `prob_27`: TIMEOUT `77480587 / T=5637 / 65.20s`
    - `prob_33`: PASS `38323059 / T=5597 / 46.15s`
    - `prob_40`: PASS `17499131 / T=25996 / 58.69s`

## Interpretation

- Propagating remaining wall time to delegated children is worth keeping as a
  future building block:
  - it removed one non-target budget cliff
  - it did not harm the already-stable easy rows materially
- But this candidate is not safe to advance because the representative smoke
  was not fully scoreable and a non-target accepted row (`prob_6`) regressed
  sharply.
- The next coherent move should isolate the `prob27-like` path directly:
  - shrink work before entering the guarded child, or
  - replace the current delegated warm-start on that slice with a more direct
    bounded builder while preserving the budget-propagation lesson from `v162`.
