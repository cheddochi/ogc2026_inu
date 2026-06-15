"""baseline_hh_v000_original.py

Strategy:
    Reference baseline for HH experiments.

Context:
    This repository did not contain an existing baseline_hh.py file when the
    versioning work started.  This v000 file therefore preserves the official
    greedy baseline behavior as the conservative reference point.

Expected strengths:
    Robust feasibility through the official greedy repair and serial fallback.

Expected weaknesses:
    Single-strategy search, limited instance awareness, and no portfolio
    selection across team algorithms.
"""

from __future__ import annotations

import baseline_greedy


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Run the official greedy baseline with its built-in repair."""
    return baseline_greedy.greedyalgorithm(prob_info, timelimit)

