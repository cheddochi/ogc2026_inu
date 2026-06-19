"""HH active submission wrapper.

Historical accepted checkpoint:
    reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094

Current-source note:
    The wrapper still points at v096 because it is the latest historically
    accepted train40 checkpoint, but current-source rechecks have reproduced
    runtime drift on prob31-like and prob37-like rows. Treat this wrapper as a
    recovery target until ACTIVE_VERSION.md and VERSION_LOG.md re-establish a
    source-consistent trusted BEST.
"""

from alg_versions import reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094 as active


ACTIVE_VERSION = "reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
