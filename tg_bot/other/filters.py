from aiogram.filters import Filter
from aiogram.types import Message

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.repositories import UsersRepository
from core.exceptions import NotFound


@inject
async def is_registered(user_id, db=Provide[Container.db]):
    async with db.session() as session:
        repo = UsersRepository(session)
        try:
            await repo.get_user_by_id(user_id)
            return True
        except NotFound:
            return False


class IsReg(Filter):
    async def __call__(self, message: Message) -> bool:
        return await is_registered(message.from_user.id)
