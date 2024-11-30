from .base import Repository
from core.dtos import CreateHackathon, Hackathon
from core import models


class HackathonsRepository(Repository):
    async def create(self, data: CreateHackathon) -> Hackathon:
        hack = models.Hackathon(
            title=data.title, start_date=data.start_date, end_date=data.end_date
        )
        self.session.add(hack)
        await self.session.commit()
        return hack.convert_to_dto()
