"""reboot_v178_20260625_v142_specialist_slices_on_v177.py

Strategy:
    Keep the published current-tree trusted parent v177 as the default line,
    then dispatch to the current-tree direct v142 body only on the narrow
    feature slices where probe evidence still shows a materially stronger row.

Metadata:
    version_id: reboot_v178_20260625_v142_specialist_slices_on_v177
    parent_version: reboot_v177_20260625_prob27like_micro_shortlist_on_v176
    status: candidate
    timestamp: 2026-06-25 KST
    strategy:
        - Preserve v177 unchanged outside the target specialist slices.
        - Use a runtime estimate guard so the expensive specialist body is only
          selected when the available timelimit comfortably covers it.
        - Route the prob31-like 4-bay concentrated tail and the prob32/prob37-
          like 3-bay low-proc diffuse tail to direct v142.
        - Keep the current v177 path on prob27-like and Family B guard rows.
    hypothesis:
        The current tree still contains a live v142 signal on a few non-prob27
        high-T rows. A narrow feature-gated portfolio dispatch can recover
        those rows without undoing the trusted v177 prob27 and Family B gains.
    intended_metric_target:
        - reduce Total T / Avg T on the current-tree trusted surface
        - preserve accepted_for_score 40/40
        - keep prob27/prob38/prob39/prob40 guard behavior from v177
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v177_20260625_prob27like_micro_shortlist_on_v176
"""

from __future__ import annotations

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as v142
from alg_versions import reboot_v177_20260625_prob27like_micro_shortlist_on_v176 as v177


ACTIVE_VERSION = "reboot_v178_20260625_v142_specialist_slices_on_v177"


def _runtime_reserve(timelimit: float) -> float:
    return max(1.0, min(10.0, timelimit * 0.08))


def _specialist_runtime_estimate(features: dict[str, float]) -> float:
    bays = int(features.get("bays", 0))
    return (
        0.18 * float(features.get("blocks", 0.0))
        + 0.60 * float(features.get("proc_mean", 0.0))
        + (4.0 if bays >= 4 else 0.0)
    )


def _matches_prob31like_slice(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 4
        and 190 <= int(features["blocks"]) <= 220
        and features["proc_mean"] >= 19.5
        and features["pref_concentration"] >= 0.72
        and features["pref_pressure"] >= 0.68
        and features["workload_imbalance_pressure"] >= 0.60
        and 4.2 <= features["slack_mean"] <= 5.6
    )


def _matches_lowproc_diffuse_tail_slice(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and int(features["blocks"]) >= 190
        and 10.5 <= features["proc_mean"] <= 12.1
        and 0.33 <= features["pref_concentration"] <= 0.42
        and 0.35 <= features["pref_pressure"] <= 0.40
        and features["workload_imbalance_pressure"] <= 0.15
        and 2.0 <= features["slack_mean"] <= 2.5
    )


def _should_use_v142_specialist(prob_info: dict, timelimit: float) -> tuple[bool, str]:
    features = v064._selector_features(prob_info)

    if _matches_prob31like_slice(features):
        label = "prob31like_v142_specialist"
    elif _matches_lowproc_diffuse_tail_slice(features):
        label = "lowproc_diffuse_tail_v142_specialist"
    else:
        return False, "keep_v177_default"

    reserve = _runtime_reserve(timelimit)
    estimate = _specialist_runtime_estimate(features)
    available = max(0.0, timelimit - reserve)
    if available < estimate:
        return False, f"runtime_guard_{label}"

    return True, label


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)

    use_specialist, label = _should_use_v142_specialist(prob_info, timelimit)
    if use_specialist:
        print(
            f"[baseline_hh reboot_v178] select_v142_specialist instance={prob_info.get('name')} "
            f"label={label} timelimit={timelimit:.2f}s"
        )
        return v142.algorithm(prob_info, timelimit)

    if label.startswith("runtime_guard_"):
        print(
            f"[baseline_hh reboot_v178] runtime_guard_keep_v177 instance={prob_info.get('name')} "
            f"label={label} timelimit={timelimit:.2f}s"
        )
    return v177.algorithm(prob_info, timelimit)
