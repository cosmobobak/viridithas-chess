

def search_reduction_factor(lateness: int, is_check: bool, gives_check: bool, is_capt: bool, is_promo: bool, d: float) -> float:
    return 1
    DO_NOT_REDUCE = is_capt or is_promo or d < 3
    CHECK_EXTENSION = is_check or gives_check
    if DO_NOT_REDUCE:
        val = 0 if CHECK_EXTENSION else 1
    else:
        if lateness == 0:
            val = 1
        elif lateness <= 5: 
            # first six moves
            val = 2
        else:
            # moves after move six
            val = max(2, d / 3)
    return max(val, 0.5)
