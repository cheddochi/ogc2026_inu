"""HH active submission wrapper.

Current trusted BEST:
    reboot_v050_20260617_2015_prob38like_release_aware

The wrapper points at the latest accepted best evidenced in VERSION_LOG.md and
the trusted full-train40 reports.
"""

from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as active


ACTIVE_VERSION = "reboot_v050_20260617_2015_prob38like_release_aware"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
