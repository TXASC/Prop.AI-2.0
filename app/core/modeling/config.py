# Stat-specific stdev priors and model version

STAT_STDEV_PRIORS = {
    "PTS": 5.5,
    "REB": 2.2,
    "AST": 1.8,
    "PRA": 6.8,
}

MODEL_VERSION = "nba_v0_market_normal_001"

BOOK_WEIGHTS = {
    "Pinnacle": 1.0,
    "Circa": 0.9,
    "FanDuel": 0.85,
    "DraftKings": 0.8,
    "BetMGM": 0.5,
    "Caesars": 0.5,
    "PointsBet": 0.5,
    "Retail": 0.2,
}

RATE_LIMITS = {
    "theodds": 30,  # requests per minute
}
