from app.core.modeling.config import STAT_STDEV_PRIORS, MODEL_VERSION
import math
try:
    from scipy.special import erfinv
except ImportError:
    erfinv = getattr(math, 'erfinv', None)
    if erfinv is None:
        raise ImportError('No erfinv available. Please install scipy or use Python 3.8+')

def consensus_mean(line, p_over, stat_type):
    # Solve for mean µ under normal so P(X > L) ≈ p_over
    stdev = STAT_STDEV_PRIORS.get(stat_type, 5.0)
    # Inverse normal CDF for over probability
    z = norm_inv(1 - p_over)
    mean = line + z * stdev
    return mean

def norm_inv(p):
    # Approximate inverse CDF for normal
    return math.sqrt(2) * erfinv(2 * p - 1)
