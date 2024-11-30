from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from core.database import Base

if TYPE_CHECKING:
    from .technology import Technology


class Vacancy(Base):
    __tablename__ = "vacancies"
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id"), nullable=False
    )
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False)

    technologies: Mapped[list["Technology"]] = relationship(
        secondary="vacancies_technologies"
    )
