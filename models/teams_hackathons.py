from sqlalchemy import Table, Column, Integer, ForeignKey
from database import Base

teams_hackathons = Table(
    "teams_hackathons",
    Base.metadata,
    Column(
        "team_id", Integer, ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "hackathon_id",
        Integer,
        ForeignKey("hackathons.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
