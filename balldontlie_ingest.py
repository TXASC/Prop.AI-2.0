import requests
import pandas as pd
from typing import List, Dict, Any

BALLDONTLIE_BASE_URL = "https://www.balldontlie.io/api/v1/"

def get_player_id(player_name: str) -> int:
    """Search for a player by name and return their balldontlie.io player ID."""
    resp = requests.get(f"{BALLDONTLIE_BASE_URL}players", params={"search": player_name})
    resp.raise_for_status()
    data = resp.json()["data"]
    if not data:
        raise ValueError(f"Player '{player_name}' not found.")
    return data[0]["id"]

def get_recent_game_logs(player_id: int, num_games: int = 10) -> List[Dict[str, Any]]:
    """Fetch recent game logs for a player by player_id."""
    stats = []
    page = 1
    while len(stats) < num_games:
        resp = requests.get(f"{BALLDONTLIE_BASE_URL}stats", params={"player_ids[]": player_id, "per_page": 100, "page": page})
        resp.raise_for_status()
        data = resp.json()["data"]
        if not data:
            break
        stats.extend(data)
        page += 1
    return stats[:num_games]

def get_season_averages(player_id: int, season: int) -> Dict[str, Any]:
    """Fetch season averages for a player."""
    resp = requests.get(f"{BALLDONTLIE_BASE_URL}season_averages", params={"player_ids[]": player_id, "season": season})
    resp.raise_for_status()
    data = resp.json()["data"]
    if not data:
        raise ValueError(f"No season averages found for player_id {player_id} in season {season}.")
    return data[0]

def player_stats_dataframe(player_name: str, num_games: int = 10, season: int = None) -> pd.DataFrame:
    """Return a DataFrame of recent game logs and season averages for a player."""
    player_id = get_player_id(player_name)
    logs = get_recent_game_logs(player_id, num_games)
    df = pd.DataFrame(logs)
    if season is None:
        # Use the season from the most recent game
        if not df.empty:
            season = df.iloc[0]["game"]["season"]
        else:
            raise ValueError("No games found for player.")
    season_avg = get_season_averages(player_id, season)
    # Add season averages as a separate row
    avg_row = {**season_avg, "is_season_avg": True}
    df["is_season_avg"] = False
    df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True, sort=False)
    return df

if __name__ == "__main__":
    # Example usage
    player = "LeBron James"
    df = player_stats_dataframe(player, num_games=10)
    print(df[["game", "pts", "reb", "ast", "is_season_avg"]])
