from app.core.pricing.odds_math import american_to_implied_prob, remove_vig
from app.core.modeling.distribution import normal_prob
from app.core.modeling.config import MODEL_VERSION
from datetime import datetime


def calculate_edge(line, price, stat_type, side, timestamp):
    p_implied = american_to_implied_prob(price)
    p_over, p_under = remove_vig(p_implied, 1 - p_implied)
    # Simple normal model
    mean = line  # Placeholder, will use consensus_mean
    stdev = 5.0  # Placeholder, will use stat-specific
    p_model = normal_prob(mean, stdev, line, side)
    fair_odds = 1 / p_model if p_model > 0 else 0
    edge = (p_model - p_implied) * 100
    freshness_score = freshness(timestamp)
    return {
        "model_version": MODEL_VERSION,
        "p_model": p_model,
        "fair_odds": fair_odds,
        "edge": edge,
        "freshness_score": freshness_score,
    }


def freshness(ts):
    # Exponential decay freshness score
    age_sec = (datetime.utcnow() - ts).total_seconds()
    decay = 0.0001
    return max(0.0, min(1.0, math.exp(-decay * age_sec)))
