"""Local wrapper-surface validator for v118 candidate.

This file intentionally mimics the thin active wrapper shape without touching
the real submission entrypoint in ogc2026/baseline/baseline_hh.py.
"""

from alg_versions import reboot_v118_20260620_0835_prob31like_gap_hard_margin_on_v116 as active


ACTIVE_VERSION = "reboot_v118_20260620_0835_prob31like_gap_hard_margin_on_v116"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    return active.algorithm(prob_info, timelimit)
