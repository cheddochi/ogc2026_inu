# v133 publish validation note (2026-06-20)

- Branch: `hh_algorithm_loop`
- Candidate active line: `reboot_v133_20260620_1705_prob40like_narrow_quantile_on_v132`
- Active surface: `ogc2026/baseline/baseline_hh.py`
- Baseline wrapper SHA256: `BAAEDBC7C3BC5074EBC59C87C4462D3BD9926D644A083FE01F1C07008574FCB9`
- v133 source SHA256: `836908D1957AA42D461FD8132F2848ADAE7C0F9E5D1CB52BA85E879EA0421287`

## Historical accepted evidence

- smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v133_tier9_20260620_001/`
- targeted:
  `reports/ogc2026_reboot_v001/target_reboot_v133_prob40like_20260620_001/`
- short stress:
  `reports/ogc2026_reboot_v001/stress_reboot_v133_prob40like_short45_20260620_001/`
- full:
  `reports/ogc2026_reboot_v001/full_reboot_v133_train40_20260620_001/`

Historical accepted full40 headline:

- `accepted_for_score=40/40`
- `objective_avg=15069943.325`
- `obj1_avg(T)=1538.825`
- `obj2_avg(L)=2683.325`
- `obj3_avg(P)=4185.775`
- `runtime_max=56.899351`

## Earlier direct/wrapper revalidation

- path:
  `reports/ogc2026_reboot_v001/verify_active_v133_publish_20260620_001/`
- result:
  - `accepted_for_score=6/6`
  - direct `baseline_hh.py` reproduced the improved `prob_40` row
  - `myalgorithm.py` stayed scoreable but missed the `prob_40` move

## Latest publish revalidation

- path:
  `reports/ogc2026_reboot_v001/verify_active_v133_publish_20260620_002/`
- scope:
  - representative rows:
    `prob_1`, `prob_6`, `prob_11`, `prob_13`, `prob_19`, `prob_25`,
    `prob_27`, `prob_31`, `prob_33`, `prob_38`
  - runtime-sensitive rows:
    `prob_39`, `prob_40`
- result:
  - `accepted_for_score=12/12`
  - timeout `0`
  - invalid/error `0`
  - `prob_39` kept the stronger row:
    - objective `48160369`
    - `T=3521`
  - `prob_40` failed to reproduce the accepted improvement:
    - historical accepted row: objective `5860829`, `T=8549`
    - latest validation row: objective `5910122`, `T=8622`

## Runtime-cliff evidence

Earlier direct revalidation log (`verify_active_v133_publish_20260620_001`):

- `[baseline_hh reboot_v130] prob40like_quantile instance=prob_40 ... T=8549.0 objective=5860829.0`
- `[baseline_hh reboot_v133] selected_prob40like_quantile instance=prob_40 T=8549.0 objective=5860829.0`

Latest publish revalidation log (`verify_active_v133_publish_20260620_002`):

- `[baseline_hh reboot_v133] skip_prob40like_guard instance=prob_40 tier=standard remaining=12.48s reserve=4.80s base_T=8622.0`

Interpretation:

- the source did not drift away from v133
- the current failure mode is runtime/headroom instability on the direct
  `baseline_hh.py` surface
- because the active surface does not reproduce the accepted `prob_40` gain
  consistently enough, the line should not be published right now as a trusted
  accepted BEST
