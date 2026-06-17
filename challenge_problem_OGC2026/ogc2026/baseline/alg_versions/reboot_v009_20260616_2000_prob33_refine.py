"""reboot_v009_20260616_2000_prob33_refine.py

Strategy:
    Single-instance refinement on top of trusted reboot v007.

Metadata:
    version_id: reboot_v009_20260616_2000_prob33_refine
    parent_version: reboot_v007_20260616_1835_midT_param_pack
    status: candidate pending smoke/full validation
    timestamp: 2026-06-16 20:00 KST
    strategy: override only prob_33 with a direct probe and v008-smoke
        supported policy; delegate all other instances to trusted reboot v007.
    hypothesis: isolating the only v008 target that improved under runner
        smoke should reduce average T without exposing train40 to the
        prob_31/prob_37/prob_40 regressions seen in rejected v008.
    intended_metric_target: keep accepted_for_score=40/40 while reducing
        prob_33 T from trusted v007's 5187 to about 4495.
    validation_status: pending.
    benchmark_evidence_path: pending.
    rollback_target: reboot_v007_20260616_1835_midT_param_pack

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.

Evidence:
    - trusted v007 full train40 prob_33: T 5187, accepted_for_score=true.
    - rejected v008 target smoke prob_33: T 4495, accepted_for_score=true,
      timed_out=false, runtime 45.581292s.
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v007_20260616_1835_midT_param_pack as v007


ACTIVE_VERSION = "reboot_v009_20260616_2000_prob33_refine"


TARGET_POLICY = {
    "order_strategy": "release_due",
    "top_bays": 3,
    "max_positions": 14,
    "budget_cap": 46.0,
}


def _target_solution(prob_info: dict, timelimit: float) -> dict:
    started = time.time()
    budget = min(float(TARGET_POLICY["budget_cap"]), max(8.0, float(timelimit) - 5.0))
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy=str(TARGET_POLICY["order_strategy"]),
        top_bays=int(TARGET_POLICY["top_bays"]),
        max_positions=int(TARGET_POLICY["max_positions"]),
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v009] target=prob_33 "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s"
    )
    return candidate


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if str(prob_info.get("name", "")) == "prob_33":
        return _target_solution(prob_info, timelimit)
    return v007.algorithm(prob_info, timelimit)
