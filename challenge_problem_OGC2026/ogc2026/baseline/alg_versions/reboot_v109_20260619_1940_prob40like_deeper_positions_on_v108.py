"""reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108.py

Strategy:
    Keep the v108 current-source recovery path as the default, then reapply
    the deeper prob40-like position scan only on the feature-matched
    high-workload family.

Metadata:
    version_id: reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108
    parent_version: reboot_v108_20260619_1857_prob38like_longlimit_gate_on_v106
    status: candidate
    timestamp: 2026-06-19 19:40 KST
    strategy:
        - Preserve v108 unchanged outside the prob40-like subtype.
        - On the prob40-like family, reuse the deeper direct due_release policy
          that still shows strong current-source row-level gains.
        - Keep all non-target rows on the v108 recovery path.
    hypothesis:
        The deeper prob40-like position scan remains a real, repeatable T
        improvement under the current source state. Limiting it strictly to the
        prob40-like feature class should reduce one of the largest remaining
        tails without disturbing the prob31/prob38 recovery work already built
        into v108.
    intended_metric_target:
        - keep accepted_for_score 40/40 on the current source state
        - reduce the prob40-like T/objective tail
        - improve total T / avg T / avg objective versus v108
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v108_20260619_1857_prob38like_longlimit_gate_on_v106
"""

from __future__ import annotations

from alg_versions import reboot_v017_20260616_2327_prob40_deeper_positions as v017
from alg_versions import reboot_v063_20260618_1605_prob40like_direct_first_due_release as v063
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v108_20260619_1857_prob38like_longlimit_gate_on_v106 as v108


ACTIVE_VERSION = "reboot_v109_20260619_1940_prob40like_deeper_positions_on_v108"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v063._selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and v063._matches_prob40like_class(features):
        return v017._prob40_solution(prob_info, timelimit)
    return v108.algorithm(prob_info, timelimit)
