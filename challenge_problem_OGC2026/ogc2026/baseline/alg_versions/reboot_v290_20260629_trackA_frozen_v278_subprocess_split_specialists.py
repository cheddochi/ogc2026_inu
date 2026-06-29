"""reboot_v290_20260629_trackA_frozen_v278_subprocess_split_specialists.py

Strategy:
    Preserve the useful prob13like and prob19like Track A specialists from
    v288, but point the isolated subprocess fallback at the frozen accepted
    direct v278 algorithm file instead of baseline_hh.py so the publish surface
    cannot recurse through itself. Non-target rows return the isolated trusted
    active result without importing specialist modules.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path


BASELINE_DIR = Path(__file__).resolve().parent.parent
OGC_DIR = BASELINE_DIR.parent
REPO_ROOT = OGC_DIR.parent
ALG_TESTER_DIR = OGC_DIR / "alg_tester"
ACTIVE_SURFACE_FILE = (
    BASELINE_DIR
    / "alg_versions"
    / "reboot_v278_20260628_trackA_coarse_gate_lazy_prob20_plus_lowproc_replay_on_active_v267.py"
)


ACTIVE_VERSION = (
    "reboot_v290_20260629_trackA_frozen_v278_subprocess_split_specialists"
)
PARENT_VERSION = (
    "reboot_v278_20260628_trackA_coarse_gate_lazy_prob20_plus_lowproc_replay_on_active_v267"
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


def _mods():
    v186 = importlib.import_module(
        "alg_versions.reboot_v186_20260625_familyA_warm_tardy_repair_on_v178"
    )
    v283 = importlib.import_module(
        "alg_versions.reboot_v283_20260629_trackA_prob14like_narrow_postfallback_on_active_v278"
    )
    return v186, v283


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _coarse_family_a_precheck(prob_info: dict) -> bool:
    blocks = list(prob_info.get("blocks", []))
    bays = list(prob_info.get("bays", []))
    weights = prob_info.get("weights", {})
    proc_values = [float(block.get("processing_time", 0.0)) for block in blocks]
    rel_values = [float(block.get("release_time", 0.0)) for block in blocks]
    due_values = [float(block.get("due_date", 0.0)) for block in blocks]
    top_choices = []
    pref_weight = [0.0] * len(bays)
    for block in blocks:
        prefs = [float(value) for value in block.get("bay_preferences", [])]
        if prefs:
            top_choices.append(
                max(range(len(prefs)), key=lambda bay_id: prefs[bay_id])
            )
        for bay_id, pref_value in enumerate(prefs):
            if bay_id < len(pref_weight):
                pref_weight[bay_id] += pref_value
    pref_concentration = 0.0
    if top_choices and blocks:
        pref_concentration = (
            max(top_choices.count(bay_id) for bay_id in range(len(bays)))
            / len(blocks)
        )
    pref_pressure = 0.0
    if pref_weight and sum(pref_weight) > 0:
        pref_pressure = max(pref_weight) / sum(pref_weight)
    slack_values = [
        due - rel - proc
        for due, rel, proc in zip(due_values, rel_values, proc_values)
    ]
    tight_slack_ratio = 0.0
    if slack_values:
        tight_slack_ratio = (
            sum(1 for value in slack_values if value <= 1.0) / len(slack_values)
        )
    return (
        len(bays) == 4
        and len(blocks) >= 235
        and float(weights.get("w1", 0.0)) >= 9000.0
        and _mean(proc_values) <= 8.0
        and _mean(slack_values) <= 1.7
        and tight_slack_ratio >= 0.50
        and pref_concentration <= 0.35
        and pref_pressure <= 0.30
    )


def _is_narrow_fourbay_candidate(prob_info: dict) -> bool:
    blocks = len(prob_info.get("blocks", []))
    bays = len(prob_info.get("bays", []))
    return bays == 4 and 235 <= blocks <= 320


def _load_active_surface_inprocess(prob_info: dict, timelimit: float) -> dict:
    search_paths = [
        ACTIVE_SURFACE_FILE.parent,
        BASELINE_DIR,
        ALG_TESTER_DIR,
        BASELINE_DIR.parent,
    ]
    for path in reversed([str(p) for p in search_paths]):
        if path not in sys.path:
            sys.path.insert(0, path)
    module_name = f"ogc_candidate_algorithm_fallback_{time.time_ns()}"
    spec = importlib.util.spec_from_file_location(module_name, ACTIVE_SURFACE_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load active surface: {ACTIVE_SURFACE_FILE}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    try:
        spec.loader.exec_module(mod)
        return mod.algorithm(prob_info, timelimit)
    finally:
        sys.modules.pop(module_name, None)


def _run_trusted_active_subprocess(
    prob_info: dict, timelimit: float
) -> tuple[dict, float, float]:
    with tempfile.TemporaryDirectory(prefix="ogc_v288_") as td:
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
            str(ACTIVE_SURFACE_FILE),
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
                "active subprocess produced no payload: "
                f"rc={completed.returncode} stderr={completed.stderr[-400:]}"
            )
        payload = json.load(out_path.open("r", encoding="utf-8"))
        if not payload.get("ok"):
            raise RuntimeError(payload.get("traceback", "active subprocess failed"))
        return payload["solution"], outer_elapsed, float(payload.get("elapsed") or 0.0)


def _trusted_active_solution(prob_info: dict, timelimit: float) -> tuple[dict, float, float, str]:
    try:
        solution, outer_elapsed, inner_elapsed = _run_trusted_active_subprocess(
            prob_info, timelimit
        )
        return solution, outer_elapsed, inner_elapsed, "subprocess"
    except Exception as exc:
        started = time.time()
        solution = _load_active_surface_inprocess(prob_info, timelimit)
        outer_elapsed = time.time() - started
        print(
            f"[baseline_hh reboot_v290] fallback_inprocess instance={prob_info.get('name')} "
            f"reason={exc!r} outer_elapsed={outer_elapsed:.2f}s"
        )
        return solution, outer_elapsed, outer_elapsed, "inprocess_fallback"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    timelimit = float(timelimit)

    fallback_solution, fallback_elapsed, child_elapsed, fallback_mode = (
        _trusted_active_solution(prob_info, timelimit)
    )

    if not _is_narrow_fourbay_candidate(prob_info):
        return fallback_solution

    if not _coarse_family_a_precheck(prob_info):
        return fallback_solution

    v186, v283 = _mods()
    tier = v186.v169._time_tier(timelimit)
    family_features = v186._selector_features(prob_info)
    subtype_features = v283._selector_features(prob_info)
    subtype = v283._subtype(subtype_features)
    if (
        subtype not in {"prob13like", "prob19like"}
        or tier in {"very_short", "short"}
        or not v186._matches_family_a_tightslack(family_features)
    ):
        return fallback_solution

    fallback_result = v283.v267.v001.check_feasibility(prob_info, fallback_solution)
    attempted: list[tuple[str, float, float]] = [
        (
            f"trusted_active_{fallback_mode}",
            float(fallback_result.get("obj1") or 0.0),
            float(fallback_result.get("objective") or 0.0),
        )
    ]
    best_label = f"trusted_active_{fallback_mode}"
    best_solution = fallback_solution
    best_result = fallback_result

    if not fallback_result.get("feasible") or float(fallback_result.get("obj1") or 0.0) <= 0.0:
        return fallback_solution

    remaining = max(0.0, timelimit - fallback_elapsed)
    if remaining <= v283.v267._safety_margin(timelimit) + 0.85:
        print(
            f"[baseline_hh reboot_v290] keep_fallback instance={prob_info.get('name')} "
            f"tier={tier} subtype={subtype} mode={fallback_mode} "
            f"outer_elapsed={fallback_elapsed:.2f}s child_elapsed={child_elapsed:.2f}s "
            f"remaining={remaining:.2f}s T={best_result.get('obj1')} "
            f"objective={best_result.get('objective')}"
        )
        return fallback_solution

    if subtype == "prob13like":
        cand_solution, cand_result, _ = v283._try_narrow_spatial_repair(
            prob_info,
            fallback_solution,
            fallback_result,
            remaining=remaining,
            timelimit=timelimit,
            tier=tier,
            subtype=subtype,
        )
        attempted.append(
            (
                "prob13_spatial",
                float(cand_result.get("obj1") or 0.0),
                float(cand_result.get("objective") or 0.0),
            )
        )
        if cand_result.get("feasible") and v283.v267.v064._result_key(cand_result) < v283.v267.v064._result_key(best_result):
            best_label = "prob13_spatial"
            best_solution = cand_solution
            best_result = cand_result

    elif subtype == "prob19like":
        warm_solution, warm_result, _ = v186._try_family_a_warm_repair(
            prob_info,
            fallback_solution,
            fallback_result,
            remaining=min(1.1, remaining),
            tier=tier,
            features=family_features,
        )
        attempted.append(
            (
                "prob19_warm",
                float(warm_result.get("obj1") or 0.0),
                float(warm_result.get("objective") or 0.0),
            )
        )
        if warm_result.get("feasible") and v283.v267.v064._result_key(warm_result) < v283.v267.v064._result_key(best_result):
            best_label = "prob19_warm"
            best_solution = warm_solution
            best_result = warm_result

    print(
        f"[baseline_hh reboot_v290] frozen_v278_subprocess_split_specialists "
        f"instance={prob_info.get('name')} tier={tier} subtype={subtype} "
        f"mode={fallback_mode} outer_elapsed={fallback_elapsed:.2f}s "
        f"child_elapsed={child_elapsed:.2f}s best={best_label} attempted={attempted} "
        f"T={best_result.get('obj1')} objective={best_result.get('objective')}"
    )
    return best_solution
