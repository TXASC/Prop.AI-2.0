from app.core.adapters.theodds import TheOddsClient
from app.core.normalization.nba_props import normalize_props
from app.core.storage.repository import NBARepository
from app.core.utils.logging import logger
from datetime import datetime


def ingest_nba_props(date):
    def parse_dt(val):
        if isinstance(val, str):
            # Handle 'Z' UTC suffix
            if val.endswith('Z'):
                val = val[:-1] + '+00:00'
            try:
                return datetime.fromisoformat(val)
            except Exception:
                return None
        return val

    client = TheOddsClient()
    repo = NBARepository()
    raw_props = client.fetch_odds(date)
    if raw_props:
        from app.core.utils.ids import generate_id
        normalized = normalize_props(raw_props)
        markets = []
        lines = []
        for m in normalized:
            market_id = generate_id()
            market_db = {
                "id": market_id,
                "game_id": m["game_id"],
                "player_id": m["player_id"],
                "stat_type": m["stat_type"],
                "created_at": parse_dt(m.get("timestamp"))
            }
            # For CLI/board, include extra fields
            market_cli = dict(market_db)
            market_cli["price_american"] = m["price_american"]
            market_cli["source"] = m["source"]
            market_cli["line_value"] = m["line_value"]
            market_cli["side"] = m["side"]  # PATCH: include side for CLI grouping
            markets.append(market_cli)
            lines.append({
                "id": generate_id(),
                "market_id": market_id,
                "source": m["source"],
                "side": m["side"],
                "line_value": m["line_value"],
                "price_american": m["price_american"],
                "timestamp": parse_dt(m.get("timestamp")),
                "latency_ms": m.get("latency_ms", 0)
            })
        repo.store_markets([{
            "id": m["id"],
            "game_id": m["game_id"],
            "player_id": m["player_id"],
            "stat_type": m["stat_type"],
            "created_at": m["created_at"]
        } for m in markets])
        repo.store_lines(lines)
        repo.store_raw_response(raw_props, date)
        logger.info(f"Ingestion complete for {date}: {len(markets)} markets, {len(lines)} lines")
        return markets
    logger.error(f"No data ingested for {date}")
    return []
