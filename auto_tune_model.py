import pandas as pd
import numpy as np
import os

def auto_tune(log_path="output/pick_log.csv"):
    if not os.path.exists(log_path):
        print("No pick log found.")
        return
    df = pd.read_csv(log_path)
    if "final_result" not in df.columns:
        print("No results to tune on yet.")
        return
    # Example: adjust projection bias if accuracy < 0.55
    stat_types = ["PTS", "REB", "AST", "PRA"]
    for stat in stat_types:
        stat_df = df[df["stat_type"] == stat]
        total = len(stat_df)
        correct = (stat_df["final_result"] == "hit").sum() if "final_result" in stat_df else 0
        acc = correct / total if total > 0 else 0
        if acc < 0.55 and total > 20:
            print(f"Tuning needed for {stat}: accuracy={acc:.2f}")
            # Example: suggest increasing projection by 0.5 for this stat type
            print(f"Suggest: Increase {stat} projections by 0.5 for next run.")
        else:
            print(f"{stat} OK: accuracy={acc:.2f}")

if __name__ == "__main__":
    auto_tune()
