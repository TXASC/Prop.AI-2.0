import os
import requests
from datetime import datetime
from app.core.utils.logging import logger

THEODDS_API_KEY = os.getenv("THEODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

class TheOddsClient:
    def __init__(self, api_key=THEODDS_API_KEY):
        self.api_key = api_key

    def get_event_ids(self):
        # Fetch NBA event IDs for today/upcoming
        events_url = "https://api.the-odds-api.com/v4/sports/basketball_nba/events"
        params = {
            "apiKey": self.api_key,
            "dateFormat": "iso",
        }
        resp = requests.get(events_url, params=params)
        logger.info(f"NBA events response: {resp.status_code}")
        if resp.status_code == 200:
            return [event["id"] for event in resp.json()]
        else:
            logger.error(f"Failed to fetch NBA events: {resp.text}")
            return []

    def fetch_odds(self, date: str):
        # Fetch player prop odds for all NBA events for the date
        event_ids = self.get_event_ids()
        if not event_ids:
            logger.error("No NBA events found for odds fetch.")
            return []
        all_props = []
        markets = "player_points,player_assists,player_rebounds,player_threes"
        for event_id in event_ids:
            odds_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/events/{event_id}/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": markets,
                "dateFormat": "iso",
                "oddsFormat": "american",
            }
            resp = requests.get(odds_url, params=params)
            logger.info(f"Event odds {event_id} response: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    all_props.append(data)
            else:
                logger.error(f"Failed to fetch odds for event {event_id}: {resp.text}")
        return all_props
