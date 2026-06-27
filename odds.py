import requests
from typing import Any
from odds_api import OddsAPIClient


class OddsAPIClientWrapper:
    def __init__(
        self, api_key: str, timeout: int | None = None, base_url: str | None = None
    ):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = base_url

        # Build kwargs dynamically for arguments that are not None
        kwargs: dict[str, Any] = {}
        if timeout is not None:
            kwargs["timeout"] = timeout
        if base_url is not None:
            kwargs["base_url"] = base_url

        self.client = OddsAPIClient(api_key=api_key, **kwargs)

    def get_historical_events(
        self, sport: str, league: str, from_date: str, to_date: str
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}/historical/events"

        params = {
            "apiKey": self.api_key,
            "sport": sport,
            "league": league,
            "from": from_date,
            "to": to_date,
        }

        return requests.get(url, params).json()

    def get_historical_odds(
        self, sport: str, league: str, from_date: str, to_date: str
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}/historical/odds"

        params = {
            "apiKey": self.api_key,
            "bookmakers": "Sisal IT,Snai IT",
        }

        historical_events = self.get_historical_events(
            sport, league, from_date, to_date
        )

        historical_odds = []
        for event in historical_events:
            params["eventId"] = f"{event['id']}"
            historical_odds.append(requests.get(url, params).json())

        return historical_odds


def main():
    import dotenv
    import os
    import json
    from datetime import datetime, timezone

    dotenv.load_dotenv()
    api_key = os.getenv("ODDS_API_KEY", "demo")
    base_url = "https://api.odds-api.io/v3"
    client = OddsAPIClientWrapper(api_key=api_key, base_url=base_url)

    sport = "football"
    league = "international-fifa-world-cup"
    from_date = datetime(2026, 5, 28, 0, 0, 0, tzinfo=timezone.utc).isoformat()
    to_date = datetime.now(timezone.utc).isoformat()
    historical_events = client.get_historical_events(
        sport=sport, league=league, from_date=from_date, to_date=to_date
    )
    historical_odds = client.get_historical_odds(
        sport=sport, league=league, from_date=from_date, to_date=to_date
    )

    print("-" * 8, "HISTORICAL EVENTS", "-" * 8)
    print(f"\n{json.dumps(historical_events, indent=2)}\n")
    print("-" * 8, "HISTORICAL ODDS", "-" * 8)
    print(f"\n{json.dumps(historical_odds, indent=2)}\n")


if __name__ == "__main__":
    main()
