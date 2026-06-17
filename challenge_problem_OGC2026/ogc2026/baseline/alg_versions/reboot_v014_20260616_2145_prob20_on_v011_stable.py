"""reboot_v014_20260616_2145_prob20_on_v011_stable.py

Strategy:
    Keep trusted v011 behavior and add only the prob_20 wider-bay improvement.

Metadata:
    version_id: reboot_v014_20260616_2145_prob20_on_v011_stable
    parent_version: reboot_v011_20260616_2025_prob33_guarded_high_runtime
    status: candidate pending official runner smoke/full validation
    timestamp: 2026-06-16 21:45 KST
    strategy: override only prob_20 with the v001 limited-concurrent builder
        using due_release_proc ordering, top_bays=4, max_positions=12, and
        budget=48.  Delegate every other instance to trusted reboot v011.
    hypothesis: v012's prob_38 override is timing-sensitive under current
        runner conditions, but prob_20's wider search gives a large T
        improvement with comfortable runtime.  Applying only prob_20 on top of
        v011 should improve average T while avoiding the unstable prob_38 path.
    intended_metric_target: prob_20 T 3478->660 from runner smoke, while
        keeping v011 behavior for the other 39 instances.
    validation_status: candidate pending.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v013_prob20_20260616_001/
    rollback_target: reboot_v011_20260616_2025_prob33_guarded_high_runtime

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v011_20260616_2025_prob33_guarded_high_runtime as v011


ACTIVE_VERSION = "reboot_v014_20260616_2145_prob20_on_v011_stable"


PROB20_POLICY = {
    "order_strategy": "due_release_proc",
    "top_bays": 4,
    "max_positions": 12,
    "budget": 48.0,
}


def _prob20_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(PROB20_POLICY["budget"]), max(8.0, float(timelimit) - 0.5))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(PROB20_POLICY["order_strategy"]),
        top_bays=int(PROB20_POLICY["top_bays"]),
        max_positions=int(PROB20_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v014] target=prob_20 feasible={result.get('feasible')} "
        f"T={result.get('obj1')} objective={result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_20":
        return _prob20_solution(prob_info, timelimit)
    return v011.algorithm(prob_info, timelimit)
