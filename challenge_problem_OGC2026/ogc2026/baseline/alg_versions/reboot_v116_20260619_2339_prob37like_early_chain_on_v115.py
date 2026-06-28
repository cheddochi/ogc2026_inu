"""reboot_v116_20260619_2339_prob37like_early_chain_on_v115.py

Strategy:
    Keep v115 as the default path, but replace only the prob37-like subtype
    with the runtime-stable early current-source recovery chain that showed the
    real T breakthrough before later phases consumed the remaining budget.

Metadata:
    version_id: reboot_v116_20260619_2339_prob37like_early_chain_on_v115
    parent_version: reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114
    status: candidate
    timestamp: 2026-06-19 23:39 KST
    strategy:
        - Preserve v115 unchanged outside the prob37-like subtype.
        - Reuse the existing feature-based prob37-like selector from v100.
        - On that subtype only, build the earlier v060 direct release_due warm
          start and then apply the cheap v065 one-block diffuse re-search.
        - Keep the best officially feasible result from that early chain only.
    hypothesis:
        The current-source prob37-like loss is a runtime-cliff problem, not a
        lack of local improvement signal. Replaying only the early v060+v065
        chain should recover the stronger row without reintroducing the later
        timing cliff that drifted the historical v096 branch.
    intended_metric_target:
        - improve the prob37-like subtype row
        - preserve v115's 40/40 scoreable contract
        - reduce the remaining avg objective gap versus historical v096
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v060_20260618_2031_threebay_gap_release_due as v060
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v065_20260618_1735_threebay_diffuse_single_research as v065
from alg_versions import reboot_v100_20260619_1355_prob37like_flattened_iterative_reinsert_on_v099 as v100
from alg_versions import reboot_v115_20260620_0032_prob31like_displaced_fast_on_v114 as v115


ACTIVE_VERSION = "reboot_v116_20260619_2339_prob37like_early_chain_on_v115"


def _prob37like_early_chain_solution(
    prob_info: dict,
    timelimit: float,
    tier: str,
) -> tuple[dict, dict]:
    started = time.time()
    base_solution = v060._class_solution(prob_info, float(timelimit), tier)
    base_result = v001.check_feasibility(prob_info, base_solution)
    if not base_result.get("feasible"):
        return base_solution, base_result

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= v064._dynamic_reserve(float(timelimit)) + 2.0:
        print(
            f"[baseline_hh reboot_v116] keep_prob37like_direct_base instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution, base_result

    candidate_solution, candidate_result = v065._try_greedy_research(
        prob_info,
        base_solution,
        base_result,
        remaining,
        float(timelimit),
        tier,
    )
    print(
        f"[baseline_hh reboot_v116] prob37like_early_chain instance={prob_info.get('name')} "
        f"tier={tier} base_T={base_result.get('obj1')} cand_T={candidate_result.get('obj1')} "
        f"base_objective={base_result.get('objective')} "
        f"cand_objective={candidate_result.get('objective')}"
    )
    if v064._result_key(candidate_result) < v064._result_key(base_result):
        return candidate_solution, candidate_result
    return base_solution, base_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    tier = v050._time_tier(float(timelimit))

    if (
        tier not in {"very_short", "short"}
        and float(timelimit) >= 55.0
        and v100._matches_prob37like_runtime_class(prob_info)
    ):
        candidate_solution, candidate_result = _prob37like_early_chain_solution(
            prob_info,
            timelimit,
            tier,
        )
        if candidate_result.get("feasible"):
            return candidate_solution
        print(
            f"[baseline_hh reboot_v116] prob37like_early_chain_fallback "
            f"instance={prob_info.get('name')} feasible={candidate_result.get('feasible')} "
            f"objective={candidate_result.get('objective')}"
        )

    return v115.algorithm(prob_info, timelimit)
