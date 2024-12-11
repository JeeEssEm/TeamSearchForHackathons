from datetime import datetime

from sqlalchemy import select, func, asc, desc

from .base import Repository
from core.dtos import CreateHackathon, Hackathon
from core import models
from core.exceptions import NotFound


class HackathonsRepository(Repository):
    async def _get(self, hack_id: int) -> models.Hackathon:
        hack = await self.session.get(models.Hackathon, hack_id)
        if not hack:
            raise NotFound('Хакатон не найден')
        return hack

    async def create(self, data: CreateHackathon) -> Hackathon:
        hack = models.Hackathon(
            title=data.title, start_date=data.start_date, end_date=data.end_date
        )
        self.session.add(hack)
        await self.session.commit()
        return hack.convert_to_dto()

    async def get_list(self, page: int, limit: int, filters: dict) -> (int, list[Hackathon]):
        today = datetime.today().date()
        date_filters = {
            'on_going': lambda q: q.where(
                models.Hackathon.start_date <= today,
                models.Hackathon.end_date >= today,
            ),
            'ended': lambda q: q.where(
                models.Hackathon.end_date < today,
            ),
            'future': lambda q: q.where(
                models.Hackathon.start_date > today,
            ),
        }
        sorting = {
            'sort_start_date': lambda q, s:
                q.order_by(models.Hackathon.start_date.asc()) if s == 'asc'
                else q.order_by(models.Hackathon.start_date.desc()),
            'sort_end_date': lambda q, s:
                q.order_by(models.Hackathon.end_date.asc()) if s == 'asc'
                else q.order_by(models.Hackathon.end_date.desc()),
        }
        stmt = select(models.Hackathon)
        date = filters.get('date')
        sort_start_date = filters.get('sort_start_date')
        sort_end_date = filters.get('sort_end_date')

        if date:
            stmt = date_filters[date](stmt)
        if sort_start_date:
            stmt = sorting['sort_start_date'](stmt, sort_start_date)
        if sort_end_date:
            stmt = sorting['sort_end_date'](stmt, sort_end_date)

        count = select(func.count()).select_from(stmt.subquery())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        total = await self.session.scalar(count)
        res = await self.session.scalars(stmt)

        return total, list(map(lambda h: h.convert_to_dto(), res))

    async def get(self, hack_id: int) -> Hackathon:
        hack = await self._get(hack_id)
        return hack.convert_to_dto()

    async def update(self, hack_id: int, data: CreateHackathon) -> Hackathon:
        hack = await self._get(hack_id)
        hack.title = data.title or hack.title
        hack.start_date = data.start_date or hack.start_date
        hack.end_date = data.end_date or hack.end_date
        await self.session.commit()
        return hack.convert_to_dto()

    async def get_hacks_by_ids(self, hack_ids: list[int]) -> list[Hackathon]:
        q = select(models.Hackathon).where(
            models.Hackathon.id.in_(hack_ids)
        )
        res = await self.session.scalars(q)
        return list(map(lambda h: h.convert_to_dto(), res))
