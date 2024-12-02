from core.dtos.response_status import ResponseStatus
from dataclasses import dataclass


@dataclass
class Technology:
    id: int
    title: str


@dataclass
class TechnologyResponse:
    technology: Technology | list[Technology]
    status: ResponseStatus
    message: str | None
