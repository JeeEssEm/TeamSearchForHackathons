import os
import sys
from pathlib import Path

from dataclasses import dataclass
from environs import Env
import other.states

from aiogram.fsm.state import State, StatesGroup

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(PROJECT_ROOT)


@dataclass
class TgBot:
    token: str


@dataclass
class BaseUser:
    avatar: str | None
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
        
        return (f"""User ID: {self.user_id}
Email: {self.email}
Last Name: {self.last_name}
First Name: {self.first_name}
Middle Name: {self.middle_name}
University: {self.university}
Course: {self.course}
Group: {self.group}
Roles: {", ".join(self.roles)}""")


class ExtendedUser(BaseUser):
    roles: list
    technologies: list
    
    # achievements: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')))
