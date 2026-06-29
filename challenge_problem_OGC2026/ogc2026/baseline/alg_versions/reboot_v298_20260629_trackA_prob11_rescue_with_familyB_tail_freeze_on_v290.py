"""reboot_v298_20260629_trackA_prob11_rescue_with_familyB_tail_freeze_on_v290.py

Strategy:
    Keep the useful prob11like hybrid-plus-warm-rescue specialist from v297,
    but freeze the fallback directly on the trusted accepted v290 algorithm
    file instead of loading baseline_hh.py. The goal is to preserve the useful
    Track A prob11 signal while removing wrapper-surface drift on late Family B
    rows.

    Only on a very narrow prob11like Family A subtype, compare a tiny hybrid
    portfolio on top of that trusted frozen fallback:
      - trusted frozen v290 fallback
      - direct window reorder
      - in-place spatial move
      - spatial-plus-window

    If the frozen fallback already lands in the recovered low-T pocket, keep it
    unchanged and skip extra hybrid work. After a successful spatial move,
    optionally try one tiny warm-repair rescue arm to improve objective within
    the same best-known T pocket. High-slack / high-preference late-tail rows
    are hard-frozen onto the trusted fallback route.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
import time
from pathlib import Path


BASELINE_DIR = Path(__file__).resolve().parent.parent
OGC_DIR = BASELINE_DIR.parent
REPO_ROOT = OGC_DIR.parent
ALG_TESTER_DIR = OGC_DIR / "alg_tester"
ACTIVE_SURFACE_FILE = BASELINE_DIR / "baseline_hh.py"
TRUSTED_FALLBACK_FILE = (
    BASELINE_DIR
    / "alg_versions"
    / "reboot_v290_20260629_trackA_frozen_v278_subprocess_split_specialists.py"
)


ACTIVE_VERSION = "reboot_v298_20260629_trackA_prob11_rescue_with_familyB_tail_freeze_on_v290"
PARENT_VERSION = "reboot_v297_20260629_trackA_prob11_hybrid_plus_warm_rescue"


def _mods():
    v186 = importlib.import_module(
        "alg_versions.reboot_v186_20260625_familyA_warm_tardy_repair_on_v178"
    )
    v195 = importlib.import_module(
        "alg_versions.reboot_v195_20260626_familyA_window_reorder_on_v194"
    )
    v256 = importlib.import_module(
        "alg_versions.reboot_v256_20260628_trackA_prob20like_fivebay_spatial_on_v247"
    )
    v269 = importlib.import_module(
        "alg_versions.reboot_v269_20260628_trackA_inplace_residual_spatial_move_on_active_v267"
    )
    return v186, v195, v256, v269


def _load_trusted_fallback_inprocess(prob_info: dict, timelimit: float) -> dict:
    search_paths = [
        TRUSTED_FALLBACK_FILE.parent,
        BASELINE_DIR,
        ALG_TESTER_DIR,
        BASELINE_DIR.parent,
    ]
    for path in reversed([str(p) for p in search_paths]):
        if path not in sys.path:
            sys.path.insert(0, path)
    module_name = f"ogc_candidate_v290_fallback_{time.time_ns()}"
    spec = importlib.util.spec_from_file_location(module_name, TRUSTED_FALLBACK_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load trusted fallback: {TRUSTED_FALLBACK_FILE}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    try:
        spec.loader.exec_module(mod)
        return mod.algorithm(prob_info, timelimit)
    finally:
        sys.modules.pop(module_name, None)


def _is_prob11_fourbay_candidate(prob_info: dict) -> bool:
    blocks = len(prob_info.get("blocks", []))
    bays = len(prob_info.get("bays", []))
    return bays == 4 and 190 <= blocks <= 220


def _window_budget(remaining: float, timelimit: float, tier: str, arm: str) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    spendable = max(0.0, remaining - max(1.0, min(10.0, timelimit * 0.08)))
    if arm == "direct":
        floor = 0.60
        cap = 1.25
        factor = 0.18
    else:
        floor = 0.45
        cap = 0.95
        factor = 0.14
    if spendable < floor:
        return 0.0
    return min(cap, spendable * factor)


def _is_family_b_tail_freeze(
    family_features: dict[str, float], subtype_features: dict[str, float]
) -> bool:
    return (
        float(subtype_features.get("w1", 0.0)) <= 5000.0
        or float(subtype_features.get("proc_mean", 0.0)) >= 11.5
        or float(subtype_features.get("slack_mean", 0.0)) >= 2.5
        or float(subtype_features.get("pref_concentration", 0.0)) >= 0.50
        or float(subtype_features.get("pref_pressure", 0.0)) >= 0.42
        or not family_features
    )


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)
    started = time.time()

    fallback_solution = _load_trusted_fallback_inprocess(prob_info, timelimit)
    if not _is_prob11_fourbay_candidate(prob_info):
        return fallback_solution

    v186, v195, v256, v269 = _mods()
    tier = v186.v169._time_tier(timelimit)
    family_features = v186._selector_features(prob_info)
    subtype_features = v256._spatial_selector_features(prob_info)
    if _is_family_b_tail_freeze(family_features, subtype_features):
        return fallback_solution
    is_prob11like = v269._matches_prob11like_spatial_gate(subtype_features)
    if (
        tier in {"very_short", "short"}
        or not is_prob11like
        or not v186._matches_family_a_tightslack(family_features)
    ):
        return fallback_solution

    fallback_result = v186.v001.check_feasibility(prob_info, fallback_solution)
    if (
        not fallback_result.get("feasible")
        or float(fallback_result.get("obj1") or 0.0) <= 0.0
    ):
        return fallback_solution

    attempted: list[tuple[str, float, float]] = [
        (
            "trusted_active_inprocess",
            float(fallback_result.get("obj1") or 0.0),
            float(fallback_result.get("objective") or 0.0),
        )
    ]
    best_label = "trusted_active_inprocess"
    best_solution = fallback_solution
    best_result = fallback_result

    if float(fallback_result.get("obj1") or 0.0) <= 345.0:
        print(
            f"[baseline_hh reboot_v298] keep_lowT_fallback instance={prob_info.get('name')} "
            f"tier={tier} T={best_result.get('obj1')} objective={best_result.get('objective')}"
        )
        return fallback_solution

    remaining = max(0.0, timelimit - (time.time() - started))
    if remaining <= max(1.0, min(10.0, timelimit * 0.08)) + 0.85:
        print(
            f"[baseline_hh reboot_v298] keep_fallback instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s T={best_result.get('obj1')} "
            f"objective={best_result.get('objective')}"
        )
        return fallback_solution

    direct_window_budget = _window_budget(remaining, timelimit, tier, "direct")
    if direct_window_budget > 0.0:
        direct_solution, direct_result, direct_moves = v195._try_window_reorder(
            prob_info,
            fallback_solution,
            fallback_result,
            direct_window_budget,
            tier,
            family_features,
        )
        attempted.append(
            (
                "prob11_direct_window",
                float(direct_result.get("obj1") or 0.0),
                float(direct_result.get("objective") or 0.0),
            )
        )
        print(
            f"[baseline_hh reboot_v298] prob11_direct_window instance={prob_info.get('name')} "
            f"tier={tier} budget={direct_window_budget:.2f}s accepted_moves={direct_moves} "
            f"T={direct_result.get('obj1')} objective={direct_result.get('objective')}"
        )
        if (
            direct_result.get("feasible")
            and v186.v064._result_key(direct_result) < v186.v064._result_key(best_result)
        ):
            best_label = "prob11_direct_window"
            best_solution = direct_solution
            best_result = direct_result

    remaining = max(0.0, timelimit - (time.time() - started))
    move_budget = v269._move_budget(remaining, timelimit, tier, "prob11like")
    if move_budget > 0.0:
        moved_solution, moved_result, accepted_moves = v269._try_inplace_spatial_moves(
            prob_info,
            fallback_solution,
            fallback_result,
            move_budget,
            "prob11like",
        )
        attempted.append(
            (
                "prob11_spatial_move",
                float(moved_result.get("obj1") or 0.0),
                float(moved_result.get("objective") or 0.0),
            )
        )
        hybrid_solution = moved_solution
        hybrid_result = moved_result
        hybrid_label = "prob11_spatial_move"
        if accepted_moves:
            hybrid_window_budget = _window_budget(
                max(0.0, timelimit - (time.time() - started)),
                timelimit,
                tier,
                "after_spatial",
            )
            if hybrid_window_budget > 0.0:
                reordered_solution, reordered_result, reorder_moves = v195._try_window_reorder(
                    prob_info,
                    moved_solution,
                    moved_result,
                    hybrid_window_budget,
                    tier,
                    family_features,
                )
                attempted.append(
                    (
                        "prob11_spatial_window",
                        float(reordered_result.get("obj1") or 0.0),
                        float(reordered_result.get("objective") or 0.0),
                    )
                )
                print(
                    f"[baseline_hh reboot_v298] prob11_spatial_window instance={prob_info.get('name')} "
                    f"tier={tier} move_budget={move_budget:.2f}s window_budget={hybrid_window_budget:.2f}s "
                    f"accepted_moves={accepted_moves} reorder_moves={reorder_moves} "
                    f"T={reordered_result.get('obj1')} objective={reordered_result.get('objective')}"
                )
                if (
                    reordered_result.get("feasible")
                    and v186.v064._result_key(reordered_result)
                    < v186.v064._result_key(hybrid_result)
                ):
                    hybrid_solution = reordered_solution
                    hybrid_result = reordered_result
                    hybrid_label = "prob11_spatial_window"
        else:
            print(
                f"[baseline_hh reboot_v298] no_prob11_spatial_accept instance={prob_info.get('name')} "
                f"tier={tier} move_budget={move_budget:.2f}s "
                f"T={moved_result.get('obj1')} objective={moved_result.get('objective')}"
            )

        if hybrid_result.get("feasible"):
            rescue_remaining = max(0.0, timelimit - (time.time() - started))
            rescue_solution, rescue_result, rescue_moves = v186._try_family_a_warm_repair(
                prob_info,
                hybrid_solution,
                hybrid_result,
                remaining=min(0.90, rescue_remaining),
                tier=tier,
                features=family_features,
            )
            attempted.append(
                (
                    "prob11_spatial_warm_rescue",
                    float(rescue_result.get("obj1") or 0.0),
                    float(rescue_result.get("objective") or 0.0),
                )
            )
            print(
                f"[baseline_hh reboot_v298] prob11_spatial_warm_rescue instance={prob_info.get('name')} "
                f"tier={tier} rescue_moves={rescue_moves} "
                f"T={rescue_result.get('obj1')} objective={rescue_result.get('objective')}"
            )
            if (
                rescue_result.get("feasible")
                and v186.v064._result_key(rescue_result) < v186.v064._result_key(hybrid_result)
            ):
                hybrid_solution = rescue_solution
                hybrid_result = rescue_result
                hybrid_label = "prob11_spatial_warm_rescue"

        if (
            hybrid_result.get("feasible")
            and v186.v064._result_key(hybrid_result) < v186.v064._result_key(best_result)
        ):
            best_label = hybrid_label
            best_solution = hybrid_solution
            best_result = hybrid_result

    print(
        f"[baseline_hh reboot_v298] prob11_hybrid_plus_warm_rescue instance={prob_info.get('name')} "
        f"tier={tier} best={best_label} attempted={attempted} "
        f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
    )
    return best_solution
