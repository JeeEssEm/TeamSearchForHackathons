from .base import Service
from core.repositories import UsersRepository
from core.dtos import User, CreateUser, UpdateUser, BaseUser, Form
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

    async def get_all_short_forms(self, page: int, filters: dict, limit: int = 10) -> (int, list[Form]):
        return await self.repository.get_all_forms(page, limit, filters)

    async def set_user_technologies(self, user_id: int, techs: list[int]):
        await self.repository.set_technologies(user_id, techs)

    async def delete_user_technology(self, user_id: int, tech_id: int):
        await self.repository.delete_technology(user_id, tech_id)

    async def set_user_roles(self, user_id: int, roles: list[int]):
        await self.repository.set_roles(user_id, roles)

    async def delete_user_roles(self, user_id: int):
        await self.repository.delete_all_roles(user_id)

    async def set_user_hacks(self, user_id: int, hack_ids: list[int]):
        await self.repository.set_hacks(user_id, hack_ids)

    async def delete_user_hacks(self, user_id: int):
        await self.repository.delete_all_hacks(user_id)
