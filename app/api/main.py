import os
from fastapi import FastAPI, Query, Body
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

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
