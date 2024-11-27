from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from database import AbstractBase


if TYPE_CHECKING:
    from .user import User


class Role(AbstractBase):
    __tablename__ = 'roles'

    title: Mapped[str] = mapped_column(String(100), nullable=False)

    users: Mapped[list['User']] = relationship('User', secondary='users_roles')
