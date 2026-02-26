from datetime import datetime


FOCUSED_STAT_TYPES = ["PTS", "REB", "AST", "PRA"]

CANONICAL_MARKET_KEY = [
    "game_id", "player_id", "stat_type", "side", "line_value"
]



def normalize_props(raw_props):
    """
    Normalize and validate event-based TheOdds API player prop odds into canonical markets.
    Args:
        raw_props (list): List of event-level odds responses from TheOdds API
    Returns:
        list: Normalized market dicts
    """
    normalized = []
    # Map API market keys to canonical stat types
    market_to_stat = {
        "player_points": "PTS",
        "player_rebounds": "REB",
        "player_assists": "AST",
        "player_threes": "3PM",
    }
    for event in raw_props:
        game_id = event.get("id")
        bookmakers = event.get("bookmakers", [])
        for book in bookmakers:
            source = book.get("title")
            for market in book.get("markets", []):
                stat_type = market_to_stat.get(market.get("key"))
                if not stat_type:
                    continue
                for outcome in market.get("outcomes", []):
                    # Player name is in outcome["description"] or outcome["name"]
                    player_id = outcome.get("description") or outcome.get("name")
                    side = outcome.get("name")  # Over/Under or player name
                    line_value = outcome.get("point")
                    price_american = outcome.get("price")
                    # Only include if all required fields are present
                    if not all([game_id, player_id, stat_type, side, line_value, source, price_american]):
                        continue
                    # Side normalization: if side is Over/Under, keep; else, skip
                    if side not in ["Over", "Under"]:
                        continue
                    # Always include 'side' as 'over' or 'under'
                    market_dict = {
                        "game_id": game_id,
                        "player_id": player_id,
                        "stat_type": stat_type,
                        "side": side.lower(),
                        "line_value": line_value,
                        "source": source,
                        "price_american": price_american,
                        "timestamp": event.get("commence_time", datetime.utcnow().isoformat()),
                        "latency_ms": 0,
                    }
                    normalized.append(market_dict)
    return normalized
