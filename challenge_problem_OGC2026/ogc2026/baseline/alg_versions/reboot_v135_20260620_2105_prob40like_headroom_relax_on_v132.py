"""reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132.py

Strategy:
    Preserve trusted v132 as the default line, then replay the narrow
    prob40-like quantile reinsertion with a slightly less conservative
    headroom gate.

Metadata:
    version_id: reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132
    parent_version: reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123
    status: accepted
    timestamp: 2026-06-20 21:05 KST
    strategy:
        - Keep the accepted v132 recovery line unchanged outside the target subtype.
        - Reuse the exact v130/v133 prob40-like selector and local move.
        - Lower only the headroom guard from reserve + 8.0 to reserve + 6.0.
        - Keep only strictly better officially feasible candidates.
    hypothesis:
        The prob40-like narrow quantile move itself is good enough, but the
        reserve + 8.0 guard is slightly too conservative under normal runtime
        noise on the direct baseline_hh surface. A reserve + 6.0 gate should
        let the already-proven T drop fire more reliably without breaking the
        60s scoreability constraint.
    intended_metric_target:
        - improve the prob40-like high-T tail row
        - preserve accepted_for_score 40/40
        - reduce total T / avg T / high-T tail and avg objective versus v132
    validation_status:
        accepted; direct active-surface revalidation reproduced the prob40
        improvement while keeping the v132-stable prob39 row
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v135_train40_20260620_001
    rollback_target: reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122 as v123
from alg_versions import reboot_v130_20260620_1125_prob40like_narrow_quantile_on_v123 as v130
from alg_versions import reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123 as v132


ACTIVE_VERSION = "reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    overall_started = time.time()
    timelimit = float(timelimit)
    tier = v123._time_tier(timelimit)
    features = v130._selector_features(prob_info)

    current_solution = v132.algorithm(prob_info, timelimit)
    current_result = v001.check_feasibility(prob_info, current_solution)

    if (
        tier in {"very_short", "short"}
        or not current_result.get("feasible")
        or not v130._matches_prob40like_narrow_tail(features)
        or float(current_result.get("obj1") or 0.0) < 5000.0
    ):
        return current_solution

    remaining = max(0.0, timelimit - (time.time() - overall_started))
    reserve = v123._dynamic_reserve(timelimit)
    if remaining <= reserve + 6.0:
        print(
            f"[baseline_hh reboot_v135] skip_prob40like_guard "
            f"instance={prob_info.get('name')} tier={tier} remaining={remaining:.2f}s "
            f"reserve={reserve:.2f}s base_T={current_result.get('obj1')}"
        )
        return current_solution

    best_solution, best_result = v130._try_narrow_quantile_reinsert(
        prob_info,
        current_solution,
        current_result,
        timelimit,
        overall_started,
        tier,
    )
    if v123._result_key(best_result) < v123._result_key(current_result):
        print(
            f"[baseline_hh reboot_v135] selected_prob40like_quantile "
            f"instance={prob_info.get('name')} T={best_result.get('obj1')} "
            f"objective={best_result.get('objective')}"
        )
        return best_solution

    print(
        f"[baseline_hh reboot_v135] keep_v132_base instance={prob_info.get('name')} "
        f"base_T={current_result.get('obj1')} cand_T={best_result.get('obj1')}"
    )
    return current_solution
