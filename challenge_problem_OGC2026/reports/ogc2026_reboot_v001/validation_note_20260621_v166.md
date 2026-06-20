# Validation Note: reboot_v166_20260621_0812_v158_flat_prob33_guard

- Decision: `rejected`

## What worked

- Representative tier smoke:
  `reports/ogc2026_reboot_v001/smoke_reboot_v166_tier9_20260621_001/`
- The direct prob33-like guard did recover the intended blocker:
  - `prob_33`:
    `159070997 / T=23225 / 64.23s`
    ->
    `100765612 / T=14795 / 46.20s`

## Why it is still rejected

- The same smoke remained only `8/9 scoreable`.
- Fixing `prob_33` reopened `prob_27`:
  - `prob_27`:
    `78787221 / T=5735 / 57.90s`
    ->
    `78787221 / T=5735 / 61.73s`
    which is a timeout under the official limit.

## Hidden-risk pattern

- Current-tree runtime behavior is still coupled across the same representative
  smoke surface.
- Non-target rows also moved materially:
  - `prob_1`: `693901 / T=11 -> 15198382 / T=509`
  - `prob_16`: `2038247 / T=15 -> 176817 / T=0`
  - `prob_25`: `2628433 / T=3820 -> 1499211 / T=2141`
  - `prob_40`: `14311856 / T=21242 -> 15650653 / T=23246`

## Interpretation

- The direct prob33-like builder is a useful component.
- But in the current tree it behaves as a trade against the prob27-like runtime
  cliff rather than as a clean isolated repair.
- The next coherent move should treat prob27-like and prob33-like as a coupled
  runtime-stability family and design one shared parent-stability hypothesis,
  instead of continuing to repair either family in isolation.
