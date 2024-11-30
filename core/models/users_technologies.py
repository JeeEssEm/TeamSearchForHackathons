from sqlalchemy import Table, Column, Integer, ForeignKey
from core.database import Base

users_technologies = Table(
    "users_technologies",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "technology_id",
        Integer,
        ForeignKey("technologies.id", onupdate="CASCADE"),
        primary_key=True,
    ),
)
