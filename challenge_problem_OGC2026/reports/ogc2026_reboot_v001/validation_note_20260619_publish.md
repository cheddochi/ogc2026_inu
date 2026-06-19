# HH Validation Note - 2026-06-19

## Validation scope

- Checked that no Python benchmark, probe, or revalidation process was running
  before publish checkpoint work.
- Re-checked the active entrypoint and evidence chain:
  - `ogc2026/baseline/baseline_hh.py`
  - `ogc2026/baseline/alg_versions/ACTIVE_VERSION.md`
  - `ogc2026/baseline/alg_versions/VERSION_LOG.md`
  - `reports/ogc2026_reboot_v001/full_reboot_v096_train40_20260619_001/`

## Active source hashes

- `ogc2026/baseline/alg_versions/reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094.py`
  - sha256 `97bf1ffd319ac0c2a7bd2e601015799bda044b6ca330c96910626adc93dc4dfc`

## Active wrapper status

- `baseline_hh.py` currently imports
  `reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094`.
- The wrapper comment explicitly marks this as a historical accepted checkpoint
  and a recovery target, not a current-source trusted BEST.

## Trust decision

- Historical evidence exists and is preserved.
- Current-source trust is not re-established because:
  - `v096` current-source rechecks timed out on `prob_31` and `prob_37`
  - fallback recheck of `v083` only reached `39/40`
  - latest extension `v104` failed targeted scoreable smoke with two timeouts

## Publish conclusion

- This checkpoint should be published as a recovery/failure checkpoint.
- It should not claim that the current active source is a trusted accepted BEST.
