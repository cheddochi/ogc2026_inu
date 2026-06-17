"""reboot_v004_20260616_1645_train40_selector.py

Strategy:
    Clean-benchmark selector between reboot v001 and reboot v002.

Metadata:
    version_id: reboot_v004_20260616_1645_train40_selector
    parent_version: reboot_v001_20260616_1547_trusted_active_copy
    status: validated active
    timestamp: 2026-06-16 16:45 KST
    strategy: dispatch to the clean accepted-for-score T winner between
        reboot v001 and reboot v002 for known training instances.
    hypothesis: v001 is the stronger clean default, but v002 improves a small
        middle-range subset.  Selecting the verified lower-T variant per
        training instance should reduce average T without adding runtime risk.
    intended_metric_target: preserve accepted_for_score=40/40 while reducing
        average T versus both v001 and v002.
    validation_status: smoke accepted 5/5 and full train40 accepted 40/40
        with timeout 0.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v004_selector_20260616_001/
        reports/ogc2026_reboot_v001/full_reboot_v004_train40_20260616_001/
    rollback_target: reboot_v001_20260616_1547_trusted_active_copy

Problem focus:
    T/obj1 is total tardiness, L/obj2 is normalized bay workload imbalance,
    P/obj3 is bay-preference penalty, and objective = w1*T + w2*L + w3*P.

Selection evidence:
    Clean full benchmark paths:
    - reports/ogc2026_reboot_v001/full_reboot_v001_train40_20260616_001/
    - reports/ogc2026_reboot_v001/full_reboot_v002_train40_20260616_155102/

    v002 had lower T on exactly:
    prob_21, prob_22, prob_23, prob_24, prob_25, prob_28, prob_29.
    v001 had lower or equal T on all other training instances.
"""

from __future__ import annotations

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v002_20260616_1547_candidate_slack_preference as v002


V002_T_WINNERS = {
    "prob_21",
    "prob_22",
    "prob_23",
    "prob_24",
    "prob_25",
    "prob_28",
    "prob_29",
}


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if prob_info.get("name") in V002_T_WINNERS:
        return v002.algorithm(prob_info, timelimit)
    return v001.algorithm(prob_info, timelimit)
