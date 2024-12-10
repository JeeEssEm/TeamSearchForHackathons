from typing import NamedTuple
from datetime import timedelta, timezone, datetime

from sqlalchemy import insert, delete, update, select, or_, and_, func

from core.dtos import CreateUser, User, BaseUser, Form, UpdateUser
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
        user.id = data.telegram_id

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return await user.convert_to_dto_user()

    async def update_user(self, user_id: int, data: UpdateUser) -> User:
        # Получаем пользователя из базы данных
        user = await self._get_by_id(user_id)
        # Обновляем данные пользователя

        if not data.year_of_study:  # ни дня без говнокода
            user.year_of_study = None

        if data.name is not None:
            user.name = data.name
        if data.surname is not None:
            user.surname = data.surname
        if data.middle_name is not None:
            user.middlename = data.middle_name
        if data.email is not None:
            user.email = data.email
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
        if not settings.TRUST_FACTOR:
            user.moderator_id = None
            user.form_status = models.FormStatus.in_review
            user.moderator_set_at = datetime.now(timezone.utc).date()

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
            models.User.form_status == models.FormStatus.in_review
        )
        res = await self.session.scalar(stmt)

        if not res:
            return None
        dto = await res.convert_to_dto_user()
        return self._convert_form(dto)

    async def set_moderator(self, moderator_id: int, user_id: int):
        user = await self._get_by_id(user_id)
        user.moderator_id = moderator_id
        user.moderator_set_at = datetime.now(timezone.utc).date()
        await self.session.commit()

    async def get_form(self, moderator_id: int) -> User | None:
        delta = timedelta(
            days=settings.MODERATOR_FORM_ROTATION_DAYS
        )
        today = datetime.now(timezone.utc) - delta
        stmt = select(models.User).where(or_(
            and_(
                models.User.moderator_id.is_not(None),
                models.User.moderator_set_at < today
            ),
            models.User.moderator_id.is_(None)
        )).where(models.User.form_status == models.FormStatus.in_review)

        res = await self.session.scalar(stmt)
        if not res:
            return None
        await self.set_moderator(moderator_id, res.id)
        await self.session.refresh(res)
        dto = await res.convert_to_dto_user()
        return self._convert_form(dto)

    async def change_user_form_state(self, user_id: int, moderator_id: int,
                                     approve=False,
                                     feedback=None):
        user = await self._get_by_id(user_id)
        user.moderator_id = moderator_id
        user.form_status = models.FormStatus.approved.value if approve else models.FormStatus.rejected.value
        user.moderator_feedback = feedback
        await self.session.commit()

    async def get_form_by_id(self, form_id: int) -> User:
        user = await self._get_by_id(form_id)
        return self._convert_form(await user.convert_to_dto_user())

    async def get_all_forms(self, page: int, limit: int, filters: dict) -> (int, list[Form]):
        stmt = select(models.User)
        count = select(func.count())

        if filters.get('moderator_id'):
            stmt = stmt.where(
                models.User.moderator_id == filters['moderator_id']
            )
        if filters.get('status'):
            stmt = stmt.where(
                models.User.form_status == filters['status']
            )
        count = select(func.count()).select_from(stmt.subquery())
        stmt = stmt.limit(limit).offset((page - 1) * limit)

        res = await self.session.scalars(stmt)
        count = await self.session.scalar(count)

        return count, list(
            map(lambda u: u.convert_to_dto_form(), res))

    async def get_teams(self, user_id: int) -> list[dict]:
        user = await self._get_by_id(user_id)
        return list(map(
            lambda t: {
                'id': t.id,
                'title': t.title,
            },
            await user.awaitable_attrs.teams)
        )

    async def set_technologies(self, user_id: int, tech_ids: list[int]) -> None:
        q = insert(models.users_technologies).values(
            [{'user_id': user_id, 'technology_id': t_id} for t_id in tech_ids]
        )
        await self.session.execute(q)
        await self.session.commit()

    async def delete_technology(self, user_id: int, tech_id: int):
        q = delete(models.users_technologies).where(
            models.users_technologies.c.user_id == user_id,
            models.users_technologies.c.technology_id == tech_id
        )
        await self.session.execute(q)
        await self.session.commit()

    async def set_roles(self, user_id: int, role_ids: list[int]):
        q = insert(models.users_roles).values(
            [{'user_id': user_id, 'role_id': r_id} for r_id in role_ids]
        )
        await self.session.execute(q)
        await self.session.commit()

    async def delete_all_roles(self, user_id: int):
        q = delete(models.users_roles).where(
            models.users_roles.c.user_id == user_id,
        )
        await self.session.execute(q)
        await self.session.commit()
