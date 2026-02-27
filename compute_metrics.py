import pandas as pd
from datetime import datetime, timedelta
import os

def compute_metrics(log_path="output/pick_log.csv", report_path="output/metrics_report.csv"):
    if not os.path.exists(log_path):
        print("No pick log found.")
        return
    df = pd.read_csv(log_path)
    # Only analyze picks with final_result (hit/miss) and closing_line/clv if available
    if "final_result" not in df.columns:
        print("No results to analyze yet.")
        return
    today = datetime.now().date()
    two_weeks_ago = today - timedelta(days=14)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    recent = df[df["date"] >= two_weeks_ago]
    stat_types = ["PTS", "REB", "AST", "PRA"]
    rows = []
    for stat in stat_types:
        stat_df = recent[recent["stat_type"] == stat]
        total = len(stat_df)
        correct = (stat_df["final_result"] == "hit").sum() if "final_result" in stat_df else 0
        acc = correct / total if total > 0 else 0
        avg_edge = stat_df["edge_pct"].astype(float).mean() if total > 0 else 0
        avg_clv = stat_df["clv"].astype(float).mean() if "clv" in stat_df and total > 0 else 0
        rows.append({
            "date": today,
            "stat_type": stat,
            "total_picks": total,
            "correct_picks": correct,
            "accuracy": round(acc, 3),
            "avg_edge": round(avg_edge, 2),
            "avg_clv": round(avg_clv, 2)
        })
    report_df = pd.DataFrame(rows)
    write_header = not os.path.exists(report_path) or os.path.getsize(report_path) == 0
    report_df.to_csv(report_path, mode="a", header=write_header, index=False)
    print("Metrics report updated.")

if __name__ == "__main__":
    compute_metrics()
