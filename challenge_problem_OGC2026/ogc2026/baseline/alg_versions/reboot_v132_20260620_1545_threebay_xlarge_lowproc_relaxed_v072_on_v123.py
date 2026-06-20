"""reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123.py

Strategy:
    Keep trusted v123 as the default line, but route the runtime-sensitive
    three-bay xlarge low-proc tight-slack subtype into a relaxed-headroom v072
    path when the timelimit is long enough.

Metadata:
    version_id: reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123
    parent_version: reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122
    status: accepted_recovery
    timestamp: 2026-06-20 15:45 KST
    strategy:
        - Preserve v123 exactly outside the target subtype.
        - Detect the v072 three-bay xlarge low-proc family from prob_info
          features only.
        - On that subtype, run a direct v072-style opportunity pass but relax
          the headroom gate from reserve + 12.0 to reserve + 10.0.
        - Fall back to v123 on any exception or off-tier case.
    hypothesis:
        The prob39-like regression comes from a small runtime cliff at the old
        v072 opportunity gate. Relaxing that gate slightly is enough to recover
        the stronger single-block repair on the long-limit-opportunity slice
        without reopening timeout risk on the rest of the train40 surface.
    intended_metric_target:
        - improve the v072-family prob39-like row
        - preserve accepted_for_score 40/40
        - reduce avg objective and avg T versus trusted v123
    validation_status:
        accepted recovery line; exact full40 headline match to v123 with
        stronger active-surface stability on prob39
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v132_train40_20260620_001
    rollback_target: reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122
"""

from __future__ import annotations

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v072_20260618_2135_threebay_xlarge_lowproc_opportunity_single as v072
from alg_versions import reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122 as v123


ACTIVE_VERSION = "reboot_v132_20260620_1545_threebay_xlarge_lowproc_relaxed_v072_on_v123"


def _time_tier(timelimit: float) -> str:
    return v123._time_tier(timelimit)


def _should_try_relaxed_v072(prob_info: dict, timelimit: float) -> bool:
    features = v072._selector_features(prob_info)
    tier = _time_tier(float(timelimit))
    return (
        tier in {"standard", "long", "very_long"}
        and float(timelimit) >= 60.0
        and v072._matches_threebay_xlarge_lowproc_class(features)
    )


def _relaxed_v072_algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    started = v064.time.time()
    features = v072._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v072.v070.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not v072._matches_threebay_xlarge_lowproc_class(features)
        or float(base_result.get("obj1") or 0.0) < 3000.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (v064.time.time() - started))
    relaxed_headroom = v072._dynamic_reserve(float(timelimit)) + 10.0
    if remaining <= relaxed_headroom:
        print(
            f"[baseline_hh reboot_v132] skip_relaxed_v072 instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s threshold={relaxed_headroom:.2f}s"
        )
        return base_solution

    research_solution, research_result = v072._try_penalty_single_research(
        prob_info,
        base_solution,
        base_result,
        remaining - v072._dynamic_reserve(float(timelimit)),
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v132] selected_relaxed_v072 instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v132] keep_v070_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    if not _should_try_relaxed_v072(prob_info, float(timelimit)):
        return v123.algorithm(prob_info, timelimit)

    try:
        print(
            f"[baseline_hh reboot_v132] direct_relaxed_v072_family "
            f"instance={prob_info.get('name')} tier={_time_tier(float(timelimit))} "
            f"timelimit={float(timelimit):.1f}s"
        )
        return _relaxed_v072_algorithm(prob_info, timelimit)
    except Exception as exc:
        print(
            f"[baseline_hh reboot_v132] fallback_v123_after_relaxed_v072_exception "
            f"instance={prob_info.get('name')} error={exc}"
        )
        return v123.algorithm(prob_info, timelimit)
