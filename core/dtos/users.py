from dataclasses import dataclass


@dataclass
class CreateUser:
    name: str
    surname: str
    middle_name: str = None
    email: str
    password: str
    uni: str = None
    year_of_study: int = None
    group: str = None  # Указываем значение по умолчанию
    about_me: str = None
    resume: str = None
    avatar: str = None


@dataclass
class BaseUser:
    id: int
    name: str
    surname: str
    middle_name: str


@dataclass
class UpdateUser:
    name: str = None
    surname: str = None
    middle_name: str = None
    email: str = None
    password: str = None
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
    description: str
    about_me: str
    # avatar: str  # потом S3 прикрутим и сделаем это
    # feedbacks:  #


@dataclass
class User:
    id: int
    name: str
    surname: str
    middle_name: str = None
    email: str
    uni: str = None
    year_of_study: int = None
    group: str = None
    about_me: str = None
    resume: str = None
    avatar: str = None
    form_status: bool = False
    is_form_private: bool = False
    technologies: list[str] = None
    roles: list[str] = None
    hackathons: list[str] = None
    sent_feedbacks: list[str] = None
    received_feedbacks: list[str] = None
    updated_at: str

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
