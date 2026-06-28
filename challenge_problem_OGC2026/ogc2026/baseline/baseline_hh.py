"""HH active submission wrapper.

Current active working line:
    direct standard-import surface on
    reboot_v278_20260628_trackA_coarse_gate_lazy_prob20_plus_lowproc_replay_on_active_v267

Publish-trust note:
    v280 is the current-tree trusted BEST on the tracked baseline_hh surface.
    It preserves the accepted v278 Track A logic and fixes the publish-surface
    drift by importing that logic directly on the official baseline_hh path.
"""

from __future__ import annotations

from alg_versions import (
    reboot_v278_20260628_trackA_coarse_gate_lazy_prob20_plus_lowproc_replay_on_active_v267 as active,
)


ACTIVE_VERSION = "reboot_v280_20260628_baseline_surface_direct_import_v278"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
