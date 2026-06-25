## 2026-06-25 Recovery Checkpoint

- scope:
  - current active wrapper surface: `ogc2026/baseline/baseline_hh.py`
  - historical trusted BEST evidence: `full_reboot_v142_train40_20260620_001`
  - recovery parent recheck: `reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151`

### Active wrapper drift recheck

- run:
  - `reports/ogc2026_reboot_v001/verify_active_v142_recheck_20260625_001/`
- result:
  - accepted_for_score `9/11`
  - timeout `2`
  - invalid/error `0`
- key failures:
  - `prob_33`: TIMEOUT, runtime `63.50s`, `objective=34809210`, `T=5110`
  - `prob_37`: TIMEOUT, runtime `90.02s`
- major regressions versus historical trusted v142 rows:
  - `prob_27`: `76200619 / T=5541 -> 77480587 / T=5637`
  - `prob_38`: `151254848 / T=11120 -> 382903971 / T=28497`
  - `prob_39`: `48160369 / T=3521 -> 48743275 / T=3563`
- interpretation:
  - the current `baseline_hh.py` wrapper surface is not trustworthy as a
    reproduced accepted BEST on this source tree.
  - keep historical `v142` evidence as historical-only.
  - do not publish the current wrapper as trusted BEST.

### Recovery parent recheck

- run:
  - `reports/ogc2026_reboot_v001/verify_reboot_v152_recheck_20260625_001/`
- result:
  - accepted_for_score `11/11`
  - timeout `0`
  - invalid/error `0`
- notable rows:
  - `prob_27`: `76200619 / T=5541`
  - `prob_33`: `26172225 / T=3805`
  - `prob_37`: `21777210 / T=5234`
  - `prob_38`: `151254848 / T=11120`
  - `prob_39`: `48160369 / T=3521`
- interpretation:
  - `v152` is currently the strongest smoke-validated recovery parent on the
    current source tree among the surfaces rechecked on 2026-06-25.
  - `v152` is still worse than the historical trusted `v142` full40 benchmark,
    so it is recovery-only, not BEST.

### Next cycle

- plateau mode: `true`
- meaningful_progress: `false`
- plateau_reason:
  - active wrapper trust is broken on the current tree, so BEST promotion is
    blocked until a scoreable recovery parent is stabilized and a new
    T-reducing candidate is validated from that parent.
- next parent:
  - `reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151.py`
- next subtype target:
  - `medium/3bay/lowproc/runtime-risk` (`prob_37`, `prob_39`) remains the
    repeated high-T family from trusted analysis, but the current-tree active
    drift also reopens `prob_33`.
- next hypothesis direction:
  - avoid broad diffuse-family direct overrides that hit `prob_32` and the
    concentrated `prob_39` sibling together.
  - start from `v152` and use a narrower, feature-gated direct repair that can
    isolate the boundary runtime member without reopening sibling rows.
