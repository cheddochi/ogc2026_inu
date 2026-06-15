# myalgorithm.py
# Public submission entrypoint.  Keep algorithm(prob_info, timelimit) unchanged.

ACTIVE = "hh"  # one of: "baseline", "dh", "hh", "hd"


def algorithm(prob_info, timelimit=60):
    """Dispatch to the selected algorithm while preserving the official API."""
    if ACTIVE == "baseline":
        import baseline_greedy

        return baseline_greedy.greedyalgorithm(prob_info, timelimit)

    if ACTIVE == "dh":
        import casat_cheddochi

        return casat_cheddochi.algorithm(prob_info, timelimit)

    if ACTIVE == "hh":
        import baseline_hh

        return baseline_hh.algorithm(prob_info, timelimit)

    if ACTIVE == "hd":
        import baseline_hd

        return baseline_hd.algorithm(prob_info, timelimit)

    import baseline_greedy

    return baseline_greedy.greedyalgorithm(prob_info, timelimit)
