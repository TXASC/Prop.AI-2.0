import streamlit as st
import requests
import pandas as pd
from datetime import date


# --- CONFIG ---
API_URL = "http://localhost:8000/board"

# --- PAGE SETUP ---

st.set_page_config(
    page_title="NBA Prop Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏀"
)


# --- FILTERS ---
selected_date = date.today()
def fetch_board(selected_date):
    try:
        resp = requests.get(API_URL, params={"date": selected_date})
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"API error: {resp.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

board_data = fetch_board(selected_date)

# --- MAIN TABLE ---

if board_data and "markets" in board_data:
    df = pd.DataFrame(board_data["markets"])
    df = df[df["stat_type"].isin(["PTS", "REB", "AST", "PRA"])]
    # Filter by minimum prop lines (DFS-typical lines)
    df = df[((df["stat_type"] == "PTS") & (df["line"] >= 7.5)) |
            ((df["stat_type"] == "REB") & (df["line"] >= 3.5)) |
            ((df["stat_type"] == "AST") & (df["line"] >= 3.5)) |
            ((df["stat_type"] == "PRA"))]
    # Calculate % Edge
    df["edge_pct"] = ((df["projection"] - df["line"]) / df["line"] * 100)
    # Add recommended side column
    df["recommended_side"] = df.apply(lambda row: "Over" if row["projection"] > row["line"] else "Under", axis=1)

    # Relaxed odds filter: allow wider range and remove favorite side filter
    if "over_price" in df.columns and "under_price" in df.columns:
        df = df[(df["over_price"] >= -200) & (df["over_price"] <= 200) & (df["under_price"] >= -200) & (df["under_price"] <= 200)]
    elif "price_american" in df.columns:
        df = df[(df["price_american"] >= -200) & (df["price_american"] <= 200)]
    # Remove duplicate player/stat lines (keep highest line)
    df = df.sort_values("line", ascending=False).drop_duplicates(["player_id", "stat_type"], keep="first")
    # Use over_price and under_price from board data if available
    if "over_price" in df.columns and "under_price" in df.columns:
        df["over_odds"] = df["over_price"]
        df["under_odds"] = df["under_price"]
    else:
        df["over_odds"] = df["price"]
        df["under_odds"] = ""
    # Filter by edge window (-35% to 35%)
    df = df[(df["edge_pct"] >= -35) & (df["edge_pct"] <= 35)]
    # Sort by absolute edge
    df = df.reindex(df["edge_pct"].abs().sort_values(ascending=False).index)
    # Select top 50
    df = df.head(50)
    # Format numbers to 1 decimal place
    df["line"] = df["line"].map(lambda x: f"{x:.1f}")
    df["projection"] = df["projection"].map(lambda x: f"{x:.1f}")
    df["edge_pct"] = df["edge_pct"].map(lambda x: f"{float(x):.1f}")
    df["over_odds"] = df["over_odds"].map(lambda x: f"{x:.1f}" if x not in ["", None] else "")
    df["under_odds"] = df["under_odds"].map(lambda x: f"{x:.1f}" if x not in ["", None] else "")

    # --- Add Odds and Notes Columns (Concise Table) ---
    odds_col = []
    notes_col = []
    books = ["FanDuel", "DraftKings", "BetMGM", "Caesars"]
    def concise_handicapper_note(row):
        notes = []
        if float(row['projection']) > float(row['line']):
            notes.append(f"Proj>{row['line']}")
        if float(row['edge_pct']) > 10:
            notes.append("Strong edge")
        elif float(row['edge_pct']) > 5:
            notes.append("Solid edge")
        return ", ".join(notes)
    for idx, row in df.iterrows():
        prop_mask = (df["player_id"] == row["player_id"]) & (df["stat_type"] == row["stat_type"]) & (df["line"] == row["line"])
        prop_df = df[prop_mask]
        odds_summary = ""
        for side in ["Over", "Under"]:
            side_df = prop_df[prop_df["recommended_side"] == side]
            book_odds = side_df[["source", f"{side.lower()}_odds"]].dropna()
            book_odds = book_odds[book_odds["source"].isin(books)]
            if not book_odds.empty:
                high_idx = book_odds[f"{side.lower()}_odds"].astype(float).idxmax()
                low_idx = book_odds[f"{side.lower()}_odds"].astype(float).idxmin()
                high_val = float(book_odds.loc[high_idx, f"{side.lower()}_odds"])
                low_val = float(book_odds.loc[low_idx, f"{side.lower()}_odds"])
                high_book = book_odds.loc[high_idx, "source"]
                low_book = book_odds.loc[low_idx, "source"]
                odds_summary += f"{side}: High {high_val:.1f} ({high_book}), Low {low_val:.1f} ({low_book})  "
        odds_col.append(odds_summary.strip())
        notes_col.append(concise_handicapper_note(row))
    df["Odds"] = odds_col
    df["Handicapper Notes"] = notes_col
    table_cols = ["player_id", "stat_type", "line", "recommended_side", "projection", "edge_pct", "Odds", "Handicapper Notes"]
    st.subheader("Top Prop Bets (Top 50 by Absolute Edge)")
    st.dataframe(df[table_cols], use_container_width=True)
    st.markdown("---")
    # --- Expander for Full Notes (One per row) ---
    for idx, row in df.iterrows():
        odds_display = row['over_odds'] if row['recommended_side'] == 'Over' else row['under_odds']
        with st.expander(f"Handicapper Notes: {row['player_id']} {row['stat_type']} @ {row['line']} Odds: {odds_display} (% Edge: {row['edge_pct']}) - {row['recommended_side']}"):
            st.write(f"Projection: {row['projection']}, Prop Line: {row['line']}, Edge: {row['edge_pct']}%. Recommended: {row['recommended_side']}. Odds: {odds_display}")
            st.markdown(f"**Handicapper Notes:** {concise_handicapper_note(row)}")
            # Odds screen/modal logic placeholder (background/modal-ready)
            st.markdown("*Click for full odds screen coming soon*")

if not (board_data and "markets" in board_data):
    st.info("No data available for the selected date.")

# --- ODDS SHOPPING SIDEBAR ---
 # Removed odds shopping sidebar

# --- PROJECTION BREAKDOWN (HISTOGRAM) ---
 # Removed projection distribution chart
