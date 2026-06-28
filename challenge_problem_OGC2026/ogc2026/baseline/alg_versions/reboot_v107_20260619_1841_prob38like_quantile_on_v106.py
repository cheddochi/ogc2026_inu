"""reboot_v107_20260619_1841_prob38like_quantile_on_v106.py

Strategy:
    Keep the v106 current-source recovery path as the default, then reapply
    the bounded prob38-like quantile single reinsertion only on that targeted
    high-pressure family.

Metadata:
    version_id: reboot_v107_20260619_1841_prob38like_quantile_on_v106
    parent_version: reboot_v106_20260619_1802_prob31like_internal_cap_on_v103
    status: candidate
    timestamp: 2026-06-19 18:41 KST
    strategy:
        - Preserve v106 unchanged outside the prob38-like subtype.
        - On the prob38-like family, reuse the accepted release-aware direct
          candidate plus the bounded quantile single reinsertion from v080.
        - Keep the inherited v106 runtime repair on all non-target rows.
    hypothesis:
        The v106 recovery path restored current-source scoreability but left
        the largest residual T/objective regression on the prob38-like
        high-pressure row. The older v080 target move proved that a single
        quantile-sampled reinsertion can recover that row-level signal under
        time. Reusing that move on top of v106 should lower the high-T tail
        without reopening the prob31-like runtime cliff.
    intended_metric_target:
        - keep accepted_for_score 40/40 under the current source state
        - reduce the prob38-like T/objective tail
        - improve total T / avg T / avg objective versus v106
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v106_20260619_1802_prob31like_internal_cap_on_v103
"""

from __future__ import annotations

from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v080_20260619_1738_prob38like_quantile_single_reinsert as v080
from alg_versions import reboot_v106_20260619_1802_prob31like_internal_cap_on_v103 as v106


ACTIVE_VERSION = "reboot_v107_20260619_1841_prob38like_quantile_on_v106"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v050._selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and v050._matches_prob38like_class(features):
        return v080._class_solution(prob_info, timelimit, tier)
    return v106.algorithm(prob_info, timelimit)
