# Publish checkpoint: v123 accepted, v124 rejected

- Branch:
  `hh_algorithm_loop`
- Checkpoint date:
  `2026-06-20`
- Publish mode:
  trusted accepted BEST checkpoint

## Active / trusted BEST

- Active wrapper:
  `ogc2026/baseline/baseline_hh.py`
- Active version id:
  `reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122`
- Trusted status:
  accepted and scoreable on the official `baseline_hh.algorithm(prob_info, timelimit)` surface

## Source hash snapshot

- `ogc2026/baseline/baseline_hh.py`
  - `sha256=9ADC1E24C6D028FA4F676D62BA63BB2BA5E7392D6198D09B6037ECC89553C809`
- `ogc2026/baseline/alg_versions/ACTIVE_VERSION.md`
  - `sha256=29A4ED20063600D02886D3CC2FB33A38B9FCE2D1FB1D7791481BEA094D82CB59`
- `ogc2026/baseline/alg_versions/VERSION_LOG.md`
  - `sha256=A888185AE59839C03C7FA1F5A55D2EFA6A2A55FBEB90FDD048FB1E64D7A6F548`
- `ogc2026/baseline/alg_versions/reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122.py`
  - `sha256=F6A5C73844E9109D1D5BEDD80F39B39D5DF22CD8EC8B3E62A03180EC7D9899C7`
- `ogc2026/baseline/alg_versions/reboot_v124_20260620_1125_fourbay_highproc_toptardy_quantile_on_v123.py`
  - `sha256=086AF2D520A7FE729814E98A1FD46C93032A2CB4D3B32C4E48369FD1E15CEB09`

## Trusted v123 evidence

- Representative smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v123_tier10_20260620_002/`
- Targeted subtype compare:
  `reports/ogc2026_reboot_v001/target_reboot_v123_threebay_highproc_20260620_001/`
- Runtime-risk subset revalidation:
  `reports/ogc2026_reboot_v001/verify_v123_runtime_subset_20260620_001/`
- Wrapper + active publish revalidation:
  `reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_001/`
- Accepted full benchmark:
  `reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/`

## Trusted v123 headline

- `accepted_for_score=40/40`
- `timed_out=0`
- `invalid=0`
- `avg objective=15071175.65`
- `total T=61626`
- `avg T=1540.65`
- `avg L=2674.325`
- `avg P=4187.625`
- `runtime_max=59.416431`

## Delta vs previous trusted v122

- improvement:
  - `prob_26`: objective `32253881 -> 31708207`, T `2345 -> 2305`
- T regressions:
  - none on the other 39 rows

## v124 candidate judgment

- Version:
  `reboot_v124_20260620_1125_fourbay_highproc_toptardy_quantile_on_v123`
- Decision:
  rejected
- Reason:
  - targeted four-bay move improved `prob_40`
  - full train40 still got worse on official objective because non-target
    runtime-risk row `prob_39` drifted to a weaker accepted result
- Key evidence:
  - targeted compare:
    `reports/ogc2026_reboot_v001/target_reboot_v124_fourbay_highproc_20260620_001/`
  - runtime-risk recheck:
    `reports/ogc2026_reboot_v001/verify_v124_prob39_20260620_001/`
  - rejected full benchmark:
    `reports/ogc2026_reboot_v001/full_reboot_v124_train40_20260620_001/`

## Publish scope

- This checkpoint publishes the current trusted accepted BEST (`v123`) and the
  minimum evidence needed to explain why `v124` is not promoted.
- Raw logs, raw solution dumps, and unfinished candidates remain intentionally
  excluded from the checkpoint.
