import os
import requests
from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI()
@app.post("/run_full")
def run_full():
    """
    Triggers a full data pull and enriches board data with game context from TheODDS API.
    """
    try:
        # Load API key
        api_key = os.getenv("THEODDS_API_KEY")
        if not api_key:
            return JSONResponse(content={"status": "error", "message": "Missing THEODDS_API_KEY in .env"}, status_code=500)

        # Fetch NBA odds from TheODDS API
        odds_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds?regions=us&oddsFormat=american&apiKey={api_key}"
        odds_resp = requests.get(odds_url)
        if odds_resp.status_code != 200:
            return JSONResponse(content={"status": "error", "message": f"Failed to fetch odds: {odds_resp.text}"}, status_code=500)
        odds_data = odds_resp.json()

        # Map games for quick lookup
        game_map = {}
        for game in odds_data:
            home = game.get("home_team")
            away = game.get("away_team")
            commence = game.get("commence_time")
            game_map[(home, away)] = {
                "commence_time": commence,
                "bookmakers": game.get("bookmakers", []),
                "home_team": home,
                "away_team": away
            }

        # Load board data
        today = str(json.loads(requests.get("http://worldtimeapi.org/api/timezone/America/New_York").text)["datetime"]).split("T")[0]
        board_path = f"output/daily_board_{today}.json"
        if not os.path.exists(board_path):
            return JSONResponse(content={"status": "error", "message": f"No board found for {today}"}, status_code=500)
        with open(board_path, "r") as f:
            board = json.load(f)

        # Enrich each market with game context
        for market in board.get("markets", []):
            # Try to match player to game
            # (Assume player_id contains enough info to match, or add team info to board for better matching)
            # For demo, just attach first game
            if game_map:
                game = list(game_map.values())[0]
                market["game_type"] = "Regular"
                market["pace"] = "N/A"  # Could be calculated from bookmaker totals
                market["expected_score"] = "N/A"
                market["expected_winner"] = game["home_team"]
            else:
                market["game_type"] = "Regular"
                market["pace"] = "N/A"
                market["expected_score"] = "N/A"
                market["expected_winner"] = "N/A"

        # Save enriched board
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
