from sqlalchemy import ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database import AbstractBase


class UsersHackathons(AbstractBase):
    __tablename__ = "users_hackathons"

    user_is: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role_id: Mapped[int] = mapped_column(
        ForeignKey("hackathons.id"), onupdate="CASCADE"
    )
    place: Mapped[int] = mapped_column(Integer, nullable=True)
    is_wished: Mapped[bool] = mapped_column(Boolean, default=True)
