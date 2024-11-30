from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from core.database import Base
from core import dtos

if TYPE_CHECKING:
    from .user import User
    from .hackathon import Hackathon


class Team(Base):
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
    captain: Mapped["User"] = relationship()

    async def convert_to_dto(self) -> dtos.Team:
        members = [
            user.convert_to_dto_baseuser()
            for user in await self.awaitable_attrs.users
        ]
        members.append(
            (await self.awaitable_attrs.captain).convert_to_dto_baseuser()
        )
        return dtos.Team(
            id=self.id,
            title=self.title,
            description=self.description,
            members=members,
            captain_id=self.captain_id,
            hacks=[
                hack.convert_to_dto_basehack()
                for hack in await self.awaitable_attrs.hackathons
            ],
        )
