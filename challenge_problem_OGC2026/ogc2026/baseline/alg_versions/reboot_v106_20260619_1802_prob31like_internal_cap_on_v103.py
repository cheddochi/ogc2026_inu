"""reboot_v106_20260619_1802_prob31like_internal_cap_on_v103.py

Strategy:
    Keep v103 unchanged outside the prob31-like subtype, but replay the same
    inherited chain with a smaller internal timelimit only on that subtype.

Metadata:
    version_id: reboot_v106_20260619_1802_prob31like_internal_cap_on_v103
    parent_version: reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102
    status: candidate
    timestamp: 2026-06-19 18:02 KST
    strategy:
        - Preserve v103 unchanged outside the targeted prob31-like subtype.
        - Detect the prob31-like runtime-sensitive subtype from `prob_info`
          features only.
        - On that subtype, call the inherited v103 chain with an internal
          timelimit cap of `58.0s` for standard-or-longer tiers.
    hypothesis:
        The current-source prob31-like instability is a timing cliff inside the
        inherited v103 chain. A small internal cap is enough to preserve the same
        best row-level signal while recovering runtime margin.
    intended_metric_target:
        - restore scoreable margin on prob31-like rows
        - preserve the v103 40/40 contract if possible
        - unblock later T-tail work on prob37/prob38/prob39-like families
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102
"""

from __future__ import annotations

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v078_20260619_1535_fourbay_runtime_family_flatten as v078
from alg_versions import reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102 as v103


ACTIVE_VERSION = "reboot_v106_20260619_1802_prob31like_internal_cap_on_v103"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v078._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    if tier not in {"very_short", "short"} and v078._matches_prob31like_class(features):
        internal_cap = min(float(timelimit), 58.0)
        print(
            f"[baseline_hh reboot_v106] prob31like_internal_cap instance={prob_info.get('name')} "
            f"tier={tier} requested={float(timelimit):.2f}s internal={internal_cap:.2f}s"
        )
        return v103.algorithm(prob_info, internal_cap)

    return v103.algorithm(prob_info, timelimit)
