"""reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116.py

Strategy:
    Keep v116 as the default path, but add one runtime-stable concentrated-gap
    single move only on the prob31-like subtype.

Metadata:
    version_id: reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116
    parent_version: reboot_v116_20260619_2339_prob37like_early_chain_on_v115
    status: candidate
    timestamp: 2026-06-20 00:33 KST
    strategy:
        - Preserve v116 unchanged outside the prob31-like subtype.
        - Rebuild the same runtime-stable prob31-like parent path that v115
          already proved scoreable.
        - Reintroduce only the historical concentrated-gap single move from the
          old high-proc family chain.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The remaining prob31-like T tail is now small enough that the
        concentrated-gap single can be replayed safely on top of the stable
        parent without waking the previous runtime cliff.
    intended_metric_target:
        - improve the prob31-like official-limit row beyond v115/v116
        - preserve accepted_for_score 40/40
        - reduce total T, avg T, and the residual high-T tail
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v116_20260619_2339_prob37like_early_chain_on_v115
"""

from __future__ import annotations

import time

from alg_versions import reboot_v070_20260618_2035_highproc_concentrated_gap_single as v070
from alg_versions import reboot_v078_20260619_1535_fourbay_runtime_family_flatten as v078
from alg_versions import reboot_v114_20260619_2358_prob31like_direct_prefix2_stable_on_v109 as v114
from alg_versions import reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114 as v115
from alg_versions import reboot_v116_20260619_2339_prob37like_early_chain_on_v115 as v116
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064


ACTIVE_VERSION = "reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116"


def _prob31like_concentrated_gap_solution(
    prob_info: dict,
    timelimit: float,
    tier: str,
) -> tuple[dict, dict]:
    started = time.time()
    parent_solution, parent_result = v114._prob31like_runtime_stable_solution(
        prob_info,
        timelimit,
        tier,
    )
    if not parent_result.get("feasible"):
        return parent_solution, parent_result

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= 0.5:
        return parent_solution, parent_result

    displaced_solution, displaced_result = v115._try_displaced_fast_reinsert(
        prob_info,
        parent_solution,
        parent_result,
        remaining,
        tier,
    )
    if not displaced_result.get("feasible"):
        return parent_solution, parent_result

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= v070._dynamic_reserve(float(timelimit)) + 2.0:
        print(
            f"[baseline_hh reboot_v117] skip_prob31like_concentrated_gap "
            f"instance={prob_info.get('name')} tier={tier} remaining={remaining:.2f}s"
        )
        return displaced_solution, displaced_result

    candidate_solution, candidate_result = v070._try_gap_single_research(
        prob_info,
        displaced_solution,
        displaced_result,
        remaining,
        tier,
    )
    print(
        f"[baseline_hh reboot_v117] prob31like_concentrated_gap instance={prob_info.get('name')} "
        f"tier={tier} parent_T={displaced_result.get('obj1')} cand_T={candidate_result.get('obj1')} "
        f"parent_objective={displaced_result.get('objective')} "
        f"cand_objective={candidate_result.get('objective')}"
    )
    if v064._result_key(candidate_result) < v064._result_key(displaced_result):
        return candidate_solution, candidate_result
    return displaced_solution, displaced_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = v078._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    if (
        tier not in {"very_short", "short"}
        and float(timelimit) >= 55.0
        and v078._matches_prob31like_class(features)
    ):
        candidate_solution, candidate_result = _prob31like_concentrated_gap_solution(
            prob_info,
            timelimit,
            tier,
        )
        if candidate_result.get("feasible"):
            return candidate_solution
        print(
            f"[baseline_hh reboot_v117] prob31like_concentrated_gap_fallback "
            f"instance={prob_info.get('name')} feasible={candidate_result.get('feasible')} "
            f"objective={candidate_result.get('objective')}"
        )

    return v116.algorithm(prob_info, timelimit)
