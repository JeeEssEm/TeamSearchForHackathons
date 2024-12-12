from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from core.database import Base
from core import dtos


if TYPE_CHECKING:
    from .user import User


class Role(Base):
    __tablename__ = "roles"

    title: Mapped[str] = mapped_column(String(100), nullable=False)

    users: Mapped[list["User"]] = relationship("User", secondary="users_roles")

    def convert_to_dto(self) -> dtos.Role:
        return dtos.Role(
            id=self.id,
            title=self.title,
        )
