"""reboot_v177_20260625_prob27like_micro_shortlist_on_v176.py

Strategy:
    Keep the published current-tree trusted parent v176 unchanged everywhere,
    then graft the proven prob27-like micro-shortlist postpass onto that
    stronger parent surface only for the 2-bay high-proc runtime-risk slice.

Metadata:
    version_id: reboot_v177_20260625_prob27like_micro_shortlist_on_v176
    parent_version: reboot_v176_20260625_prob38like_pair_quantile_on_v152
    status: candidate
    timestamp: 2026-06-25 KST
    strategy:
        - Preserve v176 unchanged outside the target subtype.
        - Build the exact v176 base solution first.
        - On the prob27-like slice only, reuse the tiny v169 efficiency
          shortlist reinsert under the same bounded budget discipline.
        - Keep only strictly better officially feasible results.
    hypothesis:
        v176 already fixed the prob38-like Family B tail, but it still leaves
        a small one-block improvement signal on the prob27-like slice. The
        v169 shortlist proved that signal is live on the current tree, so
        grafting it onto v176 should reduce T on prob27-like rows without
        reopening the newer Family B gains.
    intended_metric_target:
        - reduce the prob27-like T tail on top of v176
        - preserve accepted_for_score on the current trusted v176 surface
        - keep the stronger prob38/prob39/prob40 Family B guard rows
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v176_20260625_prob38like_pair_quantile_on_v152
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v169_20260621_0935_v152_prob27like_micro_shortlist as v169
from alg_versions import reboot_v176_20260625_prob38like_pair_quantile_on_v152 as v176


ACTIVE_VERSION = "reboot_v177_20260625_prob27like_micro_shortlist_on_v176"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    started = time.time()
    tier = v169._time_tier(timelimit)

    base_solution = v176.algorithm(prob_info, timelimit)
    base_result = v001.check_feasibility(prob_info, base_solution)
    features = v169._selector_features(prob_info)

    if (
        not base_result.get("feasible")
        or tier in {"very_short", "short"}
        or not v169._matches_prob27like_heavytail(features)
        or float(base_result.get("obj1") or 0.0) < 5000.0
    ):
        return base_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    reserve = v169._dynamic_reserve(timelimit)
    spendable = remaining - reserve
    if spendable <= 0.9:
        print(
            f"[baseline_hh reboot_v177] skip_prob27like_micro_shortlist_on_v176 "
            f"instance={prob_info.get('name')} tier={tier} remaining={remaining:.2f}s "
            f"reserve={reserve:.2f}s spendable={spendable:.2f}s "
            f"base_T={base_result.get('obj1')}"
        )
        return base_solution

    research_solution, research_result = v169._try_efficiency_shortlist_reinsert(
        prob_info,
        base_solution,
        base_result,
        spendable,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v177] selected_prob27like_micro_shortlist_on_v176 "
            f"instance={prob_info.get('name')} base_T={base_result.get('obj1')} "
            f"best_T={research_result.get('obj1')} "
            f"objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v177] keep_v176_base instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
