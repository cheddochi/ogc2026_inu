"""reboot_v164_20260621_0742_v142_pure_delegate_surface.py

Strategy:
    Minimal control wrapper that does nothing except delegate to direct v142.

Metadata:
    version_id: reboot_v164_20260621_0742_v142_pure_delegate_surface
    parent_version: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
    status: candidate
    timestamp: 2026-06-21 07:42 KST
    strategy:
        - No selector logic.
        - No local search.
        - No budget changes.
        - Delegate directly to v142 and return its result.
    hypothesis:
        A pure delegate surface should reproduce direct v142 exactly. If it
        does not, the current-tree hidden risk is deeper wrapper/module surface
        instability rather than the specific target-family selector logic.
    intended_metric_target:
        - diagnose wrapper-surface stability before the next real T-breakthrough
          candidate
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
"""

from __future__ import annotations

from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as active


ACTIVE_VERSION = "reboot_v164_20260621_0742_v142_pure_delegate_surface"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
