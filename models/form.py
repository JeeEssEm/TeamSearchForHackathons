from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, Text

if TYPE_CHECKING:
    from .user import User

class Form:
    __tablename__ = "forms"

    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_private:Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    work_exp: Mapped[int] = mapped_column(Integer, int, nullable=True)
    # role_id: Mapped[int] mapped_column() для реализация после создания Role


    users: Mapped[list["User"]] = relationship("User", secondary="users_forms", back_populates="forms")
