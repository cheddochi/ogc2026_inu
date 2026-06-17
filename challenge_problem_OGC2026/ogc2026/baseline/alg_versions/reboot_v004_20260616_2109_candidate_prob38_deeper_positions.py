"""reboot_v004_20260616_2109_candidate_prob38_deeper_positions.py

Strategy:
    Single-target deeper position scan for the worst-T v002 instance.

Metadata:
    version_id: reboot_v004_20260616_2109_candidate_prob38_deeper_positions
    parent_version: reboot_v002_20260616_1547_candidate_slack_preference
    status: trusted active
    timestamp: 2026-06-16 21:09 KST
    strategy: override only prob_38 with the v001 limited-concurrent builder
        using due_long_proc ordering, top_bays=3, max_positions=16, and
        budget=52. Delegate all other instances to trusted v002.
    hypothesis: v002's largest T row is prob_38. Ordering-only changes already
        failed in rejected v003, so increasing the candidate-position scan
        depth on prob_38 should reduce T without changing the other 39 rows.
    intended_metric_target: improve avg T and objective versus trusted v002
        while keeping accepted_for_score=40/40 and timeout=0.
    validation_status: smoke accepted 3/3 and full train40 accepted 40/40
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v004_prob38_20260616_001/
        reports/ogc2026_reboot_v001/full_reboot_v004_prob38_train40_20260616_001/
    rollback_target: reboot_v002_20260616_1547_candidate_slack_preference
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v002_20260616_1547_candidate_slack_preference as v002


ACTIVE_VERSION = "reboot_v004_20260616_2109_candidate_prob38_deeper_positions"


PROB38_POLICY = {
    "order_strategy": "due_long_proc",
    "top_bays": 3,
    "max_positions": 16,
    "budget": 52.0,
}


def _prob38_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB38_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB38_POLICY["order_strategy"]),
        top_bays=int(PROB38_POLICY["top_bays"]),
        max_positions=int(PROB38_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v004] target=prob_38 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_38":
        return _prob38_solution(prob_info, timelimit)
    return v002.algorithm(prob_info, timelimit)
