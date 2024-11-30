from enum import Enum
from dataclasses import dataclass
from typing import Optional
from technologies import ResponseStatus


@dataclass
class User:
    id: int
    telegram_id: int
    name: str
    middlename: Optional[str]
    surname: str
    email: str
    uni: Optional[str]
    year_of_study: Optional[int]
    group: Optional[str]
    about_me: Optional[str]
    resume: Optional[str]
    avatar: Optional[str]
    form_status: bool
    is_form_private: bool


@dataclass
class UserResponse:
    user: User | list[User]
    status: ResponseStatus
    message: Optional[str]
