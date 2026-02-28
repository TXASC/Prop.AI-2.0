import os
import requests
import json
from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
@app.post("/run_full")
def run_full():
    """
    Triggers a full data pull and enriches board data with game context from TheODDS API.
    """
    try:
        api_key = os.getenv("THEODDS_API_KEY")
        if not api_key:
            return JSONResponse(content={"status": "error", "message": "Missing THEODDS_API_KEY in .env"}, status_code=500)

        odds_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds?regions=us&oddsFormat=american&apiKey={api_key}"
        odds_resp = requests.get(odds_url)
        if odds_resp.status_code != 200:
            return JSONResponse(content={"status": "error", "message": f"Failed to fetch odds: {odds_resp.text}"}, status_code=500)
        odds_data = odds_resp.json()

        today = str(json.loads(requests.get("http://worldtimeapi.org/api/timezone/America/New_York").text)["datetime"]).split("T")[0]
        board_path = f"output/daily_board_{today}.json"
        if not os.path.exists(board_path):
            return JSONResponse(content={"status": "error", "message": f"No board found for {today}"}, status_code=500)
        with open(board_path, "r") as f:
            board = json.load(f)

        def enrich_market_with_odds(board, odds_data):
            """Enriches each market in board with game odds context from TheODDS API."""
            nba_teams = [
                "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls",
                "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warriors",
                "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies",
                "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
                "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers",
                "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards"
            ]
            sharp_books = [
                "circa", "pinnacle", "westgate", "draftkings", "fanduel", "betmgm", "caesars", "betonlineag",
                "pointsbetus", "unibet", "sugarhouse", "betrivers", "barstool", "bovada", "williamhill_us"
            ]
            player_team_map = {
                "Cade Cunningham": "Detroit Pistons",
                "James Harden": "Philadelphia 76ers",
                "Tobias Harris": "Philadelphia 76ers",
                "Evan Mobley": "Cleveland Cavaliers",
                "Jalen Duren": "Detroit Pistons",
                "Jarrett Allen": "Cleveland Cavaliers",
                "Duncan Robinson": "Miami Heat",
                "Jaylon Tyson": "Houston Rockets",
                "Sam Merrill": "Cleveland Cavaliers",
                "Paul Reed Jr": "Philadelphia 76ers",
                "Ausar Thompson": "Detroit Pistons",
                "Ron Holland": "Houston Rockets"
            }
            import difflib
            for market in board.get("markets", []):
                player = market.get("player_id")
                team = player_team_map.get(player, None)
                if not team and "team" in market:
                    team = difflib.get_close_matches(market["team"], nba_teams, n=1, cutoff=0.8)
                    team = team[0] if team else None
                matched_game = None
                if team:
                    for game in odds_data:
                        home = game.get("home_team")
                        away = game.get("away_team")
                        if team in [home, away]:
                            matched_game = game
                            break
                if matched_game:
                    selected_book = None
                    for book_key in sharp_books:
                        for bookmaker in matched_game.get("bookmakers", []):
                            if bookmaker.get("key") == book_key:
                                selected_book = bookmaker
                                break
                        if selected_book:
                            break
                    moneyline = None
                    total_points = None
                    winner = None
                    selected_book_name = selected_book["title"] if selected_book else "N/A"
                    if selected_book:
                        for market_obj in selected_book.get("markets", []):
                            if market_obj.get("key") == "h2h":
                                for outcome in market_obj.get("outcomes", []):
                                    if outcome.get("name") == team:
                                        moneyline = outcome.get("price")
                                        winner = team if outcome.get("price") < 0 else matched_game.get("home_team")
                            if market_obj.get("key") == "totals":
                                for outcome in market_obj.get("outcomes", []):
                                    total_points = outcome.get("point")
                    market["team_moneyline"] = moneyline if moneyline is not None else "N/A"
                    market["game_total"] = total_points if total_points is not None else "N/A"
                    market["expected_winner"] = winner if winner else "N/A"
                    market["odds_book"] = selected_book_name
                else:
                    market["team_moneyline"] = "N/A"
                    market["game_total"] = "N/A"
                    market["expected_winner"] = "N/A"
                    market["odds_book"] = "N/A"
            return board

        board = enrich_market_with_odds(board, odds_data)
        with open(board_path, "w") as f:
            json.dump(board, f, indent=2)
        return JSONResponse(content={"status": "success", "message": "Full data pull and enrichment complete."}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

THEODDS_API_KEY = os.getenv("THEODDS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class PickRequest(BaseModel):
    user_tag: str
    market_id: str
    side: str
    stake: float
    line_at_pick: float
    price_at_pick: int
    model_version: str
    projected_mean: float
    p_hit: float

@app.get("/health")
def health():
    return {"status": "OK"}


@app.get("/board")
def board(date: str = Query(..., description="YYYY-MM-DD")):
    from app.core.utils.logging import logger
    import json
    run_id = f"run_{date}"
    model_version = "nba_v0_market_normal_001"
    logger.info(f"Board requested for {date} run_id={run_id} model_version={model_version}")
    fname = f"output/daily_board_{date}.json"
    if not os.path.exists(fname):
        return {"error": f"No board found for {date}"}
    with open(fname, "r") as f:
        artifact = json.load(f)
    return artifact


@app.get("/edges")
def edges(date: str = Query(...), stat_type: str = Query(None), limit: int = Query(50)):
    from app.core.utils.logging import logger
    run_id = f"run_{date}"
    model_version = "nba_v0_market_normal_001"
    logger.info(f"Edges requested for {date} stat_type={stat_type} run_id={run_id} model_version={model_version}")
    # TODO: Query DB for edges
    return {"date": date, "stat_type": stat_type, "run_id": run_id, "model_version": model_version, "edges": [], "limit": limit}


@app.get("/metrics")
def metrics(date: str = Query(...)):
    from app.core.utils.logging import logger
    run_id = f"run_{date}"
    model_version = "nba_v0_market_normal_001"
    logger.info(f"Metrics requested for {date} run_id={run_id} model_version={model_version}")
    # TODO: Compute metrics
    return {"date": date, "run_id": run_id, "model_version": model_version, "metrics": {}}

@app.post("/picks")
def log_pick(pick: PickRequest = Body(...)):
    # TODO: Log pick in DB
    return {"status": "logged", "pick": pick}

@app.post("/ingest/run")
def ingest_run(date: str = Query(...)):
    # TODO: Run ingestion pipeline
    return {"status": "ingested", "date": date}
