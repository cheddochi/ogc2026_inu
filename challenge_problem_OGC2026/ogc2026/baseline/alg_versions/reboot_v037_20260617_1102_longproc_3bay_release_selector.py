"""reboot_v037_20260617_1102_longproc_3bay_release_selector.py

Strategy:
    Keep trusted v035 behavior and switch one structural class of large
    long-processing 3-bay instances to a release-aware ordering.

Metadata:
    version_id: reboot_v037_20260617_1102_longproc_3bay_release_selector
    parent_version: reboot_v035_20260617_0912_prob14_preference_spread
    status: rejected
    timestamp: 2026-06-17 11:02 KST
    strategy:
        - class rule: blocks>=200, bays==3, avg_processing_time>=18
        - class policy: due_release_proc, top_bays=3, max_positions=16,
          max_orients=4, budget=59
        - all other instances delegate to trusted v035
    hypothesis: the current best long-proc 3-bay class is over-committing to
        due_long_proc; adding release awareness should reduce tardiness for the
        class without disturbing the rest of train40.
    intended_metric_target:
        - direct current-chain probe on prob_38 improved T 11316->11212 and
          objective 153690186->152453868
    validation_status: import smoke passed; mandatory smoke-8 passed 8/8, but
        the targeted prob_38 benchmark regressed on both T and objective, so
        the candidate was rejected before full train40.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v037_core8_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v037_prob38_20260617_001/
    rollback_target: reboot_v035_20260617_0912_prob14_preference_spread
"""

from __future__ import annotations

import statistics
import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v035_20260617_0912_prob14_preference_spread as v035


ACTIVE_VERSION = "reboot_v037_20260617_1102_longproc_3bay_release_selector"


CLASS_POLICY = {
    "order_strategy": "due_release_proc",
    "top_bays": 3,
    "max_positions": 16,
    "max_orients": 4,
    "budget": 59.0,
}


def _is_longproc_3bay_class(prob_info: dict) -> bool:
    blocks = prob_info.get("blocks", [])
    bays = prob_info.get("bays", [])
    if len(blocks) < 200 or len(bays) != 3:
        return False
    proc_avg = statistics.mean(float(block["processing_time"]) for block in blocks)
    return proc_avg >= 18.0


def _class_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(CLASS_POLICY["budget"]), max(8.0, float(timelimit) - 0.1))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(CLASS_POLICY["order_strategy"]),
        top_bays=int(CLASS_POLICY["top_bays"]),
        max_positions=int(CLASS_POLICY["max_positions"]),
        max_orients=int(CLASS_POLICY["max_orients"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v037] target={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if _is_longproc_3bay_class(prob_info):
        return _class_solution(prob_info, timelimit)
    return v035.algorithm(prob_info, timelimit)
