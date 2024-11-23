from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import AbstractBase


class UsersTechnologies(AbstractBase):
    __tablename__ = "users_technologies"

    user_is: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role_id: Mapped[int] = mapped_column(ForeignKey("technologies.id"), onupdate="CASCADE")
