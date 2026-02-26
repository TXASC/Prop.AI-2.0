from app.core.pricing.odds_math import american_to_implied_prob, remove_vig

def test_american_to_implied_prob():
    assert round(american_to_implied_prob(-110), 4) == 0.5238
    assert round(american_to_implied_prob(150), 4) == 0.4

def test_remove_vig():
    p_over, p_under = remove_vig(0.55, 0.45)
    assert round(p_over + p_under, 4) == 1.0
    assert round(p_over, 4) == 0.55 / (0.55 + 0.45)
