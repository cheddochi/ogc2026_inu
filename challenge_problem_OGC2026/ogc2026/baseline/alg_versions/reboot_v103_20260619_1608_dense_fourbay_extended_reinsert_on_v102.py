"""reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102.py

Strategy:
    Keep v102 as the warm start, then replay the tiny extended tardy-block
    reinsertion only on the dense 4-bay high-proc family.

Metadata:
    version_id: reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102
    parent_version: reboot_v102_20260619_1506_lowproc_threebay_release_due_guard_on_v101
    status: candidate
    timestamp: 2026-06-19 16:08 KST
    strategy:
        - Preserve v102 unchanged outside the target family.
        - Build the v102 warm start first.
        - On the dense 4-bay high-proc family, replay the bounded extended
          reinsertion used by v085 on a small tardy shortlist.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The remaining gap after v102 is concentrated in the dense 4-bay
        high-proc runtime-risk family. A tiny reinsertion pass on top of the
        existing v102 warm start may recover small objective slack there
        without changing the broader chain or reopening unrelated regressions.
    intended_metric_target:
        - improve dense four-bay high-proc rows such as prob31/prob40-like
        - preserve the v102 40/40 scoreable contract
        - improve avg objective versus v102
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v102_20260619_1506_lowproc_threebay_release_due_guard_on_v101
"""

from __future__ import annotations

import time

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v074_20260618_2302_fourbay_highproc_fast_reinsert_portfolio as v074
from alg_versions import reboot_v085_20260619_0512_fourbay_dense_extended_reinsert as v085
from alg_versions import reboot_v102_20260619_1506_lowproc_threebay_release_due_guard_on_v101 as v102


ACTIVE_VERSION = "reboot_v103_20260619_1608_dense_fourbay_extended_reinsert_on_v102"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    features = v074._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v102.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    family_budget = v074._family_direct_budget(float(timelimit), tier)
    if (
        not base_result.get("feasible")
        or not v074._matches_fourbay_highproc_dense_family(features)
        or family_budget < 45.0
        or float(base_result.get("obj1") or 0.0) <= 2500.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= 0.5:
        print(
            f"[baseline_hh reboot_v103] skip_dense_fourbay_extended_reinsert instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = v085._try_extended_reinsert_portfolio(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v103] selected_dense_fourbay_extended_reinsert instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v103] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
