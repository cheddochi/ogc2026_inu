"""HH active submission wrapper.

Current active working line:
    reboot_v210_20260626_trackA_latest_feasible_tardy_repair

Publish-trust note:
    v210 is the current-tree trusted BEST on the tracked baseline_hh surface.
    It keeps the trusted v207 Track A portfolio shape and runtime-cliff guard,
    but adds a smaller mid-size four-bay tardy-repair candidate that improves
    the residual first20 backlog without reopening the prob19 runtime cliff.
"""

from alg_versions import reboot_v210_20260626_trackA_latest_feasible_tardy_repair as active


ACTIVE_VERSION = "reboot_v210_20260626_trackA_latest_feasible_tardy_repair"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
