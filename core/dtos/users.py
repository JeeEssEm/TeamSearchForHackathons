from dataclasses import dataclass


@dataclass
class BaseUser:
    id: int
    name: str
    surname: str
    middle_name: str


@dataclass
class TeamMember(BaseUser):
    role: str
    technologies: list[str]
    description: str
    about_me: str
    # avatar: str  # потом S3 прикрутим и сделаем это
    # feedbacks:  #
