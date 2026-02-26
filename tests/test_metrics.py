from app.core.metrics.metrics_aggregator import aggregate_metrics


def test_aggregate_metrics():
    grades = [
        {"profit": 10, "won": True, "clv": 1.5, "abs_error": 2.0},
        {"profit": -10, "won": False, "clv": -0.5, "abs_error": 1.0},
    ]
    metrics = aggregate_metrics(grades)
    assert metrics["correct_pct"] == 0.5
    assert metrics["clv_mean"] == 0.5
    assert metrics["counts"] == 2
