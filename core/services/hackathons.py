from .base import Service
from core.repositories import HackathonsRepository
from core.dtos import CreateHackathon, BaseHackathon, Hackathon


class HackathonsService(Service):
    repository: HackathonsRepository

    async def create_hackathon(self, data: CreateHackathon) -> Hackathon:
        return await self.repository.create(data)

    async def get_hacks_list(self, filters: dict, page: int, limit: int = 10) -> (int, list[Hackathon]):
        return await self.repository.get_list(page, limit, filters)

    async def get_hack(self, hack_id: int) -> Hackathon:
        return await self.repository.get(hack_id)

    async def edit_hack(self, hack_id: int, data: CreateHackathon) -> Hackathon:
        return await self.repository.update(hack_id, data)
