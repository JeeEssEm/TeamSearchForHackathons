from datetime import timedelta, timezone, datetime

from sqlalchemy import insert, delete, update, select, or_, and_

from core.dtos import CreateUser, User, BaseUser, Form
from core.exceptions import NotFound
from core.config import settings
import core.models as models
from .base import Repository


class UsersRepository(Repository):
    async def _get_by_id(self, user_id: int) -> models.User:
        user = await self.session.get(models.User, user_id)
        if not user:
            raise NotFound("Пользователь не найден")
        return user

    async def get_baseuser_by_id(self, user_id: int) -> BaseUser:
        user = await self._get_by_id(user_id)
        return user.convert_to_dto_baseuser()

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self._get_by_id(user_id)
        return await user.convert_to_dto_user()

    async def create_user(self, data: CreateUser) -> User:
        user = models.User(**data.__dict__)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return await user.convert_to_dto_user()

    async def update_user(self, user_id: int, data: CreateUser) -> User:
        # Получаем пользователя из базы данных
        user = await self._get_by_id(user_id)

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

        return await user.convert_to_dto_user()

    def _convert_form(self, dto):
        dto.technologies = list(map(lambda t: t.title, dto.technologies))
        dto.roles = list(map(lambda t: t.title, dto.roles))
        return dto

    async def get_moderator_form(self, moderator_id: int) -> User | None:
        stmt = select(models.User).where(
            models.User.moderator_id == moderator_id,
            models.User.form_status == models.FormStatus.in_review.value
        )
        res = await self.session.scalar(stmt)

        if not res:
            return None
        dto = await res.convert_to_dto_user()
        return self._convert_form(dto)

    async def set_moderator(self, moderator_id: int, user_id: int):
        user = await self._get_by_id(user_id)
        user.moderator_id = moderator_id

        await self.session.commit()

    async def get_form(self, moderator_id: int) -> User | None:
        delta = timedelta(
            days=settings.MODERATOR_FORM_ROTATION_DAYS
        )
        today = datetime.now(timezone.utc)
        # FIXME: разобраться с датой ревью
        stmt = select(models.User).where(or_(
            and_(
                models.User.moderator_id.is_not(None),
                models.User.updated_at - today > delta
            ),
            models.User.moderator_id.is_(None)
        )).where(models.User.form_status == models.FormStatus.in_review.value)

        res = await self.session.scalar(stmt)
        if not res:
            return None
        await self.set_moderator(moderator_id, res.id)
        await self.session.refresh(res)
        dto = await res.convert_to_dto_user()
        return self._convert_form(dto)

    async def change_user_form_state(self, user_id: int, moderator_id: int, approve=False,
                                     feedback=None):
        user = await self._get_by_id(user_id)
        user.moderator_id = moderator_id
        user.form_status = models.FormStatus.approved.value if approve else models.FormStatus.rejected.value
        user.moderator_feedback = feedback
        await self.session.commit()
    
    async def get_form_by_id(self, form_id: int) -> User:
        user = await self._get_by_id(form_id)
        return self._convert_form(await user.convert_to_dto_user())

    async def get_all_forms(self) -> list[Form]:
        stmt = select(models.User)
        res = await self.session.scalars(stmt)
        return list(map(lambda u: u.convert_to_dto_form(), res))
