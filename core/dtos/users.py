from dataclasses import dataclass


@dataclass
class BaseUser:
    id: int
    name: str
    surname: str
    middle_name: str
