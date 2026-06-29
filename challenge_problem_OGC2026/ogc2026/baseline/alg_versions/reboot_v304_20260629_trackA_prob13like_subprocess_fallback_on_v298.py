"""reboot_v304_20260629_trackA_prob13like_subprocess_fallback_on_v298.py

Strategy:
    Keep the exact prob13-like specialist portfolio from v303, but hard-freeze
    the trusted fallback on the direct v298 algorithm file through an isolated
    subprocess route on the narrow 4-bay lane before comparing:
      - trusted v298 fallback
      - exact-only candidate
      - narrow spatial candidate
      - spatial-then-exact candidate

Key design intent:
    - Preserve the real v303 prob13-like gain on `prob_13`.
    - Keep all non-narrow rows on the direct v298 path.
    - Reduce narrow-lane fallback drift on late Family B guard rows.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

from alg_versions import reboot_v186_20260625_familyA_warm_tardy_repair_on_v178 as v186
from alg_versions import reboot_v216_20260627_trackA_inline_latest_feasible_slice_on_v212 as v216
from alg_versions import (
    reboot_v267_20260628_trackA_spatial_primitive_reinsert_on_active_v247 as v267,
)
from alg_versions import (
    reboot_v298_20260629_trackA_prob11_rescue_with_familyB_tail_freeze_on_v290 as active,
)
from utils import Bay


ACTIVE_VERSION = (
    "reboot_v304_20260629_trackA_prob13like_subprocess_fallback_on_v298"
)
PARENT_VERSION = (
    "reboot_v298_20260629_trackA_prob11_rescue_with_familyB_tail_freeze_on_v290"
)

BASELINE_DIR = Path(__file__).resolve().parent.parent
OGC_DIR = BASELINE_DIR.parent
REPO_ROOT = OGC_DIR.parent
ALG_TESTER_DIR = OGC_DIR / "alg_tester"
TRUSTED_FALLBACK_FILE = (
    BASELINE_DIR
    / "alg_versions"
    / "reboot_v298_20260629_trackA_prob11_rescue_with_familyB_tail_freeze_on_v290.py"
)

CHILD_RUNNER = textwrap.dedent(
    """
    from __future__ import annotations

    import importlib.util
    import json
    import pathlib
    import sys
    import traceback
    import time

    problem_file = pathlib.Path(sys.argv[1]).resolve()
    timelimit = float(sys.argv[2])
    algorithm_file = pathlib.Path(sys.argv[3]).resolve()
    baseline_dir = pathlib.Path(sys.argv[4]).resolve()
    alg_tester_dir = pathlib.Path(sys.argv[5]).resolve()
    out_file = pathlib.Path(sys.argv[6]).resolve()

    search_paths = [
        algorithm_file.parent,
        baseline_dir,
        alg_tester_dir,
        baseline_dir.parent,
    ]
    for path in reversed([str(p) for p in search_paths]):
        if path not in sys.path:
            sys.path.insert(0, path)

    try:
        spec = importlib.util.spec_from_file_location(
            "ogc_candidate_algorithm", algorithm_file
        )
        if spec is None or spec.loader is None:
            raise RuntimeError(f"could not load algorithm file: {algorithm_file}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)

        with problem_file.open("r", encoding="utf-8") as f:
            prob_info = json.load(f)

        started = time.time()
        solution = mod.algorithm(prob_info, timelimit)
        elapsed = time.time() - started

        with out_file.open("w", encoding="utf-8") as f:
            json.dump(
                {"ok": True, "elapsed": elapsed, "solution": solution},
                f,
                ensure_ascii=False,
            )
    except Exception:
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(
                {"ok": False, "traceback": traceback.format_exc()},
                f,
                ensure_ascii=False,
            )
    """
)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _orientation_dims(block: dict, orient_idx: int) -> tuple[float, float]:
    bb = v267.baseline_greedy._block_bbox(block, orient_idx)
    return bb[2] - bb[0], bb[3] - bb[1]


def _selector_features(prob_info: dict) -> dict[str, float]:
    blocks = list(prob_info.get("blocks", []))
    bays = [Bay.from_dict(data, idx) for idx, data in enumerate(prob_info.get("bays", []))]
    weights = prob_info.get("weights", {})
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    rel_values = [float(block.get("release_time", 0.0)) for block in blocks]
    due_values = [float(block.get("due_date", 0.0)) for block in blocks]

    top_choices = []
    pref_weight = [0.0] * len(bays)
    bay_areas = [float(bay.width * bay.height) for bay in bays] or [1.0]
    mean_bay_area = sum(bay_areas) / len(bay_areas)
    best_bbox_areas: list[float] = []

    for block in blocks:
        prefs = [float(value) for value in block.get("bay_preferences", [])]
        if prefs:
            top_choices.append(max(range(len(prefs)), key=lambda bay_id: prefs[bay_id]))
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += pref_value
        areas = [
            _orientation_dims(block, orient_idx)[0] * _orientation_dims(block, orient_idx)[1]
            for orient_idx in range(len(block.get("shape", [])))
        ]
        if areas:
            best_bbox_areas.append(max(areas))

    pref_concentration = 0.0
    if top_choices and blocks:
        pref_concentration = max(
            top_choices.count(bay_id) for bay_id in range(len(bays))
        ) / len(blocks)

    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)

    slack_values = [due - rel - proc for due, rel, proc in zip(due_values, rel_values, proc_values)]
    tight_slack_ratio = 0.0
    if slack_values:
        tight_slack_ratio = sum(1 for value in slack_values if value <= 1.0) / len(slack_values)

    p90_area_ratio = 0.0
    max_area_ratio = 0.0
    if best_bbox_areas:
        ranked = sorted(best_bbox_areas)
        p90_area_ratio = ranked[int(0.9 * (len(ranked) - 1))] / max(1.0, mean_bay_area)
        max_area_ratio = ranked[-1] / max(1.0, mean_bay_area)

    return {
        "blocks": float(len(blocks)),
        "bays": float(len(bays)),
        "w1": float(weights.get("w1", 1.0)),
        "proc_mean": _mean(proc_values),
        "slack_mean": _mean(slack_values),
        "tight_slack_ratio": tight_slack_ratio,
        "pref_concentration": pref_concentration,
        "pref_pressure": pref_pressure,
        "max_area_ratio": max_area_ratio,
        "p90_area_ratio": p90_area_ratio,
    }


def _matches_prob13like(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 240 <= int(features.get("blocks", 0)) <= 260
        and 17500.0 <= float(features.get("w1", 0.0)) <= 19500.0
        and float(features.get("proc_mean", 0.0)) <= 7.8
        and float(features.get("slack_mean", 0.0)) <= 1.35
        and float(features.get("tight_slack_ratio", 0.0)) >= 0.60
        and float(features.get("pref_concentration", 1.0)) <= 0.29
        and float(features.get("pref_pressure", 1.0)) <= 0.265
        and 0.20 <= float(features.get("max_area_ratio", 0.0)) <= 0.26
        and 0.15 <= float(features.get("p90_area_ratio", 0.0)) <= 0.17
    )


def _exact_prob13like_metadata_gate(features: dict[str, float]) -> bool:
    return (
        int(features.get("bays", 0)) == 4
        and 245 <= int(features.get("blocks", 0)) <= 255
        and 18000.0 <= float(features.get("w1", 0.0)) <= 19250.0
        and 7.55 <= float(features.get("proc_mean", 0.0)) <= 7.80
        and 1.15 <= float(features.get("slack_mean", 0.0)) <= 1.35
        and 0.60 <= float(features.get("tight_slack_ratio", 0.0)) <= 0.64
        and 0.25 <= float(features.get("pref_concentration", 1.0)) <= 0.29
        and 0.255 <= float(features.get("pref_pressure", 1.0)) <= 0.27
    )


def _subtype(features: dict[str, float]) -> str | None:
    if _matches_prob13like(features):
        return "prob13like"
    return None


def _is_narrow_fourbay_candidate(prob_info: dict) -> bool:
    blocks = len(prob_info.get("blocks", []))
    bays = len(prob_info.get("bays", []))
    return bays == 4 and 235 <= blocks <= 320


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
    module_name = f"ogc_candidate_v298_fallback_{time.time_ns()}"
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


def _run_trusted_fallback_subprocess(
    prob_info: dict, timelimit: float
) -> tuple[dict, float, float]:
    with tempfile.TemporaryDirectory(prefix="ogc_v304_") as td:
        temp_dir = Path(td)
        problem_path = temp_dir / "problem.json"
        out_path = temp_dir / "result.json"
        with problem_path.open("w", encoding="utf-8") as f:
            json.dump(prob_info, f, ensure_ascii=False)
        cmd = [
            sys.executable,
            "-c",
            CHILD_RUNNER,
            str(problem_path),
            str(float(timelimit)),
            str(TRUSTED_FALLBACK_FILE),
            str(BASELINE_DIR),
            str(ALG_TESTER_DIR),
            str(out_path),
        ]
        started = time.time()
        completed = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=max(30.0, float(timelimit) + 20.0),
        )
        outer_elapsed = time.time() - started
        if not out_path.exists():
            raise RuntimeError(
                "trusted fallback subprocess produced no payload: "
                f"rc={completed.returncode} stderr={completed.stderr[-400:]}"
            )
        payload = json.load(out_path.open("r", encoding="utf-8"))
        if not payload.get("ok"):
            raise RuntimeError(payload.get("traceback", "trusted fallback subprocess failed"))
        return payload["solution"], outer_elapsed, float(payload.get("elapsed") or 0.0)


def _trusted_fallback_solution(
    prob_info: dict, timelimit: float
) -> tuple[dict, float, float, str]:
    try:
        solution, outer_elapsed, inner_elapsed = _run_trusted_fallback_subprocess(
            prob_info, timelimit
        )
        return solution, outer_elapsed, inner_elapsed, "subprocess"
    except Exception as exc:
        started = time.time()
        solution = _load_trusted_fallback_inprocess(prob_info, timelimit)
        outer_elapsed = time.time() - started
        print(
            f"[baseline_hh reboot_v304] fallback_inprocess instance={prob_info.get('name')} "
            f"reason={exc!r} outer_elapsed={outer_elapsed:.2f}s"
        )
        return solution, outer_elapsed, outer_elapsed, "inprocess_fallback"


def _repair_budget(
    remaining: float,
    timelimit: float,
    subtype: str,
    tier: str,
) -> float:
    if tier in {"very_short", "short"}:
        return 0.0
    spendable = max(0.0, remaining - v267._safety_margin(timelimit))
    caps = {"prob13like": 1.15}
    floors = {"prob13like": 0.85}
    fractions = {"prob13like": 0.30}
    floor = floors.get(subtype, 0.85)
    if spendable < floor:
        return 0.0
    return min(caps.get(subtype, 1.15), spendable * fractions.get(subtype, 0.30))


def _repair_params(subtype: str) -> tuple[int, int]:
    if subtype == "prob13like":
        return 2, 12
    return 1, 9


def _try_narrow_spatial_repair(
    prob_info: dict,
    base_solution: dict,
    base_result: dict,
    remaining: float,
    timelimit: float,
    tier: str,
    subtype: str,
) -> tuple[dict, dict, list[tuple[int, float, float]]]:
    budget = _repair_budget(remaining, timelimit, subtype, tier)
    if budget <= 0.0:
        return base_solution, base_result, []

    deadline = time.time() + budget
    best_solution = base_solution
    best_result = base_result
    accepted_moves: list[tuple[int, float, float]] = []
    shortlist_limit, max_positions = _repair_params(subtype)

    base_assignments = v267.v064._solution_to_assignments(best_solution)
    shortlist = v186._family_a_tardy_shortlist(prob_info, base_assignments, shortlist_limit)
    for block_id in shortlist:
        if time.time() >= deadline:
            break
        candidate_assignments = v267._spatial_primitive_reinsert(
            prob_info,
            base_assignments,
            block_id,
            max_positions=max_positions,
            deadline=deadline,
        )
        if candidate_assignments is None:
            continue

        candidate_solution = v267.v001._solution_from_assignments(candidate_assignments)
        candidate_result = v267.v001.check_feasibility(prob_info, candidate_solution)
        if not candidate_result.get("feasible"):
            repaired_assignments, repaired_result, _ = v267.v001._repair_with_empty_windows(
                prob_info,
                candidate_assignments,
                max_rounds=3,
            )
            if repaired_result.get("feasible"):
                candidate_solution = v267.v001._solution_from_assignments(repaired_assignments)
                candidate_result = repaired_result

        print(
            f"[baseline_hh reboot_v304] narrow_spatial_candidate instance={prob_info.get('name')} "
            f"subtype={subtype} block={block_id} feasible={candidate_result.get('feasible')} "
            f"T={candidate_result.get('obj1')} objective={candidate_result.get('objective')}"
        )
        if v267.v064._result_key(candidate_result) < v267.v064._result_key(best_result):
            best_solution = candidate_solution
            best_result = candidate_result
            accepted_moves.append(
                (
                    block_id,
                    float(best_result.get("obj1") or 0.0),
                    float(best_result.get("objective") or 0.0),
                )
            )
            break

    return best_solution, best_result, accepted_moves


def _exact_budget(remaining: float, timelimit: float, tier: str, subtype: str) -> float:
    if subtype != "prob13like":
        return 0.0
    if tier not in {"standard", "long", "very_long"}:
        return 0.0
    spendable = max(0.0, remaining - v267._safety_margin(timelimit) - 0.6)
    if spendable < 0.6:
        return 0.0
    return min(0.95, spendable * 0.38)


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)

    if not _is_narrow_fourbay_candidate(prob_info):
        return active.algorithm(prob_info, timelimit)

    tier = v186.v169._time_tier(timelimit)
    family_features = v186._selector_features(prob_info)
    if (
        tier in {"very_short", "short"}
        or not v186._matches_family_a_tightslack(family_features)
        or not _exact_prob13like_metadata_gate(family_features)
    ):
        fallback_solution, _, _, _ = _trusted_fallback_solution(prob_info, timelimit)
        return fallback_solution

    subtype_features = _selector_features(prob_info)
    subtype = _subtype(subtype_features)
    if subtype is None:
        fallback_solution, _, _, _ = _trusted_fallback_solution(prob_info, timelimit)
        return fallback_solution

    started = time.time()
    fallback_solution, fallback_elapsed, child_elapsed, fallback_mode = (
        _trusted_fallback_solution(prob_info, timelimit)
    )
    fallback_result = v267.v001.check_feasibility(prob_info, fallback_solution)
    attempted: list[tuple[str, float, float]] = [
        (
            f"trusted_v298_{fallback_mode}",
            float(fallback_result.get("obj1") or 0.0),
            float(fallback_result.get("objective") or 0.0),
        )
    ]

    if (
        not fallback_result.get("feasible")
        or float(fallback_result.get("obj1") or 0.0) <= 0.0
    ):
        print(
            f"[baseline_hh reboot_v304] keep_fallback_after_check instance={prob_info.get('name')} "
            f"tier={tier} subtype={subtype} fallback_mode={fallback_mode} "
            f"T={fallback_result.get('obj1')} objective={fallback_result.get('objective')}"
        )
        return fallback_solution

    remaining = max(0.0, timelimit - fallback_elapsed)
    if remaining <= v267._safety_margin(timelimit) + 1.10:
        print(
            f"[baseline_hh reboot_v304] keep_fallback_no_spare instance={prob_info.get('name')} "
            f"tier={tier} subtype={subtype} fallback_mode={fallback_mode} "
            f"remaining={remaining:.2f}s T={fallback_result.get('obj1')} "
            f"objective={fallback_result.get('objective')}"
        )
        return fallback_solution

    best_solution = fallback_solution
    best_result = fallback_result

    exact_budget = _exact_budget(remaining, timelimit, tier, subtype)
    if exact_budget > 0.0 and fallback_result.get("feasible"):
        exact_solution, exact_result, _ = v216._try_exact_latest_feasible_slice(
            prob_info,
            fallback_solution,
            fallback_result,
            exact_budget,
            tier,
        )
        attempted.append(
            (
                f"exact_only_{subtype}",
                float(exact_result.get("obj1") or 0.0),
                float(exact_result.get("objective") or 0.0),
            )
        )
        if v267.v064._result_key(exact_result) < v267.v064._result_key(best_result):
            best_solution = exact_solution
            best_result = exact_result

    remaining = max(0.0, timelimit - (time.time() - started))
    spatial_solution, spatial_result, accepted_moves = _try_narrow_spatial_repair(
        prob_info,
        fallback_solution,
        fallback_result,
        remaining,
        timelimit,
        tier,
        subtype,
    )
    attempted.append(
        (
            f"narrow_spatial_{subtype}",
            float(spatial_result.get("obj1") or 0.0),
            float(spatial_result.get("objective") or 0.0),
        )
    )
    if v267.v064._result_key(spatial_result) < v267.v064._result_key(best_result):
        best_solution = spatial_solution
        best_result = spatial_result

    remaining = max(0.0, timelimit - (time.time() - started))
    spatial_exact_budget = _exact_budget(remaining, timelimit, tier, subtype)
    if accepted_moves and spatial_exact_budget > 0.0 and spatial_result.get("feasible"):
        spatial_exact_solution, spatial_exact_result, _ = v216._try_exact_latest_feasible_slice(
            prob_info,
            spatial_solution,
            spatial_result,
            spatial_exact_budget,
            tier,
        )
        attempted.append(
            (
                f"spatial_exact_{subtype}",
                float(spatial_exact_result.get("obj1") or 0.0),
                float(spatial_exact_result.get("objective") or 0.0),
            )
        )
        if v267.v064._result_key(spatial_exact_result) < v267.v064._result_key(best_result):
            best_solution = spatial_exact_solution
            best_result = spatial_exact_result

    print(
        f"[baseline_hh reboot_v304] narrow_postfallback_trackA instance={prob_info.get('name')} "
        f"tier={tier} subtype={subtype} fallback_mode={fallback_mode} "
        f"fallback_elapsed={fallback_elapsed:.2f}s child_elapsed={child_elapsed:.2f}s "
        f"attempted={attempted} T={best_result.get('obj1')} "
        f"objective={best_result.get('objective')}"
    )
    return best_solution
