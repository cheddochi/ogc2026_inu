# Validation Note: reboot_v164_20260621_0742_v142_pure_delegate_surface

- Decision: `rejected`

## Goal of the test

- This was a control candidate, not a score-improvement hypothesis.
- The question was simple:
  can a wrapper that does nothing except call `v142.algorithm(...)` reproduce
  direct `v142` exactly on representative non-target rows?

## Evidence

- Probe bundle:
  `reports/ogc2026_reboot_v001/probe_v142_v164_delegate_surface_20260621_001/`

## Result

- No. The pure delegate surface still drifted materially away from direct
  `v142`.
- Representative deltas:
  - `prob_1`:
    `2108308 / T=60 -> 17195464 / T=578`
  - `prob_19`:
    `4715273 / T=389 -> 5986879 / T=509`
  - `prob_25`:
    `1798973 / T=2609 -> 1573893 / T=2267`
  - `prob_38`:
    `1167173816 / T=87306 -> 1058407054 / T=79156`

## Interpretation

- The hidden-risk is deeper than selector width or a specific repair kernel.
- Running `v142` as an imported delegated submodule is not behaviorally
  equivalent to running the same file as the main algorithm module.
- That means future real candidates should not be trusted if they rely on
  wrapper stacking over `v142` and assume the untouched non-target rows are
  preserved automatically.

## Next move

- Test a flattened direct-main-module copy of the `v142` surface first.
- If that flattened surface reproduces `v142` much more closely, use it as the
  base for the next real `prob33-like` runtime repair candidate.
