

import os
from dotenv import load_dotenv
load_dotenv()
import typer
import datetime

app = typer.Typer()

@app.command("board")
def board_today():
    """Run ingestion and output board for today's NBA games."""
    from app.core.adapters.ingest_pipeline import ingest_nba_props
    from app.core.artifacts.writer import write_daily_board
    today = datetime.date.today().strftime("%Y-%m-%d")
    run_id = f"run_{today}"
    model_version = "nba_v0_market_normal_001"
    markets = ingest_nba_props(today)
    board_data = []
    from app.core.modeling.projection import consensus_mean
    from app.core.pricing.odds_math import american_to_implied_prob, remove_vig
    from app.core.modeling.config import STAT_STDEV_PRIORS
    # Debug: Log normalization output
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("nba-prop-analytics-cli")
    logger.info(f"Normalized markets count: {len(markets)}")
    if markets:
        logger.info(f"Sample normalized market: {markets[0]}")
        logger.info("First 3 normalized markets for debug:")
        for i, m in enumerate(markets[:3]):
            logger.info(f"Market {i}: {m}")
    else:
        logger.warning("No markets after normalization!")

    # Group by (player_id, stat_type, line_value, source) and collect both Over and Under prices
    from collections import defaultdict
    grouped = defaultdict(lambda: {"over": None, "under": None, "player_id": None, "stat_type": None, "line": None, "source": None})
    for m in markets:
        key = (m.get("player_id"), m.get("stat_type"), m.get("line_value"), m.get("source"))
        side = m.get("side", "").lower()
        if side in ("over", "under"):
            grouped[key][side] = m["price_american"]
            grouped[key]["player_id"] = m.get("player_id")
            grouped[key]["stat_type"] = m.get("stat_type")
            grouped[key]["line"] = m.get("line_value")
            grouped[key]["source"] = m.get("source")
    logger.info(f"Grouped props count: {len(grouped)}")
    if grouped:
        sample_key = next(iter(grouped))
        logger.info(f"Sample grouped entry: {grouped[sample_key]}")
    else:
        logger.warning("No grouped props after grouping!")
    for key, entry in grouped.items():
        # If either over or under is present, include the prop
        if entry["over"] is not None or entry["under"] is not None:
            # Use whichever price is present for projection math
            price = entry["over"] if entry["over"] is not None else entry["under"]
            p_implied = american_to_implied_prob(price)
            p_over, p_under = remove_vig(p_implied, 1 - p_implied)
            stat_type = entry["stat_type"]
            line = entry["line"]
            mean = consensus_mean(line, p_over, stat_type)
            board_data.append({
                "player_id": entry["player_id"],
                "stat_type": stat_type,
                "line": line,
                "source": entry["source"],
                "over_price": entry["over"],
                "under_price": entry["under"],
                "projection": round(mean, 2)
            })
    write_daily_board(today, board_data, run_id, model_version)
    typer.echo(f"Board output generated for {today}")
    # For now, create empty edges and metrics artifacts to avoid NameError
    edges = []
    metrics = {}
    from app.core.artifacts.writer import write_daily_edges, write_daily_metrics
    write_daily_edges(today, edges, run_id, model_version)
    write_daily_metrics(today, metrics, run_id, model_version)
    typer.echo(f"Artifacts generated for {today}")

@app.command("pick")
def pick_add(
    market_id: str,
    side: str,
    stake: float,
    line: float,
    price: int,
    user_tag: str = typer.Option("default", help="User tag")
):
    """Add a pick."""
    # TODO: Log pick
    typer.echo(f"Pick added: {market_id} {side} {line} @ {price} for {stake}")

@app.command("grade")
def grade(date: str = typer.Option(..., help="YYYY-MM-DD")):
    """Grade picks (stub if results not available)."""
    # TODO: Grade picks
    typer.echo(f"Graded for {date}")

@app.command("report")
def report(date: str = typer.Option(..., help="YYYY-MM-DD")):
    """Generate daily report."""
    # TODO: Generate report
    typer.echo(f"Report for {date}")

if __name__ == "__main__":
    app()