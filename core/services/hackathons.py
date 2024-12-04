from .base import Service
from core.repositories import HackathonsRepository
from core.dtos import CreateHackathon, BaseHackathon, Hackathon


class HackathonsService(Service):
    repository: HackathonsRepository

    async def create_hackathon(self, data: CreateHackathon) -> Hackathon:
        hackathon = await self.repository.create_hackathon(data)
        return await self.repository.create(hackathon.id)
