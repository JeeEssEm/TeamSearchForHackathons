from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from database import AbstractBase


class Wish(AbstractBase):
    __tablename__ = 'wishes'
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    moderator_id: Mapped[int] = mapped_column(Integer, nullable=False)
    moderator_response: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean)
