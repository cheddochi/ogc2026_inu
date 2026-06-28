"""reboot_v101_20260619_1425_prob38like_feature_budget_restore_on_v100.py

Strategy:
    Keep v100 as the default path, but restore the older stable prob38-like
    direct policy through a feature-based selector instead of the drifted newer
    chain.

Metadata:
    version_id: reboot_v101_20260619_1425_prob38like_feature_budget_restore_on_v100
    parent_version: reboot_v100_20260619_1355_prob37like_flattened_iterative_reinsert_on_v099
    status: candidate
    timestamp: 2026-06-19 14:25 KST
    strategy:
        - Preserve v100 unchanged outside the prob38-like subtype.
        - Detect the prob38-like family from `prob_info` features only.
        - On that subtype, bypass the drifted v050/v080/v083 path and replay
          the older stable direct policy:
          `due_long_proc`, `top_bays=3`, `max_positions=16`, internal budget 59.
        - Keep every non-target row on the exact v100 path.
    hypothesis:
        The remaining dominant score loss is concentrated on the prob38-like
        family. The newer chain on that subtype has drifted badly under the
        current source state, but the older direct policy still reproduces a
        much stronger scoreable row. Restoring only that feature-based policy
        should sharply cut the largest regression while preserving the v100
        recovery on prob31-like and prob37-like families.
    intended_metric_target:
        - improve the prob38-like row materially under the current source state
        - preserve the recovered v100 scoreable contract
        - reduce full-train40 avg objective and avg T versus v100
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v100_20260619_1355_prob37like_flattened_iterative_reinsert_on_v099
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v100_20260619_1355_prob37like_flattened_iterative_reinsert_on_v099 as v100


ACTIVE_VERSION = "reboot_v101_20260619_1425_prob38like_feature_budget_restore_on_v100"


PROB38LIKE_POLICY = {
    "order_strategy": "due_long_proc",
    "top_bays": 3,
    "max_positions": 16,
    "budget": 59.0,
}


def _prob38like_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB38LIKE_POLICY["budget"]), max(8.0, float(timelimit) - 0.1))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB38LIKE_POLICY["order_strategy"]),
        top_bays=int(PROB38LIKE_POLICY["top_bays"]),
        max_positions=int(PROB38LIKE_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v101] prob38like_feature_budget_restore instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v050._selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and v050._matches_prob38like_class(features):
        return _prob38like_solution(prob_info, timelimit)
    return v100.algorithm(prob_info, timelimit)
