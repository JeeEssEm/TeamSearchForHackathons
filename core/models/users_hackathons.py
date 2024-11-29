from sqlalchemy import Table, Column, Integer, Boolean, ForeignKey
from database import Base

users_hackathons = Table(
    "users_hackathons",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "hackathon_id",
        Integer,
        ForeignKey("hackathons.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("place", Integer, nullable=True),
    Column("is_wished", Boolean, default=True),
)
