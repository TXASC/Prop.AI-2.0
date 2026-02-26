from datetime import datetime

class PickLogger:
    def __init__(self, repo):
        self.repo = repo

    def log_pick(self, pick):
        # pick: dict with all required fields
        pick["picked_at"] = datetime.utcnow()
        self.repo.store_pick(pick)

class Grader:
    def __init__(self, repo):
        self.repo = repo

    def grade_picks(self, date):
        # TODO: Fetch picks and results, compute grades
        picks = self.repo.get_picks(date)
        results = self.repo.get_results(date)
        grades = []
        for pick in picks:
            result = next((r for r in results if r["market_id"] == pick["market_id"]), None)
            if result:
                won = self._compute_win(pick, result)
                profit = self._compute_profit(pick, won)
                clv = self._compute_clv(pick, result)
                abs_error = abs(result["actual_value"] - pick["projected_mean"])
                grades.append({
                    "pick_id": pick["id"],
                    "won": won,
                    "profit": profit,
                    "clv": clv,
                    "abs_error": abs_error,
                    "graded_at": datetime.utcnow()
                })
        self.repo.store_grades(grades)

    def _compute_win(self, pick, result):
        # TODO: Implement push rules
        if pick["side"] == "over":
            return result["actual_value"] > pick["line_at_pick"]
        else:
            return result["actual_value"] < pick["line_at_pick"]

    def _compute_profit(self, pick, won):
        # American odds payout
        stake = pick["stake"]
        price = pick["price_at_pick"]
        if won:
            return stake * (abs(price) / 100) if price > 0 else stake
        else:
            return -stake

    def _compute_clv(self, pick, result):
        # CLV = closing_line - line_at_pick (sign adjusted)
        clv = result["actual_value"] - pick["line_at_pick"]
        if pick["side"] == "under":
            clv = -clv
        return clv
