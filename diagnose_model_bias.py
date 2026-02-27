import requests
import pandas as pd

def fetch_board():
    API_URL = "http://localhost:8000/board"
    resp = requests.get(API_URL)
    resp.raise_for_status()
    return resp.json()

def main():
    board_data = fetch_board()
    if not board_data or "markets" not in board_data:
        print("No board data available.")
        return
    df = pd.DataFrame(board_data["markets"])
    if "projection" not in df.columns or "line" not in df.columns:
        print("Missing projection or line columns.")
        return
    df["projection"] = pd.to_numeric(df["projection"], errors="coerce")
    df["line"] = pd.to_numeric(df["line"], errors="coerce")
    df = df.dropna(subset=["projection", "line"])
    df["recommended_side"] = df.apply(lambda row: "Over" if row["projection"] > row["line"] else "Under", axis=1)
    over_count = (df["recommended_side"] == "Over").sum()
    under_count = (df["recommended_side"] == "Under").sum()
    print(f"Over count: {over_count}")
    print(f"Under count: {under_count}")
    print(f"Mean projection - line: {df['projection'].mean() - df['line'].mean():.2f}")
    print(f"Median projection - line: {df['projection'].median() - df['line'].median():.2f}")
    print("Sample rows:")
    print(df[["player_id", "stat_type", "projection", "line", "recommended_side"]].head(10))

if __name__ == "__main__":
    main()
