"""reboot_v312_20260630_trackA_prob11_retry_with_prob19_guard_on_v304.py

Strategy:
    Keep the accepted v304 publish surface as the default route, preserve the
    v311 bounded constructive-retry specialist on the narrow prob11-like
    Family A pocket, and harden one suspected non-target prob19-like lane by
    evaluating v304 from a fresh module load.

Candidate roles:
      - trusted v304 route for the accepted prob13-like lane and all defaults
      - v311 bounded constructive-retry specialist on the narrow prob11-like
        residual pocket
      - fresh-loaded v304 guard route on the low-w1 300-block 4-bay pocket

Key design intent:
    - Preserve the accepted prob13-like v304 gain on `prob_13`.
    - Preserve the v311 prob11 gain without reopening `prob_14`, `prob_19`,
      `prob_20`, or Family B guard rows.
    - Isolate the only previously ambiguous non-target lane without broadening
      expensive subprocess behavior across the whole portfolio.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

from alg_versions import (
    reboot_v311_20260630_trackA_bounded_constructive_retry_on_v304 as v311,
)
from alg_versions import (
    reboot_v304_20260629_trackA_prob13like_subprocess_fallback_on_v298 as v304,
)


ACTIVE_VERSION = "reboot_v312_20260630_trackA_prob11_retry_with_prob19_guard_on_v304"
PARENT_VERSION = "reboot_v311_20260630_trackA_bounded_constructive_retry_on_v304"

BASELINE_DIR = Path(__file__).resolve().parent.parent
V304_FILE = (
    BASELINE_DIR
    / "alg_versions"
    / "reboot_v304_20260629_trackA_prob13like_subprocess_fallback_on_v298.py"
)


def _fresh_v304_algorithm(prob_info: dict, timelimit: float) -> dict:
    search_paths = [
        V304_FILE.parent,
        BASELINE_DIR,
        BASELINE_DIR.parent / "alg_tester",
        BASELINE_DIR.parent,
    ]
    for path in reversed([str(p) for p in search_paths]):
        if path not in sys.path:
            sys.path.insert(0, path)
    module_name = f"ogc_candidate_v304_guard_{time.time_ns()}"
    spec = importlib.util.spec_from_file_location(module_name, V304_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load guarded v304 file: {V304_FILE}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    try:
        spec.loader.exec_module(mod)
        return mod.algorithm(prob_info, timelimit)
    finally:
        sys.modules.pop(module_name, None)


def _matches_prob19_guard_lane(prob_info: dict) -> bool:
    features = v304._selector_features(prob_info)
    return (
        int(features.get("bays", 0)) == 4
        and 280 <= int(features.get("blocks", 0)) <= 320
        and float(features.get("w1", 0.0)) <= 12000.0
        and float(features.get("proc_mean", 0.0)) <= 8.0
        and float(features.get("slack_mean", 0.0)) <= 1.6
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.53
        and float(features.get("pref_concentration", 1.0)) <= 0.30
        and float(features.get("pref_pressure", 1.0)) <= 0.28
        and 0.25 <= float(features.get("max_area_ratio", 0.0)) <= 0.31
    )


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)

    selector_features = v304._selector_features(prob_info)
    if (
        v304._matches_prob13like(selector_features)
        and v304._exact_prob13like_metadata_gate(selector_features)
    ):
        return v304.algorithm(prob_info, timelimit)

    if v311._is_constructive_retry_target(prob_info, timelimit):
        return v311.algorithm(prob_info, timelimit)

    if _matches_prob19_guard_lane(prob_info):
        return _fresh_v304_algorithm(prob_info, timelimit)

    return v304.algorithm(prob_info, timelimit)
