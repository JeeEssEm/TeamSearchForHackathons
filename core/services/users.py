from .base import Service
from core.repositories import UsersRepository
from core.dtos import User, UserResponse, ResponseStatus
from typing import Optional


class UsersService(Service):
    repository: UsersRepository

    async def create_user(self, user_data: dict) -> UserResponse:
        """Создает пользователя с проверкой уникальности Telegram ID."""
        existing_user = await self.repository.get_by_telegram_id(
            user_data.get("telegram_id")
        )
        if existing_user:
            return UserResponse(
                status=ResponseStatus.already_exists,
                user=None,
                message="Пользователь с таким Telegram ID уже существует.",
            )
        created_user = await self.repository.create(user_data)
        return UserResponse(
            status=ResponseStatus.object_created,
            user=created_user.convert_to_dto(),
            message="Пользователь успешно создан.",
        )

    async def get_user_by_telegram_id(self, telegram_id: int) -> UserResponse:
        """Возвращает пользователя по Telegram ID."""
        user = await self.repository.get_by_telegram_id(telegram_id)
        if not user:
            return UserResponse(
                status=ResponseStatus.in_review,
                user=None,
                message="Пользователь не найден.",
            )
        return UserResponse(
            status=ResponseStatus.object_created,
            user=user.convert_to_dto(),
            message=None,
        )

    async def update_user(
        self, telegram_id: int, update_data: dict
    ) -> UserResponse:
        """Обновляет данные пользователя."""
        updated_user = await self.repository.update_user(
            telegram_id, update_data
        )
        if not updated_user:
            return UserResponse(
                status=ResponseStatus.in_review,
                user=None,
                message="Пользователь не найден.",
            )
        return UserResponse(
            status=ResponseStatus.object_created,
            user=updated_user.convert_to_dto(),
            message="Данные пользователя успешно обновлены.",
        )

    async def delete_user(self, telegram_id: int) -> UserResponse:
        """Удаляет пользователя по Telegram ID."""
        deleted = await self.repository.delete_user(telegram_id)
        if not deleted:
            return UserResponse(
                status=ResponseStatus.in_review,
                user=None,
                message="Пользователь не найден.",
            )
        return UserResponse(
            status=ResponseStatus.object_created,
            user=None,
            message="Пользователь успешно удален.",
        )

    async def get_all_users(
        self, limit: int = 100, offset: int = 0
    ) -> list[User]:
        """Возвращает список всех пользователей с пагинацией."""
        users = await self.repository.get_all_users(limit, offset)
        return [user.convert_to_dto() for user in users]
