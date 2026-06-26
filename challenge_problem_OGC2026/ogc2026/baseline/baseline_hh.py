"""HH active submission wrapper.

Current active working line:
    reboot_v195_20260626_familyA_window_reorder_on_v194

Publish-trust note:
    v195 is the current-tree trusted BEST on the tracked baseline_hh surface.
    It keeps the trusted v194 fallback path and adds a bounded Family A tardy
    window reorder that improved prob_10 and prob_20 enough to lower full40
    Total T and objective while preserving the prob_38 / prob_39 / prob_40
    guard surface on the official wrapper path.
"""

from alg_versions import reboot_v195_20260626_familyA_window_reorder_on_v194 as active


ACTIVE_VERSION = "reboot_v195_20260626_familyA_window_reorder_on_v194"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
