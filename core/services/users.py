from .base import Service
from core.repositories.users import UsersRepository
from core.dtos.users import UserResponse, UserResponseStatus


class UsersService(Service):
    repository: UsersRepository

    async def create_user(
        self, telegram_id: int, name: str, surname: str, email: str
    ) -> UserResponse:
        if await self.repository.check_if_email_exists(email):
            return UserResponse(
                status=UserResponseStatus.already_exists,
                user=[],
                message="Пользователь с таким email уже существует",
            )

        user = await self.repository.create(telegram_id, name, surname, email)
        return UserResponse(
            status=UserResponseStatus.created, user=user, message=None
        )

    async def get_user_by_telegram_id(self, telegram_id: int) -> UserResponse:
        user = await self.repository.get_by_telegram_id(telegram_id)
        if not user:
            return UserResponse(
                status=UserResponseStatus.already_exists,
                user=[],
                message="Пользователь не найден",
            )
        return UserResponse(
            status=UserResponseStatus.created, user=user, message=None
        )

    async def update_user(self, user_id: int, **fields) -> UserResponse:
        try:
            user = await self.repository.update_user(user_id, **fields)
            return UserResponse(
                status=UserResponseStatus.updated,
                user=user,
                message="Пользователь успешно обновлен",
            )
        except ValueError as e:
            return UserResponse(
                status=UserResponseStatus.already_exists,
                user=[],
                message=str(e),
            )
