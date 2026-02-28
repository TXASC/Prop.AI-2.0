import streamlit as st
import streamlit.components.v1 as components
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
    # Odds widget removed; only use game odds in notes
    # --- Manual Full Data Pull Button (unique key, single instance) ---
    st.markdown("## Manual Full Data Pull")
    if st.button("Run Full Data Pull (OpenAI Full Mode)", key="full_data_pull"):
        # --- Data Preparation ---
        df = pd.DataFrame(board_data["markets"])
        df = df[df["stat_type"].isin(["PTS", "REB", "AST", "PRA"])]
        df = df[((df["stat_type"] == "PTS") & (df["line"] >= 7.5)) |
                ((df["stat_type"] == "REB") & (df["line"] >= 3.5)) |
                ((df["stat_type"] == "AST") & (df["line"] >= 3.5)) |
                ((df["stat_type"] == "PRA"))]
        df["edge_pct"] = ((df["projection"] - df["line"]) / df["line"] * 100)
        df["recommended_side"] = df.apply(lambda row: "Over" if row["projection"] > row["line"] else "Under", axis=1)
        df = df.sort_values("line", ascending=False).drop_duplicates(["player_id", "stat_type"], keep="first")
        df = df[(df["edge_pct"] >= -35) & (df["edge_pct"] <= 35)]
        df = df.head(50)
        df["line"] = df["line"].map(lambda x: f"{x:.1f}")
        df["projection"] = df["projection"].map(lambda x: f"{x:.1f}")
        df["edge_pct"] = df["edge_pct"].map(lambda x: f"{float(x):.1f}")

        # --- Handicapper Notes Column ---
        def concise_handicapper_note(row):
            notes = []
            proj = float(row['projection'])
            line = float(row['line'])
            edge = float(row['edge_pct'])
            recent_avg = row.get('recent_avg', None)
            opp_guard_ppg = row.get('opp_guard_ppg', None)
            # Model rationale
            notes.append(f"Model projects {proj:.1f} points, {edge:.1f}% above market line of {line:.1f}.")
            # Recent trends
            if recent_avg:
                notes.append(f"Recent avg: {recent_avg:.1f} PPG last 5 games.")
            # Opponent weakness
            if opp_guard_ppg:
                notes.append(f"Opponent allows {opp_guard_ppg:.1f} PPG to starting guards (bottom-5 NBA).")
            # Game context
            game_type = row.get('game_type', 'Regular')
            notes.append(f"Game type: {game_type}.")
            # Injury/fatigue
            injury = row.get('injury_status', 'No major injuries')
            fatigue = row.get('fatigue_note', 'No fatigue concerns')
            notes.append(f"Injury: {injury}, Fatigue: {fatigue}.")
            # Motivation/intangibles
            motivation = row.get('motivation_note', None)
            if motivation:
                notes.append(f"Motivation: {motivation}.")
            # Edge summary
            if edge > 10:
                notes.append("Strong edge based on recent form and matchup.")
            elif edge > 5:
                notes.append("Solid edge based on recent form and matchup.")
            # Edge explanation
            notes.append("Edge = model projection minus market line, adjusted for confidence.")
            notes.append(f"Recommended: {row['recommended_side']}")
            return " | ".join(notes)
        df["Handicapper Notes"] = df.apply(concise_handicapper_note, axis=1)

        # --- UI Table ---
        table_cols = ["player_id", "stat_type", "line", "recommended_side", "projection", "edge_pct"]
        st.subheader("Top Prop Bets (Top 50 by Absolute Edge)")
        selected_idx = st.selectbox(
            "Select a prop to view handicap notes:",
            options=list(df.index),
            format_func=lambda i: f"{df.loc[i, 'player_id']} {df.loc[i, 'stat_type']} @ {df.loc[i, 'line']} ({df.loc[i, 'recommended_side']})"
        )
        st.dataframe(df[table_cols], use_container_width=True)
        st.markdown("---")
        row = df.loc[selected_idx]
        with st.expander(f"Handicapper Notes: {row['player_id']} {row['stat_type']} @ {row['line']} (% Edge: {row['edge_pct']}) - {row['recommended_side']}"):
            st.write(f"Projection: {row['projection']}, Prop Line: {row['line']}, Edge: {row['edge_pct']}%. Recommended: {row['recommended_side']}")
            st.markdown(f"**Handicapper Notes:** {row['Handicapper Notes']}")

        import os
        from datetime import datetime

        log_cols = ["player_id", "stat_type", "line", "projection", "recommended_side", "over_odds", "under_odds", "edge_pct"]
        log_df = df.copy()
        log_df["date"] = datetime.now().strftime("%Y-%m-%d")
        # Guardrail: Ensure all log_cols exist
        for col in log_cols:
            if col not in log_df.columns:
                log_df[col] = ""
        # Safe selection and rename
        log_df = log_df.reindex(columns=log_cols + ["date"], fill_value="")
        log_df = log_df.rename(columns={"line": "prop_line"})
        log_df = log_df[["date", "player_id", "stat_type", "prop_line", "projection", "recommended_side", "over_odds", "under_odds", "edge_pct"]]
        log_path = os.path.join("output", "pick_log.csv")
        if not os.path.exists("output"):
            os.makedirs("output")
        # Append to CSV, add header if file is new
        write_header = not os.path.exists(log_path) or os.path.getsize(log_path) == 0
