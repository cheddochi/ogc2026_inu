"""reboot_v036_20260617_1016_large_class_tardy_reinsert.py

Strategy:
    Keep trusted v035 behavior and add a bounded tardy-block reinsertion pass
    only for the large multi-bay residual class.

Metadata:
    version_id: reboot_v036_20260617_1016_large_class_tardy_reinsert
    parent_version: reboot_v035_20260617_0912_prob14_preference_spread
    status: rejected
    timestamp: 2026-06-17 10:16 KST
    strategy:
        - class rule: blocks>=200 and bays>=3
        - warm start from trusted v035
        - remove top-1 tardy block, reinsert through shared empty-window search
        - accept the post-processed solution only if official-checker T and
          objective both improve or objective improves with non-worse T
    hypothesis: the largest residual class still has isolated top-tardy blocks
        that the trusted warm start leaves in poor empty windows; one cheap
        reinsertion move may improve them without paying for a second full build.
    intended_metric_target:
        - class-level T/objective improvement on at least one of prob_37/39/40
    validation_status: import smoke passed; target class smoke on prob_37 held
        flat; runtime-risk smoke on prob_38 regressed badly, so the candidate
        was rejected before smoke-8/full.
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/smoke_reboot_v036_prob37_20260617_001/
        reports/ogc2026_reboot_v001/smoke_reboot_v036_prob38_20260617_001/
    rollback_target: reboot_v035_20260617_0912_prob14_preference_spread
"""

from __future__ import annotations

import time

from alg_versions import reboot_v001_20260616_1547_trusted_active_copy as v001
from alg_versions import reboot_v035_20260617_0912_prob14_preference_spread as v035


ACTIVE_VERSION = "reboot_v036_20260617_1016_large_class_tardy_reinsert"


def _assignments_from_solution(solution: dict) -> dict[int, dict]:
    assignments: dict[int, dict] = {}
    for time_str, ops in solution.get("operations", {}).items():
        at = int(time_str)
        for op in ops:
            block_id = int(op["block_id"])
            record = assignments.setdefault(block_id, {"block_id": block_id})
            if op["type"] == "ENTRY":
                record.update(
                    {
                        "bay_id": int(op["bay_id"]),
                        "x": int(op["x"]),
                        "y": int(op["y"]),
                        "orient_idx": int(op["orient_idx"]),
                        "entry_time": at,
                    }
                )
            else:
                record["exit_time"] = at
    return assignments


def _is_large_multi_bay_residual(prob_info: dict) -> bool:
    return len(prob_info.get("blocks", [])) >= 200 and len(prob_info.get("bays", [])) >= 3


def _top_tardy_block_ids(prob_info: dict, assignments: dict[int, dict], top_k: int = 1) -> list[int]:
    blocks = prob_info["blocks"]
    tardy_rows: list[tuple[int, int, int, int]] = []
    for block_id, assignment in assignments.items():
        due = int(blocks[block_id]["due_date"])
        proc = int(blocks[block_id]["processing_time"])
        tardiness = max(0, int(assignment["exit_time"]) - due)
        if tardiness > 0:
            tardy_rows.append((tardiness, due, -proc, block_id))
    tardy_rows.sort(reverse=True)
    return [block_id for _, _, _, block_id in tardy_rows[:top_k]]


def _bounded_tardy_reinsert(prob_info: dict, base_solution: dict, top_k: int = 1) -> dict:
    blocks = prob_info["blocks"]
    repaired = _assignments_from_solution(base_solution)
    target_ids = _top_tardy_block_ids(prob_info, repaired, top_k=top_k)
    if not target_ids:
        return base_solution

    for block_id in target_ids:
        repaired.pop(block_id, None)

    for block_id in sorted(
        target_ids,
        key=lambda idx: (blocks[idx]["due_date"], blocks[idx]["processing_time"]),
    ):
        bays, bay_schedule, bay_last_entry = v001._rebuild_empty_repair_state(prob_info, repaired)
        bay_id, x, y, orient_idx, entry, exit_at = v001._empty_window_candidate(
            block_id,
            blocks,
            bays,
            bay_schedule,
            bay_last_entry,
            respect_entry_frontier=False,
        )
        repaired[block_id] = {
            "block_id": block_id,
            "bay_id": int(bay_id),
            "x": int(round(x)),
            "y": int(round(y)),
            "orient_idx": int(orient_idx),
            "entry_time": int(round(entry)),
            "exit_time": int(round(exit_at)),
        }

    return v001._solution_from_assignments(repaired)


def _is_better(base_result: dict, trial_result: dict) -> bool:
    if not trial_result.get("feasible"):
        return False
    base_t = float(base_result["obj1"])
    trial_t = float(trial_result["obj1"])
    base_obj = float(base_result["objective"])
    trial_obj = float(trial_result["objective"])
    return (trial_t < base_t and trial_obj <= base_obj) or (
        trial_obj < base_obj and trial_t <= base_t
    )


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    base_solution = v035.algorithm(prob_info, timelimit)
    if not _is_large_multi_bay_residual(prob_info):
        return base_solution

    elapsed = time.time() - started
    if elapsed >= max(1.0, float(timelimit) - 4.0):
        return base_solution

    base_result = v001.check_feasibility(prob_info, base_solution)
    trial_solution = _bounded_tardy_reinsert(prob_info, base_solution, top_k=1)
    trial_result = v001.check_feasibility(prob_info, trial_solution)
    print(
        f"[baseline_hh reboot_v036] target={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} trial_T={trial_result.get('obj1')} "
        f"base_obj={base_result.get('objective')} trial_obj={trial_result.get('objective')} "
        f"elapsed={time.time() - started:.2f}s"
    )
    if _is_better(base_result, trial_result):
        return trial_solution
    return base_solution
