# myalgorithm.py
# This is a template for the custom algorithm.

# ↓ ACTIVE 텍스트만 바꾸면 알고리즘을 선택할 수 있습니다. (hh는 현호, dohun는 도훈, heedo는 희도 알고리즘입니다.)
ACTIVE = "baseline"  

def algorithm(prob_info, timelimit=60):
    """
    This is a template for the custom algorithm.
    The function signature must not be changed or removed, but you can define extra functions or modules that are used in this function.
    The `prob_info` is a dictionary containing the problem information, and `timelimit` is the time limit for the algorithm in seconds.
    The function should return a solution in the format specified in the problem statement.
    Please refer to baseline_greedy.py for an example implementation of a simple greedy algorithm. You can use it as a starting point or reference for your own algorithm.
    """

    # You can import other modules or define extra functions here.
    if ACTIVE == "baseline":
        import baseline_greedy
        return baseline_greedy.greedyalgorithm(prob_info, timelimit)
    
    # elif ACTIVE == "hh":
    #     import baseline_hh
    #     return baseline_hh.hhalgorithm(prob_info, timelimit)
    # elif ACTIVE == "dohun":
    #     import baseline_dohun
    #     return baseline_dohun.dohunalgorithm(prob_info, timelimit)
    #     return baseline_hh.hhalgorithm(prob_info, timelimit)
    # elif ACTIVE == "heedo":
    #     import baseline_heedo
    #     return baseline_heedo.heedoalgorithm(prob_info, timelimit)
