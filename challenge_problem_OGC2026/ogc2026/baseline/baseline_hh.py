"""HH active submission wrapper.

Current active working line:
    reboot_v176_20260625_prob38like_pair_quantile_on_v152

Publish-trust note:
    v176 is now the strongest current-tree reproducible full40 line on the
    tracked wrapper surface. Historical accepted evidence for v142 is still
    stronger, but the current source tree does not reproduce that historical
    line cleanly, so v176 is promoted as the trusted current-tree BEST rather
    than as a reclaimed all-time historical BEST.
"""

from alg_versions import reboot_v176_20260625_prob38like_pair_quantile_on_v152 as active


ACTIVE_VERSION = "reboot_v176_20260625_prob38like_pair_quantile_on_v152"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
