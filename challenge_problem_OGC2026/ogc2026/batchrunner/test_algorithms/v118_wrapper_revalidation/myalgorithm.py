"""Wrapper-surface revalidation entrypoint for v118 candidate.

This mirrors the public submission chain:
    myalgorithm.py -> baseline_hh.py -> v118 algorithm

It exists only for benchmark/revalidation and must not be treated as the
official active submission surface.
"""

ACTIVE = "hh"


def algorithm(prob_info, timelimit=60):
    if ACTIVE == "hh":
        import baseline_hh

        return baseline_hh.algorithm(prob_info, timelimit)

    import baseline_hh

    return baseline_hh.algorithm(prob_info, timelimit)
