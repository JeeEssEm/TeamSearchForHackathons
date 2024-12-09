from sqlalchemy import select, func

from .base import Repository

from core import models
from core.dtos import CreateWish, Wish
from core.exceptions import NotFound


class WishesRepository(Repository):
    async def _get(self, wid: int) -> models.Wish:
        w = await self.session.get(models.Wish, wid)
        if not w:
            raise NotFound('Фидбек не найден')
        return w

    async def get_by_id(self, wid: int) -> Wish:
        w = await self._get(wid)
        return w.convert_to_dto()

    async def get_wishes(self, page: int, limit: int, archived: bool) -> (int, list[Wish]):
        q = select(models.Wish).where(models.Wish.is_archived == archived)
        count = select(func.count()).select_from(q.subquery())

        total = await self.session.scalar(count)
        q = q.limit(limit).offset((page - 1) * limit)
        res = await self.session.scalars(q)

        return total, list(map(lambda w: w.convert_to_dto(), res))

    async def move_to_archive(self, wid: int, moderator_id: int):
        wish = await self._get(wid)
        wish.is_archived = True
        wish.moderator_id = moderator_id
        await self.session.commit()

    async def move_to_non_archive(self, wid: int):
        wish = await self._get(wid)
        wish.archived = False
        await self.session.commit()

    async def create_wish(self, data: CreateWish) -> Wish:
        wish = models.Wish(
            user_id=data.user_id,
            description=data.description
        )
        self.session.add(wish)
        await self.session.commit()
        return wish.convert_to_dto()

    async def make_feedback(self, wid: int, moderator_id: int, feedback: str):
        w = await self._get(wid)
        w.moderator_id = moderator_id
        w.feedback = feedback
        await self.session.commit()
