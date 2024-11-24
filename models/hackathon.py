from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import AbstractBase


if TYPE_CHECKING:
    from .user import User
    from .team import Team


class Hackathon(AbstractBase):
    __tablename__ = "hackathons"

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    on_going: Mapped[bool] = mapped_column(Boolean, default=True)

    users: Mapped[list["User"]] = relationship("User", secondary="users_hackathons")

    teams: Mapped[list["Team"]] = relationship("Team", secondary="teams_hackathons")
