from dataclasses import dataclass

from .users import BaseUser
from .hackathons import BaseHackathon


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
    members: list[BaseUser]
    hacks: list[BaseHackathon]
