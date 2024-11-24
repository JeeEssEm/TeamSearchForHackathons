from enum import Enum

from dataclasses import dataclass


class ResponseStatus(Enum):
    object_created = 1  # объект успешно создан
    in_review = 2  # объект отправлен на модерацию
    already_exists = 3  # объект уже существует


@dataclass
class Technology:
    id: int
    title: str


@dataclass
class TechnologyResponse:
    technology: Technology | list[Technology]
    status: ResponseStatus
    message: str | None
