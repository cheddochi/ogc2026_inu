"""reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093.py

Strategy:
    Keep trusted v093 as the default path, then replay the older medium 3-bay
    diffuse gap-aware single-block repair on top of the newer active parent.

Metadata:
    version_id: reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093
    parent_version: reboot_v093_20260619_0917_threebay_midproc_slackband_on_v092
    status: accepted
    timestamp: 2026-06-19 09:31 KST
    strategy:
        - Preserve v093 unchanged outside the target subtype.
        - Build the trusted v093 warm start first.
        - On the target family, replay the v069 gap-aware single-block repair
          over the current active warm start.
        - Keep only strictly better officially feasible results.
    hypothesis:
        The medium 3-bay diffuse family still carries a useful gap-aware target
        selection signal. Replaying the old v069 repair on top of the improved
        v093 parent should lower prob32-like objective again while leaving the
        sibling prob33-like row neutral.
    intended_metric_target:
        - improve the medium 3-bay diffuse family
        - preserve the current 40/40 scoreable contract
        - improve avg objective versus trusted v093
    validation_status:
        accepted_for_score=40/40 on full train40 benchmark
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v094_train40_20260619_001
    rollback_target: reboot_v093_20260619_0917_threebay_midproc_slackband_on_v092
"""

from __future__ import annotations

import time

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v069_20260618_1950_threebay_medium_diffuse_gap_single as v069
from alg_versions import reboot_v093_20260619_0917_threebay_midproc_slackband_on_v092 as v093


ACTIVE_VERSION = "reboot_v094_20260619_0931_threebay_medium_diffuse_gap_on_v093"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    features = v069._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v093.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not v069._matches_threebay_medium_diffuse_gap_class(features)
        or float(base_result.get("obj1") or 0.0) < 3000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= v069._dynamic_reserve(float(timelimit)) + 10.0:
        print(
            f"[baseline_hh reboot_v094] skip_threebay_medium_diffuse instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = v069._try_gap_single_research(
        prob_info,
        base_solution,
        base_result,
        remaining - v069._dynamic_reserve(float(timelimit)),
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v094] selected_threebay_medium_diffuse instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v094] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
