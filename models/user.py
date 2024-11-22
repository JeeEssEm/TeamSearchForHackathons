from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from ..database import Base

if TYPE_CHECKING:
    from .form import Form
    

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    middlename: Mapped[str] = mapped_column(String(50), nullable=True)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    uni: Mapped[str] = mapped_column(String(50), nullable=True)
    year_of_study: Mapped[int] = mapped_column(Integer, nullable=True)
    group: Mapped[str] = mapped_column(String(50), nullable=True)
    about_me: Mapped[str] = mapped_column(Text, nullable=True)
    achievements: Mapped[str] = mapped_column(Text, nullable=True)
    resume: Mapped[str] = mapped_column(String(255), nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)


    forms: Mapped[list["Form"]] = relationship("Form", secondary="users_forms", back_populates="users")

