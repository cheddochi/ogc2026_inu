"""HH active submission wrapper.

Current active working line:
    reboot_v212_20260627_trackA_reserved_specialist_budget_on_v210

Publish-trust note:
    v212 is the current-tree trusted BEST on the tracked baseline_hh surface.
    It preserves the stable v210 Track A fallback and reserves a small
    specialist budget earlier so the profitable late four-bay repairs still run
    on the official wrapper surface.
"""

from alg_versions import reboot_v212_20260627_trackA_reserved_specialist_budget_on_v210 as active


ACTIVE_VERSION = "reboot_v212_20260627_trackA_reserved_specialist_budget_on_v210"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
