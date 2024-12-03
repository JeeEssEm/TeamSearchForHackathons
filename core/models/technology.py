from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, relationship, mapped_column

from core.database import Base
from core import dtos


if TYPE_CHECKING:
    from .user import User


class Technology(Base):
    __tablename__ = "technologies"

    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at = Annotated[datetime, mapped_column(server_default=func.now())]

    users: Mapped[list["User"]] = relationship(secondary="users_technologies")

    def convert_to_dto(self):
        return dtos.Technology(
            id=self.id,
            title=self.title,
        )
