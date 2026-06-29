"""HH active submission wrapper.

Current active working line:
    direct standard-import surface on
    reboot_v298_20260629_trackA_prob11_rescue_with_familyB_tail_freeze_on_v290

Publish-trust note:
    v299 is the current-tree trusted BEST candidate on the tracked
    baseline_hh surface. It preserves the accepted v290 frozen fallback path,
    but adds the bounded prob11 specialist from v298 while freezing the late
    Family B tail on the trusted v290 route.
"""

from __future__ import annotations

from alg_versions import (
    reboot_v298_20260629_trackA_prob11_rescue_with_familyB_tail_freeze_on_v290 as active,
)


ACTIVE_VERSION = "reboot_v299_20260629_baseline_surface_direct_import_v298"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
