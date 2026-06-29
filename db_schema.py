from datetime import datetime
from sqlmodel import SQLModel, Field


class Match(SQLModel, table=True):
    match_id: int | None = Field(default=None, primary_key=True)
    # Reference the "team" table and its "slug" column
    home_team_slug: str = Field(max_length=100, foreign_key="team.slug")
    away_team_slug: str = Field(max_length=100, foreign_key="team.slug")
    # Reference the "league" table and its "league_slug" column
    league_slug: str = Field(max_length=100, foreign_key="league.league_slug")
    home_odd: float
    draw_odd: float
    away_odd: float
    home_score: int | None = None
    away_score: int | None = None
    is_concluded: bool
    date: datetime | None = None


class League(SQLModel, table=True):
    league_slug: str = Field(max_length=100, primary_key=True)
    name: str = Field(max_length=255)
    # Reference the "team" table and its "slug" column
    winner_slug: str | None = Field(
        default=None, max_length=100, foreign_key="team.slug"
    )
    is_concluded: bool = False


class Team(SQLModel, table=True):
    slug: str = Field(max_length=100, primary_key=True)
    name: str = Field(max_length=255)


# Added table=True here assuming this is your Many-to-Many junction table
class TeamLeague(SQLModel, table=True):
    team_slug: str = Field(max_length=100, primary_key=True, foreign_key="team.slug")
    league_slug: str = Field(
        max_length=100, primary_key=True, foreign_key="league.league_slug"
    )
