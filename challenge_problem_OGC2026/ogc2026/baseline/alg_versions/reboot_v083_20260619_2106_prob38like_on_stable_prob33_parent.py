"""reboot_v083_20260619_2106_prob38like_on_stable_prob33_parent.py

Strategy:
    Keep the stabilized v082 parent as the default path, then reapply the
    bounded prob38-like quantile single reinsertion on top of that parent.

Metadata:
    version_id: reboot_v083_20260619_2106_prob38like_on_stable_prob33_parent
    parent_version: reboot_v082_20260619_2022_prob33like_on_v074_parent
    status: candidate
    timestamp: 2026-06-19 21:06 KST
    strategy:
        - Preserve v082 unchanged outside the prob38-like subtype.
        - On the prob38-like family, build the trusted release-aware direct
          candidate first.
        - Reuse the v080 quantile-sampled one-block reinsertion and keep only
          strictly better feasible results.
    hypothesis:
        The earlier prob38-like objective improvement was real, but it was
        evaluated on a parent that still leaked prob33 runtime-risk. With the
        v082 stable parent underneath, the same targeted move may finally clear
        full train40 as a genuine score improvement.
    intended_metric_target:
        - improve prob38-like rows
        - preserve the stable prob33like runtime fix from v082
        - improve avg objective versus trusted v074
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v082_20260619_2022_prob33like_on_v074_parent
"""

from __future__ import annotations

from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v082_20260619_2022_prob33like_on_v074_parent as v082


ACTIVE_VERSION = "reboot_v083_20260619_2106_prob38like_on_stable_prob33_parent"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v050._selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and v050._matches_prob38like_class(features):
        return v080._class_solution(prob_info, timelimit, tier)
    return v082.algorithm(prob_info, timelimit)

