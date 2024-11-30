from typing import TYPE_CHECKING
from datetime import date

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core import dtos

if TYPE_CHECKING:
    from .user import User
    from .team import Team


class Hackathon(Base):
    __tablename__ = "hackathons"

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date]
    end_date: Mapped[date]

    users: Mapped[list["User"]] = relationship(
        "User", secondary="users_hackathons"
    )

    teams: Mapped[list["Team"]] = relationship(
        "Team", secondary="teams_hackathons", back_populates="hackathons"
    )

    def convert_to_dto_basehack(self) -> dtos.BaseHackathon:
        return dtos.BaseHackathon(
            id=self.id,
            title=self.title,
        )

    def convert_to_dto(self) -> dtos.Hackathon:
        return dtos.Hackathon(
            id=self.id,
            title=self.title,
            start_date=self.start_date,
            end_date=self.end_date,
        )
