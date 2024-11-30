from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from database import AbstractBase

if TYPE_CHECKING:
    from .user import User
    from .hackathon import Hackathon


class Team(AbstractBase):
    __tablename__ = "teams"
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False)
    users: Mapped[list["User"]] = relationship("User", secondary="users_teams")
    hackathons: Mapped[list["Hackathon"]] = relationship(
        "Hackathon", secondary="teams_hackathons"
    )
    captain_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    # поле для получения капитана
    # captain: Mapped['User'] = relationship('User', foreign_keys=[captain_id])
