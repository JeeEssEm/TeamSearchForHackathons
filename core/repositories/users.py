from sqlalchemy import insert, delete, update, select
from core.dtos import CreateUser, User, BaseUser
from core.exceptions import NotFound
from .base import Repository
import core.models as models


class UsersRepository(Repository):
    async def _get_by_id(self, user_id: int) -> models.User:
        user = await self.session.get(user_id)
        if not user:
            raise NotFound("Пользователь не найден")
        return user

    async def get_baseuser_by_id(self, user_id: int) -> BaseUser:
        user = await self._get_by_id(user_id)
        return await user.convert_to_dto_baseuser()

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self._get_by_id(user_id)
        return await user.convert_to_dto_user()

    async def create_user(self, data: CreateUser) -> User:
        user = models.User(**data.__dict__)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user.convert_to_dto_user()

    async def update_user(self, user_id: int, data: CreateUser) -> User:
        # Получаем пользователя из базы данных
        user = await self._get_user_by_id(user_id)

        # Обновляем данные пользователя
        if data.name is not None:
            user.name = data.name
        if data.surname is not None:
            user.surname = data.surname
        if data.middle_name is not None:
            user.middlename = data.middle_name
        if data.email is not None:
            user.email = data.email
        if data.password is not None:
            user.password = data.password
        if data.uni is not None:
            user.uni = data.uni
        if data.year_of_study is not None:
            user.year_of_study = data.year_of_study
        if data.group is not None:
            user.group = data.group
        if data.about_me is not None:
            user.about_me = data.about_me
        if data.resume is not None:
            user.resume = data.resume
        if data.avatar is not None:
            user.avatar = data.avatar

        await self.session.commit()
        await self.session.refresh(user)

        return user.convert_to_dto_user()
