from dataclasses import dataclass
from .technologies import Technology


@dataclass
class CreateVacancy:
    description: str
    team_id: int
    role_id: int
    technologies: list[int]


@dataclass
class Vacancy(CreateVacancy):
    id: int


@dataclass
class VacancyView:
    id: int
    description: str
    team_id: int
    role: str
    role_id: int
    technologies: list[Technology]
