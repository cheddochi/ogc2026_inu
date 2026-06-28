"""HH active submission wrapper.

Current active working line:
    reboot_v267_20260628_trackA_spatial_primitive_reinsert_on_active_v247

Publish-trust note:
    v267 is the current-tree trusted BEST on the tracked baseline_hh surface.
    It preserves the exact trusted v247 wrapper result first, then applies a
    narrow primitive-level Track A spatial reinsertion only on the feature-only
    prob13like / prob19like residual subtype.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_active_module():
    module_path = (
        Path(__file__).resolve().parent
        / "alg_versions"
        / "reboot_v267_20260628_trackA_spatial_primitive_reinsert_on_active_v247.py"
    )
    spec = importlib.util.spec_from_file_location(
        "_ogc2026_active_baseline_hh_v267",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load active module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


active = _load_active_module()

ACTIVE_VERSION = "reboot_v267_20260628_trackA_spatial_primitive_reinsert_on_active_v247"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
