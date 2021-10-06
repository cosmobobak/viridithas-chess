

def search_reduction_factor(lateness: int, is_check: bool, gives_check: bool, is_capt: bool, is_promo: bool, d: float) -> float:
    # return 1.0
    DO_NOT_REDUCE = is_capt or is_promo or d < 3
    CHECK_EXTENSION = is_check or gives_check and d > 3
    if DO_NOT_REDUCE:
        return 0.4 if CHECK_EXTENSION else 1
    else:
        return 1.0
        if lateness <= 5:
            return 1
        if lateness <= 10:
            # moves after move six
            return 1.4
        # moves after move 11
        return 1.7
