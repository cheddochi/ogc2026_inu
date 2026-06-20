# Validation Note: reboot_v158_20260621_prob40like_narrow_builder_on_v152

- Decision: `rejected`
- Reason:
  - The narrow prob40-like builder is real and strong on the current tree.
  - However, the canonical full40 run failed the scoreability gate at
    `accepted_for_score=39/40` because `prob_33` timed out.
  - A follow-up direct compare showed that the same `prob_33` timeout also
    reopened under the parent `v152`, so `v158` did not create the drift.
  - Even so, the candidate cannot be promoted while the canonical full40 surface
    is not scoreable.

## Evidence

- Tier-representative smoke:
  - `reports/ogc2026_reboot_v001/smoke_reboot_v158_tier9_20260621_001/`
  - `accepted_for_score=9/9`, timeout `0`, invalid `0`
- Targeted subtype compare:
  - `reports/ogc2026_reboot_v001/target_reboot_v158_prob40family_20260621_001/`
  - `accepted_for_score=6/6`, timeout `0`, invalid `0`
  - row deltas vs `v152`:
    - `prob_31`: `51965561 / T=3656 -> 53363711 / T=3757`
    - `prob_39`: unchanged at `48743275 / T=3563`
    - `prob_40`: `13048125 / T=19319 -> 7117822 / T=10439`
- Full40:
  - `reports/ogc2026_reboot_v001/full_reboot_v158_train40_20260621_001/`
  - `accepted_for_score=39/40`, timeout `1`, invalid `0`
  - failed row:
    - `prob_33`: `26500068 / T=3854 / L=1150 / P=5293 / runtime=61.069551s`
- Parent drift recheck:
  - `reports/ogc2026_reboot_v001/verify_reboot_v158_prob31_prob33_prob40_20260621_001/`
  - `v152` also timed out on `prob_33`:
    - `26500068 / T=3854 / runtime=62.243792s`
  - `v158` kept the large `prob_40` gain in the same check:
    - `13708345 / T=20310 -> 7117822 / T=10439`

## Interpretation

- `v158` isolated a useful current-tree prob40-family fix.
- The blocking issue for promotion is now the reopened prob33-like runtime
  drift on the delegated parent path, not the prob40 slice itself.
- The next coherent move should preserve the `v158` prob40-family signal while
  flattening or replacing the current prob33-like runtime-risk chain.

