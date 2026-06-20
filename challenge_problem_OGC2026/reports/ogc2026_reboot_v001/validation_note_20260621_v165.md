# Validation Note: reboot_v165_20260621_0755_v142_flattened_main_surface

- Decision: `rejected`

## Goal of the test

- This was a structural control test.
- The question was:
  does a flattened main-module copy of the `v142` body reproduce direct `v142`
  more faithfully than an imported delegate wrapper?

## Evidence

- Probe bundle:
  `reports/ogc2026_reboot_v001/probe_v142_v165_flattened_surface_20260621_001/`

## Result

- No. The flattened copy still drifted materially.
- Representative deltas:
  - `prob_1`:
    `1076550 / T=24 -> 5350203 / T=169`
  - `prob_19`:
    `4715273 / T=389 -> 17119187 / T=1545`
  - `prob_25`:
    `1671338 / T=2415 -> 1851356 / T=2688`
  - `prob_38`:
    `1082278381 / T=80949 -> 1212252311 / T=90691`

## Interpretation

- The current-tree hidden risk is broader than imported wrapper delegation.
- Simply flattening the `v142` body into a new main module is not enough to
  recover a trustworthy parent surface.
- The next useful structural base should therefore come from a line with its
  own direct current-tree smoke evidence rather than from trying to reuse `v142`
  as a newly stable parent.

## Next move

- Use the direct current-tree `v158` surface as the next structural base.
- Inline only the useful prob33-like direct guard from `v159` on top of that
  direct surface and test whether it preserves the `v158` smoke stability while
  recovering `prob_33`.
