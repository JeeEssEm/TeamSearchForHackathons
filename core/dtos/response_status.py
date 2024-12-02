from enum import Enum


class ResponseStatus(Enum):
    object_created = 1  # объект успешно создан
    in_review = 2  # объект отправлен на модерацию
    already_exists = 3  # объект уже существует
