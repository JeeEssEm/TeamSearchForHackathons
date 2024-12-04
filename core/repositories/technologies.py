from sqlalchemy import select, delete, func

from .base import Repository
import core.models as models
from core.dtos import Technology
from core.exceptions import NotFound


class TechnologiesRepository(Repository):
    async def _get_by_id(self, tech_id: int) -> models.Technology:
        tech = await self.session.get(models.Technology, tech_id)
        if not tech:
            raise NotFound('Технология не найдена')
        return tech

    async def create(self, title: str) -> Technology:
        tech = models.Technology(title=title)
        self.session.add(tech)
        await self.session.commit()
        return tech.convert_to_dto()

    async def get_technologies(self, limit: int, page: int) -> list[Technology]:
        stmt = select(models.Technology)
        q = select(models.Technology, func.count())

        items = await self.session.execute(stmt.limit(limit).offset((page - 1) * limit))
        count = await self.session.execute(q)
        #         # .order_by(models.Technology.created_at)
        #         )
        # total_stmt = select(func.count(models.Technology)).select_from(
        #     stmt.subquery()
        # )
        # total = await self.session.scalar(total_stmt)
        # techs = await self.session.scalars(stmt.limit(limit).offset((page - 1) * limit))
        # print(total, techs)
        return count.first()[1], list(map(lambda t: t.convert_to_dto(), items.scalars()))

    async def get_technologies_by_id(self, ids: list[int]) -> list[Technology]:
        stmt = select(models.Technology).where(models.Technology.id.in_(ids))
        res = await self.session.execute(stmt)
        return list(map(lambda t: t.convert_to_dto(), res.scalars()))

    async def get_by_id(self, tech_id: int) -> Technology:
        return (await self._get_by_id(tech_id)).convert_to_dto()

    async def edit(self, tech_id: int, title: str) -> Technology:
        tech = await self._get_by_id(tech_id)
        tech.title = title
        await self.session.commit()
        return tech.convert_to_dto()

    async def delete_technologies_by_id(self, ids: list[int]):
        stmt = delete(models.Technology).where(models.Technology.id.in_(ids))
        await self.session.execute(stmt)
        await self.session.commit()

    async def check_if_same_exists(self, title: str) -> bool:
        return False

    async def get_same_technologies(self, title: str) -> list[Technology]:
        return [...]
