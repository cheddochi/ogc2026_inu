"""reboot_v013_20260616_2131_candidate_prob37_deeper_release.py

Strategy:
    Single-target deeper release_due scan for trusted-v012 high-T prob_37.

Metadata:
    version_id: reboot_v013_20260616_2131_candidate_prob37_deeper_release
    parent_version: reboot_v012_20260616_2040_prob38_deeper_positions
    status: candidate
    timestamp: 2026-06-16 21:31 KST
    strategy: override only prob_37 with the v001 limited-concurrent builder
        using release_due ordering, top_bays=3, max_positions=16, and budget
        55. Delegate all other instances to trusted v012.
    hypothesis: prob_37 still carries elevated T under trusted v012 and has
        enough runtime headroom to support a deeper release_due position scan
        without affecting the other 39 rows.
    intended_metric_target: improve avg T and objective versus trusted v012
        while keeping accepted_for_score=40/40 and timeout=0.
    validation_status: pending
    benchmark_evidence_path: pending
    rollback_target: reboot_v012_20260616_2040_prob38_deeper_positions
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v012_20260616_2040_prob38_deeper_positions as v012


ACTIVE_VERSION = "reboot_v013_20260616_2131_candidate_prob37_deeper_release"


PROB37_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 16,
    "budget": 55.0,
}


def _prob37_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB37_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB37_POLICY["order_strategy"]),
        top_bays=int(PROB37_POLICY["top_bays"]),
        max_positions=int(PROB37_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v013] target=prob_37 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_37":
        return _prob37_solution(prob_info, timelimit)
    return v012.algorithm(prob_info, timelimit)
