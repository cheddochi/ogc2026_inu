"""HH active submission wrapper.

Current active working line:
    reboot_v217_20260627_trackA_prob19_long_fourbay_repair_on_v212

Publish-trust note:
    v217 is the current-tree trusted BEST on the tracked baseline_hh surface.
    It preserves the trusted v212 Track A and runtime-cliff surface, then adds
    one narrow long four-bay tardy-repair specialist that lowers first20
    residual T on the prob_19-like subtype without changing the rest of the
    accepted surface.
"""

from alg_versions import reboot_v217_20260627_trackA_prob19_long_fourbay_repair_on_v212 as active


ACTIVE_VERSION = "reboot_v217_20260627_trackA_prob19_long_fourbay_repair_on_v212"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
