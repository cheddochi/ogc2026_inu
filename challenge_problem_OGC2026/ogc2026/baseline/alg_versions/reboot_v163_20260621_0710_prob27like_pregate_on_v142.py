"""reboot_v163_20260621_0710_prob27like_pregate_on_v142.py

Strategy:
    Keep trusted v142 as the default path, and enter the heavier prob27-like
    recovery path only after a narrow pre-gate confirms the exact target slice.

Metadata:
    version_id: reboot_v163_20260621_0710_prob27like_pregate_on_v142
    parent_version: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
    status: candidate
    timestamp: 2026-06-21 07:10 KST
    strategy:
        - Preserve v142 unchanged outside the target subtype.
        - Compute a lightweight prob27-like selector first.
        - Only on the matching slice, reuse the existing v146 guarded recovery.
        - Avoid any broader family activation or additional search logic.
    hypothesis:
        The useful current-tree signal lives on the exact prob27-like slice,
        while the broader v146 surface still carries sibling spillover risk.
        Pre-gating that path before entering its heavier warm-start / research
        stack should preserve the target recovery and leave non-target rows on
        the direct v142 surface.
    intended_metric_target:
        - preserve accepted_for_score 40/40
        - recover the prob27-like runtime/T tail
        - avoid sibling prob25 spillover before any broader T-polish work
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136
"""

from __future__ import annotations


ACTIVE_VERSION = "reboot_v163_20260621_0710_prob27like_pregate_on_v142"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    rel_values = [float(block.get("release_time", 0.0)) for block in blocks]
    due_values = [float(block.get("due_date", 0.0)) for block in blocks]

    top_choices = []
    pref_weight = [0.0] * len(bays)
    pref_gap_values = []
    for block in blocks:
        prefs = [float(value) for value in block.get("bay_preferences", [])]
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
            ordered = sorted(prefs, reverse=True)
            pref_gap_values.append(ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0))
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += pref_value

    pref_concentration = 0.0
    if top_choices and blocks:
        pref_concentration = (
            max(top_choices.count(bay_id) for bay_id in range(len(bays))) / len(blocks)
        )

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    slack_values = [
        due - rel - proc
        for due, rel, proc in zip(due_values, rel_values, proc_values)
    ]

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": _mean(proc_values),
        "slack_mean": _mean(slack_values),
        "pref_concentration": pref_concentration,
        "pref_pressure": pref_pressure,
        "pref_gap_mean": _mean(pref_gap_values),
    }


def _matches_prob27like_heavytail(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 2
        and int(features["blocks"]) >= 140
        and features["proc_mean"] >= 20.0
        and features["slack_mean"] >= 4.5
        and features["pref_concentration"] >= 0.65
        and features["pref_pressure"] >= 0.62
        and features["pref_gap_mean"] >= 65.0
    )


def _time_tier(timelimit: float) -> str:
    if timelimit < 25.0:
        return "very_short"
    if timelimit < 45.0:
        return "short"
    if timelimit < 90.0:
        return "standard"
    if timelimit < 300.0:
        return "long"
    return "very_long"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    tier = _time_tier(timelimit)
    features = _selector_features(prob_info)

    from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as v142

    if tier in {"very_short", "short"} or not _matches_prob27like_heavytail(features):
        return v142.algorithm(prob_info, timelimit)

    from alg_versions import reboot_v146_20260621_0215_prob27like_efficiency_shortlist_on_v142 as v146

    return v146.algorithm(prob_info, timelimit)
