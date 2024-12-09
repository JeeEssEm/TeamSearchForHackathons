from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from core import dtos


class Wish(Base):
    __tablename__ = "wishes"
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    moderator_id: Mapped[int | None]
    moderator_response: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    def convert_to_dto(self) -> dtos.Wish:
        return dtos.Wish(
            id=self.id,
            user_id=self.user_id,
            moderator_id=self.moderator_id,
            moderator_response=self.moderator_response,
            description=self.description,
            is_archived=self.is_archived
        )
