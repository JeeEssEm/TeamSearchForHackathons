from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from core.database import AsyncSession
from core.models import User
from .base import Repository


class UsersRepository(Repository):
    async def create(self, user_data: dict) -> User:
        """Создает нового пользователя."""
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Получает пользователя по Telegram ID."""
        query = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return query.scalar_one_or_none()

    async def update_user(
        self, telegram_id: int, update_data: dict
    ) -> User | None:
        """Обновляет данные пользователя."""
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            return None
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.session.commit()
        return user

    async def delete_user(self, telegram_id: int) -> bool:
        """Удаляет пользователя по Telegram ID."""
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            return False
        await self.session.delete(user)
        await self.session.commit()
        return True

    async def get_all_users(
        self, limit: int = 100, offset: int = 0
    ) -> list[User]:
        """Возвращает список пользователей с пагинацией."""
        query = await self.session.execute(
            select(User).offset(offset).limit(limit)
        )
        return query.scalars().all()
