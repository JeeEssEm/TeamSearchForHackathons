from datetime import datetime
from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models import FormStatus
    from core.dtos.technologies import Technology
    from core.dtos import Hackathon


@dataclass
class CreateUser:
    telegram_id: int
    name: str
    surname: str
    middlename: str = None
    uni: str = None
    year_of_study: int = None
    group: str = None  # Указываем значение по умолчанию
    about_me: str = None
    email: str = None
    # resume: str = None
    # avatar: str = None


@dataclass
class BaseUser:
    id: int
    name: str
    surname: str
    middle_name: str


@dataclass
class Form(BaseUser):
    moderator_id: int
    form_status: 'FormStatus'
    updated_at: datetime


@dataclass
class UpdateUser:
    name: str = None
    surname: str = None
    middle_name: str = None
    email: str = None
    uni: str = None
    year_of_study: int = None
    group: str = None
    about_me: str = None
    resume: str = None
    avatar: str = None


@dataclass
class TeamMember(BaseUser):
    role: str
    technologies: list[str]
    about_me: str
    contact: str = None
    # avatar: str  # потом S3 прикрутим и сделаем это
    # feedbacks:  #


@dataclass
class User:
    updated_at: datetime
    id: int
    name: str
    surname: str
    middle_name: str = None
    uni: str = None
    year_of_study: int = None
    group: str = None
    about_me: str = None
    resume: str = None
    avatar: str = None
    moderator_id: int = None
    form_status: 'FormStatus' = None
    moderator_feedback: str = None
    is_form_private: bool = False
    technologies: list['Technology'] = None
    roles: list[str] = None
    hackathons: list['Hackathon'] = None
    sent_feedbacks: list[str] = None
    received_feedbacks: list[str] = None

    def __post_init__(self):
        if self.technologies is None:
            self.technologies = []
        if self.roles is None:
            self.roles = []
        if self.hackathons is None:
            self.hackathons = []
        if self.sent_feedbacks is None:
            self.sent_feedbacks = []
        if self.received_feedbacks is None:
            self.received_feedbacks = []
