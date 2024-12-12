from dataclasses import dataclass
from datetime import date


@dataclass
class BaseHackathon:
    id: int
    title: str


@dataclass
class CreateHackathon(BaseHackathon):
    title: str
    start_date: date
    end_date: date


@dataclass
class Hackathon(CreateHackathon):
    id: int
