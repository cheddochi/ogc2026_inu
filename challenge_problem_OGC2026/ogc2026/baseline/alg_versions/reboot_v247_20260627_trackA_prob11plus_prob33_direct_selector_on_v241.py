"""reboot_v247_20260627_trackA_prob11plus_prob33_direct_selector_on_v241.py

Strategy:
    Route sensitive feature subtypes directly to the strongest currently
    validated specialist while preserving trusted v241 elsewhere:
      - ultra-tight prob11-like Family A lane -> v245 tail-retry specialist
      - prob33-like runtime-cliff lane -> direct v081 runtime-flatten specialist
      - everything else -> exact trusted v241

    This removes the late-budget race that blocked v246 while keeping the
    routing fully feature-based.
"""

from __future__ import annotations

from alg_versions import reboot_v081_20260619_1948_prob33like_runtime_flatten as v081
from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
from alg_versions import reboot_v241_20260627_trackA_split_prob11_guard_from_first20_subgroup_on_v218 as v241
from alg_versions import reboot_v245_20260627_trackA_prob11_tail_retry_on_v241 as v245


ACTIVE_VERSION = "reboot_v247_20260627_trackA_prob11plus_prob33_direct_selector_on_v241"


def _allow_prob11like_ultratight_lane(features: dict[str, float]) -> bool:
    return v245._allow_prob11like_ultratight_lane(features)


def _allow_prob33like_runtime_lane(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 3
        and 200 <= int(features.get("blocks", 0)) < 240
        and 15.0 <= float(features.get("proc_mean", 0.0)) <= 17.5
        and 0.40 <= float(features.get("pref_concentration", 0.0)) <= 0.46
        and 0.40 <= float(features.get("pref_pressure", 0.0)) <= 0.42
        and 3.4 <= float(features.get("slack_mean", 0.0)) <= 4.0
    )


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v186._selector_features(prob_info)

    if _allow_prob11like_ultratight_lane(features):
        return v245.algorithm(prob_info, timelimit)

    if _allow_prob33like_runtime_lane(features):
        return v081.algorithm(prob_info, timelimit)

    return v241.algorithm(prob_info, timelimit)
