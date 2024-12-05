from .base import Service
from core.repositories import UsersRepository
from core.dtos import User, CreateUser, UpdateUser
from core.exceptions import NotFound


class UsersService(Service):
    repository: UsersRepository

    async def create_user(self, data: CreateUser) -> User:
        return await self.repository.create_user(data)

    async def get_user(self, user_id: int) -> User:
        return await self.repository.get_user_by_id(user_id)

    async def update_user(self, user_id: int, data: UpdateUser) -> User:
        return await self.repository.update_user(user_id, data)

    async def delete_user(self, user_id: int):
        user = await self.repository._get_user_by_id(user_id)
        if not user:
            raise NotFound("Пользователь не найден")
        await self.repository.delete(user_id)
