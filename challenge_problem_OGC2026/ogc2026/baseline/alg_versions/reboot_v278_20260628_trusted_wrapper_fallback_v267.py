"""Frozen trusted wrapper fallback for v278.

This snapshot preserves the exact trusted active v267 wrapper surface so the
new bounded Track A candidate can delegate unchanged rows without touching the
active pointer.
"""

from __future__ import annotations

from alg_versions import reboot_v267_20260628_trackA_spatial_primitive_reinsert_on_active_v247 as active


ACTIVE_VERSION = "reboot_v267_20260628_trackA_spatial_primitive_reinsert_on_active_v247"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
