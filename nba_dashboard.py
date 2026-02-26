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

# --- HEADER ---
st.markdown("""
<style>
    .main {background-color: #000000; color: #ffffff;}
    .stApp {background-color: #000000; color: #ffffff;}
    .sticky-header th {position: sticky; top: 0; background: #181c24; color: #ffffff; z-index: 2;}
</style>
""", unsafe_allow_html=True)

st.title("NBA Prop Analytics Dashboard")

# --- NAVIGATION ---
tabs = ["Dashboard", "Player Props", "Bet Tracker", "Insights"]
selected_tab = st.tabs(tabs)[0]

# --- FILTERS ---
stat_type = st.selectbox("Stat Type", ["PTS", "REB", "AST", "PTS + REB + AST"], index=0)
selected_date = st.date_input("Date", value=date.today())

# --- DATA FETCH ---
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
    # Only show PTS, REB, AST, PRA
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
    # Strict odds filter: only include props where BOTH over_price and under_price are within -130 to +120
    if "over_price" in df.columns and "under_price" in df.columns:
        df = df[(df["over_price"] >= -130) & (df["over_price"] <= 120) & (df["under_price"] >= -130) & (df["under_price"] <= 120)]
        # Only show props where recommended side matches favorite (lowest odds)
        def favorite_side(row):
            # Over is favorite if over_price < under_price, Under is favorite if under_price < over_price
            if row["over_price"] < row["under_price"]:
                return row["recommended_side"] == "Over"
            elif row["under_price"] < row["over_price"]:
                return row["recommended_side"] == "Under"
            else:
                return False  # Exclude if odds are equal (no clear favorite)
        df = df[df.apply(favorite_side, axis=1)]
    elif "price_american" in df.columns:
        df = df[(df["price_american"] >= -130) & (df["price_american"] <= 120)]
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
    # Table columns
    table_cols = ["player_id", "stat_type", "line", "recommended_side", "over_odds", "under_odds", "projection", "edge_pct"]
    st.subheader("Top Prop Bets (Top 50 by Absolute Edge)")
    # Color highlighting by absolute edge
    def highlight_edge(row):
        abs_edge = abs(float(row["edge_pct"]))
        color = "background-color: #444444; color: #ffffff;"
        if abs_edge > 10:
            color = "background-color: #2ecc40; color: #000000;"  # green
        elif abs_edge > 5:
            color = "background-color: #ffe066; color: #000000;"  # yellow
        return [color]*len(row)
    styled_df = df[table_cols].style.apply(highlight_edge, axis=1).set_table_styles([
        {"selector": "th", "props": [("position", "sticky"), ("top", "0"), ("background", "#181c24"), ("color", "#ffffff"), ("z-index", "2")]}])
    # Display with custom headers
    st.write(styled_df.to_html(header_names=["Player", "Stat", "Prop Line", "Recommended Side", "Over Odds", "Under Odds", "Our Projection", "% Edge"]), unsafe_allow_html=True)
    # Expandable explanation per prop
    st.markdown("---")
    st.subheader("Why is this a good pick?")
    for idx, row in df.iterrows():
        odds_display = row['over_odds'] if row['recommended_side'] == 'Over' else row['under_odds']
        with st.expander(f"{row['player_id']} {row['stat_type']} @ {row['line']} Odds: {odds_display} (% Edge: {row['edge_pct']}) - {row['recommended_side']}"):
            st.write(f"Projection: {row['projection']}, Prop Line: {row['line']}, Edge: {row['edge_pct']}%. Recommended: {row['recommended_side']}. Odds: {odds_display}")
            st.write("A positive edge means our projection is higher than the prop line, indicating value. The higher the edge, the more favorable the bet. The recommended side is based on whether our projection is above (Over) or below (Under) the line. Both Over and Under odds are shown for reference.")
else:
    st.info("No data available for the selected date.")

# --- ODDS SHOPPING SIDEBAR ---
 # Removed odds shopping sidebar

# --- PROJECTION BREAKDOWN (HISTOGRAM) ---
 # Removed projection distribution chart
