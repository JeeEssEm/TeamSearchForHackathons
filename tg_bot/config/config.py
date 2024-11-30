from dataclasses import dataclass
from environs import Env

from aiogram.fsm.state import State, StatesGroup


@dataclass
class TgBot:
    token: str


@dataclass
class BaseUser:
    user_id: str
    email: str
    last_name: str
    first_name: str
    middle_name: str
    university: str
    course: int
    group: str

    roles: list[str]

    def __str__(self):
        print(type(self.roles))

        return f"""User ID: {self.user_id}
Email: {self.email}
Last Name: {self.last_name}
First Name: {self.first_name}
Middle Name: {self.middle_name}
University: {self.university}
Course: {self.course}
Group: {self.group}
Roles: {", ".join(self.roles)}"""


class ExtendedUser(BaseUser):
    roles: list

    # achivements: str


class UserForm(StatesGroup):
    user_id = State()
    email = State()
    last_name = State()
    first_name = State()
    middle_name = State()
    university = State()
    course = State()
    group = State()
    roles = State()


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env("BOT_TOKEN")))
