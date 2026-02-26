import math

def american_to_implied_prob(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return -odds / (-odds + 100)

def remove_vig(p_over, p_under):
    total = p_over + p_under
    return p_over / total, p_under / total
