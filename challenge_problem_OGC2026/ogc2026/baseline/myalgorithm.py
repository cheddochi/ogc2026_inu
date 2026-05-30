# myalgorithm.py
# This is a template for the custom algorithm.

# ↓ ACTIVE 텍스트만 바꾸면 알고리즘을 선택할 수 있습니다. (dh는 도훈, hh는 현호, hd는 희도 알고리즘입니다.)
ACTIVE = "dh"  # "baseline", "dh", "hh", "hd" 중에서 선택 

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
    
    elif ACTIVE == "dh":
        import casat_cheddochi
        return casat_cheddochi.algorithm(prob_info, timelimit)

    # 현호와 희도의 알고리즘은 아직 구현되지 않았으므로, 주석 처리된 상태로 남겨두었습니다. 필요에 따라 활성화하여 사용할 수 있습니다.    
    # elif ACTIVE == "hh":
    #     import baseline_hh
    #     return baseline_hh.algorithm(prob_info, timelimit)

    # elif ACTIVE == "hd":
    #     import baseline_hd
    #     return baseline_hd.algorithm(prob_info, timelimit)
