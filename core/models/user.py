from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, func
from database import AbstractBase
from datetime import datetime

if TYPE_CHECKING:
    from .role import Role
    from .technology import Technology
    from .hackathon import Hackathon
    from .feedback import Feedback


class User(AbstractBase):
    __tablename__ = 'users'
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    middlename: Mapped[str] = mapped_column(String(50), nullable=True)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
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

    roles: Mapped[list['Role']] = relationship(
        'Role', secondary='users_roles', back_populates='users'
    )

    technologies: Mapped[list['Technology']] = relationship(
        'Technology', secondary='users_technologies', back_populates='users'
    )

    hackathons: Mapped[list['Hackathon']] = relationship(
        'Hackathon', secondary='users_hackathons', back_populates='users'
    )

    sent_feedbacks: Mapped[list['Feedback']] = relationship(
        'Feedback', back_populates='sender', foreign_keys='Feedback.sender_id'
    )
    received_feedbacks: Mapped[list['Feedback']] = relationship(
        'Feedback', back_populates='receiver', foreign_keys='Feedback.receiver_id'
    )
