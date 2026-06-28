"""Frozen trusted wrapper fallback for v267.

This snapshot preserves the exact wrapper surface that pointed to the trusted
v247 active line before baseline_hh.py moved on to v267.
"""

from __future__ import annotations

from alg_versions import reboot_v247_20260627_trackA_prob11plus_prob33_direct_selector_on_v241 as active


ACTIVE_VERSION = "reboot_v247_20260627_trackA_prob11plus_prob33_direct_selector_on_v241"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
