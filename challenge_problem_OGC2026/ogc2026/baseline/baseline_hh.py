"""HH active submission wrapper.

Current active working line:
    reboot_v177_20260625_prob27like_micro_shortlist_on_v176

Publish-trust note:
    v177 is now the strongest current-tree reproducible full40 line on the
    tracked wrapper surface. Historical accepted evidence for v142 is still
    slightly stronger, but the current source tree does not reproduce that
    historical line cleanly, so v177 is promoted as the trusted current-tree
    BEST rather than as a reclaimed all-time historical BEST.
"""

from alg_versions import reboot_v177_20260625_prob27like_micro_shortlist_on_v176 as active


ACTIVE_VERSION = "reboot_v177_20260625_prob27like_micro_shortlist_on_v176"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
