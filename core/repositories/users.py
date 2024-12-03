from sqlalchemy import insert, delete, update
from core import models
from core.dtos import CreateUser
from core.exceptions import NotFound
from .base import Repository


class UsersRepository(Repository):
    async def _get_by_id(self, user_id: int) -> models.User:
        user = await self.session.get(models.User, user_id)
        if not user:
            raise NotFound("Пользователь не найден")
        return user

    async def create_user(self, data: CreateUser) -> models.User:
        user = models.User(**data.__dict__)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> models.User:
        result = await self.session.execute(
            select(models.User).filter(models.User.email == email)
        )
        user = result.scalars().first()
        if not user:
            raise NotFound("Пользователь с таким email не найден")
        return user

    async def update_user(self, user_id: int, data: CreateUser) -> models.User:
        user = await self._get_by_id(user_id)
        for key, value in data.__dict__.items():
            setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> None:
        user = await self._get_by_id(user_id)
        await self.session.delete(user)
        await self.session.commit()

    async def add_technologies(self, user_id: int, tech_ids: list[int]) -> None:
        stmt = insert(models.users_technologies).values(
            [
                {"user_id": user_id, "technology_id": tech_id}
                for tech_id in tech_ids
            ]
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_technologies(
        self, user_id: int, tech_ids: list[int]
    ) -> None:
        stmt = delete(models.users_technologies).where(
            models.users_technologies.c.user_id == user_id,
            models.users_technologies.c.technology_id.in_(tech_ids),
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_user_technologies(self, user_id: int) -> list:
        result = await self.session.execute(
            select(models.Technology)
            .join(models.users_technologies)
            .filter(models.users_technologies.c.user_id == user_id)
        )
        technologies = result.scalars().all()
        return technologies
