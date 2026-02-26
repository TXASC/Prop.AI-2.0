import math

def normal_prob(mean, stdev, line, side):
    # Compute probability for over/under/push
    if side == "over":
        return 1 - normal_cdf(line, mean, stdev)
    elif side == "under":
        return normal_cdf(line, mean, stdev)
    else:
        return 0.0

def normal_cdf(x, mean, stdev):
    return 0.5 * (1 + math.erf((x - mean) / (stdev * math.sqrt(2))))
