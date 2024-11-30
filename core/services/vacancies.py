from .base import Service
from core.repositories import VacanciesRepository
from core.dtos import VacancyView, CreateVacancy


class VacanciesService(Service):
    repository: VacanciesRepository

    async def create_vacancy(self, data: CreateVacancy) -> VacancyView:
        vac = await self.repository.create_vacancy(data)
        await self.repository.add_technologies(vac.id, data.technologies)
        return await self.repository.get_by_id(vac.id)

    async def get_vacancy(self, vac_id: int) -> VacancyView:
        return await self.repository.get_by_id(vac_id)

    async def edit_vacancy(self, vac_id: int, data: CreateVacancy) -> VacancyView:
        if data.technologies:
            await self.repository.remove_all_technologies(vac_id)
            await self.repository.add_technologies(vac_id, data.technologies)
        return await self.repository.edit(vac_id, data)

    async def remove_vacancy(self, vac_id: int):
        await self.repository.delete(vac_id)
