import pandas as pd
from datetime import datetime, timedelta
import os

def morning_report(log_path="output/pick_log.csv", report_path="output/morning_report.csv"):
    if not os.path.exists(log_path):
        print("No pick log found.")
        return
    df = pd.read_csv(log_path)
    if "final_result" not in df.columns:
        print("No results to report yet.")
        return
    yesterday = (datetime.now() - timedelta(days=1)).date()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    day_df = df[df["date"] == yesterday].head(50)
    rows = []
    for stat in ["PTS", "REB", "AST", "PRA"]:
        stat_df = day_df[day_df["stat_type"] == stat]
        total = len(stat_df)
        correct = (stat_df["final_result"] == "hit").sum() if "final_result" in stat_df else 0
        acc = correct / total if total > 0 else 0
        avg_edge = stat_df["edge_pct"].astype(float).mean() if total > 0 else 0
        avg_clv = stat_df["clv"].astype(float).mean() if "clv" in stat_df and total > 0 else 0
        rows.append({
            "date": yesterday,
            "stat_type": stat,
            "top50_total": total,
            "top50_correct": correct,
            "top50_accuracy": round(acc, 3),
            "top50_avg_edge": round(avg_edge, 2),
            "top50_avg_clv": round(avg_clv, 2)
        })
    report_df = pd.DataFrame(rows)
    write_header = not os.path.exists(report_path) or os.path.getsize(report_path) == 0
    report_df.to_csv(report_path, mode="a", header=write_header, index=False)
    print("Morning report generated for", yesterday)

if __name__ == "__main__":
    morning_report()