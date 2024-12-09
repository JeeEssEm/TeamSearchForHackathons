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

    async def get_technologies(self, limit: int, page: int, sort: str = None) -> (int, list[Technology]):
        stmt = select(models.Technology)
        count = select(func.count()).select_from(stmt.subquery())

        sorts = {
            'asc': lambda query: query.order_by(models.Technology.title.asc()),
            'desc': lambda query: query.order_by(models.Technology.title.desc()),
        }

        if sort:
            stmt = sorts[sort](stmt)

        items = await self.session.scalars(stmt.limit(limit).offset((page - 1) * limit))
        count = await self.session.scalar(count)

        return count, list(map(lambda t: t.convert_to_dto(), items))

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

    async def search_technologies(self, title: str) -> list[Technology]:
        q = (select(models.Technology)
             .where(func.similarity(models.Technology.title, title) > 0.5)
             .order_by(func.similarity(models.Technology.title, title).desc())
             )
        res = await self.session.scalars(q)
        return list(map(lambda t: t.convert_to_dto(), res))
