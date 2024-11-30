from .base import Repository
import core.models as models
from core.dtos.users import UserDTO


class UsersRepository(Repository):
    async def create(
        self, telegram_id: int, name: str, surname: str, email: str
    ) -> UserDTO:
        user = models.User(
            telegram_id=telegram_id, name=name, surname=surname, email=email
        )
        self.session.add(user)
        await self.session.commit()
        return user.convert_to_dto()

    async def get_by_telegram_id(self, telegram_id: int) -> UserDTO | None:
        result = await self.session.execute(
            select(models.User).where(models.User.telegram_id == telegram_id)
        )
        user = result.scalars().first()
        return user.convert_to_dto() if user else None

    async def check_if_email_exists(self, email: str) -> bool:
        result = await self.session.execute(
            select(models.User).where(models.User.email == email)
        )
        return result.scalars().first() is not None

    async def update_user(self, user_id: int, **fields) -> UserDTO:
        result = await self.session.execute(
            select(models.User).where(models.User.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            raise ValueError("User not found")

        for key, value in fields.items():
            setattr(user, key, value)

        await self.session.commit()
        return user.convert_to_dto()
