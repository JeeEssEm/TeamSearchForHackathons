from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import AbstractBase


class UsersRoles(AbstractBase):
    __tablename__ = "users_roles"

    user_is: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), onupdate="CASCADE")
