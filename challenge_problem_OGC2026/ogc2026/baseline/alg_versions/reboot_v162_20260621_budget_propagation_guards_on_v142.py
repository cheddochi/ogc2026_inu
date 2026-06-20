"""reboot_v162_20260621_budget_propagation_guards_on_v142.py

Strategy:
    Keep trusted v142 as the default line and keep the v161 family guards, but
    stop resetting the child's wall-clock budget on each delegated wrapper
    call.

Metadata:
    version_id: reboot_v162_20260621_budget_propagation_guards_on_v142
    parent_version: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
    status: candidate
    timestamp: 2026-06-21 KST
    strategy:
        - Preserve v142 unchanged outside the target runtime-risk families.
        - Preserve the prob27-like guard from v146.
        - Preserve the prob33-like guard from v159.
        - Propagate only the remaining wall time to delegated children instead
          of passing the original full timelimit through every wrapper layer.
    hypothesis:
        The current runtime cliff is materially driven by optimistic timelimit
        reset across delegated wrapper layers. Keeping the same family guards
        but making delegation elapsed-aware should recover scoreability on the
        non-target inherited path and stabilize the guarded runtime-risk rows.
    intended_metric_target:
        - preserve accepted_for_score 40/40 and timeout 0
        - stabilize prob27-like and prob33-like runtime-risk families
        - stop non-target prob40-like timeout regressions before new T-tail work
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
"""

from __future__ import annotations

import time

from alg_versions import reboot_v141_20260620_1530_prob33like_postpass_on_v136 as v141
from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as v142
from alg_versions import reboot_v146_20260621_0215_prob27like_efficiency_shortlist_on_v142 as v146
from alg_versions import reboot_v158_20260621_prob40like_narrow_builder_on_v152 as v158
from alg_versions import reboot_v159_20260621_prob33_guard_on_v158 as v159


ACTIVE_VERSION = "reboot_v162_20260621_budget_propagation_guards_on_v142"

_MIN_CHILD_TIMELIMIT = 8.0


def _remaining_child_timelimit(started: float, timelimit: float) -> float:
    remaining = max(0.0, float(timelimit) - (time.time() - started))
    return max(_MIN_CHILD_TIMELIMIT, remaining)


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    timelimit = float(timelimit)
    tier = v158.v050._time_tier(timelimit)
    if tier in {"very_short", "short"}:
        return v142.algorithm(prob_info, _remaining_child_timelimit(started, timelimit))

    prob27_features = v146._selector_features(prob_info)
    if v146._matches_prob27like_heavytail(prob27_features):
        return v146.algorithm(prob_info, _remaining_child_timelimit(started, timelimit))

    prob33_features = v141._selector_features(prob_info)
    if v141._matches_prob33like_moderate_highproc(prob33_features):
        return v159.algorithm(prob_info, _remaining_child_timelimit(started, timelimit))

    return v142.algorithm(prob_info, _remaining_child_timelimit(started, timelimit))
