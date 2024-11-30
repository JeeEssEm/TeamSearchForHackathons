from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from core.database import Base
from core import dtos

if TYPE_CHECKING:
    from .user import User


class Technology(Base):
    __tablename__ = "technologies"

    title: Mapped[str] = mapped_column(String, nullable=False)

    users: Mapped[list["User"]] = relationship(secondary="users_technologies")

    def convert_to_dto(self):
        return dtos.Technology(
            id=self.id,
            title=self.title,
        )
