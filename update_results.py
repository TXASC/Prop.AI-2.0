import requests
import pandas as pd
import os
from datetime import datetime

BALLDONTLIE_BASE_URL = "https://www.balldontlie.io/api/v1/"

def get_game_stats(game_id):
    resp = requests.get(f"{BALLDONTLIE_BASE_URL}stats", params={"game_ids[]": game_id, "per_page": 100})
    resp.raise_for_status()
    return resp.json()["data"]

def update_results(log_path="output/pick_log.csv"):
    if not os.path.exists(log_path):
        print("No pick log found.")
        return
    df = pd.read_csv(log_path)
    # Only update picks without a final_result
    mask = df["final_result"].isnull() if "final_result" in df.columns else [True]*len(df)
    df["final_result"] = df.get("final_result", pd.Series([None]*len(df)))
    for idx, row in df[mask].iterrows():
        # Try to get yesterday's or earlier games
        try:
            player = row["player_id"]
            stat_type = row["stat_type"]
            game_date = row["date"]
            # Find the game for the player on that date
            player_id = None
            # Use balldontlie to get player id
            player_search = requests.get(f"{BALLDONTLIE_BASE_URL}players", params={"search": player})
            player_search.raise_for_status()
            pdata = player_search.json()["data"]
            if not pdata:
                continue
            player_id = pdata[0]["id"]
            # Get all games for player on that date
            stats = requests.get(f"{BALLDONTLIE_BASE_URL}stats", params={"player_ids[]": player_id, "dates[]": game_date, "per_page": 1}).json()["data"]
            if not stats:
                continue
            stat_row = stats[0]
            # Determine hit/miss
            stat_map = {"PTS": "pts", "REB": "reb", "AST": "ast", "PRA": None}
            if stat_type == "PRA":
                actual = stat_row["pts"] + stat_row["reb"] + stat_row["ast"]
            else:
                actual = stat_row[stat_map[stat_type]]
            prop_line = float(row["prop_line"])
            side = row["recommended_side"]
            if (side == "Over" and actual > prop_line) or (side == "Under" and actual < prop_line):
                df.at[idx, "final_result"] = "hit"
            else:
                df.at[idx, "final_result"] = "miss"
            df.at[idx, "actual"] = actual
        except Exception as e:
            print(f"Error updating result for {row['player_id']} {row['stat_type']} {row['date']}: {e}")
    df.to_csv(log_path, index=False)
    print("Results updated.")

if __name__ == "__main__":
    update_results()
