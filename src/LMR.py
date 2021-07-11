
def search_reduction_factor(lateness: int, is_check: bool, gives_check: bool, is_capt: bool, is_promo: bool, d: float) -> float:
    reduction = 1
    if is_check or gives_check:
        reduction += -1
    elif is_capt or is_promo:
        reduction += -0.5
    elif d < 3:
        pass
    else:
        if lateness <= 5: # first six moves
            reduction += 1
        else:
            reduction += max(d / 3, 1)
    return max(reduction, 0.4)
