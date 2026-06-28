"""reboot_v092_20260619_0859_prob40like_runtime_stable_orient3.py

Strategy:
    Keep trusted v089 as the default path, then replace only the original
    prob40-like high-workload family path with a lower-branching direct
    builder plus the existing tiny reinsertion pass.

Metadata:
    version_id: reboot_v092_20260619_0859_prob40like_runtime_stable_orient3
    parent_version: reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass
    status: accepted
    timestamp: 2026-06-19 08:59 KST
    strategy:
        - Preserve v089 unchanged outside the target family.
        - On the prob40-like family, bypass the unstable inherited direct-first
          warm start and build a lower-branching direct candidate first.
        - Reuse the tiny dense-family reinsertion pass on top of that stable
          warm start.
        - Keep the stable candidate only when it is officially feasible.
    hypothesis:
        The runtime-stable orient3 direct builder is still useful, but it
        should only be applied to the original prob40-like high-workload
        family. Narrowing the selector back to that workload-aware subtype
        should keep the prob40 gain while avoiding the prob31 regression seen
        in v091.
    intended_metric_target:
        - improve the prob40-like family objective
        - preserve the current 40/40 scoreable contract
        - improve avg objective versus trusted v089
    validation_status:
        accepted_for_score=40/40 on full train40 benchmark
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v092_train40_20260619_001
    rollback_target: reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v063_20260618_1605_prob40like_direct_first_due_release as v063
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v085_20260619_0512_fourbay_dense_extended_reinsert as v085
from alg_versions import reboot_v089_20260619_0743_fourbay_lowproc_diffuse_third_pass as v089


ACTIVE_VERSION = "reboot_v092_20260619_0859_prob40like_runtime_stable_orient3"


def _stable_direct_plus_reinsert(prob_info: dict, timelimit: float, tier: str) -> tuple[dict, dict]:
    started = time.time()
    budget = v063._direct_budget(float(timelimit), tier)
    direct_solution = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="due_release_proc",
        top_bays=4,
        max_positions=12,
        max_orients=3,
    )
    direct_result = v001.check_feasibility(prob_info, direct_solution)
    print(
        f"[baseline_hh reboot_v092] prob40like_stable_direct instance={prob_info.get('name')} "
        f"feasible={direct_result.get('feasible')} T={direct_result.get('obj1')} "
        f"objective={direct_result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f}s tier={tier}"
    )
    if not direct_result.get("feasible"):
        return direct_solution, direct_result

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    improved_solution, improved_result = v085._try_extended_reinsert_portfolio(
        prob_info,
        direct_solution,
        direct_result,
        remaining,
        tier,
    )
    if v064._result_key(improved_result) < v064._result_key(direct_result):
        print(
            f"[baseline_hh reboot_v092] selected_prob40like_reinsert instance={prob_info.get('name')} "
            f"T={improved_result.get('obj1')} objective={improved_result.get('objective')}"
        )
        return improved_solution, improved_result

    print(
        f"[baseline_hh reboot_v092] keep_prob40like_direct instance={prob_info.get('name')} "
        f"T={direct_result.get('obj1')} objective={direct_result.get('objective')}"
    )
    return direct_solution, direct_result


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    features = v063._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    if v063._matches_prob40like_class(features):
        budget = v063._direct_budget(float(timelimit), tier)
        if budget >= 45.0 and tier not in {"very_short", "short"}:
            candidate_solution, candidate_result = _stable_direct_plus_reinsert(prob_info, timelimit, tier)
            if candidate_result.get("feasible"):
                return candidate_solution
            print(
                f"[baseline_hh reboot_v092] prob40like_stable_direct_fallback "
                f"instance={prob_info.get('name')} feasible={candidate_result.get('feasible')} "
                f"objective={candidate_result.get('objective')}"
            )

    return v089.algorithm(prob_info, timelimit)
