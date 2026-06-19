"""reboot_v108_20260619_1857_prob38like_longlimit_gate_on_v106.py

Strategy:
    Keep the v106 current-source recovery path as the default, but only allow
    the prob38-like direct-plus-quantile move when the dynamic direct budget is
    large enough to support it safely.

Metadata:
    version_id: reboot_v108_20260619_1857_prob38like_longlimit_gate_on_v106
    parent_version: reboot_v106_20260619_1802_prob31like_internal_cap_on_v103
    status: candidate
    timestamp: 2026-06-19 18:57 KST
    strategy:
        - Preserve v106 unchanged outside the prob38-like subtype.
        - Reuse the prob38-like release-aware / quantile path from v107 only
          when the dynamic direct budget is high enough.
        - Fall back to v106 on shorter standard-tier limits.
    hypothesis:
        The prob38-like move is beneficial at 55s and 60s but harmful at 45s
        and 50s. A stricter budget gate can keep the good long-limit signal
        while removing the short-limit regression that rejected v107.
    intended_metric_target:
        - keep accepted_for_score 40/40 on the current source state
        - preserve v106 behavior on shorter limits
        - reduce the prob38-like T/objective tail on longer limits
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v106_20260619_1802_prob31like_internal_cap_on_v103
"""

from __future__ import annotations

from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v107_20260619_1841_prob38like_quantile_on_v106 as v107
from alg_versions import reboot_v106_20260619_1802_prob31like_internal_cap_on_v103 as v106


ACTIVE_VERSION = "reboot_v108_20260619_1857_prob38like_longlimit_gate_on_v106"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v050._selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))
    direct_budget = v050._policy_budget(float(timelimit), tier)
    if (
        tier not in {"very_short", "short"}
        and v050._matches_prob38like_class(features)
        and direct_budget >= 41.5
    ):
        return v107.algorithm(prob_info, timelimit)
    return v106.algorithm(prob_info, timelimit)
