"""HH active submission wrapper.

Current active working line:
    direct standard-import surface on
    reboot_v290_20260629_trackA_frozen_v278_subprocess_split_specialists

Publish-trust note:
    v291 is the current-tree trusted BEST candidate on the tracked
    baseline_hh surface. It preserves the useful v288 subprocess guard idea,
    but freezes the child fallback target on direct v278 so the publish surface
    cannot recurse through baseline_hh.py.
"""

from __future__ import annotations

from alg_versions import (
    reboot_v290_20260629_trackA_frozen_v278_subprocess_split_specialists as active,
)


ACTIVE_VERSION = "reboot_v291_20260629_baseline_surface_direct_import_v290"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
