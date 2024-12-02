from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from typing import Union
from dtos.response_status import ResponseStatus


@dataclass
class User:
    telegram_id: int
    name: str
    surname: str
    middlename: Optional[str]
    email: str
    uni: Optional[str]
    year_of_study: Optional[int]
    group: Optional[str]
    about_me: Optional[str]
    resume: Optional[str]
    avatar: Optional[str]
    moderator_id: int
    updated_at: datetime
    form_status: bool
    is_form_private: bool


class UserResponse:
    """DTO для ответа операций с пользователем."""

    status: ResponseStatus  # Статус операции
    user: Optional[Union[User, List[User]]] = (
        None  # Один пользователь или список
    )
    message: Optional[str] = (
        None  # Сообщение об ошибке или дополнительная информация
    )
