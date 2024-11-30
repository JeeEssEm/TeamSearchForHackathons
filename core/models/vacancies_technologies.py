from sqlalchemy import Table, Column, Integer, ForeignKey
from core.database import Base


vacancies_technologies = Table(
    "vacancies_technologies",
    Base.metadata,
    Column(
        "vacancy",
        Integer,
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "technology_id",
        Integer,
        ForeignKey("technologies.id", onupdate="CASCADE"),
        primary_key=True,
    ),
)
