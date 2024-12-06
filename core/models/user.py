from enum import IntEnum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, func

from core.database import Base
from core import dtos

if TYPE_CHECKING:
    from .role import Role
    from .technology import Technology
    from .hackathon import Hackathon
    from .feedback import Feedback


class FormStatus(IntEnum):
    rejected = 0
    in_review = 1
    approved = 2


class User(Base):
    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    middlename: Mapped[str] = mapped_column(String(50), nullable=True)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    # email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    uni: Mapped[str] = mapped_column(String(50), nullable=True)
    year_of_study: Mapped[int] = mapped_column(Integer, nullable=True)
    group: Mapped[str] = mapped_column(String(50), nullable=True)
    about_me: Mapped[str] = mapped_column(String(300), nullable=True)
    resume: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    moderator_feedback: Mapped[str | None]
    moderator_id: Mapped[int | None]
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    form_status: Mapped[FormStatus] = mapped_column(default=FormStatus.in_review.value)
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

    def convert_to_dto_baseuser(self) -> dtos.BaseUser:
        return dtos.BaseUser(
            id=self.id,
            name=self.name,
            middle_name=self.middlename or "",
            surname=self.surname,
        )
    
    def convert_to_dto_form(self) -> dtos.Form:
        return dtos.Form(
            id=self.id,
            name=self.name,
            middle_name=self.middlename or "",
            surname=self.surname,
            updated_at=self.updated_at,
            moderator_id=self.moderator_id,
            form_status=self.form_status
        )

    async def convert_to_dto_user(self) -> dtos.User:
        return dtos.User(
            id=self.id,
            name=self.name,
            middle_name=self.middlename or "",
            surname=self.surname,
            uni=self.uni,
            moderator_feedback=self.moderator_feedback,
            year_of_study=self.year_of_study,
            group=self.group,
            about_me=self.about_me,
            resume=self.resume,
            avatar=self.avatar,
            moderator_id=self.moderator_id,
            form_status=self.form_status,
            technologies=[
                tech.convert_to_dto()
                for tech in await self.awaitable_attrs.technologies],
            roles=[
                role.convert_to_dto()
                for role in await self.awaitable_attrs.roles],
            hackathons=[
                hackathon.convert_to_dto()
                for hackathon in await self.awaitable_attrs.hackathons
            ],
            updated_at=self.updated_at,
        )
