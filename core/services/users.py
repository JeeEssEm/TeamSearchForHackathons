from .base import Service
from core.repositories import UsersRepository
from core.dtos import User, CreateUser, UpdateUser, BaseUser
from core.exceptions import NotFound


class UsersService(Service):
    repository: UsersRepository

    async def create_user(self, data: CreateUser) -> User:
        return await self.repository.create_user(data)

    async def get_user(self, user_id: int) -> User:
        return await self.repository.get_user_by_id(user_id)

    async def update_user(self, user_id: int, data: UpdateUser) -> User:
        return await self.repository.update_user(user_id, data)

    # async def delete_user(self, user_id: int):
    #     await self.repository.get_user_by_id(user_id)
    #     await self.repository.delete(user_id)

    async def get_form(self, moderator_id: int) -> User | None:
        moder_form = await self.repository.get_moderator_form(moderator_id)
        if not moder_form:
            moder_form = await self.repository.get_form(moderator_id)
        return moder_form

    async def get_form_by_id(self, form_id: int) -> User:
        return await self.repository.get_form_by_id(form_id)

    async def approve_user(self, user_id: int, moderator_id: int, feedback: str = None):
        await self.repository.change_user_form_state(user_id, moderator_id, approve=True, feedback=feedback)

    async def reject_user(self, user_id: int, moderator_id: int, feedback: str = None):        
        await self.repository.change_user_form_state(user_id, moderator_id, approve=False, feedback=feedback)

    async def get_all_short_forms(self):
        return await self.repository.get_all_forms()
