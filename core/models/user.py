from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, func
from core.database import Base

from datetime import datetime
from core import dtos

if TYPE_CHECKING:
    from .role import Role
    from .technology import Technology
    from .hackathon import Hackathon
    from .feedback import Feedback


class User(Base):
    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    middlename: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    uni: Mapped[str] = mapped_column(String(50), nullable=True)
    year_of_study: Mapped[int] = mapped_column(Integer, nullable=True)
    group: Mapped[str] = mapped_column(String(50), nullable=True)
    about_me: Mapped[str] = mapped_column(String(300), nullable=True)
    resume: Mapped[str] = mapped_column(String(255), nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    moderator_id: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    form_status: Mapped[bool] = mapped_column(Boolean, default=False)
    is_form_private: Mapped[bool] = mapped_column(Boolean, default=False)

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary="users_roles", back_populates="users"
    )

    technologies: Mapped[list["Technology"]] = relationship(
        "Technology", secondary="users_technologies", back_populates="users"
    )

    hackathons: Mapped[list["Hackathon"]] = relationship(
        "Hackathon", secondary="users_hackathons", back_populates="users"
    )

    sent_feedbacks: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="sender", foreign_keys="Feedback.sender_id"
    )
    received_feedbacks: Mapped[list["Feedback"]] = relationship(
        "Feedback",
        back_populates="receiver",
        foreign_keys="Feedback.receiver_id",
    )

    def convert_to_dto(self):
        return dtos.User(
            id=self.id,
            telegram_id=self.telegram_id,
            name=self.name,
            surname=self.surname,
            middlename=self.middlename,
            email=self.email,
            uni=self.uni,
            year_of_study=self.year_of_study,
            group=self.group,
            about_me=self.about_me,
            resume=self.resume,
            avatar=self.avatar,
            form_status=self.form_status,
            is_form_private=self.is_form_private,
        )
