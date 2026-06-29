import os
from datetime import datetime
from typing import Any
import dotenv
from sqlmodel import create_engine, Session
from db_schema import Match

dotenv.load_dotenv()

db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_url = os.getenv("DB_URL")

full_url = f"mariadb+mariadbconnector://{db_username}:{db_password}@{db_url}/soccerbets"


engine = create_engine(full_url, echo=True)


def to_match_schema(m: dict[str, Any]) -> dict[str, Any]:
    # Convert to an ISO string, but make it naive right after parsing
    dt_aware = datetime.fromisoformat(m["date"].replace("Z", "+00:00"))

    match_obj = {
        "match_id": None,
        "home_team_slug": m["home"].lower().replace(" ", "-"),
        "away_team_slug": m["away"].lower().replace(" ", "-"),
        "league_slug": m["league"]["slug"].lower().replace(" ", "-"),
        "home_score": m["scores"]["home"],
        "away_score": m["scores"]["away"],
        "is_concluded": m["status"] == "settled",
        # .replace(tzinfo=None) strips the +00:00 so MariaDB accepts it smoothly
        "date": dt_aware.replace(tzinfo=None),
    }

    sisal_odds = m["bookmakers"].get("Sisal IT")
    snai_odds = m["bookmakers"].get("Snai IT")
    odds = sisal_odds or snai_odds
    if odds is not None:
        ml_odd = next((el["odds"][0] for el in odds if el["name"] == "ML"), dict())
        home_odd, draw_odd, away_odd = (
            ml_odd["home"],
            ml_odd["draw"],
            ml_odd["away"],
        )
        match_obj.update(
            home_odd=home_odd,
            draw_odd=draw_odd,
            away_odd=away_odd,
        )

    return match_obj


def insert_matches(matches: list[dict[str, Any]]):
    matches_odds = list(map(to_match_schema, matches))

    with Session(engine) as session:
        for match_data in matches_odds:
            match = Match(**match_data)
            session.add(match)
        session.commit()


def main():
    # from datetime import datetime, timedelta, timezone
    # import dotenv

    # from odds import OddsAPIClientWrapper
    import json

    #
    # dotenv.load_dotenv()
    #
    # api_key = os.getenv("ODDS_API_KEY", "dummy")
    # client = OddsAPIClientWrapper(api_key)
    #
    # sport = "football"
    # league = "international-fifa-world-cup"
    # to_date = datetime.now(timezone.utc)
    # from_date = to_date - timedelta(days=31)
    # from_date = from_date.isoformat()
    # to_date = to_date.isoformat()
    # matches = client.get_historical_odds(
    #     sport=sport, league=league, from_date=from_date, to_date=to_date
    # )
    #
    with open("/tmp/odds.json", "r", encoding="utf-8") as fp:
        matches = json.load(fp)

    # insert_matches(matches)

    print(list(map(to_match_schema, matches)))


if __name__ == "__main__":
    main()
