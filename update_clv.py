import requests
import pandas as pd
import os
from datetime import datetime

THEODDS_API_URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds-history/"
API_KEY = os.getenv("THEODDS_API_KEY")

# This function assumes you have the event/game id and stat type for each pick
# and that TheODDS API provides closing lines for each market

def get_closing_line(event_id, stat_type):
    # Example endpoint, may need to adjust for your provider
    params = {"apiKey": API_KEY, "regions": "us", "markets": stat_type.lower()}
    resp = requests.get(f"{THEODDS_API_URL}{event_id}", params=params)
    if resp.status_code != 200:
        return None
    data = resp.json()
    # Find the closing line for the stat_type
    for market in data.get("markets", []):
        if market.get("key", "").upper() == stat_type.upper():
            # Assume last price/line is closing
            outcomes = market.get("outcomes", [])
            if outcomes:
                # Find the last line value
                return outcomes[-1].get("point")
    return None

def update_clv(log_path="output/pick_log.csv"):
    if not os.path.exists(log_path):
        print("No pick log found.")
        return
    df = pd.read_csv(log_path)
    if "event_id" not in df.columns:
        print("No event_id column in pick log. Cannot update CLV.")
        return
    df["clv"] = df.get("clv", pd.Series([None]*len(df)))
    for idx, row in df.iterrows():
        if pd.notnull(row.get("clv")):
            continue  # Already updated
        event_id = row["event_id"]
        stat_type = row["stat_type"]
        closing_line = get_closing_line(event_id, stat_type)
        if closing_line is not None:
            try:
                prop_line = float(row["prop_line"])
                side = row["recommended_side"]
                # CLV is positive if you beat the closing line in the right direction
                if side == "Over":
                    clv = closing_line - prop_line
                else:
                    clv = prop_line - closing_line
                df.at[idx, "closing_line"] = closing_line
                df.at[idx, "clv"] = clv
            except Exception as e:
                print(f"Error updating CLV for {row['player_id']} {row['stat_type']} {row['date']}: {e}")
    df.to_csv(log_path, index=False)
    print("CLV updated.")

if __name__ == "__main__":
    update_clv()
