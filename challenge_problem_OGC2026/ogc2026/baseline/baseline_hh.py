"""HH active submission wrapper.

Current active working line:
    reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136

Publish-trust note:
    v142 is currently restored as the recovery rollback line because the newer
    v146 candidate reopened canonical wrapper drift. Historical accepted
    evidence for v142 still exists, but the current source tree is under
    revalidation and should not be described as a newly re-trusted BEST until
    the wrapper surface is stable again.
"""

from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as active


ACTIVE_VERSION = "reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
