# Validation note: v119 and v120 high-proc tail rejection (2026-06-20)

## Scope

- parent trusted historical line:
  `reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116`
- rejected candidates:
  - `reboot_v119_20260620_0635_highproc_pressure_shallow_portfolio_on_v117`
  - `reboot_v120_20260620_0705_highproc_tail_shallow_portfolio_on_v117`

## Evidence paths

- `v119` representative smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v119_tier9_20260620_001/`
- `v119` targeted family smoke:
  `reports/ogc2026_reboot_v001/target_reboot_v119_highproc_pressure_20260620_001/`
- `v120` representative smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v120_tier9_20260620_001/`
- `v120` family completion check:
  `reports/ogc2026_reboot_v001/target_reboot_v120_prob26_prob40_20260620_001/`

## Outcome summary

- `v119`
  - scoreability: preserved on smoke and target rows
  - effective result: no-op
  - root cause: reused stale selector from `v053` did not match the current
    feature band of the intended rows
- `v120`
  - scoreability: preserved on the checked rows
  - effective result: keep-best guard held on every row
  - root cause: once the selector was corrected, the shallow direct-order
    rebuild candidates were catastrophically worse than the warm start and only
    added runtime overhead

## Practical conclusion

- The residual high-proc tail family should not be attacked next with another
  shallow direct rebuild.
- The next coherent attempt should preserve the `v117` warm start and test
  bounded local moves / local repair instead.
