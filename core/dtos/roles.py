from dataclasses import dataclass
from typing import List


@dataclass
class CreateRole:
    title: str


@dataclass
class RoleView:
    id: int
    title: str
    users: List[int]


@dataclass
class UpdateRole:
    title: str


@dataclass
class Role(CreateRole):
    id: int
