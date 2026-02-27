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
    df["projection"] = pd.to_numeric(df["projection"], errors="coerce")
    df["line"] = pd.to_numeric(df["line"], errors="coerce")
    df = df.dropna(subset=["projection", "line"])
    df["recommended_side"] = df.apply(lambda row: "Over" if row["projection"] > row["line"] else "Under", axis=1)
    # Before filtering
    print(f"Before filtering: Over={sum(df['recommended_side']=='Over')}, Under={sum(df['recommended_side']=='Under')}")
    # Apply dashboard filters
    df = df[df["stat_type"].isin(["PTS", "REB", "AST", "PRA"])]
    df = df[((df["stat_type"] == "PTS") & (df["line"] >= 7.5)) |
            ((df["stat_type"] == "REB") & (df["line"] >= 3.5)) |
            ((df["stat_type"] == "AST") & (df["line"] >= 3.5)) |
            ((df["stat_type"] == "PRA"))]
    if "over_price" in df.columns and "under_price" in df.columns:
        df = df[(df["over_price"] >= -130) & (df["over_price"] <= 120) & (df["under_price"] >= -130) & (df["under_price"] <= 120)]
        def favorite_side(row):
            if row["over_price"] < row["under_price"]:
                return row["recommended_side"] == "Over"
            elif row["under_price"] < row["over_price"]:
                return row["recommended_side"] == "Under"
            else:
                return False
        df = df[df.apply(favorite_side, axis=1)]
    elif "price_american" in df.columns:
        df = df[(df["price_american"] >= -130) & (df["price_american"] <= 120)]
    df = df.sort_values("line", ascending=False).drop_duplicates(["player_id", "stat_type"], keep="first")
    df = df[(df["projection"] - df["line"]).abs() / df["line"] * 100 >= -35]
    # After filtering
    print(f"After filtering: Over={sum(df['recommended_side']=='Over')}, Under={sum(df['recommended_side']=='Under')}")
    print(df[["player_id", "stat_type", "projection", "line", "recommended_side"]].head(10))

if __name__ == "__main__":
    main()
