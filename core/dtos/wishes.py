from dataclasses import dataclass


@dataclass
class CreateWish:
    user_id: int
    description: str


@dataclass
class Wish(CreateWish):
    id: int
    moderator_response: str
    moderator_id: int
    is_archived: bool
