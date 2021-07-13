
def search_reduction_factor(lateness: int, is_check: bool, gives_check: bool, is_capt: bool, is_promo: bool, d: float) -> float:
    # return 1
    reduction = 1
    if is_check or gives_check:
        reduction += -1 # 0 reduction
    elif is_capt or is_promo:
        reduction += -0.5 # 0.5 reduction
    elif d < 3:
        pass
    else:
        if lateness == 0:
            reduction -= 0.5 # 0.5 reduction
        elif lateness <= 5: 
            # first six moves
            reduction += 0 # 1 reduction
        else:
            # moves after move six
            reduction += max(d / 3, 1) # either d / 3 + 1 or 2 reduction
    return max(reduction * 2, 0.5)
