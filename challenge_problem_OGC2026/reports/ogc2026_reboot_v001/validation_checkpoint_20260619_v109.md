# Validation Note for v109

Candidate:

- `reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108`

Hypothesis closed in this checkpoint:

- after the prob38like repair in `v108`, re-enable the deeper direct policy only for the prob40like feature class
- keep every non-target row on `v108`

Validation summary:

1. Targeted guard compare
   - path: `reports/ogc2026_reboot_v001/compare_v108_v109_prob31_prob39_prob40_20260619_001/`
   - result: `accepted_for_score=6/6`, timeout `0`, invalid `0`
   - effect:
     - `prob_31`: unchanged
     - `prob_39`: unchanged
     - `prob_40`: improved to objective `5910122`, T `8622`

2. Time-stress guard
   - path: `reports/ogc2026_reboot_v001/compare_v108_v109_prob40_short45_20260619_001/`
   - result: `accepted_for_score=2/2`
   - effect:
     - `prob_40 @ 45s`: objective `6743716 -> 5910122`
     - `prob_40 @ 45s`: T `9882 -> 8917`

3. Tier smoke
   - path: `reports/ogc2026_reboot_v001/smoke_reboot_v109_tier9_20260619_001/`
   - result: `accepted_for_score=9/9`, timeout `0`, invalid `0`

4. Full train40
   - path: `reports/ogc2026_reboot_v001/full_reboot_v109_train40_20260619_001/`
   - result: `accepted_for_score=40/40`, timeout `0`, invalid `0`
   - summary:
     - avg objective `15111152.25`
     - avg T `1545.5`
     - avg L `2623.75`
     - avg P `4187.025`
     - runtime max `58.032762s`

Interpretation:

- `v109` clearly improves the current-source recovery line over `v108`
- it also improves avg T below the historical `v096` benchmark
- it is still not safe to promote as trusted BEST because avg objective remains worse than historical `v096`, and the remaining deficit is concentrated in the prob31/prob37 family

Next likely hypothesis after this checkpoint:

- keep `v109` as parent
- target the 3-bay xlarge low-proc family with a stricter long-budget gate derived from the `v098` current-source signal
