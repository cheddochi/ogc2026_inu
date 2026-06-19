# Subtype Backlog after v109

Context:

- historical active surface: `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`
- current status of that surface: historical accepted evidence exists, but current-source rechecks are not trusted
- current-source leading candidate: `reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108`

Current-source candidate summary:

- full path: `reports/ogc2026_reboot_v001/full_reboot_v109_train40_20260619_001/`
- accepted_for_score `40/40`
- timeout `0`
- invalid `0`
- avg objective `15111152.25`
- avg T `1545.5`
- avg L `2623.75`
- avg P `4187.025`

Historical-v096 comparison backlog:

- remaining objective/T gap is concentrated in:
  - `prob_31`: objective `39781302 -> 40328756`, T `2751 -> 2792`
  - `prob_37`: objective `17454197 -> 17949088`, T `3961 -> 4040`
- already repaired or improved families:
  - prob40-like:
    - `prob_40`: objective `6333528 -> 5910122`, T `9268 -> 8622`
  - prob38-like recovered on the accepted benchmark lineage, but single-row
    current-source reruns still show drift risk and must be guarded carefully

31-40 feature taxonomy snapshot:

| Instance | Bays | Blocks | proc_mean | slack_mean | workload_mean | pref_conc | pref_pressure | imbalance | Class note |
|----------|------|--------|-----------|------------|---------------|-----------|---------------|-----------|------------|
| prob_31 | 4 | 200 | 21.495 | 4.930 | 128.560 | 0.795 | 0.731 | 0.790 | 4-bay concentrated runtime-risk |
| prob_32 | 3 | 200 | 11.455 | 2.410 | 94.125 | 0.345 | 0.359 | 0.030 | 3-bay medium low-pressure |
| prob_33 | 3 | 200 | 16.795 | 3.835 | 92.060 | 0.445 | 0.414 | 0.225 | 3-bay mid-proc diffuse |
| prob_34 | 4 | 200 | 16.435 | 3.690 | 128.850 | 0.335 | 0.303 | 0.140 | 4-bay diffuse |
| prob_35 | 3 | 200 | 11.380 | 2.420 | 132.225 | 0.595 | 0.533 | 0.440 | 3-bay mixed pressure |
| prob_36 | 4 | 250 | 11.384 | 2.304 | 89.800 | 0.808 | 0.701 | 0.792 | 4-bay concentrated low-proc |
| prob_37 | 3 | 250 | 11.508 | 2.276 | 143.232 | 0.400 | 0.391 | 0.112 | 3-bay xlarge low-proc diffuse prob37-like |
| prob_38 | 3 | 250 | 21.348 | 4.480 | 112.784 | 0.568 | 0.516 | 0.424 | 3-bay high-proc prob38-like |
| prob_39 | 3 | 250 | 11.120 | 2.200 | 111.832 | 0.572 | 0.538 | 0.424 | 3-bay xlarge low-proc concentrated prob39-like |
| prob_40 | 4 | 250 | 21.688 | 4.928 | 174.664 | 0.760 | 0.695 | 0.744 | 4-bay xlarge high-workload prob40-like |

Implications:

- `prob_37` and `prob_39` are in the same coarse `3-bay xlarge low-proc` family
- they split cleanly by preference concentration / pressure / imbalance:
  - `prob_37` is diffuse / low-pressure
  - `prob_39` is concentrated / higher-pressure / runtime-risk
- a broad family replay is too risky on the current source state:
  - short-45 compare:
    `reports/ogc2026_reboot_v001/compare_v109_v098_prob37_prob39_short45_20260619_001/`
    - `v109 prob_37`: not scoreable at `45.217551s`
    - `v098 prob_37`: subprocess timeout `67.528688s`
    - `v098 prob_39`: runtime `45.442129s`, not scoreable
  - long-60 compare:
    `reports/ogc2026_reboot_v001/compare_v109_v098_prob37_prob39_long60_20260619_001/`
    - `v098 prob_37`: objective improved but runtime `63.290928s`, not scoreable
    - `v098 prob_39`: tiny objective gain only

Representative tier smoke set for the next post-v110 cycle:

- tier `1-4`: `prob_1`
- tier `5-8`: `prob_6`
- tier `9-12`: `prob_11`
- tier `13-16`: `prob_13`
- tier `17-20`: `prob_19`
- tier `21-25`: `prob_25`
- tier `26-30`: `prob_27`
- tier `31-35`: `prob_31`
- tier `36-40`: `prob_37` or `prob_39` depending on whether the next hypothesis targets diffuse or concentrated xlarge-lowproc subtype

Next hypothesis direction after v110 rejection:

- do not reopen the entire xlarge-lowproc family
- the prob37-like cheap move stack no longer improves the `v109` warm start
- the next structural T-breakthrough hypothesis should shift toward the prob31-like 4-bay concentrated runtime-risk family or a more stable source of prob38-like recovery under current-source drift
