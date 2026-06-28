"""reboot_v082_20260619_2022_prob33like_on_v074_parent.py

Strategy:
    Keep trusted v074 as the default path, then intercept only the prob33-like
    runtime-risk subtype with the shallower flattened repair chain from v081.

Metadata:
    version_id: reboot_v082_20260619_2022_prob33like_on_v074_parent
    parent_version: reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio
    status: candidate
    timestamp: 2026-06-19 20:22 KST
    strategy:
        - Preserve v074 unchanged outside the prob33-like runtime-risk subtype.
        - Reuse the accepted v065 warm start plus the v081 sampled gap single
          and cheap v073 fast single only on the targeted subtype.
        - Keep every non-target row on the exact trusted v074 path.
    hypothesis:
        The v081 prob33like flatten is good, but its v078 parent changed the
        prob31like row. Reusing the same targeted runtime-risk fix directly on
        top of v074 should keep the trusted full-train40 score everywhere else
        while giving prob33 much larger time margin.
    intended_metric_target:
        - keep prob33-like rows scoreable with more runtime margin
        - preserve trusted v074 objective/T/L/P on all non-target rows
        - provide a stable equal-score parent for future score-improvement work
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio
"""

from __future__ import annotations

from alg_versions import reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio as v074
from alg_versions import reboot_v081_20260619_1948_prob33like_runtime_flatten as v081


ACTIVE_VERSION = "reboot_v082_20260619_2022_prob33like_on_v074_parent"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v081.v064._selector_features(prob_info)
    tier = v081.v064.v050._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and v081._matches_prob33like_runtime_class(features):
        return v081._class_solution(prob_info, timelimit, tier)
    return v074.algorithm(prob_info, timelimit)

