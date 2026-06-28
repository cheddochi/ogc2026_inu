"""reboot_v060_20260618_2031_threebay_gap_release_due.py

Strategy:
    Keep trusted v057 as the default path, but add one feature-based direct
    release_due policy for a packed 3-bay low-proc moderate-gap subtype.

Metadata:
    version_id: reboot_v060_20260618_2031_threebay_gap_release_due
    parent_version: reboot_v057_20260618_0006_prob38like_dual_policy_portfolio
    status: candidate
    timestamp: 2026-06-18 20:31 KST
    strategy:
        - Preserve every existing v057 path, including the prob38-like dual
          policy portfolio and the current 4-bay runtime-sensitive chain.
        - On a packed 3-bay large/xlarge low-proc moderate-gap subtype, run a
          direct deeper release_due scan.
    hypothesis:
        That subtype still leaves objective on the table under v057's inherited
        direct chain. A slightly deeper release_due scan can improve objective
        there without touching the current high-risk high-proc family.
    intended_metric_target:
        - improve the packed 3-bay low-proc moderate-gap subtype
        - preserve smoke-8 rows unchanged
        - improve avg objective versus trusted v057
    validation_status:
        pending
    benchmark_evidence_path:
        pending
    rollback_target: reboot_v057_20260618_0006_prob38like_dual_policy_portfolio
"""

from __future__ import annotations

import time

import baseline_greedy
from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v050_20260617_2015_prob38like_release_aware as v050
from alg_versions import reboot_v057_20260618_0006_prob38like_dual_policy_portfolio as v057


ACTIVE_VERSION = "reboot_v060_20260618_2031_threebay_gap_release_due"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]

    pref_gap_values = []
    packing_scores = []
    for block in blocks:
        prefs = list(block.get("bay_preferences", []))
        if prefs:
            ordered = sorted((float(value) for value in prefs), reverse=True)
            pref_gap_values.append(ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0))

        best_ratio = 0.0
        for orient_idx in range(len(block.get("shape", []))):
            x0, y0, x1, y1 = baseline_greedy._block_bbox(block, orient_idx)
            width = x1 - x0
            height = y1 - y0
            area = width * height
            for bay in bays:
                bay_w = float(bay["width"])
                bay_h = float(bay["height"])
                if width <= bay_w + 1e-9 and height <= bay_h + 1e-9:
                    best_ratio = max(best_ratio, area / (bay_w * bay_h))
        packing_scores.append(best_ratio)

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "proc_mean": _mean(proc_values),
        "pref_gap_mean": _mean(pref_gap_values),
        "packing_pressure": _mean(packing_scores),
    }


def _matches_threebay_gap_release_class(features: dict[str, float]) -> bool:
    return (
        int(features["bays"]) == 3
        and int(features["blocks"]) >= 200
        and 10.5 <= features["proc_mean"] <= 12.0
        and features["packing_pressure"] >= 0.13
        and 46.0 <= features["pref_gap_mean"] <= 51.0
    )


def _policy_budget(timelimit: float, tier: str) -> float:
    reserve = max(4.0, timelimit * 0.08)
    fraction = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 0.92,
        "long": 0.92,
        "very_long": 0.92,
    }[tier]
    cap = {
        "very_short": 0.0,
        "short": 0.0,
        "standard": 58.0,
        "long": 58.0,
        "very_long": 59.0,
    }[tier]
    return min(cap, max(8.0, timelimit * fraction - reserve))


def _policy_max_positions(tier: str) -> int:
    return {
        "very_short": 8,
        "short": 10,
        "standard": 18,
        "long": 18,
        "very_long": 18,
    }[tier]


def _class_solution(prob_info: dict, timelimit: float, tier: str) -> dict:
    started = time.time()
    budget = _policy_budget(float(timelimit), tier)
    candidate = v001._build_limited_concurrent_solution(
        prob_info,
        budget=budget,
        order_strategy="release_due",
        top_bays=3,
        max_positions=_policy_max_positions(tier),
        max_orients=4,
    )
    result = v001.check_feasibility(prob_info, candidate)
    print(
        f"[baseline_hh reboot_v060] threebay_gap_release_due instance={prob_info.get('name')} "
        f"feasible={result.get('feasible')} T={result.get('obj1')} "
        f"objective={result.get('objective')} elapsed={time.time() - started:.2f}s "
        f"budget={budget:.1f} tier={tier}"
    )
    if result.get("feasible"):
        return candidate
    print(
        f"[baseline_hh reboot_v060] threebay_gap_release_due_fallback instance={prob_info.get('name')} "
        f"tier={tier}"
    )
    return v057.algorithm(prob_info, timelimit)


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    features = _selector_features(prob_info)
    tier = v050._time_tier(float(timelimit))
    if tier not in {"very_short", "short"} and _matches_threebay_gap_release_class(features):
        return _class_solution(prob_info, timelimit, tier)
    return v057.algorithm(prob_info, timelimit)
