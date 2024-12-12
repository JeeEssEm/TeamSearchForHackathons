from dataclasses import dataclass

from .users import TeamMember
from .hackathons import Hackathon
from .vacancies import VacancyView


@dataclass
class BaseTeam:
    captain_id: int
    title: str
    description: str


@dataclass
class CreateTeam(BaseTeam):
    hacks: list[int]


@dataclass
class Team(CreateTeam):
    id: int
    members: list[TeamMember]
    hacks: list[Hackathon]
    vacancies: list[VacancyView]


@dataclass
class EditTeam:
    title: str | None = None
    description: str | None = None
