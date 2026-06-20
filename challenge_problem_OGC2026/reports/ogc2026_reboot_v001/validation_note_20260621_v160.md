# Validation Note: reboot_v160_20260621_prob33_prob40_direct_slices_on_v152

- Decision: `rejected`
- Reason:
  - The two explicit direct slices both worked:
    - `prob_33` became scoreable with a large runtime margin
    - `prob_40` kept the strong narrow-direct gain
  - But tier-representative smoke still failed because untouched `prob_27`
    timed out on the inherited parent surface.

## Evidence

- Tier-representative smoke:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v160_tier9_20260621_001/`
  - smoke rows:
    - `prob_1`, `prob_6`, `prob_11`, `prob_16`, `prob_19`,
      `prob_25`, `prob_27`, `prob_33`, `prob_40`
  - `v152` baseline in the same run:
    - `prob_33`: TIMEOUT `26500068 / T=3854 / 61.47s`
    - `prob_40`: PASS `12062727 / T=17844 / 58.68s`
  - `v160` candidate in the same run:
    - `prob_33`: PASS `28906951 / T=4204 / 40.85s`
    - `prob_40`: PASS `7117822 / T=10439 / 43.57s`
    - `prob_27`: TIMEOUT `77480587 / T=5637 / 60.69s`

## Interpretation

- The direct-slice mechanism is promising.
- The blocking issue is now broader than the two targeted slices:
  - the current parent surface is unstable across both `prob27-like` and
    `prob33-like` runtime-risk families.
- The next coherent move should stabilize those two runtime families together
  before replaying the prob40-like gain for any promotion attempt.
