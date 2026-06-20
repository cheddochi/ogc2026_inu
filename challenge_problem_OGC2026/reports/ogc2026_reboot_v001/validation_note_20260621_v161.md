# Validation Note: reboot_v161_20260621_joint_runtime_guards_on_v142

- Decision: `rejected`
- Reason:
  - The two targeted runtime guards did what they were supposed to do:
    - `prob_27` became scoreable again under the current tree
    - `prob_33` became scoreable again with clear runtime margin
  - But the tier-representative smoke still failed because non-target
    `prob_40` timed out on the same run.
  - The more important hidden-risk signal is that `v161 prob_40` should have
    delegated to the same `v142` path as the direct `v142 prob_40` row in the
    same smoke, yet the two rows produced materially different outcomes. That
    points to same-process state drift or mutable global state in the inherited
    chain, not just a narrow family selector miss.

## Evidence

- Tier-representative smoke:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v161_tier9_20260621_001/`
  - smoke rows:
    - `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_19`,
      `prob_25`, `prob_27`, `prob_33`, `prob_40`
  - `v142` in the same run:
    - `prob_27`: TIMEOUT `77480587 / T=5637 / 65.84s`
    - `prob_33`: TIMEOUT `41926242 / T=6176 / 62.98s`
    - `prob_40`: PASS `18230025 / T=27087 / 58.11s`
  - `v161` in the same run:
    - `prob_27`: PASS `77480587 / T=5637 / 58.92s`
    - `prob_33`: PASS `33726859 / T=4907 / 45.94s`
    - `prob_40`: TIMEOUT `16476222 / T=24454 / 60.81s`

## Interpretation

- The joint `prob27-like` + `prob33-like` runtime hypothesis is directionally
  correct for those two families.
- It is not sufficient for promotion because the surrounding inherited surface
  is still not deterministic enough inside a single benchmark process.
- The next coherent move should target state stability itself:
  - isolate or reset inherited mutable state in the `v142` chain, or
  - replace the remaining non-target delegated warm-start path with a stable
    direct builder on the rows that still drift under same-process smoke.
