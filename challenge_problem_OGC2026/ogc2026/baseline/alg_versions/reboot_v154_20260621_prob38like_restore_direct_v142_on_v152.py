"""reboot_v154_20260621_prob38like_restore_direct_v142_on_v152.py

Strategy:
    Keep v152 as the scoreable recovery parent, but restore the direct v142
    algorithm path on the narrow prob38-like family only.

Metadata:
    version_id: reboot_v154_20260621_prob38like_restore_direct_v142_on_v152
    parent_version: reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151
    status: rejected
    timestamp: 2026-06-21 KST
    strategy:
        - Preserve v152 unchanged outside the target subtype.
        - On the prob38-like family only, bypass the weaker recovery-parent
          path and call the direct v142 algorithm path.
        - Keep the direct candidate only when it is officially feasible;
          otherwise fall back to v152.
    hypothesis:
        The biggest residual T regression on the scoreable recovery surface is
        the prob38-like row, and earlier direct evidence showed that the v142
        file path still reproduced the stronger scoreable family result. A thin
        family-specific restore should recover that tail without reopening the
        broader runtime backlog.
    intended_metric_target:
        - lower the largest remaining high-T tail on the 40/40 recovery surface
        - preserve accepted_for_score 40/40 and timeout 0
        - improve total T / avg T before any polish-only work
    validation_status:
        rejected after target compare reopened a prob40 timeout
    benchmark_evidence_path:
        - reports/ogc2026_reboot_v001/smoke_reboot_v154_tier12_20260621_001/
        - reports/ogc2026_reboot_v001/target_reboot_v154_prob38like_20260621_001/
    rollback_target: reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151
"""

from __future__ import annotations

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050


ACTIVE_VERSION = "reboot_v154_20260621_prob38like_restore_direct_v142_on_v152"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)

    from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as v142
    from alg_versions import reboot_v152_20260621_runtime_backlog_direct_flatten_on_v151 as v152

    tier = v050._time_tier(timelimit)
    if tier in {"very_short", "short"}:
        return v152.algorithm(prob_info, timelimit)

    features = v050._selector_features(prob_info)
    if not v050._matches_prob38like_class(features):
        return v152.algorithm(prob_info, timelimit)

    candidate_solution = v142.algorithm(prob_info, timelimit)
    candidate_result = v001.check_feasibility(prob_info, candidate_solution)
    print(
        f"[baseline_hh reboot_v154] prob38like_restore_direct_v142 "
        f"instance={prob_info.get('name')} feasible={candidate_result.get('feasible')} "
        f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
    )
    if candidate_result.get("feasible"):
        return candidate_solution

    print(
        f"[baseline_hh reboot_v154] prob38like_restore_fallback_v152 "
        f"instance={prob_info.get('name')} feasible={candidate_result.get('feasible')} "
        f"objective={candidate_result.get('objective')}"
    )
    return v152.algorithm(prob_info, timelimit)
