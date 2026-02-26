
def aggregate_metrics(grades):
    correct_pct = sum(1 for g in grades if g["won"]) / len(grades) if grades else 0
    clv_mean = sum(g["clv"] for g in grades) / len(grades) if grades else 0
    clv_pct_positive = sum(1 for g in grades if g["clv"] > 0) / len(grades) if grades else 0
    mae = sum(g["abs_error"] for g in grades) / len(grades) if grades else 0
    rmse = (sum(g["abs_error"] ** 2 for g in grades) / len(grades)) ** 0.5 if grades else 0
    return {
        "correct_pct": correct_pct,
        "clv_mean": clv_mean,
        "clv_pct_positive": clv_pct_positive,
        "mae": mae,
        "rmse": rmse,
        "counts": len(grades)
    }
