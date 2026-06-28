"""reboot_v099_20260619_1845_prob31like_runtime_flatten_on_v096.py

Strategy:
    Keep current v096 as the default path, but replace the prob31-like
    runtime-cliff subtype with the flattened v078 direct family path.

Metadata:
    version_id: reboot_v099_20260619_1845_prob31like_runtime_flatten_on_v096
    parent_version: reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094
    status: candidate
    timestamp: 2026-06-19 18:45 KST
    strategy:
        - Preserve v096 unchanged outside the target subtype.
        - On the 4-bay high-proc concentrated-preference prob31-like subtype,
          bypass the inherited v094 chain that currently drifts into overtime.
        - Reuse the already flattened direct runtime-sensitive family path from
          v078 only for that subtype.
    hypothesis:
        Current-source reruns show a runtime cliff on the prob31-like subtype
        inside the inherited v096 chain. The flattened v078 path is weaker on
        some other families, but it is more stable on prob31-like rows. Using
        it only there should recover scoreable runtime without disturbing the
        stronger current handling elsewhere.
    intended_metric_target:
        - recover prob31-like scoreability under the current source state
        - preserve prob37-like and prob40-like handling from v096
        - restore a path toward current-source 40/40 scoreability
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094
"""

from __future__ import annotations

from alg_versions import reboot_v078_20260619_1535_fourbay_runtime_family_flatten as v078
from alg_versions import reboot_v096_20260619_1228_xlarge_lowproc_fast_reinsert_on_v094 as v096


ACTIVE_VERSION = "reboot_v099_20260619_1845_prob31like_runtime_flatten_on_v096"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v078._selector_features(prob_info)
    tier = v078._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and v078._matches_prob31like_class(features):
        return v078.algorithm(prob_info, timelimit)
    return v096.algorithm(prob_info, timelimit)
